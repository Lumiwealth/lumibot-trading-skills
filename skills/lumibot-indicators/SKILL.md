---
name: lumibot-indicators
description: Load whenever LumiBot strategy code computes technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, stochastic, VWAP, Supertrend, z-scores or custom rolling values), migrates hand-rolled pandas rolling calculations, or needs indicators, signals and trades to appear on the backtest chart with add_line, add_marker and add_ohlc, including debugging an empty or missing indicator chart.
license: MIT
metadata:
  title: "LumiBot Indicators and Charting"
---
# LumiBot Indicators and Charting

This skill covers two related jobs in LumiBot
(https://github.com/Lumiwealth/lumibot, docs at https://lumibot.lumiwealth.com):

1. **Computing indicators** inside a strategy with `self.indicators`, a cached,
   point-in-time accessor backed by pandas-ta-classic.
2. **Charting** indicators, signals and trades in backtests with
   `self.add_line`, `self.add_marker` and `self.add_ohlc`.

Related skills: `lumibot-strategy-building` (lifecycle), `stock-etf-strategies`
and `options-strategies` (strategy patterns), `fast-lumibot-strategies`
(speed), `lumibot-api-reference` (API details).

Reference files (load with `skills` action=get, name=lumibot-indicators,
reference=<path>):

- `references/computing-indicators.md`: the full `self.indicators` contract,
  return types, custom indicators, windows, bar timing and migrating
  hand-rolled code.
- `references/charting-indicators.md`: full charting signatures, panels,
  marker rules, a complete MACD and RSI example, and debugging an empty chart.

Nothing here is investment advice; indicator settings are illustrations.

---

## 1. Computing indicators: the short version

`self.indicators` exists on every Strategy. No import or setup is needed.

```python
import pandas as pd

sma_50 = self.indicators.sma(asset, length=50, timestep="day")      # scalar
rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")   # scalar
macd = self.indicators.macd(asset, fast=12, slow=26, signal=9, timestep="day")  # row
bands = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")       # row

if sma_50 is None or pd.isna(sma_50):
    return  # not enough history yet
```

Key facts:

- **Any pandas-ta-classic indicator** is available by its snake_case name
  (about 130 of them: `sma`, `ema`, `rsi`, `macd`, `bbands`, `atr`, `adx`,
  `stoch`, `vwap`, `supertrend` and many more). Keyword arguments pass
  straight through. An unknown name raises an AttributeError that tells you
  to use `custom`.
- **Single-column indicators return the current scalar** (a float). Do not
  read attributes like `.sma_50` from it.
- **Multi-column indicators return an IndicatorRow** for the current bar:
  read fields as attributes (`macd.MACD_12_26_9`, `macd.MACDs_12_26_9`,
  `macd.MACDh_12_26_9`) or with brackets (`macd["MACDs_12_26_9"]`). Field
  names keep pandas-ta-classic's case; attribute access replaces dots and
  hyphens with underscores, so the Bollinger upper band `BBU_20_2.0` is
  `bands.BBU_20_2_0`. Call `row.as_dict()` to see the exact names.
- **Results are cached** per asset, timestep and parameters, and refresh
  automatically when new bars arrive. Calling inline in
  `on_trading_iteration` is cheap; no manual precomputation is needed.
- **It fetches its own history**, as of the current strategy time, so it does
  not look ahead in backtests. Warmup still depends on the data source having
  enough past bars.
- **Always guard for None and NaN.** Early in a series, or when data is
  missing, results are None or NaN. Guard the row and the fields you read.
- **Custom logic** goes through
  `self.indicators.custom("name", fn, asset, timestep="day", **kwargs)`, where
  `fn(df, **kwargs)` returns a Series (you get a scalar) or a DataFrame (you
  get an IndicatorRow).

```python
def _zscore(df, window=20):
    mean = df["close"].rolling(window).mean()
    std = df["close"].rolling(window).std()
    return (df["close"] - mean) / std

z = self.indicators.custom("zscore_20", _zscore, asset, timestep="day", window=20)
```

- **Windowed calculations**: `self.indicators.calculate_window(asset, "sma",
  start=..., end=..., timestep="day", parameters={"length": 20})` uses only
  bars inside an inclusive, timezone-aware window (no borrowed warmup), which
  is useful for "average of this month" style rules.
- Works the same in backtests and live trading.

Load `references/computing-indicators.md` for timing rules, migration from
hand-rolled code and more examples.

---

## 2. Bar timing: avoid look-ahead and extra delay

- Know which bar was complete at decision time. Historical bars describe
  completed periods; for daily data during the session, the latest row is
  normally yesterday.
- Apply the requested completed-bar selection once. If the history already
  ends at the latest completed bar, adding `.shift(1)` delays the signal by an
  extra bar. Do not add a shift "just to be safe".
- Custom functions must be causal: no centered windows, negative shifts or
  anything that reads later rows.
- For multi-timeframe logic, align each input by when it became available,
  then separate the signal time from the order and fill time.
- Verify a few signal values against the raw bars at boundaries. A strategy's
  own logged indicator repeats its own calculation and is not independent
  confirmation.

---

## 3. Charting: logging is not charting

`self.log_message(...)` writes logs. It does **not** create chart data.
Anything the user expects to see on the backtest indicator chart must be
emitted through:

- `self.add_line(name, value, ...)` for continuous series: moving averages,
  bands, RSI, MACD and its signal and histogram, stops, trailing stops,
  thresholds, position size.
- `self.add_marker(name, value=None, ...)` for sparse events: entries, exits,
  fills, stop hits, crossovers, regime changes, skipped trades worth seeing.
- `self.add_ohlc(name, open, high, low, close, ...)` for candles (price or a
  custom OHLC series such as Heikin Ashi).

Essential parameters (all three accept them): `color`, `detail_text` (hover
text), `dt` (timestamp of the point), `plot_name` (panel, default
"default_plot") and `asset` (attach to that asset's chart). `add_line` also
takes `style` ("solid", "dashed", ...) and `width`; `add_marker` takes
`symbol` and `size`.

Rules that prevent most chart bugs:

- Use `detail_text` for hover text. There is no `text` parameter; passing
  `text=` raises an error.
- Marker symbols: use `"arrow-up"` for buys and entries, `"arrow-down"` for
  sells and exits, `"star"` for special events. The default is `"circle"`.
  LumiBot accepts standard Plotly marker names; do not invent names such as
  "up", "down" or "triangle_up".
- Values must be finite numbers. None, NaN and infinity are skipped, so guard
  and convert with `float(...)`.
- Pass `asset=` when you have an Asset so overlays land on its chart.
- Pass `dt=` aligned to the bar you are plotting. Plotting historical bars
  with the current time stacks every point on one timestamp.
- Keep price-scale series (averages, bands, stops, entries) on the default
  panel. Put other scales (RSI, MACD, stochastic, ADX) in their own
  `plot_name` so they do not flatten the price chart. Keep the panel count
  small.
- Never add a marker every iteration for a continuous value; use a line.
- Put markers on every trade path: entries, exits, stop-outs, reversals and
  early-return exits.

```python
dt = self.get_datetime()
self.add_line("SMA 50", float(sma_50), color="blue", dt=dt, asset=asset)
self.add_line("RSI", float(rsi_14), color="purple", plot_name="RSI", dt=dt, asset=asset)
self.add_line("RSI 70", 70.0, color="gray", style="dashed", plot_name="RSI", dt=dt, asset=asset)
self.add_marker("Buy", float(price), color="green", symbol="arrow-up",
                detail_text=f"RSI {rsi_14:.1f}", dt=dt, asset=asset)
```

Load `references/charting-indicators.md` for the full signatures, a complete
multi-panel example and troubleshooting.

---

## 4. Seeing the chart on BotSpot (MCP tools)

After a backtest completes:

- `show_backtest_dashboard` or `get_backtest_visuals` (with
  `includeIndicators`) to view the indicator chart and tearsheet.
- `get_backtest_artifact` for the indicators artifact, then `query_csv` to
  inspect the plotted rows (for example
  `SELECT * FROM data LIMIT 50`). The indicators CSV and Parquet files are
  built from your `add_line`, `add_marker` and `add_ohlc` calls.
- `get_backtest_logs` for errors, such as a `text=` parameter error or NaN
  warnings.

If the artifact has the expected rows but the chart does not show them, that
is a display problem, not a strategy bug; report it with `send_feedback`
(kind "bug") instead of changing strategy logic.

---

## 5. Migrating hand-rolled indicators

When a strategy builds indicator columns by hand
(`df["sma"] = df["close"].rolling(50).mean()`, `.ewm(...)`, or a
`compute_indicators()` helper), `self.indicators` is usually simpler and
faster. Migrate only when it is requested or clearly helpful, and only as a
local change that preserves behavior: same algorithm, smoothing,
initialization, inputs and decision timing. Compare values before and after.
Do not turn a narrow user edit into an unrelated migration. Details and rules
are in `references/computing-indicators.md`.

The strategy-code path is `self.indicators`. Tools available to AI agents that
run inside a LumiBot strategy are a different mechanism and are not the way
to compute indicators in ordinary strategy code.
