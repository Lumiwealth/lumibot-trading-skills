> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

- Never add markers on every trading iteration! this creates a HUGE mess. Use add_ohlc for price candles (bars), add_line for continuous single-value indicators like moving averages, and add_marker for infrequent events like buy/sell signals. For example: self.add_ohlc("SPY", open=o, high=h, low=l, close=c, dt=dt, asset=spy_asset), self.add_line("SPY_SMA20", sma_value, dt=dt, asset=spy_asset), self.add_marker("buy_signal", price, color="green", symbol="arrow-up", dt=dt, asset=spy_asset).
- It's worth repeating: add_marker() should be rare, never on every iteration because it will crash the chart. Charts cannot handle too many markers, so use them sparingly. Use add_ohlc() for price bars and add_line() for continuous indicators.
- Chart panel rule: when you have `asset=...`, keep overlays on that asset chart and avoid `plot_name` by default. Use `plot_name` only for intentionally separate panes (RSI/MACD/Stochastic/etc.), and keep pane count small unless the user explicitly asks for many panes.
- CRITICAL: add_ohlc(), add_line(), and add_marker() do NOT have a 'text' parameter - using 'text=' will cause a TypeError! The correct signatures are:
  - add_ohlc(name, open, high, low, close, color=None, detail_text=None, dt=None, asset=None) - Example: self.add_ohlc("SPY", open=o, high=h, low=l, close=c, detail_text="SPY Price", asset=my_asset)
  - add_line(name, value, color=None, style='solid', width=None, detail_text=None, dt=None, asset=None) - Example: self.add_line("SMA_20", sma_value, color="blue", detail_text="20-day moving average", asset=my_asset)
  - add_marker(name, value, color=None, symbol='circle', size=None, detail_text=None, dt=None, asset=None) - Example: self.add_marker("Buy Signal", price, color="green", symbol="arrow-up", detail_text="Bullish crossover", asset=my_asset)
  - Use 'name' (first param) for the label and 'detail_text' for hover text. There is NO 'text' parameter!
