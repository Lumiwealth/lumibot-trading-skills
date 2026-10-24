# Crypto strategies in LumiBot

Use with the `lumibot-strategy-building` skill for spot crypto, crypto quote
assets and crypto perpetual futures.

## Crypto spot assets

- The `Asset` symbol is the base coin only:
  `Asset("BTC", asset_type=Asset.AssetType.CRYPTO)`.
- The quote is a separate asset, for example
  `Asset("USD", asset_type=Asset.AssetType.FOREX)` for BTC/USD, or the
  requested quote such as USDT or EUR.
- Never use pair strings such as `BTC-USD`, `BTC/USD`, `BTCUSD`, `BTC/EUR` or
  `BTCEUR` as the symbol. The runner then looks for a nonexistent asset such as
  `BTC-USD/USD` and the backtest can finish with no trades.
- Preserve the requested quote. Do not silently convert BTC/EUR to BTC/USD.
- If you set a quote asset, set it for both the backtest call and the live
  strategy construction.

## Market hours and data

- Crypto trades around the clock. Call `self.set_market("24/7")` in
  `initialize`; without it the strategy stops at the stock market close.
- Keep `datasource_class=None` in the backtest harness so the environment picks
  the provider. BotSpot Auto routes spot crypto to a managed source.
- Avoid huge history requests; request the lookback you need plus a buffer.

## Quantities

- Crypto allows fractional quantities (0.5 BTC, 0.01 ETH). Keep enough decimal
  places; LumiBot rounds to what the venue accepts, but rounding too coarsely
  yourself can make an order too small to fill.
- Size from confirmed cash and include fees.

## Crypto perpetual futures

- Use the full pair symbol with the futures type, for example
  `Asset("BTCUSDT", asset_type=Asset.AssetType.CRYPTO_FUTURE)` (ETHUSDT and
  SOLUSDT work the same way). The default quote for USDT-margined perpetuals is
  `Asset("USDT", Asset.AssetType.CRYPTO)`.
- Close positions with `self.close_position(asset)`. On some venues a
  `submit_order` on the opposite side opens a new position instead of closing.
  Use `close_position` to exit, then `submit_order` to open the next position.
- In backtests, USDT perpetuals use matching spot history as a proxy (BTCUSDT
  maps to BTC/USDT, not BTC/USD). Keep `datasource_class=None`.
- For live trading, if direct perpetual prices are unavailable, read spot with
  `Asset("BTC", asset_type=Asset.AssetType.CRYPTO)` and place orders with the
  futures asset.
- Quantities can be fractional.

## Common failure causes

- Pair string used as the base asset.
- Test window too short for long-lookback rules, or warmup history not
  requested before the window.
- An indicator that cannot compute on the available bars, so every iteration
  returns early.
- Data download is slower on the first simulated day than later days.

## Repair approach

- Read the logs for missing crypto data, symbol construction and quote asset
  errors.
- Fix technical defects (asset construction, data availability, indicator
  computation, API usage, state handling) and keep the user's signals,
  thresholds, warmups, sizing and risk.
- If a rule change is needed, propose the exact change and get approval before
  saving it.
- If a specific pair truly lacks data, explain that limit and offer a supported
  pair.
