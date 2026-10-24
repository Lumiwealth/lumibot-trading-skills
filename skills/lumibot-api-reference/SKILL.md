---
name: lumibot-api-reference
description: Load when you need exact LumiBot API names, signatures, lifecycle methods, entities (Asset, Order, Position, Quote, Bars) or working code examples while writing, editing or debugging a LumiBot strategy. Covers orders, positions, prices, quotes, options chains and OptionsHelper, indicators, charting, cash accounting, components and AI agents.
license: MIT
metadata:
  title: "LumiBot API Reference"
---
# LumiBot API Reference

LumiBot is an open-source Python trading library
(https://github.com/Lumiwealth/lumibot, docs https://lumibot.lumiwealth.com).
A strategy is one Python file with a `Strategy` subclass whose lifecycle methods
LumiBot calls during backtests and live trading. This skill is the API reference:
exact method names, signatures, return types, entity shapes and copyable
examples.

Use it alongside the workflow skills:

- `lumibot-strategy-building`: how to design, write, backtest and deploy a
  strategy on BotSpot end to end.
- `fast-lumibot-strategies`: making scans, order handling and backtests fast.
- `options-strategies`, `stock-etf-strategies`: asset-specific patterns.
- `lumibot-indicators`: indicators and charting in depth.
- `lumibot-ai-agents`: AI-agent strategies in depth.
- `using-botspot-mcp`: the BotSpot tools for files, backtests and deployments.

This SKILL.md has the core facts you need most often. For anything more
specific, load exactly the reference that matches the question (with the
`skills` tool: action=get, name=lumibot-api-reference,
reference=references/<file>). Do not load every reference; pick the smallest
one that answers the question. When the exact behavior still matters and the
reference is not enough, the LumiBot source on GitHub is the final authority.

## Which reference to load

| Question is about | Load |
|---|---|
| Strategy method signatures: orders, positions, cash, prices, quotes, history, options chains, Greeks, datetime, charting, parameters, strategy attributes | `references/methods-properties.md` |
| `Asset`, `Order`, `Position`, `Quote`, `Bars`, `Chains`, `SmartLimitConfig`, `TradingFee`, crypto base/quote pairs, futures and options asset construction | `references/entities.md` |
| Which lifecycle hook to use (`initialize`, `before_market_opens`, `on_trading_iteration`, fill/cancel callbacks, `on_bot_crash`, ...), partial-fill accounting, restart and reconnect recovery, live versus backtest differences | `references/lifecycle-methods.md` |
| File and class shape, imports, the `__main__` backtest/live block | `references/strategy-structure.md` |
| Components: `self.indicators`, charting rules, `OptionsHelper` (full method list), QuiverHelper, PerplexityHelper, AI agents API summary | `references/components-overview.md` |
| `DriftRebalancerLogic` portfolio rebalancing | `references/drift-rebalancer.md` |
| Guardrails and common mistakes (crypto, futures, options sizing, fees, logging, charting, `self.vars`) | `references/notes-reminders.md` |
| Examples: AI agents (single agent, teams, committees, news, `@agent_tool`) | `references/examples-ai-agents.md` |
| Examples: historical prices, quotes, VIX, option/crypto/forex orders, cash accounting, chains, delta strikes, positions, `self.vars`, `self.indicators`, `set_market` | `references/examples-data-orders.md` |
| Examples: strikes for an expiry, OptionsHelper spreads (calendar, straddle, strangle, diagonal, ratio), option market evaluation, order details, spread profit, PerplexityHelper | `references/examples-options-and-helpers.md` |
| Examples: charts, Heikin Ashi, crypto futures, explicit and continuous futures, backtest fees, quotes, smart limit orders, Greeks, retroactive indicators | `references/examples-charts-futures.md` |
| Slow scanners, batched quotes, fast cancel/hedge order state machines | the `fast-lumibot-strategies` skill |

## Lifecycle at a glance

| Method | Runs | Use for |
|---|---|---|
| `initialize(self)` | once at start | `self.sleeptime`, `set_market(...)`, assets, components such as `OptionsHelper(self)`, default `self.vars`. Never place orders here. |
| `before_market_opens(self)` | before each session | daily watchlists, resetting daily counters |
| `on_trading_iteration(self)` | every `sleeptime` while the market is open | the main decision loop: reconcile pending orders first, then scan and trade |
| `before_market_closes(self)` / `after_market_closes(self)` | near and after the close | end-of-day exits, summaries |
| `on_new_order`, `on_partially_filled_order`, `on_filled_order`, `on_canceled_order` | on broker or simulator events | bookkeeping, hedge-after-fill. A callback reports an observation; `on_canceled_order` does not cancel anything. |
| `on_bot_crash(self, error)` | on an unhandled exception | diagnostics only; never trade from here |

`self.sleeptime` accepts `"10S"` (seconds), `"1M"` (minutes) or `"1D"` (days) style strings. Default to
`"1D"` unless the strategy really needs intraday decisions. Sleeptime is the gap
after an iteration finishes; it never interrupts a running iteration.

## Core API cheat sheet

Orders:

```python
order = self.create_order(asset, quantity, Order.OrderSide.BUY,
                          limit_price=None, stop_price=None,
                          order_type=None, order_class=None,
                          time_in_force="gtc", quote=None,
                          secondary_limit_price=None, secondary_stop_price=None,
                          smart_limit=None)
submitted = self.submit_order(order)          # also accepts a list of orders
self.cancel_order(order)                      # a request, not confirmation
self.get_order(order.identifier)              # exact-order refresh
self.get_orders(statuses=Order.ACTIVE_STATUSES)
self.close_position(asset, fraction=1.0)      # uses the actual position size
self.sell_all()
```

- Status filters use `Order.OrderStatus` enums or `Order.ACTIVE_STATUSES`, never
  strings. Rejections surface as `Order.OrderStatus.ERROR`.
- Bracket/OTO exits: `order_class=Order.OrderClass.BRACKET` (or `OTO`/`OCO`)
  with `secondary_limit_price` / `secondary_stop_price`. The older
  `take_profit_price` / `stop_loss_price` names are deprecated aliases.
- Options in live trading: prefer `order_type=Order.OrderType.SMART_LIMIT` or
  `smart_limit=SmartLimitConfig(preset=SmartLimitPreset.NORMAL)` over market
  orders.
- Crypto futures exit with `self.close_position(asset)`; a sell order opens the
  opposite position.

Account and positions:

```python
cash = self.get_cash()                    # may be None if a live refresh fails
value = self.get_portfolio_value()        # may be None; never treat None as 0
pos = self.get_position(asset)            # None if not held
positions = self.get_positions()          # includes the USD cash position
```

Cash from a sale is not available until the next iteration. In backtests,
`deposit_cash`, `withdraw_cash`, `adjust_cash`, `configure_cash_financing` and
`set_cash_financing_rates` model real cashflows and financing; never fake them
through prices or returns.

Prices and data:

```python
bars = self.get_historical_prices(asset, 100, "day")   # Bars or None; use bars.df
many = self.get_historical_prices_for_assets(assets, 100, "day")  # batched
last = self.get_last_price(asset)        # last trade, may be None or stale
lasts = self.get_last_prices(assets)     # batched last trades
q = self.get_quote(asset)                # Quote: bid, ask, mid_price, times; may be None
qs = self.get_quotes(assets)             # LumiBot 4.6.19+: {Asset: Quote or None}
now = self.get_datetime()                # never datetime.now()
```

- `get_last_price` is trade-based. For options and thin markets use
  `get_quote(...).mid_price` with bid/ask validation, or
  `OptionsHelper.evaluate_option_market(...)`.
- Always guard None (and NaN) from prices, quotes, Greeks and indicators.

Indicators and charts:

```python
sma = self.indicators.sma(asset, length=50, timestep="day")      # float or None/NaN
bb = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")
lower = bb.BBL_20_2_0                                             # IndicatorRow fields
self.add_ohlc("SPY", open=o, high=h, low=l, close=c, asset=spy)
self.add_line("SMA 50", sma, color="blue", asset=spy)
self.add_marker("Buy signal", price, color="green", symbol="arrow-up", asset=spy)
```

`self.indicators` computes once and caches; do not recompute rolling windows by
hand every iteration. Chart helpers use `detail_text` for hover text (there is no
`text` parameter). Markers are for rare events, never every iteration.

Options:

```python
from lumibot.components.options_helper import OptionsHelper
self.options_helper = OptionsHelper(self)                 # in initialize
chains = self.get_chains(underlying)                      # slow: cache per day
expiry = self.options_helper.get_expiration_on_or_after_date(
    target_date, chains, "call", underlying_asset=underlying)
option = self.options_helper.find_next_valid_option(underlying, strike, expiry, "call")
strike = self.options_helper.find_strike_for_delta(
    underlying_asset=underlying, underlying_price=price,
    target_delta=0.30, expiry=expiry, right="call")
evaluation = self.options_helper.evaluate_option_market(option, max_spread_pct=0.15)
if self.options_helper.has_actionable_price(evaluation):
    ...
```

Never pick expiries or strikes by hand from chains, and never loop `get_greeks`
over every strike to hunt a delta. Option prices are per share; one contract is
usually 100 shares, so size with `price * 100`.

Assets:

```python
Asset("AAPL")                                                 # stock
Asset("SPY", asset_type=Asset.AssetType.OPTION, expiration=date(2025, 1, 17),
      strike=500, right=Asset.OptionRight.CALL)
Asset("BTC", asset_type=Asset.AssetType.CRYPTO)               # base only; quote via quote=
Asset("ES", asset_type=Asset.AssetType.CONT_FUTURE)           # root symbol
Asset("VIX", asset_type=Asset.AssetType.INDEX)
```

`Asset` takes no `exchange=` or `currency=` argument. Crypto and forex pairs use
a separate quote asset (for example `Asset("USD", asset_type=Asset.AssetType.FOREX)`)
passed as `quote=` to price and order calls. Futures use the root symbol plus
`expiration=`; continuous futures use the bare root.

State and parameters:

- Put persistent state in `self.vars` (survives iterations and restarts). Never
  assign arbitrary attributes like `self.name`, `self.asset` or `self.symbol`;
  they can collide with LumiBot internals.
- Declare one `parameters = {}` dictionary at the top of the class and read it
  with `self.parameters`.
- Never call `time.sleep()`; use `self.sleep(...)` sparingly, and prefer storing
  timestamps in `self.vars` and checking them next iteration.
- Never add `from __future__ import annotations`; it breaks backtests.
- Keep strategy code broker-agnostic: no broker keys or broker SDK calls. Broker
  credentials come from the environment.
- Log every decision (`self.log_message(..., color=...)`, colors white, red,
  green, blue, yellow), including why the bot did not trade.

## Backtesting basics

- On BotSpot, the backtest date range and data provider are chosen when you call
  `start_backtest` (and `set_data_provider` where available). Do not hardcode
  backtest dates in the script, and leave `datasource_class=None` in the
  `__main__` block unless the user asks for a specific provider.
- Use `TradingFee(per_contract_fee=0.65)` style fees for options and futures and
  `TradingFee(percent_fee=0.001)` for stocks; `flat_fee` is per order and
  undercounts multi-contract trades.
- Crypto strategies must call `self.set_market("24/7")` in `initialize`.
- Backtest quotes do not carry live bid/ask timestamps; run quote-age checks only
  when `not self.is_backtesting`.

## Working with strategy files on BotSpot

The usual loop with the BotSpot MCP tools: read the code with `get_file` (or
`list_files`), make focused edits with `patch_file` or full rewrites with
`replace_file`, read the saved revision back with `get_file`, then run
`start_backtest` and follow it with `backtest_status`, `get_backtest_logs` and
`get_backtest_artifact`. See `lumibot-strategy-building` and `using-botspot-mcp`
for the full workflow. Live deployment and any real-money trade always require
the user's own approval on botspot.trade.

Examples in this skill illustrate the API. They are not investment advice or
recommendations, and nothing here implies any expected return.