- RETROACTIVE INDICATORS (PREFERRED): For most charting (support/resistance, trendlines, patterns, signals), draw retroactively using the dt parameter. Use `for dt in self.get_historical_prices(asset, 30, "day").df.index: self.add_line(...)` or store datetimes in self.vars and loop back. Only draw per-iteration for simple deterministic indicators like EMAs/RSI.
- When a value should stay constant across time (support levels, detected patterns), LOCK it in self.vars when first detected and keep outputting that same locked value. Recalculating each iteration causes jagged/noisy visuals.
- 🚨 UPGRADE TO add_ohlc(): If you see a strategy using add_line() to track raw asset prices (e.g., close prices), you should STRONGLY RECOMMEND upgrading to add_ohlc(). The add_ohlc() method provides full candlestick visualization (open, high, low, close) which is far more valuable for understanding price action than a simple line chart. This upgrade significantly improves the user's ability to analyze their strategy. Unless the user explicitly declines, always suggest this upgrade when refining strategies that use add_line() for price data.
- Remember the options are x100, so you have to multiply the price by 100 to get the correct price for the option. For example, if the price of the option is 0.5, then the price of the option is actually 50 dollars. So you have to multiply the price by 100 to get the correct price for the option. So far example if I tell you to use 10% of the account and the option is trading at 1.50 and you have 100,000 in the account, then you have to use 10% of 100,000 which is 10,000 and then divide that by 100 to get the correct amount of options to buy. So in this case you would buy 10,000 / 1.50 / 100 = 66.67 options. So you would buy 66 options.
- Remember that get_last_price() can return None and does so pretty often so you should always check if the price is None before using it. Also remember it is the last trade (can be stale) — for options and thin markets prefer get_quote() and validate bid/ask before using mid_price.
- CRITICAL FOR OPTIONS: get_greeks() can return None when option price data is unavailable (e.g., illiquid options with no recent trades or quotes). ALWAYS check if greeks is None before accessing values like delta, gamma, theta, vega. Use a guard pattern: `greeks = self.get_greeks(option_asset); if greeks is not None: delta = greeks.get("delta"); # use delta here`. Do NOT use `return` when Greeks is None - that would block the entire strategy from continuing.
- IMPORTANT: Remember that you need to set_market("24/7") in intialize for any crypto bot to work properly. Without this the bot will stop trading at 4pm EST which is wrong for crypto.
- So that means strategies for BTC or ETH, or any other crypto coin MUST USE set_market("24/7") in the initialize method. For backtesting, prefer datasource_class=None so LumiBot can resolve the configured provider from the environment. If the user explicitly requests a direct provider binding, PolygonDataBacktesting or CcxtBacktesting are valid explicit choices. If the user does not specify a market then you should set it to "24/7" by default.
- For BTC/USD, ETH/USD, or stablecoin-quoted spot crypto, create the crypto `Asset` from the base coin only, for example `Asset("BTC", asset_type=Asset.AssetType.CRYPTO)`, and pass/set a separate USD quote asset when needed. Never use pair strings such as `BTC-USD`, `BTC/USD`, or `BTCUSD` as a spot crypto asset symbol.
- If you are instructed to do something "before the market opens", implement it in the before_market_opens lifecycle method and store any needed state in self.vars so it can be accessed later in on_trading_iteration.
- If you are instructed to do something "during trading hours" or "during market hours", implement it in the on_trading_iteration lifecycle method.
- Be verbose with logs (self.log_message()) around trading decisions, data fetches, and guard clauses so we can trace each branch.
- When buying crypto make sure that you allow fractions of the asset for a few decimal places, lumibot will correct it if you use too many decimals, but if you use too few decimals then it may not buy the asset at all. So for example if you want to buy 0.5464 BTC then you should use 0.5464 and not 0.546 or 0.55 or 0.5, because lumibot will correct it to the nearest decimal place and it may not buy the asset at all. So try to use as many decimal places as possible when buying crypto.
- self.log_message() can only use the colors white, red, green, blue, or yellow. Do not use any other colors or it will not work!
- Seriously make sure you are verbose with logs. If  you are not going to trade then log it (this is important so people know why the bot is not trading), if you are going to trade then log it (this is important so people know what the bot is doing), if you are going to sleep then log it (this is important so people know why the bot is not trading), if you are going to do something then log it (this is important so people know what the bot is doing). Aim for 2-3 informative messages per decision block, not copy-pasted spam.
- TRADING FEES BY ASSET CLASS: Use the correct TradingFee type for each asset class. For OPTIONS, use `TradingFee(per_contract_fee=0.65)` (IBKR standard $0.65/contract/leg; this is multiplied by order quantity, so a 40-contract order costs $26). For FUTURES, use `TradingFee(per_contract_fee=0.85)` (standard) or `TradingFee(per_contract_fee=0.50)` (micros). For STOCKS, use `TradingFee(percent_fee=0.001)` (0.1% of order value). NEVER use flat_fee for options or futures because flat_fee is a fixed amount per ORDER regardless of contract count, which massively undercounts commissions on multi-contract trades.
- Strategy logic must be broker-agnostic: never include broker API keys, never call broker SDK/REST directly, and never implement broker-specific order semantics inside Strategy methods.
- It is OK for the `if __name__ == "__main__":` harness to set `datasource_class=None` and let the environment choose the real backtesting provider. Only hardcode a datasource class when the user explicitly requests a provider or the strategy truly depends on a direct local datasource such as PandasDataBacktesting.
- Alpaca is never hardcoded. A user who wants Alpaca data selects the Alpaca data source for the strategy; BotSpot supplies credentials from their connected Alpaca account (Broker Connections). Keep `datasource_class=None`, and never read `ALPACA_API_KEY`, `ALPACA_API_SECRET`, or `ALPACA_OAUTH_TOKEN` in strategy code or declare them as required secrets: those names are reserved for broker connections and cannot be saved.
- Futures backtests should also default to datasource_class=None unless the user explicitly requests a direct provider binding such as InteractiveBrokersRESTBacktesting or DataBentoDataBacktesting.
- Futures symbols are roots (not spot tickers). IBKR/CME crypto examples: Bitcoin micro `MBT` vs standard `BRR`; Ether micro `MET` vs standard `ETHUSDRR`.
- If you are trading SPX options or NDX options, make sure to use the correct underlying asset, which is an Asset object that represents the index itself (e.g., SPX or NDX) and not a stock or ETF that tracks the index. Asset("SPX", asset_type=AssetType.INDEX) for example is the underlying asset for SPX options, not an ETF or stock
- VIX is an index, not a stock: ALWAYS fetch it as `Asset("VIX", asset_type=Asset.AssetType.INDEX)` (never `^VIX`), and treat `get_last_price(...)` returning None/NaN as “VIX unavailable” (log it and skip/disable the VIX filter for that iteration).
- If you need very up to date data then get_historical_prices() is not a good choice, you should use get_last_price() or get_quote(). The get_historical_prices is for HISTORICAL data and is usually delayed by up to a minute, it does not provide not up to the second prices. get_last_price and get_quote are designed to be more real-time and provide the latest available prices.
- If a user asks you to get historical data and make sure that it is up-to-date or has to be very timely, then you might want to consider using a combination of the get_historical_prices method along with the `get_last_price` or `get_quote` method together where you would have to build kind of your own thing where you're using historical data along with current data.
- If a user wants faster price action or complains that the speed is too slow in terms of trading, then a likely culprit could be that you're using `get_historical_prices` instead of `get_quote` or `get_last_price`, which are much faster and up-to-date with most brokers. They will get data in between bars, whereas `get_historical_prices` has a speed limit of 1 minute bars at best.

