# Computing Indicators with self.indicators

Part of the `lumibot-indicators` skill.

`self.indicators` is a built-in accessor on every LumiBot Strategy. It gives
cached, point-in-time indicator values backed by pandas-ta-classic. Prefer it
over hand-rolled `rolling(...)` columns: it is shorter, cached, and does not
look ahead in backtests.

## When to use it

- Any standard indicator: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX,
  stochastic, VWAP, Supertrend and the rest of pandas-ta-classic (about 130).
- Any custom computation over historical bars (rolling medians, slopes,
  z-scores, spreads): use `self.indicators.custom(...)`.

## Built-in indicators

Call the snake_case pandas-ta-classic name with the asset, a timestep and that
indicator's keyword arguments:

```python
sma_50 = self.indicators.sma(asset, length=50, timestep="day")
ema_20 = self.indicators.ema(asset, length=20, timestep="day")
rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")
atr_14 = self.indicators.atr(asset, length=14, timestep="day")
macd = self.indicators.macd(asset, fast=12, slow=26, signal=9, timestep="day")
bands = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")
```

### Return types

- **Single-column built-ins** (SMA, EMA, RSI, ATR and similar) return the
  current scalar value, usually a float. Do not access attributes such as
  `.sma_50` on it.
- **Multi-column built-ins** (MACD, Bollinger Bands, stochastic, ADX and
  similar) return an `IndicatorRow`: a read-only, attribute-style view of the
  current bar.

```python
if macd is not None:
    macd_line = macd.MACD_12_26_9
    signal_line = macd.MACDs_12_26_9
    hist = macd.MACDh_12_26_9

if bands is not None:
    upper, mid, lower = bands.BBU_20_2_0, bands.BBM_20_2_0, bands.BBL_20_2_0
```

IndicatorRow fields are case-sensitive and keep pandas-ta-classic's original
names. Attribute access only replaces dots and hyphens with underscores, so
`bands["BBU_20_2.0"]` and `bands.BBU_20_2_0` are the same field. Parameter
changes change the names; call `row.as_dict()` and log it instead of
guessing.

### Guard everything

```python
import pandas as pd

sma_50 = self.indicators.sma(asset, length=50, timestep="day")
if sma_50 is None or pd.isna(sma_50):
    self.log_message("SMA not ready", color="yellow")
    return

row = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")
if row is None:
    return
upper = row.BBU_20_2_0
if upper is None or pd.isna(upper):
    return
```

Early in a series, with missing data, or with too few bars, results are None
or NaN. Guard both the row and each field you read.

## Custom indicators

`self.indicators.custom(name, fn, asset, timestep="day", **kwargs)` runs
`fn(df, **kwargs)` over a copy of the history available at the current
strategy time. `df` has the usual `open`, `high`, `low`, `close` and `volume`
columns.

- `fn` returns a Series: you get the current scalar.
- `fn` returns a DataFrame: you get an IndicatorRow.
- `name` is a stable label used in the cache key; give each distinct
  indicator its own name. Keyword arguments are part of the cache key too.

```python
def _median(df, window=200):
    return df["close"].rolling(window).median()

median_200 = self.indicators.custom("median_200", _median, asset, timestep="day", window=200)

def _ema_pair(df, fast=50, slow=200):
    return pd.DataFrame({
        "ema_fast": df["close"].ewm(span=fast, adjust=False).mean(),
        "ema_slow": df["close"].ewm(span=slow, adjust=False).mean(),
    })

pair = self.indicators.custom("ema_pair_50_200", _ema_pair, asset, timestep="day")
if pair is not None and pair.ema_fast is not None and pair.ema_slow is not None:
    trend_up = pair.ema_fast > pair.ema_slow
```

Custom functions must be causal: no centered rolling windows, no negative
shifts, nothing that reads later rows. LumiBot rejects some non-causal
parameters, but it cannot prove an arbitrary function is causal.

## Other accessor methods

- `self.indicators.calculate(asset, "rsi", timestep="day", parameters={"length": 14})`:
  same as the attribute call, with the indicator name as a string.
- `self.indicators.calculate_window(asset, "sma", start=..., end=..., timestep="day", parameters={"length": 20})`:
  uses only bars inside an inclusive window with timezone-aware `start` and
  `end` (end no later than the strategy time). No warmup is borrowed from
  before the window; an insufficient window returns a missing value, never
  zero.
- `self.indicators.fibonacci(asset, timestep="day", direction="up", length=None)`:
  range retracement levels from observed bars. It does not infer trend,
  pivots or signals.
- `self.indicators.invalidate(asset=None)`: drop cached results (rarely
  needed; the cache refreshes itself when new bars arrive).

## How caching works

- The cache key includes asset, timestep, indicator name and parameters.
- Results refresh automatically when the underlying history changes (new
  bars), so there is nothing to clear between iterations.
- Lookup of the current bar is fast (binary search on the index), so calling
  the accessor every iteration is fine.

## Bar availability and timing

- Establish the data source's timestamp convention and which bar was fully
  complete at the decision time. A timestamp alone does not prove a bar was
  complete.
- Apply the requested completed-bar selection once. If history already ends
  at the latest completed bar, an extra `.shift(1)` adds a one-bar delay. Do
  not add a shift merely to "avoid look-ahead" or because execution happens
  in the next session.
- Keep the calculation's original index. For multi-timeframe inputs, align by
  availability time, then distinguish when a signal is observed from when the
  order fills.
- Check values against the original bars at signal boundaries, including
  signals that did not produce a fill. A strategy's own logged indicator can
  repeat a calculation error and is not independent confirmation.

## Migrating hand-rolled indicators

Only migrate when it is requested or clearly helpful, and only as a local,
behavior-preserving change.

1. `df = self.get_historical_prices(asset, length=...).df` followed by
   `df["sma_x"] = df["close"].rolling(x).mean()` (or `.ewm(...)` or another
   window operation) can usually become
   `sma_x = self.indicators.sma(asset, length=x, timestep=...)`.
   Remember the built-in returns a scalar, not a column.
2. A `compute_indicators(self, asset)` helper can usually become a nested
   function passed to `self.indicators.custom("name", fn, asset, timestep=...)`.
3. Equivalence is not automatic. Match the algorithm, smoothing (for example
   EMA `adjust` setting, Wilder smoothing for RSI and ATR), initialization,
   inputs and decision timing. Log old and new values side by side for a few
   bars before removing the old code.
4. If logs or the installed LumiBot version show the accessor is unavailable,
   do not use it; explain that a newer LumiBot version is needed.
5. Tell the user what changed and why (for example "replaced hand-rolled
   rolling averages with cached `self.indicators` calls; values unchanged").

## Charting what you compute

Computed values are not charted automatically. Emit them with `add_line` and
`add_marker`; see `references/charting-indicators.md`.
