---
name: lumibot-strategy-building
description: Load this before writing, editing, fixing or backtesting any LumiBot trading strategy on BotSpot. It covers the full build workflow through the BotSpot MCP tools (create_strategy, get_file, patch_file, replace_file, start_backtest, backtest_status, logs and artifacts, revisions), strategy structure, cash-bounded sizing, order lifecycle and reconciliation, exits, data providers, backtest correctness checks and common mistakes.
license: MIT
metadata:
  title: "Building LumiBot Strategies on BotSpot"
---
# Building LumiBot Strategies on BotSpot

LumiBot is an open-source Python trading library
(https://github.com/Lumiwealth/lumibot, docs https://lumibot.lumiwealth.com).
BotSpot stores LumiBot strategies as versioned files, backtests them, and runs
them live after the owner approves a deployment on botspot.trade.

This is the main "how to build a strategy well" skill. Use it for new builds,
substantial rewrites, bug fixes and behavior edits. Load companion skills for
specific topics (with `skills` action=get, name=<skill>):

| Topic | Skill |
|---|---|
| Exact LumiBot methods, entities, lifecycle callbacks, examples | `lumibot-api-reference` |
| Fast strategies, scanners, timed cancels and hedges | `fast-lumibot-strategies` |
| Indicators (`self.indicators`) and chart output | `lumibot-indicators` |
| AI-owned or hybrid strategies (`self.agents`) | `lumibot-ai-agents` |
| Stock and ETF patterns (breakout, mean reversion, moving averages) | `stock-etf-strategies` |
| Options (OptionsHelper, spreads, wheel, fees) | `options-strategies` |
| Using the BotSpot MCP tools in general | `using-botspot-mcp` |

References in this skill (load with `skills` action=get,
name=`lumibot-strategy-building`, reference=<path>):

| Reference | Load when |
|---|---|
| `references/editing-existing-strategies.md` | Patching saved code, bounded parameter edits, copying rules between strategies, fill-price or stale-value repairs |
| `references/backtest-validation.md` | Choosing a test window, reading results, no-trade or failed runs, metric-target loops, correctness audit |
| `references/scaffolds.md` | Choosing a first-version template for stocks, crypto, futures, options, AI or a sample bot |
| `references/extended-hours-equities.md` | Pre-market, after-hours or overnight US stock trading, session guards, live quote freshness |
| `references/crypto-strategies.md` | Crypto spot pairs, quote assets, crypto perpetual futures |
| `references/futures-strategies.md` | Futures, continuous futures, session windows |
| `references/order-operation-ownership.md` | Duplicate orders from competing callback, polling or fallback paths |
| `references/order-quantity-accounting.md` and `references/order-quantity-example.py` | Partial or canceled replacements, late or repeated fills, overfills across attempts |

Everything here is engineering guidance, not investment advice. Example symbols,
thresholds and sizes are illustrations, not recommendations.

---

# Part 1: The BotSpot build workflow

## 1. Check the Marketplace before building

For a new strategy request, first search existing published strategies with
`marketplace_strategies` action=list and two to four plain keywords from the
request (tickers, the rule, the data source). Skip this when the user asked to
build from scratch, is editing an existing strategy, or already picked a
listing.

If a listing closely matches, read it with action=get and tell the user its
name, its Marketplace link, one line on what it does, what the publisher shares,
and any API key the user must supply. Offer two paths: copy it with
`clone_strategy` (listingId, only when the listing allows cloning), or build
their own version starting from its shared code (action=get_code, only when
code is shared). Respect exactly what the publisher shared: never show, quote,
paraphrase or guess code, rules, positions or trades a listing does not grant.
If nothing fits, build normally.

## 2. Decide who makes the trading decisions

Before writing code, decide whether the user wants automation at all. If they
only want to understand an account, research a trade or learn, help directly
instead of creating a strategy.

When automation is wanted, separate fast mechanical work (polling, order
reconciliation, time windows) from the cadence of an intelligent decision:

1. Decisions that react within seconds or happen more often than about hourly
   fit Python ownership, or a hybrid. AI calls are slower and cost more.
2. Frequent polling with slower judgment fits a hybrid: Python polls and
   reconciles quickly and calls the AI only at decision windows.
3. Hourly or slower judgment-based decisions can be AI-owned. Load
   `lumibot-ai-agents` for that architecture.
4. Respect an explicit user choice (Python, hybrid or frequent AI) after one
   clear cost and latency note. Preserve an existing Python strategy unless the
   user asks to convert it.

Exact thresholds and rules do not by themselves force Python; an AI-owned
strategy can follow exact rules too. The rest of this skill focuses on
Python-owned (rules-based) code and the parts shared by every strategy.

## 3. Is the request specific enough to build?

Build when the user gives a concrete supported market or universe plus enough
intent to pick a first version (style, entry idea, risk posture, timeframe or
validation goal). Choose simple defaults for unstated details and disclose them
after building. If the target market is missing, ask one short question. Do not
send a long intake form. Critique, advice or "what do you think" is not a build
request; answer it conversationally.

Market support to keep in mind:

- Supported: US stocks and ETFs, US stock, ETF and index options, US futures
  and continuous futures, spot crypto pairs (for example BTC/USD, ETH/USD,
  BTC/USDT, BTC/EUR) and crypto perpetual futures where a broker supports them.
- Not supported as written: spot forex pairs (EURUSD, USDJPY), spot gold or
  silver (XAUUSD, XAGUSD), and Indian index options. Ask whether to switch to a
  supported proxy such as GLD, SLV or gold and silver futures. Never silently
  drop part of a mixed list or substitute SPY or QQQ.
- Nasdaq 100, US100 or NAS100 futures requests map to continuous `NQ` or
  `MNQ`, not QQQ, unless the user asks for an ETF.

## 4. First build: the tool sequence

1. `create_strategy` with a human-readable name (under 60 characters, natural
   words, not a slug) and a description. It returns a workspace with a
   neutral starter `main.py` and an empty `requirements.txt`, plus a files
   manifest. Trust that manifest instead of rediscovering the starter files.
2. `get_file` for `main.py` (and `requirements.txt` if you will need it). Each
   read returns an `editHandle`.
3. `replace_file` with the complete new `main.py`. The starter is boilerplate;
   do not patch your strategy into it. Send `path`, `editHandle` and the full
   `content` together. A successful write returns a new revision.
4. If the code imports third-party packages the platform does not provide,
   `replace_file` on `requirements.txt` with exact pins (`package==1.2.3`).
   Use `replace_file`, not `create_file`, because the file already exists.
5. `get_file` again on the newest revision and audit the saved code (see the
   pre-backtest checklist below). Fix real defects with another write and
   readback. Do not restyle working code before the first backtest has run;
   the backtest is the check.
6. `start_backtest` on the newest revision with a sensible window (see Part 1
   section 7). It is asynchronous and returns a backtest id.
7. `backtest_status` with that id. Summarize progress instead of polling in a
   tight loop. When terminal, inspect results (section 8).

A file write only succeeded if the tool returned a new revision. An error such
as an invalid or stale edit handle means nothing was saved: call `get_file`
again for a fresh handle and retry. Never report a change as saved, or
start a backtest, on the strength of a failed write.

## 5. Editing an existing strategy

- Always read the saved file with `get_file` first. Do not edit from memory or
  from an earlier summary.
- Stay on the strategy the user means. If they name a different strategy than
  the one in context, resolve it with `list_strategies` and `list_revisions`
  and pass that strategy's ids explicitly. Use `switch_active_strategy` or
  `set_strategy_revision` when the conversation should point at another
  strategy or an older revision.
- For a small targeted change, use one `patch_file` call holding every
  non-overlapping operation for that request. Copy `oldText` byte for byte from
  the latest readback, including whitespace, and include enough surrounding
  context to make it unique. For a broad rewrite, use `replace_file`.
- Replace stale behavior; do not append a competing line after it. The readback
  must show the old behavior is gone.
- Read back the saved file once after the edit and check every requested change
  plus the behavior that must stay the same.
- Do not start a backtest just because an edit was saved, unless the user asked
  for one or this is the first validation of a new build.

`references/editing-existing-strategies.md` has the detailed rules: ambiguous
anchors, preserving sizing when a shared parameter changes, copying rules from
one strategy to another without copying its identity, credential identity, and
fill-price source repairs.

## 6. Identifiers, revisions and supporting files

- Strategy, revision and backtest ids are opaque. Copy them exactly from a tool
  result; never retype, shorten or rebuild them. A revision id is not a
  backtest id, and neither is a deployment id.
- Every successful write creates a new immutable revision. Use the newest
  revision id for the next read and for `start_backtest`. Old revisions remain
  available through `list_revisions`.
- Many file tools default to the conversation's current strategy when you omit
  `strategyId` and `revisionId`. Pass explicit ids only for a different
  strategy or a specific historical revision.
- `main.py` and `requirements.txt` form one executable contract. After any
  import change, check every third-party import against the requirements file.
  Do not list the standard library, LumiBot, or packages the platform already
  provides. Never make a required import optional just to dodge a dependency
  error.
- The strategy must be self-contained: one file, no local config files that
  will not exist at runtime.
- If the strategy has a `rules.json` (BotSpot's saved trading Rules), keep it
  aligned with code when you change trading behavior. Only read it after
  `list_files` shows it exists; do not probe for it.

## 7. Running a backtest

- Window: do not hardcode backtest start and end dates in the script. The
  `start_backtest` call supplies the window. For a first test, use a short
  window (about a week of trading for intraday or frequent strategies) and
  lengthen it when the rules need it: a daily 20/50 moving-average cross may
  need one to three months to fire; monthly rebalances need several months.
  Minute data history is commonly limited to roughly the last two years, so
  keep minute-level windows inside that.
- Duration requests: "backtest it for a year" is a window for
  `start_backtest`, not a request to change `sleeptime` or lookbacks.
- Data provider: by default the backtest uses BotSpot Auto (`botspot_auto`),
  which routes each asset class to a managed source. MCP clients outside the
  BotSpot chat pass `dataProvider` (for example `alpaca` or `polygon`) on
  `start_backtest` to choose another source. Options data availability changes
  over time; read the `start_backtest` description and any returned error code
  for the current options route. Typical alternatives are the user's connected
  Alpaca account or their own Polygon key.
- In strategy code keep `datasource_class=None` so the environment chooses the
  provider. Never hardcode broker or data credentials in strategy code.
- Errors are information: `DATA_ACCESS_REQUIRED` means the user needs to unlock
  data access, not that you should switch providers silently.
  `DATA_PROVIDER_UNAVAILABLE` or an options-data-source error means no
  backtest started; tell the user and offer the listed alternatives.
- A start that returns a failure is repair feedback: fix and retry, do not wait
  on a backtest that never started.

## 8. Reading results and proving correctness

Use one backtest id consistently for every log and artifact call in an answer.

- `get_backtest_logs` for errors, tracebacks, order and fill lines and "why
  did it not trade". Logs are the first evidence for a failed or no-trade run.
- `list_backtests` (includeArtifacts=true) or `get_backtest_artifact` to see
  which artifacts exist (trades, stats, indicators, tearsheet) and their
  schema, then `query_csv` with SQL against one artifact.
- `get_backtest_visuals` for tearsheet and chart links to show the user.

A completed status and positive return do not prove the strategy is correct.
Before calling an unleveraged strategy correct, check:

1. Minimum cash during the run. Negative cash without intended margin is a
   bug to fix, never something to hide with `adjust_cash` or fake deposits.
2. Fees actually charged and that they match the configured fee model.
3. The order lifecycle: submitted, filled, partially filled, canceled.
4. Positions left open at the end, and whether exits fired when they should.
5. Every user rule that a backtest cannot evaluate (for example a live quote
   age limit) is named in your answer along with what the backtest does instead.

A run that produced trades but ended in a failed status is still failed;
diagnose the failure. `references/backtest-validation.md` covers no-trade
diagnosis, rescue rules and metric-target loops.

## 9. Never weaken the user's rules to get a trade

Implement the user's rules exactly. Technical repairs that keep intent are fine
(API fixes, warmup history, asset construction, order plumbing, error
handling). Changes to signals, thresholds, cadence, universe, sizing, risk or
option structure need the user's approval: propose the exact change and wait.

Never add fake fills, dummy orders, backtest-only branches or a simplified
substitute just to show a trade. Never broaden an exact date, symbol, quantity
or eligibility boundary to force a fill. A zero-trade result under strict rules
is evidence to explain, not a reason to rewrite the strategy.

Validation goals ("make sure it trades at least once") are acceptance checks,
not trading instructions. Never code an order whose only purpose is to satisfy
a validation target.

When two of the user's rules conflict only in an edge case, apply the
risk-reducing reading (exits, stops and forced closes win over entry filters)
and tell the user.

## 10. Deploying

`start_deployment` prepares a deployment for the owner's review. It does not
start a bot or place trades by itself. The owner selects the broker account and
approves on botspot.trade; after approval the bot can place real-money trades.
Never ask for secret values in chat; missing variables are entered through the
secure cards the readiness check returns. Saved API keys for data or AI services
are managed with `saved_env_vars`. A backtest is not a substitute for a
deployment the user asked for, and a deployment is not a way to place a one-off
trade.

---

# Part 2: Writing the strategy code

## 11. File shape

A complete, runnable `main.py` has imports, one `Strategy` subclass, a single
`parameters` dict, lifecycle methods and the standard `__main__` harness.

```python
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset, Order, TradingFee
from lumibot.credentials import IS_BACKTESTING

from decimal import Decimal, InvalidOperation, ROUND_FLOOR


class RsiPullbackStrategy(Strategy):
    """Buys a liquid ETF after a short-term pullback and exits on recovery or stop.

    Illustration only, not a recommendation.
    """

    parameters = {
        "symbol": "SPY",
        "rsi_length": 14,
        "rsi_entry": 35,
        "rsi_exit": 60,
        "stop_pct": 0.05,
        "cash_fraction": 0.95,
        "limit_buffer_pct": 0.002,
        "percent_fee": 0.001,
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.vars.asset = Asset(self.parameters["symbol"], Asset.AssetType.STOCK)
        self.vars.entry_price = None

    def on_trading_iteration(self):
        asset = self.vars.asset
        p = self.parameters

        bars = self.get_historical_prices(asset, 30, "day")
        if bars is None or bars.df is None or bars.df.empty:
            self.log_message(f"{asset.symbol}: no bars yet, skipping.", color="yellow")
            return
        df = bars.df[bars.df.index <= self.get_datetime()]
        if df.empty:
            self.log_message(f"{asset.symbol}: no bars at or before now, skipping.", color="yellow")
            return
        last = df.iloc[-1]
        close = float(last["close"])
        self.add_ohlc(asset.symbol, open=float(last["open"]), high=float(last["high"]),
                      low=float(last["low"]), close=close, dt=df.index[-1], asset=asset)

        rsi = self.indicators.rsi(asset, timestep="day", length=p["rsi_length"])
        if rsi is None or rsi != rsi:  # None or NaN while warming up
            self.log_message(f"{asset.symbol}: RSI not ready, skipping.", color="yellow")
            return
        self.add_line("RSI", float(rsi), plot_name="RSI")

        active = [o for o in self.get_orders() if o.asset == asset and o.is_active()]
        position = self.get_position(asset)
        held = position is not None and position.quantity > 0

        # Exits first: a pending entry must never block a required exit.
        if held:
            entry = self.vars.entry_price
            stop_hit = entry is not None and close <= entry * (1 - p["stop_pct"])
            if rsi >= p["rsi_exit"] or stop_hit:
                working_sells = [o for o in active if o.side == Order.OrderSide.SELL]
                if working_sells:
                    self.log_message(f"{asset.symbol}: exit already working, waiting for it to resolve.")
                    return
                for o in active:  # a leftover buy must not block the exit
                    self.cancel_order(o)
                reason = "stop" if stop_hit else "RSI recovery"
                self.log_message(f"{asset.symbol}: exit on {reason}, RSI={rsi:.1f}, close={close:.2f}.")
                self.close_position(asset)
                self.add_marker("Exit", close, color="red", symbol="arrow-down", asset=asset)
            else:
                self.log_message(f"{asset.symbol}: holding, RSI={rsi:.1f}.")
            return

        if active:
            self.log_message(f"{asset.symbol}: {len(active)} order(s) still working, no new entry.")
            return
        if rsi > p["rsi_entry"]:
            self.log_message(f"{asset.symbol}: no entry, RSI={rsi:.1f} above {p['rsi_entry']}.")
            return

        cash = self.get_cash()
        if cash is None:
            self.log_message("Cash unavailable, skipping sizing.", color="red")
            return
        limit_price = round(close * (1 + p["limit_buffer_pct"]), 2)
        order = submit_cash_bounded_entry(
            self, asset,
            spendable_cash=cash * p["cash_fraction"],
            limit_price=limit_price,
            percent_fee=p["percent_fee"],
            fixed_fee_bound=0,
        )
        if order is not None:
            self.log_message(f"{asset.symbol}: entry submitted at limit {limit_price}, RSI={rsi:.1f}.")
            self.add_marker("Entry signal", close, color="green", symbol="arrow-up", asset=asset)

    def on_filled_order(self, position, order, price, quantity, multiplier):
        # Position state comes from confirmed fills, not from submission.
        if order.asset == self.vars.asset:
            if order.side == Order.OrderSide.BUY:
                self.vars.entry_price = float(price)
            elif position is None or position.quantity == 0:
                self.vars.entry_price = None


def submit_cash_bounded_entry(strategy, asset, *, spendable_cash, limit_price,
                              percent_fee, fixed_fee_bound):
    """Submit a whole-share DAY limit buy that fits cash after fees.

    Args:
        strategy: The running Strategy.
        asset: The stock or ETF Asset to buy.
        spendable_cash: Budget for this entry, already net of other commitments.
        limit_price: Highest acceptable fill price.
        percent_fee: Fee rate as a fraction of order value.
        fixed_fee_bound: Upper bound on fixed fees for the order.

    Returns:
        The submitted Order, or None when nothing fits or inputs are invalid.
    """
    try:
        balance, budget, price, fee_rate, fixed_fee = (
            Decimal(str(value)) for value in (
                strategy.get_cash(), spendable_cash, limit_price,
                percent_fee, fixed_fee_bound,
            )
        )
        if (not all(v.is_finite() for v in (balance, budget, price, fee_rate, fixed_fee))
                or price <= 0 or fee_rate < 0 or fixed_fee < 0):
            raise ValueError("Invalid cash, price or fee evidence")
    except (InvalidOperation, TypeError, ValueError):
        strategy.log_message("Entry not submitted: cash, price or fee evidence is invalid.", color="red")
        return None
    available = min(balance, budget)
    quantity = int(((available - fixed_fee) / (price * (1 + fee_rate))).to_integral_value(rounding=ROUND_FLOOR))
    if quantity <= 0:
        return None
    order = strategy.create_order(asset, quantity, Order.OrderSide.BUY,
                                  limit_price=float(price), time_in_force="day")
    return strategy.submit_order(order)


if __name__ == "__main__":
    if IS_BACKTESTING:
        fee = TradingFee(percent_fee=0.001)
        RsiPullbackStrategy.backtest(
            datasource_class=None,
            benchmark_asset=Asset("SPY", Asset.AssetType.STOCK),
            buy_trading_fees=[fee],
            sell_trading_fees=[fee],
            quote_asset=Asset("USD", Asset.AssetType.FOREX),
        )
    else:
        trader = Trader()
        trader.add_strategy(RsiPullbackStrategy(quote_asset=Asset("USD", Asset.AssetType.FOREX)))
        trader.run_all()
```

Check exact signatures in `lumibot-api-reference` when in doubt. Do not invent
methods because they sound plausible.

## 12. Hard rules (each of these has broken real backtests)

- Never use `from __future__ import annotations` or any future import. It can
  stop the strategy from starting once files are patched.
- Never assign arbitrary attributes on `self` (`self.name`, `self.asset`,
  `self.symbol`, `self.quote_asset`). They can collide with LumiBot internals.
  Use `self.vars` for state that must persist across iterations and restarts,
  and local variables for temporary values.
- Do not define helpers with private names that look like framework state
  (`_portfolio_value`, `_cash`, `_positions`, `_orders`, `_broker`,
  `_last_price`, `_strategy`). A collision produces errors such as
  "'float' object is not callable". Use clearly strategy-local names such as
  `calculate_target_weights`.
- Never call `datetime.now()`. Use `self.get_datetime()` so backtests see
  simulated time.
- Keep all parameters in one `parameters` dict at the top of the class. Do not
  redefine them in the `__main__` block.
- Do not pass `exchange=` or `currency=` to `Asset(...)`; `Asset` does not
  accept them.
- Use `self.create_order(...)` plus `self.submit_order(order)`. Do not use
  convenience calls like `self.buy(...)` or `self.sell(...)`.
- Stocks and ETFs use buy and sell sides (sell also closes a long). Option
  opening and closing sides apply only to option contracts.
- Default `self.sleeptime = "1D"` unless the user asks for intraday trading or
  a specific cadence. Do not silently default to minutes or seconds.
- Avoid blocking sleeps in normal strategy logic; check elapsed time on the
  next iteration instead. Short `self.sleep(1, process_pending_orders=True)`
  waits are for tight order-management loops only (see
  `fast-lumibot-strategies`).
- Avoid broad `try/except` that hides errors. When you catch, log the error.
- `self.log_message()` colors are limited to white, red, green, blue and
  yellow.
- Read API keys for outside services with `os.getenv("MY_SERVICE_API_KEY")`
  and treat a missing key as `None` with a clear log. Never default to a fake
  string like "your_api_key_here".
- Strategy code is broker-agnostic. Never read broker credentials, call broker
  SDKs or REST APIs directly, or branch on a broker name for ordinary logic.
  The platform supplies the broker connection.
- Write only working code. No pseudo-code, demo stubs or "for demonstration"
  branches.
- Do not compute conditional expressions inside f-string format specs; compute
  the display value first.
- Do not use `self.first_iteration` unless the user really needs a one-time
  action; most strategies do not.
- `tearsheet_custom_metrics(...)` is rare-use only, for strategy-specific
  summary rows the user asked for.

## 13. Sizing and cash

Default posture: invest available cash with executable, cash-aware sizing,
unless the user specifies otherwise. That never authorizes negative cash,
silent leverage or spending proceeds you do not have yet.

- `get_cash()` and `get_portfolio_value()` can return `None` when a live
  balance refresh fails. Log it and skip sizing; never treat `None` as zero.
- A prior close is not the next fill price. A gap can make a market order cost
  more than the cash you sized it with. Use a limit price within budget (as in
  `submit_cash_bounded_entry` above), a supported broker cash-amount order, or a
  clear buffer, and disclose the choice and its unfilled-order risk. Do not
  silently change an order type the user explicitly requested.
- Include fees in the sizing. Do not assume zero fees.
- A submitted sell is not cash. Spend its proceeds only after the fill is
  confirmed and cash has refreshed.
- A target allocation is not spendable cash. For rebalances: submit reductions
  first, then size buys from confirmed cash, current holdings and still-working
  orders, without counting the same reservation twice. A weekly or monthly
  signal schedules new targets but must not stop the strategy from finishing an
  already accepted rebalance between signal dates. Keep the user's weights and
  cadence; do not hide an execution shortfall by changing their allocation or
  enabling margin. LumiBot's drift rebalancer component (see
  `lumibot-api-reference`) handles many portfolio-rebalance requests.
- Whole shares for most stock sizing; crypto and some brokers allow fractions.
  Never truncate a fractional position with `int(position.quantity)` when
  closing it; use `self.close_position(asset)`.
- Options are priced per share with a 100 multiplier: a 1.50 premium costs
  about 150 per contract. See `options-strategies`.
- Use `deposit_cash()`, `withdraw_cash()` and `adjust_cash()` only for real,
  intended cash flows, and `configure_cash_financing()` or
  `set_cash_financing_rates()` for intended margin or interest modeling. Never
  use them to mask an overdraft.
- Default fee models for backtests: stocks `TradingFee(percent_fee=0.001)`;
  options `TradingFee(per_contract_fee=0.65)`; futures
  `TradingFee(per_contract_fee=0.85)` (micros about 0.50). Never use
  `flat_fee` for options or futures; it charges once per order regardless of
  contract count.
- If the user gives a starting budget, pass it as `budget=` to the backtest.

## 14. Orders, lifecycle and reconciliation

- Open orders: filter `self.get_orders()` by the exact asset or option
  contract and by active status (`Order.ACTIVE_STATUSES` or
  `order.is_active()`). Filled, canceled, rejected, expired or error orders must
  not block new entries.
- Track the identifier of each order you submit and check it with
  `self.get_order(order.identifier)`. Broad order lists can lag briefly after a
  submit.
- Submission is not a fill. Set entry price, stops, targets, counters and
  "position held" flags only from confirmed fills (`on_filled_order` or a
  refreshed filled order), never in the line after `submit_order`. Apply the
  same rule to exits: do not clear position state because a sell was
  submitted.
- `on_filled_order` is helpful but not guaranteed. Verify live state with
  `self.get_positions()` before clearing position or order state. Note that
  cash appears as a USD position in `get_positions()`.
- A cancel request is not completion. A cancel-pending order can still fill.
  Keep it in duplicate blocking until the broker confirms a terminal state,
  then reconcile its cumulative fills before replacing it.
- Keep unfilled and partially filled order ids until their state and the
  remaining position are reconciled. Preserve an accepted exit intent across a
  rejection, partial fill or restart, and resize it against the actual
  remaining quantity. Scope this to the affected asset, not unrelated symbols.
- No blind retry after an uncertain submit result. Reconcile first.
- Brackets, OCO and OTO: set `order_class=Order.OrderClass.BRACKET` (or OCO,
  OTO) with a valid `order_type` such as MARKET or LIMIT, and use
  `secondary_limit_price` and `secondary_stop_price` (optionally
  `secondary_stop_limit_price`). Do not use the deprecated `take_profit_price`
  or `stop_loss_price` with `limit_price`.
- When several paths (fill callback, polling, fallback, queue continuation)
  can submit for the same obligation, load
  `references/order-operation-ownership.md`. For partial or canceled
  replacements and late fills, load `references/order-quantity-accounting.md`
  and `references/order-quantity-example.py`. Timed cancels and fast hedges
  belong to `fast-lumibot-strategies`.

## 15. Exits and protective stops

- Evaluate exits and risk before entry-only duplicate checks. A pending entry
  must never stop a held position from exiting.
- Keep each rule's timing. A daily entry signal does not make a protective stop
  a once-a-day close check. When protection must work between iterations, use
  a supported stop order anchored to the confirmed entry fill and the remaining
  held quantity.
- Distinguish pending entries from protective exit orders so an active stop
  does not suppress a requested signal exit. Before a discretionary full exit,
  reconcile or cancel the existing protective order so you do not double sell
  or go short by accident.
- A market sell placed after yesterday's low crossed a stop level does not show
  that the stop executed at the cross. Disclose data and fill-model limits
  instead of claiming intrabar precision.
- Daily-only flags (for example "already traded today") must reset at the next
  session.
- An exit-only repair must not change entries, and an entry-only repair must
  not add new exit features.
- Crypto perpetual futures close with `self.close_position(asset)`; a
  `submit_order` on the opposite side can open a new position instead.

## 16. Data and prices

- Use `Asset` objects for every traded instrument and reuse the same object for
  history, prices, positions, orders and charts. Do not mix raw strings and
  `Asset` objects for the same instrument. Persist full `Asset` objects (strike,
  expiry, right included) rather than symbols.
- After `get_historical_prices(...)` inside an iteration, filter the bars to
  timestamps at or before `self.get_datetime()` before computing signals.
  Never trade from the last row of an unfiltered frame. If the filtered frame is
  empty, skip that asset for the iteration.
- `get_last_price()` returns the last trade and can be `None` or stale. Always
  check for `None`. In backtests it falls back to the newest completed bar.
- For intraday stock backtests where you already have filtered bars, use the
  latest filtered bar close for sizing, stops and chart lines. Use
  `get_last_price()` as a live convenience, not the primary backtest price.
- `get_quote(asset)` returns bid, ask and mid. Prefer it for options and thin
  markets, after validating bid and ask.
- Backtest quotes never carry live quote timestamps: `quote.bid_time`,
  `quote.ask_time` and `quote.quote_time` are `None` in a backtest, and stock
  quotes rebuilt from bars usually have bid and ask equal to the close or
  missing. Enforce quote-age, spread and depth rules only when
  `not self.is_backtesting`, price backtest decisions from the bar, and tell the
  user which rules are live-only.
- `get_historical_prices` gives completed bars (one minute at best). For the
  freshest price use `get_last_price()` or `get_quote()`, combined with history
  for context when needed.
- For many symbols, use `get_historical_prices_for_assets(...)` instead of a
  loop of single requests.
- Request only the lookback you need plus a small buffer. Avoid huge history
  requests (for example 10,000 bars) and unnecessary date arithmetic.
- VIX is an index: `Asset("VIX", asset_type=Asset.AssetType.INDEX)`, never
  `^VIX`. Treat a missing VIX price as unavailable for that iteration.
- SPX and NDX options use the index itself as the underlying
  (`Asset("SPX", asset_type=Asset.AssetType.INDEX)`).
- `set_market(...)` takes LumiBot market names such as `"NYSE"`, `"NASDAQ"`,
  `"stock"` or `"24/7"`. Product schedule labels like "regular" are not valid
  values. Ordinary US stock strategies usually omit it; crypto needs
  `self.set_market("24/7")`.

## 17. Indicators and charts

- Prefer `self.indicators.<name>(asset, timestep="day", **kwargs)` for built-in
  indicators (sma, ema, rsi, atr, bbands, macd, adx, stoch and more) and
  `self.indicators.custom(...)` for your own. They compute once over the series
  and return the current value quickly. Do not hand-roll
  `df["close"].rolling(...)` on full history every iteration; it is slow on long
  backtests. A result is `None` when no bars exist and NaN while warming up.
  Details: `lumibot-indicators`.
- Chartable strategies should emit chart data: `add_ohlc(...)` for price
  candles, `add_line(...)` for continuous values (indicators, stops, levels) and
  `add_marker(...)` for infrequent events. Marker symbols are `arrow-up`,
  `arrow-down` or `star`.
- The chart methods use `name`, `value` and `detail_text`; there is no `text`
  parameter. Pass `asset=` when you have the Asset so overlays group with its
  price chart; use `plot_name` only for a separate pane such as RSI or MACD, and
  keep panes and lines few (three or four).
- Never add a marker every iteration. Plot only valid numeric values.

## 18. Logging

Log every decision branch with `self.log_message()`: what was checked, the
values compared, and what the bot did (submitted, skipped, closed, waited). For
every order, log symbol, side, quantity and the signal that drove it. "Why did
it not trade" is answered from these logs.

## 19. Asset-class notes

- Stocks and ETFs: see `stock-etf-strategies` for complete patterns, and
  `references/extended-hours-equities.md` for pre-market and after-hours work.
- Options: always go through `OptionsHelper` for expiries, strikes and
  actionable prices; never brute-force deltas by looping strikes. See
  `options-strategies`.
- Crypto: base-coin `Asset("BTC", Asset.AssetType.CRYPTO)` with a separate
  quote asset, never `"BTC-USD"` or `"BTC/USD"` as the symbol; `set_market("24/7")`.
  See `references/crypto-strategies.md`.
- Futures: root symbols only (`ES`, `MES`, `NQ`, `CL`); dated contracts via
  `expiration=`; continuous futures with `Asset.AssetType.CONT_FUTURE`. See
  `references/futures-strategies.md`.

## 20. Pre-backtest checklist

Run this against the saved readback before `start_backtest`:

- [ ] Complete file: imports, one strategy class, lifecycle methods, one
      `__main__` harness, no leftover starter class or duplicate runner block.
- [ ] No future imports, no `self.name`-style attributes, no framework-like
      private helper names, no `datetime.now()`.
- [ ] Every user rule is implemented as stated; nothing was loosened.
- [ ] Orders via `create_order` + `submit_order`; duplicate checks filter by
      exact asset and active status; exits are evaluated before entry guards.
- [ ] Position state set only from confirmed fills.
- [ ] Sizing respects cash and fees; `None` cash or price is handled.
- [ ] Historical bars filtered to the current simulated time.
- [ ] Live-only quote checks guarded by `self.is_backtesting`.
- [ ] Chart output present for chartable strategies; logs on every branch.
- [ ] `requirements.txt` pins every non-provided third-party import.
- [ ] No hardcoded backtest dates, credentials or broker-specific code.

## 21. Common mistakes

| Mistake | Fix |
|---|---|
| Patching the strategy into the neutral starter | `replace_file` with the complete file for the first implementation |
| Claiming a fix after a failed write | Re-read for a fresh handle, retry, confirm the new revision |
| `oldText` typed from memory | Copy it byte for byte from the latest `get_file` |
| Trading from unfiltered history rows | Filter bars to `<= self.get_datetime()` |
| Treating `get_cash()` `None` as 0 | Log and skip sizing |
| Entry price set right after `submit_order` | Set it in `on_filled_order` from the confirmed fill |
| Pending entry blocks a stop exit | Evaluate exits first; filter guards by asset and order type |
| Market order sized from yesterday's close | Bound with a limit price or buffer that fits cash and fees |
| Quote-age rule rejects every backtest bar | Guard it with `not self.is_backtesting` and disclose it |
| `flat_fee` for options or futures | `per_contract_fee` |
| `Asset("BTC-USD")` | `Asset("BTC", CRYPTO)` plus a USD quote asset |
| `get_last_price` `None` blocks every futures bar | Fall back to the latest completed bar close |
| Loosening rules so a short test trades | Lengthen the window, or propose the change and wait for approval |
| Negative cash hidden with `adjust_cash` | Fix the sizing or order lifecycle |