## US Equity Extended-Hours Strategies

This section is mandatory whenever the user asks for US stock or ETF trading
before the regular open, after the regular close, pre-market, post-market, or
overnight.

- For a scheduled US equity/options strategy that must run data preparation
  after the exchange closes but submit orders only during regular hours,
  `self.set_market("24/7")` is the preferred LumiBot wake/calendar setting. It
  lets ordinary scheduled strategy iterations run after hours. It is not the
  default for ordinary equity strategies and is not permission to trade at all
  hours.
- When using `self.set_market("24/7")` for this pattern, do not use
  `self.broker.is_market_open()` as the order-safety check because the configured
  broker market is intentionally continuous. Compute the real session from a
  separate timezone-aware US exchange calendar, then require that gate before
  every submit, cancel, modify, close, or cleanup operation. Data fetching,
  scoring, and durable plan persistence may run outside that gate.
- Persist after-hours plans and idempotency state through BotSpot's scheduled
  state backend, not process memory alone. A later scheduled task must load the
  same plan identity and reconcile broker positions and orders before acting. If
  a planned execution is missed because of a holiday, unexpected closure,
  failed task, or incomplete ladder, keep the plan pending and allow the next
  valid regular-session invocation to continue it. Never silently recapture and
  reorder symbols to hide missing state.
- Keep this behavior in strategy code and ordinary scheduled invocations. Do not
  add a user-specific LumiBot lifecycle, global framework event, or hidden
  runtime override to implement after-hours preparation.
- Separate four concerns in the saved code: framework wake/calendar behavior,
  the broker's supported session window, current quote availability, and order
  eligibility. `set_market("24/7")`, `set_market("24/5")`, descriptive flags,
  or disabled sleeps can keep the strategy loop awake; none of them proves that
  the selected broker can quote or execute the requested symbol at that time.
- Separate the requested decision clock from the permitted execution session.
  An exact HH:MM decision means that local calendar minute, once per eligible
  day; do not replace it with any later time after HH:MM unless the user asked
  for catch-up. Guard each reachable order-submission path with the actual
  timezone-aware exchange session/calendar. Preserve an explicitly requested
  entry-time restriction at entries, but do not silently extend a signal's
  evaluation minute to every protective exit or other order. Preserve the
  user's distinct exit and risk-reduction requirements.
- Use a maintained exchange calendar for trading-day and session boundaries,
  including observed holidays that cross a year boundary and early closes.
  A hand-written weekday/holiday list is not equivalent to the exchange schedule.
  Declare any required calendar package in the strategy requirements and preserve
  the separate 24/7 wake calendar for assets that need it.
