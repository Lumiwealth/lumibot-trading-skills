> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Converting an indicator from another platform

Use this when the person supplies indicator source from another platform, even
when they paste it with no instruction at all. Source code in a message is the
request: convert it. Do not ask whether they want it converted, and do not
explain the script back to them instead of converting it.

Then load the file for the source language:

- TradingView Pine Script: `references/indicator-conversion/pine-script.md`.
- Another language, such as MetaTrader MQL4 or MQL5, ThinkScript, EasyLanguage or
  NinjaScript: there is no language file yet. Apply this workflow and the same
  drawing limits below, and say which language behaviors you could not verify.

## Workflow

1. Read the whole script. List every value it plots and how it draws each one:
   its kind, color, width, transparency, and any color that changes bar by bar.
   List anything else it draws, such as fills, background colors or colored bars.
2. Write one LumiBot `Indicator` class with the contract in
   `references/custom-chart-indicators.md`. Keep the script's exact defaults,
   input names, arithmetic and plotted outputs. A quirk in the math is part of the
   script: keep it. You may point out something that looks wrong, but do not fix
   it silently. Say so if the source and its name disagree.
3. Before saving, read your code once against the script, line by line:
   - For each `cond ? a : b` color, write down which condition gets which color, and
     check the sign. `b - a > 0` is the same as `a - b < 0`.
   - One output for each color a plot can take. One output with one color is wrong
     for a plot whose color changes.
   - One output for every `plot`, `plotshape` and `plotchar` that has a value, including
     flip points and dots. Count them against the script.
   - No early `return` that blanks every output while one calculation warms up. A plot of
     a constant draws from the first bar, and each value appears as soon as its own
     parts exist.
   - The class runs as written: valid Python, only the base class's own attributes,
     and a check for `None` before every comparison, sum or calculation, including every
     value in a window.
   Then save it with `indicators` `action: "create"`. If the save is refused, fix the
   named problems and save again. Save once. Do not save another version unless you
   found a real error.
4. Put it on the chart with the `chartKey` from the save reply, copied exactly. Never
   build a key yourself from the class key or the name. If you save a new version
   after that, read the `instanceId` from the chart reply before updating it.
   - If they named an instrument, open that chart with `create_chart`, even when
     another chart exists. "Bitcoin" is the crypto pair, not a stock or fund. A
     perpetual or futures request needs that instrument from a source that has it.
   - If they have a chart open, add it there.
   - If neither applies, say it is saved privately and end your reply with the question:
     which symbol should it go on?
5. In your reply, say in plain words what was saved and where it is showing. When some
   source visual could not be drawn, add a short list headed "What this chart does not
   show yet", naming each one in the source's own terms: each fill, background color,
   colored bars, gradient, text label and alert, with what you drew instead. A shape with
   `text=` has a text label even when you kept its point, so name it. Small styling
   differences such as line width or dash style go in one plain sentence, not in that
   list. Leave the list out when everything was drawn. Call a mark what the chart draws:
   a source cross shows as a dot, so say dot. Never claim the chart looks the same as the
   source when a part of it is missing. Do not paste the source or the converted code
   unless asked.

## What the chart can draw

| The source draws | Do this |
| --- | --- |
| A line | `OutputSpec(id, label, "line", color)` |
| A histogram or columns | `OutputSpec(id, label, "histogram", color)` |
| An area | `OutputSpec(id, label, "area", color)` |
| Circles, crosses, or shapes at a value | `OutputSpec(id, label, "scatter", color)` |
| A fixed guide line | `Level(value, label)` |
| A line with gaps | Return `None` on the gap bars |

- Every `plot`, `plotshape` and `plotchar` with a value becomes an output, in the source's
  color. Do not drop one because a text label or a fill beside it cannot be drawn.
- `"scatter"` is the kind for points. The `"markers"` kind is not drawn on the
  live chart: a marker saved that way never appears.
- **A color that changes by bar is one output per color.** Each output carries one
  fixed color and returns its value only on the bars that have that color, and
  `None` on every other bar. A histogram with four colors is four histogram outputs
  and a line that switches between two colors is two line outputs. This matches the
  source exactly, so do not list it as a limitation.
- Transparency goes in the color as eight hex digits, `#RRGGBBAA`.
- Output colors are hex values, and they are the source's own colors. Do not swap
  in nicer ones.
- A color input must change the drawing. Use the `describe` override in
  `references/custom-chart-indicators.md`.

## What the chart cannot draw yet

Say so plainly in your reply for each one the source uses. Do not fake it with extra
outputs that change the price scale or look like data.

- A fill between two lines or plots. Draw the lines themselves when the source shows
  them, or the value the fill is built on when it hides them.
- A background color. Keep the calculation out of the price pane: a -1 or +1 state
  squashes the price axis.
- Colored bars or custom candles.
- A smooth gradient. Stepping it into a few colors by range, one output per color, is
  allowed when you describe it as stepped.
- Text labels, tables, and drawn lines or boxes from code. A point at the same value
  is fine, and say the text is missing.
- Data from another symbol or another timeframe, because `step` sees one bar of the
  chart's own series. Say the indicator was not converted faithfully if it needs one.
- Alerts. Mention them only when the script defines some.

## Privacy

Supplied source and the code derived from it stay in the person's private indicator.
Do not offer to publish them, add them to a marketplace or a shared example, or show
them to anyone else.
