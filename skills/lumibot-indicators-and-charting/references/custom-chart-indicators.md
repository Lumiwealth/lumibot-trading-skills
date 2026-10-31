> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Custom chart indicators (saved with the `indicators` tool)

Use this when the person asks you to make, change, or show one of their own
indicators for BotSpot charts ("make me an indicator", "add my own indicator to
the chart", "change my indicator to use 20 bars"). This is not strategy code:
do not create a strategy, a plan, or a backtest for it.

## Save it with the `indicators` tool

- `action: "create"` with `name`, a short `description`, the full Python
  `source`, and `metadata` (`placement`: `"overlay"` draws on the price,
  `"pane"` draws in its own pane; `outputs`: `[{ "name": "<output id>" }]`).
- If a save is refused, the reply names each problem in the code. Fix exactly
  those and save again; only say it is saved after a save succeeds.
- `action: "update"` with the indicator id and the full new `source` saves a new
  version; old versions are kept, so anything pinned to one keeps working.
  Without `source` only the name or description changes.
- `action: "list"` and `action: "get"` read what the person already has. Check
  `list` before creating a near-duplicate.
- Indicators are private to their owner. Never ask for or show another
  person's indicator code.

After saving, tell the person it is saved and that they add it from the
**Indicator** button on their chart (it is listed under "Your indicators").
Live updates start when they turn on **Live** on that chart.

## Write a LumiBot `Indicator` class

The same class runs on the chart, in backtests and in live bots. Keep it one
class in one file; it runs in a locked process with no files and no keys, but it
may call public web APIs over HTTP(S).

```python
from collections import deque

from lumibot.indicators import Indicator, InputSpec, OutputSpec


class RangeMidline(Indicator):
    key = "range_mid"          # lowercase, unique within the file
    version = 1                # bump when the math changes
    title = "Range midline"
    short_title = "RMID"
    overlay = True             # True: on the price chart; False: own pane

    inputs = [InputSpec("length", "int", 10, min=1, label="Length")]
    outputs = [OutputSpec("mid", "Midline", "line", "#F59E0B")]

    def init_state(self):
        n = self.inputs["length"]
        return {"highs": deque(maxlen=n), "lows": deque(maxlen=n)}

    def step(self, state, bar):
        state["highs"].append(bar.high)
        state["lows"].append(bar.low)
        if len(state["highs"]) < self.inputs["length"]:
            return {"mid": None}   # not enough bars yet
        return {"mid": (max(state["highs"]) + min(state["lows"])) / 2}
```

Rules that matter:

- `step(state, bar)` gets one bar at a time (`bar.open`, `bar.high`, `bar.low`,
  `bar.close`, `bar.volume`, `bar.time`, plus `bar.hl2`, `bar.hlc3`,
  `bar.ohlc4`) and returns one value per declared output. Return `None` until
  there is enough data; never invent a value.
- Every number the person might tune (a lookback such as "the last 14 bars",
  a smoothing length, a multiplier) is an `InputSpec` with that default, read
  from `self.inputs`; never hard-code it in `init_state` or `step`. Guide-line
  values go in `levels`.
- Keep running state in `init_state`, not in globals, so live updates continue
  from history instead of recomputing everything.
- Output kinds: `"line"`, `"area"`, `"histogram"`, `"scatter"`, `"markers"`.
  Fixed guide lines (for example 70/30) go in `levels` as `Level(70, "High")`
  objects (see below).
- Use the indicator math LumiBot already has (its built-ins follow
  TradingView's formulas) rather than TA-Lib where they differ.
- Imports: the standard library, `numpy`, `pandas`, `requests` and
  `lumibot.indicators`. No `eval`, `exec`, `open`, or dunder tricks; the save
  check refuses them.

### Own pane with guide lines

An oscillator (0 to 100, a ratio, a score) goes in its own pane: `overlay = False`
and metadata `placement: "pane"`. Guide lines are `Level` objects.

```python
from collections import deque

from lumibot.indicators import Indicator, InputSpec, Level, OutputSpec


class CloseInRange(Indicator):
    key = "close_in_range"
    version = 1
    title = "Close in range"
    short_title = "CIR"
    overlay = False            # own pane under the price

    inputs = [InputSpec("length", "int", 14, min=2, label="Length")]
    outputs = [OutputSpec("score", "Score", "line", "#3B82F6")]
    levels = [Level(80, "High"), Level(20, "Low")]   # guide lines: Level objects

    def init_state(self):
        n = self.inputs["length"]
        return {"highs": deque(maxlen=n), "lows": deque(maxlen=n)}

    def step(self, state, bar):
        state["highs"].append(bar.high)
        state["lows"].append(bar.low)
        if len(state["highs"]) < self.inputs["length"]:
            return {"score": None}
        top, bottom = max(state["highs"]), min(state["lows"])
        if top == bottom:
            return {"score": 50.0}
        return {"score": 100.0 * (bar.close - bottom) / (top - bottom)}
```

**Declarations are objects, never dicts.** `inputs` holds `InputSpec(...)`,
`outputs` holds `OutputSpec(...)` and `levels` holds `Level(value, label)`, all
imported from `lumibot.indicators`. A dict such as `{"value": 70, "label": "70"}`
looks harmless but the indicator cannot load: it breaks the chart it is added to.
The ids `step` returns must be exactly the ids in `outputs`.

**Every save is test-run.** Before saving, BotSpot loads the code in the chart
sandbox, describes it and runs it over sample bars. If the save is refused, the
reply lists each problem (for example "levels[0] must be a Level(...) object, got
dict"). Fix those exact problems and save again; do not tell the person it is
saved until a save succeeds.

### What goes on the price chart, and lines that switch sides

- With `overlay = True`, every output is drawn on the price scale. Only output
  prices there (a level, a band, a stop). Never output a direction (-1/+1), a
  state, a signal flag or a count from an overlay indicator: it squashes the
  price axis to a range that includes 0. Keep it in `state`, or, when the
  person wants to see it, make it a separate `overlay = False` indicator.
- A line that switches between two bands (SuperTrend, Chandelier exit, a
  trailing stop) is two outputs, one per side (for example `"long_stop"` and
  `"short_stop"`). Each is `None` on bars where the other side is active, so
  the chart draws separate segments instead of one line jumping between bands.

```python
    outputs = [
        OutputSpec("up", "Up trend", "line", "#22C55E"),
        OutputSpec("down", "Down trend", "line", "#EF4444"),
    ]

    def step(self, state, bar):
        ...  # compute `line` and `trend` (1 up, -1 down) from the inputs
        if trend == 1:
            return {"up": line, "down": None}
        return {"up": None, "down": line}
```

- SuperTrend follows TradingView exactly. With `atr` = Wilder's ATR (RMA of
  true range), `basic_upper = hl2 + factor * atr`,
  `basic_lower = hl2 - factor * atr`:
  `upper = basic_upper if basic_upper < prev_upper or prev_close > prev_upper else prev_upper`;
  `lower = basic_lower if basic_lower > prev_lower or prev_close < prev_lower else prev_lower`.
  The direction flips using the current bar's finalized bands: when the
  previous line was the upper band, it turns up when `close > upper`;
  when it was the lower band, it turns down when `close < lower`. The first
  bar with an ATR starts in a downtrend on the upper band (Pine's default).
  The line is `lower` in an uptrend and `upper` in a downtrend.
- Warm-up: a value built from other values (Hull's chained weighted averages,
  an ATR feeding a band) is `None` until every part exists. Check each part
  for `None` before doing math with it; a crash on the first bars breaks the
  chart it is added to.

### Changing an indicator that is already on a chart

`indicators` `action: "update"` saves version N, but the chart stays on the
version it was added with. Move it with `live_chart` `action:
"update_indicator"` (its `instanceId` and `version: N`), then read the result
with `live_chart` `action: "summarize"` before saying the lines are right.

### Public data in an indicator

An indicator may fetch public data with `requests` (keyless public endpoints
only), for example the 10-year Treasury yield from FRED's public CSV:
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`. Fetch once (keep
it in `state`, sorted by date), and for each bar return the latest
observation dated on or before the bar's date (weekends and holidays have no
row of their own, so an exact-date lookup leaves gaps). Return `None` only
before the first observation; skip missing values such as `.`. When the person wants outside data on their live chart,
save it as an indicator like this; do not switch to `run_data_analysis` or
say the live chart cannot show it.

More examples and the full reference: LumiBot docs, "Indicators" section
(`lookup_lumibot_docs` with "custom indicator").
