# First-version strategy templates

Use these patterns as a starting shape for a new strategy's first version. They
never replace the user's request: keep the user's named asset, direction, risk
limits and rejected ideas first, then adapt the closest template. The goal is a
first version whose own logic has a realistic chance to trade in its test
window. Templates must never become fake proof trades or backtest-only branches.
When the user gave exact rules, implement those rules; simplify only with the
user's approval.

## US stocks and ETFs

Examples: SPY, QQQ, IWM, AAPL, NVDA, leveraged ETFs.

- In `initialize`, create one to three `Asset(symbol, Asset.AssetType.STOCK)`
  objects in `self.vars`, set `sleeptime`, and keep thresholds in `parameters`.
- In `on_trading_iteration`, fetch a small bar window filtered to the current
  simulated time and a reference price. Use simple logic that belongs to the
  idea: momentum buys strength, mean reversion buys weakness, risk-off reduces
  exposure, ranking strategies rank a tiny liquid universe.
- Run exits, stops and risk caps from the start.
- Log skipped entries with the exact condition that blocked them.

Avoid for a sample bot: 20/50 or 50/200 crossovers, rare RSI extremes, volume
plus trend plus breakout stacks, or any warmup gate as the only entry path.
(If the user asked for those rules, use them and pick a long enough window.)

See `stock-etf-strategies` for complete breakout, mean-reversion and
moving-average examples.

## Crypto (spot market)

Examples: BTC/USD, ETH/USD, BTC/USDT, ETH/USDT, BTC/EUR.

- Base coin as `Asset("BTC", Asset.AssetType.CRYPTO)`; quote created separately
  as `Asset("USD", Asset.AssetType.FOREX)` or the requested quote asset.
- Never encode `BTC-USD`, `BTC/USD`, `BTCUSD`, `BTC/EUR` or `BTCEUR` as the
  base symbol.
- `self.set_market("24/7")`; pass the quote asset to history, price and order
  calls.
- Avoid huge history requests (for example 10,000 bars) and never convert
  BTC/EUR to USD silently.

Details: `references/crypto-strategies.md`.

## Futures

Examples: ES, MES, NQ, MNQ, RTY, M2K, Nasdaq 100 futures.

- Use `Asset.AssetType.CONT_FUTURE` with the root symbol for continuous futures
  unless the user asks for a dated contract.
- A reference-price helper that tries `get_last_price(asset)` first and falls
  back to the latest completed bar close from `get_historical_prices`. Use it
  for sizing and order decisions.
- Session windows compare plain `datetime.time` values, or datetimes converted
  to the same timezone. Never compare a naive `datetime(...)` with
  `self.get_datetime()` or bar timestamps.

Avoid: logging only "price unavailable" while bars exist; substituting QQQ for
a futures request. Details: `references/futures-strategies.md`.

## US options

Calls, puts, spreads, covered calls, wheels, options momentum.

- Use `OptionsHelper` with documented methods only: `self.get_chains(...)` as
  input, `get_expiration_on_or_after_date(...)`, `find_next_valid_option(...)`,
  `find_strike_for_delta(...)` with keyword arguments including
  `underlying_price`, and `evaluate_option_market(...)`.
- Trade only when `OptionsHelper.has_actionable_price(evaluation)` is true;
  otherwise log the evaluation's data quality flags and skip.
- Size with the 100 multiplier and `TradingFee(per_contract_fee=0.65)`.
- Use `import numpy as np` for numeric math. Never `pd.np`; modern pandas does
  not have it.
- For a sample options bot, a single-leg version of the directional idea is a
  fine first version. For a user who asked for a specific spread, build that
  spread; ask before replacing it with a simpler structure.

Avoid: invented helper names; using a mid price without validating bid and ask;
returning from the iteration before trying the entry path just because a
secondary indicator is still warming up. See `options-strategies`.

## AI-owned trading

When the user asks for an AI, LLM or agent-owned strategy:

- Create the agent (or research agents plus one trading agent) once in
  `initialize`.
- Keep `on_trading_iteration` a thin delegation layer unless the user asked for
  deterministic hybrid controls.
- Only the final trading agent has trading enabled; research and review agents
  do not.
- Do not parse agent prose with brittle substring checks, and do not add manual
  order submission around a trading-enabled agent unless the code prevents
  duplicate execution.

See `lumibot-ai-agents` for the full pattern.

## Sample or starter request

- If the user named a supported market, use the matching template above.
- If they asked for a sample or default bot without a market, use a simple SPY
  stock template and explain that default after building.
- Otherwise ask one short question for the market before building.
