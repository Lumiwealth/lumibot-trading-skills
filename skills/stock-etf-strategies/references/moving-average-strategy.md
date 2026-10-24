# Moving Average Strategies

Part of the `stock-etf-strategies` skill. Covers SMA and EMA crossovers, price
versus average trend filters, and multi-average regimes. Illustrations only,
not recommendations.

## Rules to confirm

- Average type (SMA or EMA) and exact lookbacks.
- Signal: a **crossover event** (fast crosses above slow) or a **state** (fast
  is above slow). These trade very differently. Do not swap one for the other
  without approval.
- Bar size and when the check runs.
- Exit: opposite cross, price below an average, a stop, or a time exit.

## Example: daily 50/200 crossover on one ETF

```python
import pandas as pd
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class MovingAverageCross(Strategy):
    parameters = {"symbol": "SPY", "fast": 50, "slow": 200}

    def initialize(self):
        self.sleeptime = "1D"
        self.vars.prev_fast = None
        self.vars.prev_slow = None

    def on_trading_iteration(self):
        p = self.parameters
        asset = Asset(p["symbol"], asset_type=Asset.AssetType.STOCK)

        fast = self.indicators.sma(asset, length=p["fast"], timestep="day")
        slow = self.indicators.sma(asset, length=p["slow"], timestep="day")
        if fast is None or slow is None or pd.isna(fast) or pd.isna(slow):
            self.log_message("Averages not ready yet", color="yellow")
            return

        prev_fast = self.vars.get("prev_fast")
        prev_slow = self.vars.get("prev_slow")
        self.vars.prev_fast, self.vars.prev_slow = float(fast), float(slow)

        dt = self.get_datetime()
        self.add_line("SMA fast", float(fast), color="blue", dt=dt, asset=asset)
        self.add_line("SMA slow", float(slow), color="orange", dt=dt, asset=asset)

        if prev_fast is None or prev_slow is None:
            return  # need one prior observation to detect a cross

        crossed_up = prev_fast <= prev_slow and fast > slow
        crossed_down = prev_fast >= prev_slow and fast < slow
        position = self.get_position(asset)

        if crossed_up and position is None:
            price = self.get_last_price(asset)
            if price is None or price <= 0:
                return
            quantity = int((self.get_cash() * 0.99) // price)
            if quantity > 0:
                self.submit_order(self.create_order(asset, quantity, "buy"))
                self.add_marker("Buy", float(price), color="green", symbol="arrow-up",
                                dt=dt, asset=asset)
        elif crossed_down and position is not None and position.quantity > 0:
            self.submit_order(self.create_order(asset, position.quantity, "sell"))
            self.add_marker("Sell", float(self.get_last_price(asset) or fast), color="red",
                            symbol="arrow-down", dt=dt, asset=asset)
```

Notes:

- `self.indicators.sma(...)` returns the current scalar and fetches its own
  history; guard for None and NaN. See the `lumibot-indicators` skill.
- A crossover needs the previous values. Storing them in `self.vars` is the
  simplest way; alternatively compute both averages over a short series and
  compare the last two rows.
- On the first iteration after a restart there is no previous value, so no
  cross can be detected that day. That is correct behavior, not a bug.

## Choosing a test window

- A daily 20/50 cross usually needs one to three months to fire once.
- A 50/200 cross is rare (often once or twice a year or less). Say plainly
  when an affordable test window may show no trade.
- Intraday crosses on minute bars fire often; a few days is usually enough.

## Common no-trade causes

- **Window too short.** Fix the window, never the rules. Rerun the same saved
  revision over a longer window.
- **History too short for the long average** when computing averages by hand
  with `get_historical_prices`: request more bars than the slow lookback.
- **Cross detection compares values that are never stored**, so no cross is
  ever seen (a code bug).
- **Returning early when an optional average is missing.** Only the averages
  the rule needs should gate the trade.

## Repair rules

- Check the window first. Then inspect logs and the indicators artifact
  (`get_backtest_artifact`, then `query_csv`) to see whether averages were NaN
  (code or data) or simply never crossed (rules).
- Never shorten lookbacks, switch a crossover to an "already above" state, or
  add a buy-now entry to force a trade unless the user approves that exact
  change.
