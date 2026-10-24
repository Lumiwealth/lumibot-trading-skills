# Futures strategies in LumiBot

Use with the `lumibot-strategy-building` skill for futures, continuous futures
and session-window logic.

## Assets

- Continuous futures: `Asset("ES", asset_type=Asset.AssetType.CONT_FUTURE)`.
  Use the base symbol only (`ES`, `MES`, `NQ`, `MNQ`), never `ES1` or `MNQ1`;
  the continuous type resolves the contract.
- Dated contracts: `Asset("CL", asset_type=Asset.AssetType.FUTURE, expiration=...)`.
  Always the root symbol plus `expiration=`. Never embed month or year codes in
  the symbol. A calendar spread uses two Asset objects with the same root and
  different expirations.
- Nasdaq 100, US100 or NAS100 futures requests use `NQ` or `MNQ`, not QQQ,
  unless the user asks for an ETF proxy. Micro contracts (MES, MNQ, MGC) are a
  smaller-size option when the user wants one; changing contract size is a
  sizing change, so confirm it.
- Futures symbols are roots, not spot tickers. Crypto futures on CME use their
  own roots (for example a micro bitcoin root differs from the standard one);
  check the exact root before building.

## Prices

`get_last_price(asset)` can return `None` in backtests even when bars and
indicators exist for the same contract. Do not let that block every iteration:

```python
def reference_price(self, asset):
    """Return the latest trade price, or the last completed bar close.

    Args:
        asset: The futures Asset.

    Returns:
        A float price, or None when neither source has data.
    """
    price = self.get_last_price(asset)
    if price is not None:
        return float(price)
    bars = self.get_historical_prices(asset, 5, "minute")
    if bars is None or bars.df is None or bars.df.empty:
        return None
    df = bars.df[bars.df.index <= self.get_datetime()]
    if df.empty:
        return None
    self.log_message(f"{asset.symbol}: using last bar close as reference price.")
    return float(df["close"].iloc[-1])
```

Define it as a method of your strategy class. Log which source was used.

## Sessions and timezones

- Compare plain `datetime.time` values, or convert every datetime to the same
  timezone before comparing. Never compare a naive `datetime(...)` with
  `self.get_datetime()` or bar index timestamps; that raises offset-naive versus
  offset-aware errors.
- Make sure the session the strategy waits for actually occurs in the backtest
  window.

## Fees

Backtest futures with `TradingFee(per_contract_fee=0.85)` for standard
contracts or about `0.50` for micros. Never `flat_fee`, which charges once per
order regardless of contract count.

## Data provider

Keep `datasource_class=None`. BotSpot Auto routes futures to a managed source.
If a symbol or contract is not covered there, an alternative is a
bring-your-own-key futures data provider; the user supplies that key as a
saved environment variable.

## Common failure causes

- Timezone comparison errors in session windows.
- `get_last_price` unavailable in the backtest while bars exist.
- Waiting for a session open or close that never occurs in the tested range.
- Wrong contract type or symbol shape.

## Repair approach

Read the logs for datetime, price-unavailable, contract and session messages.
If bars and indicators exist but no orders were placed, check whether a price or
sizing gate returned before order placement. Keep the requested market and the
user's rules.
