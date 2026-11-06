---
name: lumibot-indicators-and-charting
public-name: lumibot-indicators
visibility: public
title: "LumiBot Indicators and Charting"
description: "Use when LumiBot strategy code needs indicator computation, pandas-ta-classic helpers, self.indicators migration, charted indicator lines, trade markers, OHLC visualizations, or missing backtest indicator graph debugging, or making and saving the person's own custom chart indicator. Not for a chart or indicator question answered in chat; that uses chart-artifacts and data-analysis."
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

## Loading this same guide in different clients

This canonical file is used internally and externally without rewriting. In
clients with native skills, use the advertised skill-loading and resource tools;
these may be named `load_skill` and `load_skill_resource`. In the BotSpot MCP,
use `skills` with action=list or action=get. The frontmatter's `name` is the
canonical skill identity and `public-name` is its compatible MCP discovery name.
For a qualified canonical resource identity, use that public-name as MCP name
and pass the unchanged relative reference path. Native resource tools use their
advertised resource identities. Discover the actual tools before calling them;
a tool name in an example does not install that tool in another client.

# LumiBot Indicators And Charting

Use this skill whenever strategy code computes indicators or needs visible
backtest chart artifacts.

Mandatory resource-loading contract: this `SKILL.md` is routing guidance only
and is intentionally incomplete. After loading this skill, the very next
substantive tool call must be `load_skill_resource` for the smallest matching
reference before answering, searching source, looking up docs, or inspecting
saved code. A final answer based only on this file is incomplete.

Two related contracts live here:

- Indicator computation: `self.indicators` and pandas-ta-classic backed helpers
  for SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, stochastic, VWAP,
  Supertrend, custom rolling values, and migration away from hand-rolled
  `df.rolling(...)` helpers. Load `references/computing-indicators.md` with
  `load_skill_resource` when code computes or migrates indicators. Do not use
  `lookup_lumibot_docs`, `get_code`, or another skill as a substitute for this
  resource load on indicator-computation questions.
  When answering indicator-computation explanations or migration questions,
  the final answer must explicitly say that
  `self.indicators` provides cached lookups and that
  single-column built-ins such as SMA/EMA/RSI return the current scalar value,
  while multi-column built-ins return a current-bar row. Custom Series results
  return a scalar; custom DataFrame results return an IndicatorRow.
  Also say that `self.indicators.custom(...)` is the escape hatch for custom
  rolling logic. Do not recommend the AI-agent runtime tools `get_indicator` or
  `get_indicators` as the strategy-code migration path for hand-rolled rolling
  DataFrame columns; use `self.indicators` in the strategy code.
- Chart emission: `self.add_ohlc`, `self.add_line`, and `self.add_marker` for
  price candles, continuous numeric series, entries, exits, stops, thresholds,
  fills, and visual debugging. Load `references/charting-indicators.md` with
  `load_skill_resource` when
  the user expects anything to appear on the BotSpot indicator chart.
  Final answers for chart-emission questions must explicitly name
  `add_line`, `add_marker`, `add_ohlc`, the accepted marker symbols
  `arrow-up` and `arrow-down`, and the hover-text parameter rule:
  use `detail_text`, never `text`.

- Custom chart indicators: when the person asks you to make, change or save
  their own indicator for BotSpot charts, load
  `references/custom-chart-indicators.md` with `load_skill_resource`, write a
  LumiBot `Indicator` class, and save it with the `indicators` tool
  (`action: "create"`, or `"update"` for a new version). Do not create a
  strategy, plan or backtest for it. `inputs`, `outputs` and `levels` hold
  `InputSpec(...)`, `OutputSpec(...)` and `Level(...)` objects, never dicts.
  Every save is test-run; if it is refused, fix the named problems and save
  again. Before you reply, check `live_chart` `action: "list"`: a saved indicator
  goes on the chart the person has open, with `add_indicator` and the `chartKey`
  the save returns, even when they only asked to create it. This saved-object
  `chartKey` is different from Python's `Indicator.key`; never place the Python
  class key on a chart. For several requested indicators, carry every returned
  saved reference into the placement call and verify the complete set. When they
  want a chart and none is open, use `create_chart` (see `chart-artifacts`).

Core rule: logging is not charting. A strategy that only logs an indicator, threshold,
entry, exit, or stop has not created chart data. For chartable strategies,
verify the saved code actually emits finite values through `add_line`,
`add_marker`, or `add_ohlc` before claiming chart coverage.

If the user asks about an empty indicators chart, missing plotted signals,
markers, OHLC candles, or logging values that do not show up visually, load
`references/charting-indicators.md` before answering and explicitly mention
`detail_text` rather than a nonexistent `text` parameter.

For deep artifact/UI diagnosis after the basic charting contract is followed,
load `backtest-indicator-chart-diagnostics`.
