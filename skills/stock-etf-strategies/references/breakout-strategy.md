# Breakout Strategies

Part of the `stock-etf-strategies` skill. Covers channel and Donchian
breakouts, support and resistance breaks, momentum breakouts and opening-range
breakouts. Illustrations only, not recommendations.

## Rules to confirm

- Breakout level: highest high of N bars, a prior day's high, an opening range,
  a fixed level.
- Confirmation: close above the level, price trading above it, volume above a
  baseline, ATR filter.
- Entry timing and the latest allowed entry time.
- Exit: opposite channel, trailing stop, fixed stop and target, end of day.

## Example: daily Donchian channel breakout

```python
import pandas as pd
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class DonchianBreakout(Strategy):
    parameters = {"symbol": "QQQ", "entry_lookback": 20, "exit_lookback": 10}

    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        p = self.parameters
        asset = Asset(p["symbol"], asset_type=Asset.AssetType.STOCK)
        length = max(p["entry_lookback"], p["exit_lookback"]) + 5
        bars = self.get_historical_prices(asset, length=length, timestep="day")
        if bars is None or bars.df is None or len(bars.df) < length - 5:
            self.log_message("Not enough history", color="yellow")
            return
        df = bars.df

        last_close = float(df["close"].iloc[-1])
        # Channel from the bars BEFORE the latest completed bar
        upper = float(df["high"].iloc[-(p["entry_lookback"] + 1):-1].max())
        lower = float(df["low"].iloc[-(p["exit_lookback"] + 1):-1].min())

        dt = df.index[-1]
        self.add_line("Upper channel", upper, color="green", dt=dt, asset=asset)
        self.add_line("Lower channel", lower, color="red", dt=dt, asset=asset)

        position = self.get_position(asset)
        if position is None and last_close > upper:
            price = self.get_last_price(asset)
            if price is None or price <= 0:
                return
            quantity = int((self.get_cash() * 0.99) // price)
            if quantity > 0:
                self.submit_order(self.create_order(asset, quantity, "buy"))
                self.add_marker("Breakout", last_close, color="green", symbol="arrow-up",
                                dt=dt, asset=asset)
        elif position is not None and position.quantity > 0 and last_close < lower:
            self.submit_order(self.create_order(asset, position.quantity, "sell"))
            self.add_marker("Exit", last_close, color="red", symbol="arrow-down",
                            dt=dt, asset=asset)
```

The channel excludes the bar being tested. Including it makes "close above
the highest high" impossible on that same bar.

## Opening-range breakout (intraday)

- Build the range from regular-session bars starting at the open, for the
  exact duration in the rules (for example the first 15 minutes).
- A bar timestamp marks the start of its interval. With 5-minute bars, a
  15-minute range starting at 09:30 uses the bars starting 09:30, 09:35 and
  09:40. The bar starting 09:45 is the first candidate after the range.
- A bar is complete only when its start plus its interval is at or before the
  current time. Never decide from an unfinished bar.
- If only 1-minute bars are available, aggregate exact, non-overlapping
  intervals yourself before comparing closes or volume.
- When the rule says "higher volume" with no baseline, compare against the
  opening-range bars of the same session. Pre-market and after-hours bars are
  not part of it.
- The first completed bar after the range that meets the rule is the breakout.
  Unless the rules limit how late an entry may be, it stays valid at a later
  check while price still holds above the range.
- Use timezone-aware times from `self.get_datetime()` (US equities are on
  America/New_York time). A naive time comparison can skip the session.
- Set `self.sleeptime` to the bar interval or finer (for example "5M") and
  stop entries before `self.minutes_before_closing` cuts off iterations. A
  late order can be rejected or never fill.
- Exits at end of day: use `before_market_closes()` or a time check.

## Choosing a test window

- Intraday rules: about a week or less is usually enough to see entries.
- Daily multi-week breakouts on one symbol may need one to three months.

## Common no-trade causes

- Window too short for how rarely the breakout fires.
- Session or timezone logic skips the trading period (a code bug).
- The channel includes the bar being tested (a code bug).
- Orders placed too late in the day and rejected by the close cutoff (a code
  bug).
- Breakout, volume and ATR filters never all agree in an adequate window (a
  rules issue).

## Repair rules

- Check the window first; if it was too short, rerun the same revision over
  a longer window without editing.
- Use logs and the indicators artifact to find the first blocked condition.
  Fix code-level blockers (session, timezone, close cutoff, channel window)
  without changing rules.
- If the user's own thresholds never fire in an adequate window, explain why
  and offer specific choices before changing any threshold, volume multiple,
  trading window or universe.