- Use an explicit timezone-aware session guard. When Schwab is named, default to
  its standard equity sessions: pre-market `07:00-09:25 ET`, regular
  `09:30-16:00 ET`, and after-hours `16:05-20:00 ET`. Do not generate or claim
  pre-`07:00 ET` Schwab Trader API execution merely because Schwab advertises
  24/5 trading on thinkorswim. That exact BotSpot/LumiBot API capability needs
  separate source-backed live proof. Convert `self.get_datetime()` with
  `ZoneInfo("America/New_York")` before comparing session times; do not compare a
  raw datetime's clock fields and merely label them ET. Preserve the
  `09:25-09:30 ET` and `16:00-16:05 ET` gaps; a single continuous `07:00-20:00`
  guard is not equivalent to the three supported sessions.
- For the current decision price, call `self.get_quote(asset)` before historical
  bars. Require a usable bid and ask, validate that the quote timestamp is fresh
  enough for the strategy cadence, and reject a spread wider than the
  strategy's explicit risk threshold. `get_last_price()` is a fallback and may
  be stale. Do not use the latest one-minute bar close as if it were the live
  executable price. For Schwab, prefer the actual `bid_time`, `ask_time`, or
  `quote_time` carried by the quote when checking freshness; do not treat a
  locally synthesized fallback timestamp as proof that the broker quote is
  fresh. If history is subsequently incomplete, log that the live quote worked
  but signal context is incomplete. These quote checks are live-only: a backtest
  quote is rebuilt from bars without broker timestamps, so skip them when
  `self.is_backtesting` and price from the bar, or every backtest bar is
  rejected.
- Use `get_historical_prices()` for the requested lookback context, such as the
  prior 15 completed minute highs. Request a wide enough window to survive a
  minute with no trade. An empty one-minute candle request does not prove that
  the broker's quote endpoint has no current market data. If the signal itself
  needs bars and the lookback is still incomplete, log that the signal context
  is incomplete; do not misreport a total pricing outage.
- Outside the regular US equity session, use `create_order(...)` plus
  `submit_order(...)` with an explicit `limit_price` for entries and exits.
  Never generate a market order for an extended-hours stock trade. Schwab,
  Alpaca, and Tradier require limit orders for their extended-hours equity
  sessions; IBKR's regular Outside-RTH support is more nuanced, but limit orders
  remain the safe broker-generic default and are required for its overnight
  equity session.
- A limit price alone does not select the extended session on every broker.
  Apply the named integration's routing contract:
  - Schwab: LumiBot currently maps simple stock limit orders to Schwab
    `SEAMLESS`; market orders map to `NORMAL`.
  - Alpaca: set the order's broker custom parameter `extended_hours=True` and
    use `day` or `gtc`; Alpaca rejects other extended-hours order/TIF shapes.
  - Tradier: use an equity limit order with `time_in_force="pre"` or
    `time_in_force="post"` for the intended session. Do not use `day` and assume
    it selects extended hours. Tradier's current official pages disagree on the
    exact pre-market opening time, so do not hardcode an unverified start.
  - IBKR: standard Outside-RTH and the separate Overnight destination require
    broker routing attributes in addition to price. Do not promise IBKR
    extended execution unless the active LumiBot adapter is proven to serialize
    the required Outside-RTH/overnight setting; a limit order by itself is not
    proof.
- Do not generate a bracket, OCO, OTO, trailing-stop, or stop-order child for an
  extended-hours stock trade unless the named broker's exact API path has been
  proven to support every child outside regular hours. A limit parent does not
  make a stop or market child extended-hours eligible. For a broker-generic
  pre-market strategy, monitor take-profit and stop thresholds in strategy code
  and submit a bounded marketable limit exit from a fresh quote when a threshold
  is reached. Revalidate the quote used to price the exit. Do not replace a
  previously validated quote with a second unchecked `get_quote()` result inside
  the exit helper.
- Before any entry submit, reconcile the exact tracked order with
  `self.get_order(order_id)` when available and check same-asset open orders with
  `self.get_orders(statuses=Order.ACTIVE_STATUSES)`. A submitted, open, new, or
  partially filled same-asset entry blocks another entry. Filter by the exact
  asset or contract so unrelated and terminal orders do not block trading.
