# Mean Reversion Strategies

Part of the `stock-etf-strategies` skill. Covers RSI oversold and overbought,
Bollinger Band touches, z-scores and pairs. Illustrations only, not
recommendations.

## Rules to confirm

- Indicator and parameters (RSI length, band length and width, z-score
  window).
- Entry threshold and whether it needs a cross back (for example RSI crosses
  back above 30) or just a level.
- Exit: return to the mean, opposite threshold, stop, or a maximum holding
  period.
- Any trend filter (for example only buy dips above the 200-day average).

## Example: RSI dip buying with a trend filter

```python
import pandas as pd
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class RsiMeanReversion(Strategy):
    parameters = {
        "symbol": "SPY",
        "rsi_length": 14,
        "entry_rsi": 30,
        "exit_rsi": 55,
        "trend_length": 200,
        "max_hold_days": 10,
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.vars.entry_date = None

    def on_trading_iteration(self):
        p = self.parameters
        asset = Asset(p["symbol"], asset_type=Asset.AssetType.STOCK)
        rsi = self.indicators.rsi(asset, length=p["rsi_length"], timestep="day")
        trend = self.indicators.sma(asset, length=p["trend_length"], timestep="day")
        price = self.get_last_price(asset)
        if any(v is None or pd.isna(v) for v in (rsi, trend)) or price is None:
            self.log_message("Inputs not ready", color="yellow")
            return

        dt = self.get_datetime()
        self.add_line("RSI", float(rsi), color="purple", plot_name="RSI", dt=dt, asset=asset)
        self.add_line("RSI entry", float(p["entry_rsi"]), color="gray", style="dashed",
                      plot_name="RSI", dt=dt, asset=asset)

        position = self.get_position(asset)
        if position is None:
            if rsi < p["entry_rsi"] and price > trend:
                quantity = int((self.get_cash() * 0.99) // price)
                if quantity > 0:
                    self.submit_order(self.create_order(asset, quantity, "buy"))
                    self.vars.entry_date = dt.date().isoformat()
                    self.add_marker("Buy", float(price), color="green", symbol="arrow-up",
                                    dt=dt, asset=asset)
            return

        held_days = 0
        if self.vars.get("entry_date"):
            held_days = (dt.date() - pd.Timestamp(self.vars.entry_date).date()).days
        if rsi > p["exit_rsi"] or held_days >= p["max_hold_days"]:
            self.submit_order(self.create_order(asset, position.quantity, "sell"))
            self.vars.entry_date = None
            self.add_marker("Sell", float(price), color="red", symbol="arrow-down",
                            dt=dt, asset=asset)
```

## Bollinger Bands and z-scores

- `self.indicators.bbands(asset, length=20, std=2.0, timestep="day")` returns
  a row with lower, middle and upper fields (names such as `BBL_20_2.0`
  become attributes like `BBL_20_2_0`; inspect `row.as_dict()` if unsure).
- A z-score is easiest with `self.indicators.custom(...)` computing
  `(close - rolling_mean) / rolling_std`.
- Pairs: compute the spread or ratio of two assets from aligned histories.
  Make sure both legs have data for the same timestamps; a missing leg is a
  data problem, not a signal.

## Choosing a test window

Extreme thresholds on daily bars (for example RSI below 20) may need months to
fire. Check plausibility and say plainly when an affordable test may show no
trade.

## Common no-trade causes

- Window too short for how rarely the thresholds fire.
- Indicators not ready because history is missing (a data or code issue).
- Several rare confirmations required at once, or conditions that conflict
  (for example oversold and above a fast trend line at the same moment).
- One leg of a pair has no data (a data problem).

## Repair rules

- Check the window first; if it was too short, rerun the same revision over a
  longer window without editing.
- Use the indicators artifact to see whether the signal never computed (code
  or data) or never crossed the threshold (rules).
- When the rules never fire in an adequate window, explain why and offer
  specific choices (a longer test, one exact threshold change, or dropping one
  named filter). Wait for the user's choice.
- Do not add artificial orders, and do not turn mean reversion into trend
  following without approval.
- For options-based mean reversion, also load the `options-strategies` skill.
