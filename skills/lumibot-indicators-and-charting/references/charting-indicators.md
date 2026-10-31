> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-chart-indicators
description: Use when LumiBot strategy code needs charted indicators, plotted lines, trade markers, OHLC visualizations, or missing backtest indicator graph debugging.
---

--------------------------------------------------------------
CHARTED INDICATORS AND SIGNALS
--------------------------------------------------------------

Use this skill when a user asks to add, inspect, explain, or fix strategy charts, indicator graphs, plotted signals, trade markers, backtest visualizations, missing indicators, missing markers, or anything involving `add_line`, `add_marker`, or `add_ohlc`.

Core rule: logging is not charting. `self.log_message(...)` explains decisions in logs, but it does not create indicator graph data. Anything the user expects to see on the backtest indicator chart must be emitted through:

- `self.add_ohlc(...)` for price candles or custom OHLC series.
- `self.add_line(...)` for continuous numeric series such as SMA, EMA, RSI, MACD, signal, histogram, Supertrend, trailing stops, hard stops, position size, support/resistance, and risk thresholds.
- `self.add_marker(...)` for sparse events such as buy/sell signals, fills, exits, stop hits, crossovers, regime changes, and rejected/skipped trade decisions that are important enough to inspect visually.

Answer contract: every user-facing answer about empty/missing chart output must
say that logs are not chart data, must name `add_line`, `add_marker`, and
`add_ohlc`, must give accepted buy/sell marker symbols (`arrow-up` and
`arrow-down`), and must explicitly warn to use `detail_text` rather than a
nonexistent `text` parameter.

Before claiming a product bug, read the saved strategy code and check:

1. Does it compute the indicator only in local variables/logs, or does it call `add_line` for every visible series the user expects?
2. Do marker calls happen on every real trade/event path, including exits, stop-outs, reversals, and early-return branches?
3. Are the plotted values finite numbers? `None`, NaN, and infinity are skipped by LumiBot.
4. Is `asset=...` passed when an Asset object exists so the overlay lands on the asset chart?
5. Is `dt=...` aligned to the historical bar timestamp when plotting old bars, not accidentally using the current wall-clock timestamp for every point?

Function signatures:

```python
self.add_ohlc(
    name,
    open,
    high,
    low,
    close,
    color=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)

self.add_line(
    name,
    value,
    color=None,
    style="solid",
    width=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)

self.add_marker(
    name,
    value=None,
    color="blue",
    symbol="arrow-up",
    size=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)
```

Use `detail_text`, not `text`. The `text=` parameter does not exist and will crash.
Use accepted marker symbols: `arrow-up`, `arrow-down`, or `star`. Do not invent
symbols such as `up`, `down`, `triangle-up`, `triangle_up`, or `circle` in
generated code examples.

Panel and scale guidance:

- Keep price-scale overlays on the default asset plot: OHLC candles, SMA/EMA, Bollinger bands, Supertrend, stops, trailing stops, entries/exits.
- Use a separate `plot_name` for non-price-scale series that would distort the price chart: RSI, MACD, MACD histogram, Stochastic, ADX, VIX-like filters.
- Keep pane count small. A common layout is the main price plot plus one `RSI` pane and one `MACD` pane.
- Multi-line indicators need one `add_line` call per series. A MACD panel normally has MACD line, signal line, and histogram. RSI often includes RSI, 70, 50, and 30 reference lines if those levels matter to decisions.

Safe plotting helper pattern:

```python
def _plot_line(self, name, value, *, asset, dt, color=None, plot_name="default_plot", detail_text=None, style="solid"):
    if value is None or pd.isna(value):
        return
    self.add_line(
        name,
        float(value),
        color=color,
        style=style,
        detail_text=detail_text,
        dt=dt,
        plot_name=plot_name,
        asset=asset,
    )
```

Example: chart MACD and RSI that the strategy already computes:

```python
dt = latest_bar.name if hasattr(latest_bar, "name") else self.get_datetime()
close_price = float(latest_bar["close"])

self.add_ohlc(
    "BTC",
    open=float(latest_bar["open"]),
    high=float(latest_bar["high"]),
    low=float(latest_bar["low"]),
    close=close_price,
    dt=dt,
    asset=asset,
)

self.add_line("Entry EMA", entry_ema, color="blue", width=2, dt=dt, asset=asset)
self.add_line("Exit EMA", exit_ema, color="orange", width=2, dt=dt, asset=asset)

self.add_line("MACD", macd_line, color="blue", dt=dt, plot_name="MACD", asset=asset)
self.add_line("MACD Signal", macd_signal, color="orange", dt=dt, plot_name="MACD", asset=asset)
self.add_line(
    "MACD Histogram",
    macd_hist,
    color="green" if macd_hist >= 0 else "red",
    dt=dt,
    plot_name="MACD",
    asset=asset,
)

self.add_line("RSI", rsi_value, color="purple", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 70", 70.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 30", 30.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)
```

Marker rules:

- Never add a marker on every iteration for a continuous value. That makes charts unusable. Use `add_line` instead.
- Add markers only when an event happens. Examples: entry signal, submitted buy, filled buy, exit signal, submitted sell, stop triggered, crossover confirmed.
- Use `symbol="arrow-up"` for buy/entry events and `symbol="arrow-down"` for
  sell/exit events unless `star` is the clearest event marker.
- If users complain that trades are missing from the chart, check whether every trade path has a marker and whether the platform's trade chart/artifact path is also working. A strategy can be missing marker emissions and the UI can still have a separate artifact/display bug.

Backtest artifact debugging:

- `indicators.csv` and `indicators.parquet` come from the accumulated `add_line`, `add_marker`, and `add_ohlc` calls.
- If the strategy emits chart data but the UI does not show it, inspect artifact metadata and the artifact manifest for `indicators.html`, `indicators.csv`, and `indicators.parquet` consistency before changing strategy logic.
- If `indicators.csv`/parquet has expected rows but HTML or the UI is missing them, treat that as a product serving/rendering bug.
