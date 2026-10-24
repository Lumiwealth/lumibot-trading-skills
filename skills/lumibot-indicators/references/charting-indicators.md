# Charting Indicators, Signals and Trades

Part of the `lumibot-indicators` skill. Use this when adding, fixing or
explaining strategy charts: plotted indicators, trade markers, candles, or an
empty or incomplete indicator chart after a backtest.

## Logging is not charting

`self.log_message(...)` explains decisions in logs. It does not create chart
data. Everything the user expects to see on the indicator chart must be
emitted through:

- `self.add_ohlc(...)` for price candles or custom OHLC series.
- `self.add_line(...)` for continuous numeric series: SMA, EMA, RSI, MACD,
  signal, histogram, Supertrend, trailing stops, hard stops, position size,
  support and resistance, risk thresholds.
- `self.add_marker(...)` for sparse events: buy and sell signals, fills,
  exits, stop hits, crossovers, regime changes, and skipped trades important
  enough to inspect.

## Signatures

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
    symbol="circle",
    size=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)
```

- Hover text is `detail_text`. There is no `text` parameter; `text=` raises an
  error.
- Marker `symbol`: use `"arrow-up"` for buys and entries, `"arrow-down"` for
  sells and exits, and `"star"` for special events. Standard Plotly marker
  names are accepted (the default is `"circle"`). Do not invent names such as
  "up", "down" or "triangle_up".

## Checklist before blaming the platform

Read the saved strategy code and check:

1. Is the indicator only computed into local variables or logs, or is
   `add_line` called for every series the user expects?
2. Do marker calls happen on every trade or event path, including exits,
   stop-outs, reversals and early-return branches?
3. Are plotted values finite numbers? None, NaN and infinity are skipped.
4. Is `asset=...` passed when an Asset exists, so the overlay lands on that
   asset's chart?
5. Is `dt=...` the timestamp of the bar being plotted? When plotting older
   bars, using the current time for every point stacks them on one timestamp.

## Panels and scale

- Keep price-scale overlays on the default plot: candles, SMA and EMA,
  Bollinger Bands, Supertrend, stops, trailing stops, entries and exits.
- Put other scales in their own `plot_name`: RSI, MACD and its histogram,
  stochastic, ADX, volatility filters. Otherwise they flatten the price chart.
- Keep the number of panels small. A common layout is the main price plot plus
  an `RSI` panel and a `MACD` panel.
- Multi-line indicators need one `add_line` call per series. MACD usually has
  the MACD line, the signal line and the histogram. RSI often has the RSI plus
  reference lines at the levels the rules use.

## Safe plotting helper

```python
import pandas as pd

def _plot_line(self, name, value, *, asset, dt, color=None, plot_name="default_plot",
               detail_text=None, style="solid"):
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

## Example: candles, EMAs, MACD and RSI

```python
bars = self.get_historical_prices(asset, length=1, timestep="day")
latest_bar = bars.df.iloc[-1]
dt = latest_bar.name  # timestamp of the bar
close_price = float(latest_bar["close"])

self.add_ohlc(
    asset.symbol,
    open=float(latest_bar["open"]),
    high=float(latest_bar["high"]),
    low=float(latest_bar["low"]),
    close=close_price,
    dt=dt,
    asset=asset,
)

self._plot_line("Entry EMA", entry_ema, color="blue", dt=dt, asset=asset)
self._plot_line("Exit EMA", exit_ema, color="orange", dt=dt, asset=asset)

self._plot_line("MACD", macd_line, color="blue", dt=dt, plot_name="MACD", asset=asset)
self._plot_line("MACD Signal", macd_signal, color="orange", dt=dt, plot_name="MACD", asset=asset)
self._plot_line(
    "MACD Histogram",
    macd_hist,
    color="green" if macd_hist is not None and macd_hist >= 0 else "red",
    dt=dt,
    plot_name="MACD",
    asset=asset,
)

self._plot_line("RSI", rsi_value, color="purple", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 70", 70.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 30", 30.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)

if entered_this_bar:
    self.add_marker(
        "Buy",
        close_price,
        color="green",
        symbol="arrow-up",
        detail_text=f"RSI {rsi_value:.1f}, MACD {macd_line:.3f}",
        dt=dt,
        asset=asset,
    )
```

## Marker rules

- Never add a marker every iteration for a continuous value; that makes the
  chart unreadable. Use `add_line` instead.
- Add markers only when an event happens: entry signal, submitted buy, filled
  buy, exit signal, submitted sell, stop triggered, crossover confirmed.
- Use `"arrow-up"` for buys and entries and `"arrow-down"` for sells and exits
  unless `"star"` is clearer for the event.
- If trades are missing from the chart, check that every trade path adds a
  marker. Filled trades are also recorded separately in the trades artifact.

## Backtest artifacts on BotSpot

- The indicators CSV and Parquet artifacts are built from the accumulated
  `add_line`, `add_marker` and `add_ohlc` calls, and the indicator chart is
  rendered from them.
- To inspect them: `get_backtest_artifact` for the indicators artifact, then
  `query_csv` (for example `SELECT * FROM data LIMIT 50`), or view the chart
  with `show_backtest_dashboard` or `get_backtest_visuals`.
- If the strategy emits chart data and the artifact contains the expected
  rows but the chart does not show them, treat it as a display problem rather
  than a strategy bug, and report it with `send_feedback` (kind "bug").
- If the artifact is empty, the strategy did not emit valid points: go back
  to the checklist above.
