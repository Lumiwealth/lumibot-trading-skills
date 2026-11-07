> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Pine Script to a LumiBot Indicator

Read `references/indicator-conversion/README.md` first. This file only maps the
language. Sources: [Pine reference](https://www.tradingview.com/pine-script-reference/v5/),
[colors](https://www.tradingview.com/pine-script-docs/visuals/colors/) and
[plots](https://www.tradingview.com/pine-script-docs/visuals/plots/).

## Declarations

| Pine | LumiBot |
| --- | --- |
| `indicator(...)` or `study(...)` with `overlay=true` | `overlay = True`, metadata `placement: "overlay"` |
| no overlay, or `overlay=false` | `overlay = False`, metadata `placement: "pane"` |
| `input(20, "Length")`, `input.int`, `input.float` | `InputSpec("length", "int" or "float", 20, label="Length")` |
| `input.source(close)` or `input(close)` | `InputSpec("source", "source", "close", label=...)`, read `bar.source(...)` |
| `input.color(...)` | `InputSpec(name, "color", "#RRGGBB")` plus the `describe` override |
| `input.bool` | `InputSpec(name, "bool", value)` |
| `var x = 0`, or `x := ...` carried across bars | a value kept in `state` |
| `x[1]` | keep the previous value in `state`; `x[n]` needs a `deque(maxlen=n + 1)` |

## Drawing

| Pine | LumiBot |
| --- | --- |
| `plot(x, color=c)` | `"line"` output |
| `style=histogram`, `plot.style_histogram`, `plot.style_columns` | `"histogram"` output |
| `style=area`, `plot.style_area` | `"area"` output |
| `style=circles`, `style=cross`, `plot.style_circles`, `plot.style_cross` | `"scatter"` output |
| `plot.style_linebr` | `"line"` output with `None` on the gap bars |
| `style=3` or `linestyle=dashed` | `"line"` output; the chart has no dashed plot, so mention it |
| `plot(constant)` used as a guide | `Level(constant, label)` |
| `hline(price, ...)` | `Level(price, label)` |
| `plotshape(cond ? x : na, location=location.absolute, ...)` | `"scatter"` output returning `x` on those bars |
| `plotshape(cond, location=location.abovebar)` | `"scatter"` output returning `bar.high` on those bars |
| `plotshape(cond, location=location.belowbar)` | `"scatter"` output returning `bar.low` on those bars |
| `plotchar(...)` | same as `plotshape` |
| `plot(x, color = cond ? a : b)` | one output per color; see the README |
| `plot(x, color=na)` or `display.none` | do not show it unless the fill it supports needs it as the stand-in |
| `fill(...)`, `bgcolor(...)`, `barcolor(...)`, `plotcandle(...)`, `color.from_gradient(...)` | cannot be drawn yet; see the README |
| `label.new`, `line.new`, `box.new`, `table.new` | cannot be drawn yet |
| `alertcondition(...)`, `alert(...)` | no equivalent; mention it |

## Colors

Named colors depend on the script's version, so read its `//@version=` line first and use
only the list for that version.

- No version line, or `//@version=1`, `2` or `3` (plain names such as `lime`): lime `#00FF00`, green `#008000`, red `#FF0000`, maroon `#800000`, blue `#0000FF`, black `#000000`, gray `#808080`, yellow `#FFFF00`, orange `#FF7F00`, aqua `#00FFFF`, purple `#800080`, teal `#008080`, fuchsia `#FF00FF`, navy `#000080`, olive `#808000`, silver `#C0C0C0`, white `#FFFFFF`.
- `//@version=4` or `//@version=5` (`color.red` style names): lime `#00E676`, green `#4CAF50`, red `#FF5252`, maroon `#880E4F`, blue `#2196F3`, black `#363A45`, gray `#787B86`, yellow `#FFEB3B`, orange `#FF9800`, aqua `#00BCD4`, purple `#9C27B0`, teal `#00897B`, fuchsia `#E040FB`, navy `#311B92`, olive `#808000`, silver `#B2B5BE`, white `#FFFFFF`.
- `//@version=6`: lime `#00E676`, green `#4CAF50`, red `#F23645`, maroon `#880E4F`, blue `#2196F3`, black `#363A45`, gray `#787B86`, yellow `#FDD835`, orange `#FF9800`, aqua `#00BCD4`, purple `#9C27B0`, teal `#089981`, fuchsia `#E040FB`, navy `#311B92`, olive `#808000`, silver `#B2B5BE`, white `#FFFFFF`.

For example, `color.yellow` in a version 5 script is `#FFEB3B`, not `#FFFF00`, and
`color.red` in a version 4 script is `#FF5252`, not `#F23645`.

`color.new(c, t)` and `transp=t` set transparency from 0 (solid) to 100 (invisible):
the alpha byte is `round(255 * (100 - t) / 100)`. A plot with no color uses `#2962FF`.

## Math

`na` behavior and the editable color pattern are in `references/custom-chart-indicators.md`.
Build each of these from running state, one bar at a time. Check every part for `None`
before using it.

- `tr`: `high - low` on the first bar, then
  `max(high - low, abs(high - close[1]), abs(low - close[1]))`.
- `ta.rma(x, n)`: the plain average of the first `n` values, then
  `(previous * (n - 1) + x) / n`. `ta.atr(n)` is the RMA of `tr`, never a rolling average.
- `ta.rsi(x, n)`: the RMA of gains and the RMA of losses from the second bar on.
  `100 - 100 / (1 + gains / losses)`; 100 when losses are 0.
- `ta.ema(x, n)`: `alpha = 2 / (n + 1)`, starting on the first defined value.
- `ta.sma(x, n)`: the average of the last `n` values, undefined until there are `n`.
- `ta.stdev(x, n)`: population standard deviation, dividing by `n`, by default.
- `ta.highest(x, n)` and `ta.lowest(x, n)` include the current bar.
- `ta.linreg(x, n, 0)`: the least squares line through the last `n` values, read at
  the current bar. `offset` moves that read point.
- `ta.wma(x, n)`: weights 1 to `n`, newest heaviest. `ta.hma(x, n)` uses
  `wma(2 * wma(x, n / 2) - wma(x, n), round(sqrt(n)))`.
- `ta.cross(a, b)`: the sign of `a - b` changed from the previous bar, or it is exactly 0.
  `ta.crossover` needs `a > b` now and `a <= b` before.
- `nz(x)` is `x`, or 0 when `x` is `na`. `nz(x, y)` uses `y`. Keep it where the source has it.
- `iff(c, a, b)` is `a if c else b`.
- Dividing by zero gives `na`, never infinity. A comparison with `na` is false.
- A plain `x = 1` followed by `x := nz(x[1], x)` starts at that value and then carries over.
  Keep the first state the script sets: it decides the early bars.
- Older scripts use the same functions without `ta.` or `math.` in front.

## Mistakes that change the numbers

- **The script's own lines win over any recipe.** A script that writes its own trend or
  band logic, instead of calling a built-in such as `ta.supertrend`, has its own rule for
  when it flips and what state it starts in. Translate those lines, even when they look
  like a well-known indicator you have a recipe for.
- **Keep every fixed number where the script wrote it.** `ta.sma(wt1, 3)` averages 3 bars
  even when an input such as `n2` sits on the line above. Do not swap a fixed number for a
  nearby input, or an input for a number. Only values the script reads from `input(...)`
  become inputs.
- **Each plot warms up on its own.** Do not blank every output until the slowest
  calculation is ready. `plot(0, color=c)` draws from the first bar, while a long
  average beside it is still empty. Return only the values that do not exist yet as `None`.
- **A per-bar color follows its own condition.** When `plot(0, color = cond1 ? a : cond2 ? b : c)`
  sits beside a slower calculation, evaluate `cond1` and `cond2` on every bar where their own
  inputs exist and draw that color. Do not hold the mark at a default color, or hide it,
  until the slower plot is ready: each condition is independent of the other plots.
- **Read a chained color in order.** `cond1 ? a : cond2 ? b : c` means color `a` when `cond1`
  is true, else `b` when `cond2` is true, else `c`. Write each color next to its own
  condition, and name outputs after those conditions, not after what you expect the colors
  to mean. A cross dot colored by `x <= 0 ? green : red` is green when `x <= 0`.
- **A function of an expression uses that expression's past values.**
  `ta.linreg(close - ta.sma(close, n), n, 0)` needs the last `n` results of
  `close - ta.sma(close, n)`, each computed on its own bar. Keep them in a `deque`. Never
  subtract today's average from the past `n` closes: that gives a different number.
- **Warm-up, counted exactly.** An `n` bar average of an `m` bar average first has a value on
  bar `m + n - 2`, counting from 0. A window fills from the first defined value, so never
  wait for extra bars. Compute a window on every bar once it is full, with `deque(maxlen=n)`
  and `len(window) == n`.
- **A zero is a value.** `ta.ema(abs(x - ta.ema(x, n)), n)` starts at 0 on the first bar,
  because `x` equals its own first average. That 0 starts the second average. Do not skip
  it, because the first bar's effect lasts for many bars. Only the division by it gives `na`.
- **Use the variable the script uses.** When a script computes a value and then does not use
  it, such as an input it never reads, keep the input and leave it unused.
- `nz(x[1])` on the first defined bar reads 0. Compare with 0 there, rather than treating
  a missing previous value as its own case.
- A value that has not warmed up makes a comparison false, so an `else` branch still
  runs: `cond ? a : b` draws `b` during warm-up.
