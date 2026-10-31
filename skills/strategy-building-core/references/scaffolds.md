> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: strategy-template-catalog
description: Use when choosing a known-good first-cycle strategy scaffold before generating or refining a BotSpot strategy.
---

# Strategy Template Catalog

Use these patterns as starting guidance for first-cycle strategy creation.
They are not substitutes for the raw user request. Preserve the user's named
asset, direction, risk constraints, and rejected ideas first, then adapt the
closest template so the strategy's own simplified first revision has a
realistic path to at least one filled trade in the first-test
window. These templates must not become fake proof trades or unrelated
backtest-only branches.

## us_stock_etf_first_cycle_smoke

Best for US stock or ETF strategies such as SPY, QQQ, IWM, AAPL, NVDA, SPXL,
or TQQQ.

Template contract:
- In `initialize`, create one to three `Asset(symbol, Asset.AssetType.STOCK)`
  objects, set a small risk budget, and keep user thresholds as parameters.
- In `on_trading_iteration`, fetch a small bar window and a current/reference
  price. Use simple first-revision signal logic that belongs to the user's idea:
  momentum can buy strength, mean reversion can buy weakness, risk-off can reduce
  or avoid exposure, and contest/ranking strategies can rank a tiny liquid
  universe.
- Run the user's exits, stops, and risk caps from the beginning.
- Log skipped entries with the exact condition that blocked them.

Avoid:
- 20/50, 50/200, rare RSI extremes, volume plus trend plus breakout stacks, or
  any warmup gate as the only entry path for the first cycle.

## usd_quoted_crypto_first_cycle_smoke

Best for BTC/USD, ETH/USD, BTC/USDT, ETH/USDT, BTC/EUR, ETH/EUR, or similar
spot crypto pairs with a proven runner/data path.

Template contract:
- Create the base coin as `Asset("BTC", Asset.AssetType.CRYPTO)` or
  `Asset("ETH", Asset.AssetType.CRYPTO)` and create the quote separately as
  `Asset("USD", Asset.AssetType.FOREX)` or the requested quote asset.
- Do not encode `BTC-USD`, `BTC/USD`, `BTCUSD`, `BTC/EUR`, or `BTCEUR` as the
  crypto base symbol.
- Treat crypto as 24/7. Use quote-aware history/price/order calls.
- Use a simple first-revision version of the requested crypto signal before
  long warmups, crossovers, or stacked gates can return with no trade.

Avoid:
- huge history fetches such as 10000 bars;
- converting BTC/EUR or ETH/EUR to USD silently.

## supported_futures_first_cycle_smoke

Best for ES, MES, NQ, MNQ, RTY, M2K, US100, NAS100, or Nasdaq 100 futures-style
requests that BotSpot can express as supported futures.

Template contract:
- Use `Asset.AssetType.CONT_FUTURE` for ES/MES/NQ/MNQ-style continuous futures
  unless the user explicitly asks for a dated contract.
- Create a helper that first tries `get_last_price(asset)` and then falls back
  to the latest completed historical bar close from `get_historical_prices`.
- Use that reference price for sizing and validation decisions.
- Use a simple first-revision version of the requested futures signal before
  session windows, breakout boxes, indicator warmup, or strict confirmation
  gates can skip every bar.
- If the strategy has session windows, compare plain `datetime.time` values or
  normalize all datetimes through the same LumiBot timezone helper before
  comparing. Never compare naive `datetime(...)` objects against
  `self.get_datetime()` or bar-index timestamps; that can crash with
  offset-naive versus offset-aware datetime errors.

Avoid:
- logging only "price unavailable" while OHLC bars exist;
- silently substituting QQQ for a futures request.

## us_options_first_cycle_smoke

Best for US stock/ETF/index options where the user wants calls, puts, spreads,
covered calls, wheels, or options momentum.

Template contract:
- Use `OptionsHelper` with documented methods only: `self.get_chains(...)`,
  `get_expiration_on_or_after_date(...)`, `find_next_valid_option(...)`, and
  `evaluate_option_market(...)`.
- Before indicator gates or complex spread validation can return, use a
  simplified first-revision option path that still matches the user's direction,
  DTE range, and instrument.
- If a multi-leg spread is too strict for the first smoke, make the first saved
  revision a single-leg version of the same directional idea. If an indicator is
  unavailable, log that the strict signal is deferred, but do not skip the
  first-cycle order path when the underlying price, option chain, and actionable
  option price are available.
- Buy one contract or the smallest affordable size when
  `OptionsHelper.has_actionable_price(evaluation)` is true and
  `evaluation.buy_price` is executable. Use a permissive smoke spread cap such
  as `max_spread_pct=1.0`.
- Keep the user's multi-leg spread/wheel/covered-call logic as stricter later
  revision logic or as a secondary path after the simplified first-revision path.
- Use `import numpy as np` for numeric math. Never use `pd.np`; modern pandas
  does not expose that alias and the backtest will fail before trades are
  written.

Avoid:
- inventing helper names such as `get_chains_expirations_with_data`;
- using `evaluation.mid_price`;
- letting one missing or wide spread leg block the whole first smoke run;
- returning from `on_trading_iteration` because RSI or another normal-mode
  indicator is unavailable before the starter path has tried to enter.

## ai_agent_trader_scaffold

Best when the user explicitly asks for an AI, LLM, GPT, Gemini, Claude, or
agent-owned trading strategy.

Template contract:
- Create the agent or agent committee once in `initialize`.
- Keep `on_trading_iteration` as a thin delegation layer unless the user asked
  for deterministic hybrid controls.
- Use `allow_trading=True` only for the final trading agent that should place
  orders. Research, bull, bear, and risk-review agents should use
  `allow_trading=False`.
- For first-cycle validation, prefer a clear trading-enabled final agent prompt
  that tells it to place orders when justified; do not create a parallel
  indicator strategy unless the user asked for hybrid execution.

Avoid:
- parsing agent prose with brittle substring checks;
- adding manual order submission around a trading-enabled agent unless the code
  prevents duplicate execution.

## supported_starter_first_cycle_smoke

Best when the user asks for a sample, starter, demo, or first BotSpot strategy
but does not specify a detailed method.

Template contract:
- If the user named a concrete supported market, use the matching template
  above.
- If the user did not name a market and this is a sample/default build, use a
  simple SPY stock/ETF starter and explain the default after tool execution.
- If the user did not name a market and did not ask for a sample/default build,
  ask one concise clarification before generation.