- Treat HTTP or tool-level submission success as transport acknowledgement, not
  as a fill. Store the returned order identifier, but set entry basis, counters,
  markers, profit targets, stops, and position-owned state only from confirmed
  fill evidence such as `on_filled_order` or a refreshed filled order. Clear or
  retry tracked state only after a confirmed terminal error, rejection,
  cancellation, or expiration, using a bounded cooldown. Apply the same
  fill-based rule to exits; do not clear position state merely because a sell
  was submitted. In particular, do not assign `entry_price`, take-profit, stop,
  held-position flags, or trade counters in the branch immediately following
  `submit_order(...)`; submission-time signal timestamps and the returned order
  identifier are not position state.
- A historical smoke backtest can validate syntax, control flow, order type,
  duplicate-entry protection, and basic signal behavior at any time of day. It
  cannot prove that Schwab is returning fresh quotes or accepting an order in a
  live extended-hours session. State that live proof boundary clearly.

Use a small broker-generic validation helper instead of burying these checks
after historical-data early returns. Adapt thresholds to the strategy cadence:

```python
from datetime import timezone
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")

def _fresh_equity_quote(self, asset, max_age_seconds=30):
    quote = self.get_quote(asset)  # Must happen before historical-bar requests.
    if quote is None:
        return None
    if self.is_backtesting:
        # Backtest quotes are rebuilt from bars and never carry bid_time,
        # ask_time, or quote_time, with any data provider. Freshness and
        # spread checks are live-only; the backtest prices from the bar.
        return quote if quote.price is not None else None
    if quote.bid is None or quote.ask is None:
        return None
    bid, ask = float(quote.bid), float(quote.ask)
    if bid <= 0 or ask <= 0 or ask < bid:
        return None

    broker_times = [
        value
        for value in (quote.bid_time, quote.ask_time, quote.quote_time)
        if value is not None
    ]
    if not broker_times:
        return None  # Do not use Quote.timestamp's local fallback as broker proof.
    broker_time = max(broker_times)
    if broker_time.tzinfo is None:
        broker_time = broker_time.replace(tzinfo=timezone.utc)
    now_utc = self.get_datetime().astimezone(timezone.utc)
    if abs((now_utc - broker_time.astimezone(timezone.utc)).total_seconds()) > max_age_seconds:
        return None
    return quote

def _now_et(self):
    return self.get_datetime().astimezone(NEW_YORK)
```

After this helper returns a fresh quote, request the historical lookback. If the
lookback is incomplete, log that quote pricing is available but the signal lacks
enough completed bars. In live trading the missing-time branch must fail
closed: do not write `if broker_times: validate_age` and then accept the quote
when the list is empty. A live quote with no `bid_time`, `ask_time`, or
`quote_time` cannot prove freshness and must skip the trade. In a backtest those
fields never exist, which is why the helper returns the bar-based quote before
any live-only check.

## Supported implementation references

The implementation catalog has one owner: `lumibot-api-reference`. Use its
existing `skills reference get` references for the specific API fact needed by
this build or edit. The core workflow does not embed a second copy of those
references. Preserve the user's architecture and requirements while using
the supported API; a reference example is not permission to change their rules.

- File/class shape: `references/strategy-structure.md`.
- Historical bars, price methods, orders and positions: `references/methods-properties.md`.
- Fills, partial fills, cancellation, restart and reconciliation: `references/lifecycle-methods.md`.
- Asset/contract identity and base/quote pairs: `references/entities.md`.
- A reusable implementation pattern: `references/examples.md`.
- Fast cancel/hedge deadlines: `references/fast-order-management.md`.

These paths belong to `skill_name="lumibot-api-reference"`. Load the smallest
relevant reference, then return to implementation. Do not load this list as a
checklist, and do not load the large examples catalog for a simple edit whose
API contract is already established. If an exact method or broker behavior is
still uncertain, inspect the corresponding supported LumiBot source. Missing
or conflicting evidence requires a source check, not an invented signature.
