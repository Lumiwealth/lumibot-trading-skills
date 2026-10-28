---
name: stock-etf-strategies
title: Stock and ETF Strategies in LumiBot
description: Load before writing, editing, debugging or backtesting a LumiBot strategy that trades stocks or ETFs, including rotation, rebalancing, momentum, trend following, moving-average crossovers, breakouts, opening-range breakouts, mean reversion, RSI or Bollinger setups, and baskets, or when a stock backtest makes no trades. Covers universe choice, warmup history, cash-bounded sizing, fractional shares, rebalancing, market hours, gaps, benchmarks and BotSpot backtest workflow.
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

# Stock and ETF Strategies in LumiBot

This skill helps an AI agent write correct stock and ETF strategies with LumiBot
(https://github.com/Lumiwealth/lumibot, docs at https://lumibot.lumiwealth.com),
then backtest and deploy them on BotSpot (https://botspot.trade).

Related skills: `lumibot-strategy-building` (lifecycle and structure),
`lumibot-api-reference` (API details), `lumibot-indicators` (computing and
charting indicators), `fast-lumibot-strategies` (speed), `options-strategies`
(anything with options), `using-botspot-mcp` (tool workflow).

Nothing here is investment advice. Symbols, lookbacks and thresholds in
examples illustrate mechanics, not recommendations.

Reference files (load with `skills` action=get, name=stock-etf-strategies,
reference=<path>):

- `references/moving-average-strategy.md`: SMA and EMA crossovers and trend
  filters, with a complete example.
- `references/breakout-strategy.md`: channel, Donchian and opening-range
  breakouts, with session timing.
- `references/mean-reversion-strategy.md`: RSI, Bollinger Band and z-score
  setups.
- `references/rotation-and-rebalancing.md`: momentum rotation, fixed-weight
  portfolios and rebalancing with cash-bounded sizing.

---

## 1. Before writing code: pin down the rules

Know these before you write the first line:

1. **Universe.** The exact symbols, or how to choose them.
2. **Bar size.** Daily or intraday (and which interval).
3. **Signals.** Entry and exit conditions with exact lookbacks and thresholds.
4. **Sizing.** Fixed dollars, percent of portfolio, equal weight, target
   weights, or risk-based (stop distance or volatility).
5. **Timing.** When decisions happen (at the open, before the close, every
   N minutes) and how often to rebalance.
6. **Exits and risk.** Stops, targets, time exits, max positions, max weight
   per position, whether shorting is allowed.

Implement the user's rules exactly. If a rule is ambiguous, ask one precise
question rather than guessing. Never add your own extra filters or
confirmations.

---

## 2. Choosing a universe

- Prefer liquid US-listed stocks and ETFs (for example SPY, QQQ, IWM, DIA,
  GLD, TLT, or the exact symbols the user named). Liquid symbols have complete
  history and realistic fills.
- Keep the universe explicit and small to start. A strategy that needs
  screening data for thousands of stocks (fundamentals, full-market scans)
  may not have that data available in backtests. Start with a named list and
  explain that it can grow later.
- When the user says "gold" or "silver" without asking for spot or futures,
  an ETF such as GLD or SLV is the usual stock-account substitute. Say so
  plainly before using it.
- Survivorship: a hand-picked list of today's winners makes any backtest look
  better than reality. Mention this when a user builds a universe from current
  favorites.
- Create assets explicitly: `Asset("SPY", asset_type=Asset.AssetType.STOCK)`.
  ETFs use the stock asset type.

---

## 3. Data: history, warmup and point-in-time correctness

```python
bars = self.get_historical_prices(asset, length=250, timestep="day")
if bars is None or bars.df is None or bars.df.empty:
    self.log_message(f"No history for {asset.symbol}", color="yellow")
    return
df = bars.df  # columns include open, high, low, close, volume
```

- **Request enough history.** The length must cover the longest lookback plus
  a margin (for a 200-day average, ask for 250 or more). Requesting fewer bars
  than the lookback means the indicator is never computed and the strategy
  silently never trades.
- **Completed bars only.** Historical bars describe completed periods. In a
  daily strategy the last row is normally the most recent completed day, not
  today's unfinished session. Do not read a future close, and do not relabel
  the prior bar's open as "today's open".
- **Signal price versus execution price.** Compute signals from completed
  bars. Size and place orders from the current price
  (`self.get_last_price(asset)`). A stale close used for sizing can produce
  wrong quantities.
- **Batch history for a universe.** Use
  `self.get_historical_prices_for_assets(assets, length, timestep)` instead of
  looping one symbol at a time, and `self.get_last_prices(assets)` for current
  prices. See `fast-lumibot-strategies` for more.
- **Guard every value.** Indicators return None or NaN early in a series or
  when data is missing. Check before comparing.
- **Corporate actions.** Splits and dividends affect price history. Use the
  data source's adjusted data where the strategy depends on long lookbacks,
  and never assume a sudden price jump is a signal without considering a
  split.

For indicator computation (`self.indicators.sma(...)` and friends) and chart
output, load the `lumibot-indicators` skill.

---

## 4. Sizing that never overspends

Base every order on current account state:

```python
cash = self.get_cash()
portfolio_value = self.get_portfolio_value()
price = self.get_last_price(asset)
if price is None or price <= 0:
    return

target_value = portfolio_value * weight          # weight from the user's rule
target_value = min(target_value, cash * 0.99)    # never spend more than cash
quantity = int(target_value // price)            # whole shares
if quantity <= 0:
    self.log_message(f"Order too small for {asset.symbol}", color="yellow")
    return
order = self.create_order(asset, quantity, "buy")
self.submit_order(order)
```

Rules:

- **Never exceed cash** unless the user explicitly wants margin and the broker
  allows it. Keep a small buffer for price movement between decision and fill.
- **Account for open orders.** Cash does not drop until a buy fills. If you
  submit several buys in one iteration, subtract each order's estimated cost
  from a local cash budget before sizing the next.
- **Sell before you buy when rotating.** Sales free cash only after they fill.
  In a backtest, market sales normally fill at the next available price; live,
  wait for the fill (check on the next iteration, or in `on_filled_order`)
  before sizing the replacement from updated cash.
- **Zero quantity means no trade.** Skip and log; do not round up.
- **Risk-based sizing.** With a stop, per-share risk is `entry - stop`;
  `quantity = floor(risk_budget / per_share_risk)`, then cap by cash.

### Fractional shares

LumiBot accepts fractional quantities (a float or `Decimal`), and backtests
fill them. Live support depends on the broker and order type (some brokers
allow fractional quantities only for market or day orders, and some not at
all). If the user wants fractional shares, round to the precision the broker
allows (for example `round(target_value / price, 4)`) and confirm the
deployment broker supports it. Default to whole shares otherwise.

---

## 5. Orders and positions

- `self.create_order(asset, quantity, side, limit_price=None, stop_price=None, ...)`
  then `self.submit_order(order)`. Side is "buy" or "sell".
- Market orders are simplest for daily strategies. Use limit orders priced
  from the current price, not from a historical close (a buy limit below the
  current price often never fills).
- Bracket and OCO exits: pass `secondary_limit_price` (take profit) and
  `secondary_stop_price` (stop) with the appropriate `order_class` if the user
  wants exits attached to the entry. Broker support varies.
- Read positions with `self.get_position(asset)` (None when flat) and
  `self.get_positions()`. Quantities are signed.
- One intended change, one order. If an order for the same position change is
  still open (`order.is_active()`), do not submit another. Check
  `self.get_orders()` once per iteration, not inside a per-symbol loop.
- `self.sell_all()` closes everything; use it only when the rules say so.
- Shorting requires the broker to allow it and the user to want it.

---

## 6. Market hours, timing and gaps

- `self.sleeptime` controls how often `on_trading_iteration` runs (for example
  "1D", "60M", "5M"). Daily strategies normally use "1D".
- `self.set_market("NYSE")` (or "NASDAQ", the default) sets trading hours for
  US equities. Use "24/7" only for crypto.
- `self.minutes_before_closing` (default 5) sets how early iterations stop
  before the close; `before_market_closes()` runs near the close and
  `before_market_opens()` runs before the open.
- Intraday entries must happen inside the session. Compare times with
  timezone-aware datetimes from `self.get_datetime()`; a naive comparison can
  skip the whole session.
- **Gaps.** Prices can open far from the prior close. A stop placed on the
  prior close may fill much worse at the open. Logic that compares "today's
  open" to a level must use a real current price, not the previous bar.
- **Holidays and half days.** Do not assume every weekday trades. Use the
  bars you actually received.

---

## 7. Rebalancing

For target-weight portfolios and rotation strategies:

1. Compute target weights from the user's rule.
2. Compute current weights from positions and current prices.
3. Sell overweight positions first, then buy underweight ones with the cash
   actually available.
4. Use a tolerance band (for example skip trades under 1 to 2 percent of
   portfolio value) only if the user wants one; it reduces churn.
5. Track the last rebalance date in `self.vars` so a restart does not trigger
   an extra rebalance.

Load `references/rotation-and-rebalancing.md` for complete examples.

---

## 8. State and restarts

Store anything the strategy must remember (last rebalance date, entry prices,
stop levels) in `self.vars`. Initialize every field in `initialize()` and read
with `self.vars.get(name, default)`, because a restored bot may have state
saved before a new field existed. Derive "am I in a position" from
`self.get_position(...)`, not from a flag alone.

---

## 9. Benchmarks and honest evaluation

- LumiBot backtests compare the strategy to a benchmark (SPY by default) in
  the tearsheet. For a sector or single-asset strategy, also compare to simply
  holding the same asset or universe over the same window.
- A short window can show nothing or mislead. Daily crossover systems may
  trade only a few times a year. Choose a window that fits the rules, and say
  plainly when an affordable test may show no trade.
- Backtest results are simulations. Do not present them as expected returns.

---

## 10. Building and testing on BotSpot with MCP tools

1. `create_strategy` for a new workspace, or `list_strategies` and
   `get_strategy` for an existing one. `marketplace_strategies` and
   `clone_strategy` let the user start from a published strategy.
2. `get_file` for `main.py`, then `replace_file` (whole file) or `patch_file`
   (targeted edit) with the returned `editHandle`. Read the result back with
   `get_file`.
3. `start_backtest` with `revisionId`, `startDate` and `endDate`. Stocks and
   ETFs work on BotSpot's default data route; pass `dataProvider` only if the
   user wants a specific source. Only start a backtest when the user wants one.
4. `backtest_status` to follow progress.
5. `get_backtest_logs` for errors and your `log_message` output;
   `get_backtest_artifact` then `query_csv` on the trades or indicators
   artifact; `show_backtest_dashboard` or `get_backtest_visuals` for charts.
6. `list_revisions` and `set_strategy_revision` to compare or roll back.
7. `start_deployment` only when the user asks. Deployment and every
   real-money action need the user's approval on botspot.trade.

---

## 11. When a backtest makes no trades

Work through these in order:

1. **Window too short.** Daily rules can need months to fire once. If so,
   rerun the same saved revision over a longer window without editing.
2. **Warmup not requested.** Fewer bars than the longest lookback means the
   indicator is never ready (a code bug).
3. **Session or timezone logic** skips the trading period, or an entry runs
   after the close guard (a code bug).
4. **Sizing returns zero** because of a stale or missing price, or too little
   cash.
5. **Too many confirmations** that never agree in the window (a rules issue).

Use `get_backtest_logs` (search for "Skip", "No history", "Traceback") and
the indicators artifact to see which condition blocked. Fix proven code
defects without changing rules. If the user's own rules never fire in an
adequate window, explain why in plain words and offer specific choices (a
longer test, one exact threshold change, or dropping one named filter).
Change nothing until the user picks. Never add an artificial buy just to make
a test trade, and never change the strategy type (for example mean reversion
into trend following) without approval.

The pattern references each contain pattern-specific no-trade causes.
