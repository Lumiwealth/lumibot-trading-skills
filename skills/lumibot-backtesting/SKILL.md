---
name: lumibot-backtesting
description: Diagnose failed, no-trade or suspicious LumiBot backtests using saved code, logs, actual fills and artifacts. Supports local LumiBot and BotSpot MCP without changing the user's trading rules.
license: MIT
metadata:
  title: "Backtest and debug a LumiBot strategy"
---
# Backtest and debug a LumiBot strategy

Use this for a failed run, a no-trade result, a suspicious metric or a request
to validate saved strategy code. Preserve the user's trading rules while fixing
technical defects. A clean zero-trade run can be correct when the rules did not
fire; do not add a dummy trade or loosen a signal to manufacture success.

## Choose the execution path

- **Local LumiBot:** use the strategy's existing backtest runner and selected
  data source. `Strategy.backtest(datasource_class, start, end, **options)` runs
  the strategy; `self.get_datetime()` is simulated time. Configure the requested
  window and credentials outside the strategy's decision rules. Use
  `lumibot-api-reference` for the exact API when editing code.
- **BotSpot MCP:** inspect the saved strategy/revision, call `start_backtest`
  with that revision and the requested window, and retain its returned backtest
  identifier. Use `backtest_status`, `get_backtest_logs`,
  `get_backtest_artifact` and `get_backtest_visuals` for that same run. Discover
  the tool schemas from the connected server; do not guess arguments or IDs.
  If the installed server offers consolidated tools, use its advertised actions.

Starting a backtest is different from completing it. A failed start has no run
to poll. A queued or running job has no final performance result. Respect a
request to analyze only; skill instructions do not authorize starting a run,
changing a saved strategy, spending money or deploying a bot.

## Start with evidence

Record the code/revision, installed LumiBot version, data provider, asset and
bar interval, requested window, warmup, fees and terminal status. Keep missing
information explicit. Read the actual traceback and nearby log lines before
editing. On BotSpot, inspect which artifacts exist and their returned schema
before querying their columns. Keep logs, trade rows, charts and metrics bound
to the same run and revision.

| Observation | Next check |
|---|---|
| Import or missing-method error | Confirm the installed version, public method signature and dependency requirements. |
| No bars or prices | Check the provider's actual coverage, asset construction, timezone and simulated cutoff. Missing prices are not zero. |
| Indicator never ready | Compare available completed bars with the requested lookback and warmup. |
| No filled trades | Read branch/skip logs, rejected orders and signal frequency. Extend the window if appropriate; preserve the signal. |
| Unexpected cash or exposure | Reconcile quantities, fees, contract multipliers, partial fills and overlapping pending orders. |
| Duplicate orders | Reconcile exact order IDs and active status across callbacks and polling before resubmitting. |
| Research request unavailable | Inspect that source's error and other available evidence; keep unrelated tools usable. |

## Historical research with messy data

Prefer dated sources and evidence available by simulated time. Date-only values,
missing timestamps and incomplete vintage metadata can still be useful. Explain
any reasonable date approximation and its basis. Never invent a timestamp, use
known future evidence, silently substitute current revised values, or label an
approximation exact point-in-time data. Do not require a separately attested
server clock or unavailable provenance merely to let ordinary research run.

Use `lumibot connect botspot` when the strategy should gain BotSpot research
tools. The connection is optional and free; source availability and account
permissions still apply. An external assistant's ability to start hosted
backtests is a separate workflow from research inside a running strategy.

## Repair and verify

Fix the demonstrated defect at its existing owner, save/read back the changed
code, and rerun the affected scenario when authorized. Compare the before/after
trace, orders, fills and positions. A local import check or mocked price fixture
is useful setup evidence, not a completed data-backed backtest.

A completed run establishes execution for that window and data, not investment
quality. Report failed and no-trade runs honestly. If rules naturally need a
longer window, explain that rather than inserting a special backtest-only path.
Check fees, cash, exposures, warmup, missing data and unclosed orders before
trusting the reported result. Separate technical correctness from profitability
and in-sample tuning from out-of-sample validation. Backtests do not promise
future returns.
