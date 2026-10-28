---
name: lumibot-indicators
title: LumiBot Indicators and Charting
description: Use when LumiBot strategy code needs indicator computation, pandas-ta-classic helpers, self.indicators migration, charted indicator lines, trade markers, OHLC visualizations, or missing backtest indicator graph debugging. Not for a chart or indicator question answered in chat; that uses chart-artifacts and data-analysis.
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

# LumiBot Indicators And Charting

Use this skill whenever strategy code computes indicators or needs visible
backtest chart artifacts.

Mandatory resource-loading contract: this `SKILL.md` is routing guidance only
and is intentionally incomplete. After loading this skill, the very next
substantive tool call must be `skills reference get` for the smallest matching
reference before answering, searching source, looking up docs, or inspecting
saved code. A final answer based only on this file is incomplete.

Two related contracts live here:

- Indicator computation: `self.indicators` and pandas-ta-classic backed helpers
  for SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, stochastic, VWAP,
  Supertrend, custom rolling values, and migration away from hand-rolled
  `df.rolling(...)` helpers. Load `references/computing-indicators.md` with
  `skills reference get` when code computes or migrates indicators. Do not use
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
  `skills reference get` when
  the user expects anything to appear on the BotSpot indicator chart.
  Final answers for chart-emission questions must explicitly name
  `add_line`, `add_marker`, `add_ohlc`, the accepted marker symbols
  `arrow-up` and `arrow-down`, and the hover-text parameter rule:
  use `detail_text`, never `text`.

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
