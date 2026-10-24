# Backtest validation, diagnosis and repair

Use with the `lumibot-strategy-building` skill when choosing a backtest window,
reading results, or repairing a run that failed or made no trades.

## What a good first validation is

For a new strategy, the first backtest should reach a terminal `completed`
status with at least one filled trade, and for chartable strategies it should
produce indicator or marker output. A run that produced trades but ended
`failed` is still a failed run. A `trades.csv` with filled rows does not turn
a failed run into a success.

After a strategy has one good filled-trade backtest, a later zero-trade run
can be legitimate (the rules simply did not fire in that window).

## Choosing the window

- Start short for intraday or frequent strategies, about one week of trading,
  so the user gets feedback quickly and cheaply.
- Lengthen the window to fit the rules. Reason about whether the rules can
  plausibly fire: a daily 20/50 moving-average cross on one symbol may need one
  to three months; a monthly rebalance needs several months; rare extremes (for
  example RSI under 10) may need a year.
- If even an affordable window probably cannot show a trade, say so and offer a
  longer test. Never shorten lookbacks, drop confirmations or add a buy-now path
  so a short test trades, unless the user approves that exact change.
- Request warmup history before the window (via the lookback) instead of
  waiting inside the window for indicators to fill.
- AI-owned strategies make a model call per decision; keep their first window
  modest.
- Minute data history is commonly limited to roughly the last two years.
- Never hardcode dates in the script. `start_backtest` controls the window.

## First-version strategy shape

When the user asks for a sample or starter bot without detailed rules, make the
first version deliberately simple and tradeable: broad entry logic that belongs
to the idea, conservative sizing, clear exits. Do not invent a long-lookback
crossover or stacked filters as the only entry path. Later revisions can tighten
it. `references/scaffolds.md` has per-asset first-version templates.

When the user did specify rules, implement them exactly, even if they are
strict. Preserve them; explain the trade frequency risk instead.

Screening, ranking and contest strategies: for the first run, use the same
ranking logic on a tiny liquid universe (one to three names such as SPY, AAPL,
MSFT) instead of crawling dozens of symbols with missing data. For date-bound
contest rules, keep the contest dates for live behavior but do not let a date
gate make the only trade path return during the test window; use earlier bars
for warmup.

## Reading a finished run

Keep one backtest id for the whole analysis.

1. `backtest_status`: terminal status, progress, return, open orders and
   positions at the end.
2. `get_backtest_logs`: errors, tracebacks, skipped-entry reasons, order and fill
   lines. Use a large limit when diagnosing a failure; batch several filter
   queries in one call when you can.
3. `get_backtest_artifact` or `list_backtests` with includeArtifacts=true:
   which artifacts exist and their schema.
4. `query_csv` on one artifact at a time. Useful queries:
   - Total rows: `SELECT COUNT(*) FROM data`
   - Filled trades:
     `SELECT * FROM data WHERE lower(coalesce(status, '')) = 'filled' ORDER BY time LIMIT 100`
   - Per symbol (after confirming the column exists):
     `SELECT symbol, COUNT(*) FROM data GROUP BY symbol`
   - Indicator rows: `SELECT * FROM data LIMIT 50`
   Match timestamp literals to the actual column type in the returned schema.
5. `get_backtest_visuals` for the tearsheet and charts to share.

Running backtests usually have no tabular artifacts yet; wait for a terminal
status before querying trades or stats.

## Correctness audit for unleveraged strategies

Check these before calling a strategy correct:

- Minimum cash over the run. Negative cash without intended margin is a bug.
  Positive ending cash does not excuse an earlier overdraft.
- Fees charged per trade and per contract match the configured fee model.
- Order lifecycle: every submitted order reached a terminal state; partial fills
  were handled; no duplicate entries for the same signal.
- Exits: stops and signal exits fired when their conditions were met; nothing
  was abandoned open by mistake.
- Remaining positions at the end are expected.
- Rules that a backtest cannot evaluate (live quote age, spread, depth,
  seconds-level reaction) are listed in your answer with what the backtest did
  instead.

Repair the cause and retest the same rules. Never mask debt with
`adjust_cash`, fake deposits or a changed signal.

## Diagnosing a failed run

Read the logs first. Common causes and technical repairs (these keep the
user's intent and need no approval):

- Wrong API usage or a guessed method name: check `lumibot-api-reference`.
- A future import, an attribute on `self` colliding with internals, or a
  private helper name colliding with framework state.
- Price snapshot or "outside of the data's date range" errors: history was not
  filtered to the current simulated time, or `get_last_price` was used where a
  filtered bar close was available.
- Naive versus timezone-aware datetime comparison in session windows.
- Missing dependency in `requirements.txt`.
- Crypto symbol built as a pair string (`BTC-USD`).

## Diagnosing a zero-trade run

1. Confirm zero filled trades from the trades artifact or logs.
2. Read the skipped-entry logs and the saved code to find which condition
   blocked every entry.
3. Decide whose problem it is:
   - A technical defect (data not loading, a price gate that always returns,
     wrong asset construction, an indicator that never computes, an order that
     is rejected): fix it, read back, rerun.
   - The user's own rules did not fire in this window: do not edit. Explain the
     evidence, propose a longer window, or propose the exact rule change and
     wait for the user's approval.
4. A clean run with no errors proves the code executes, so cosmetic changes
   (chart styling, a different but equivalent constructor, a preferred runner
   block) are never the fix for zero trades.

Never add an unrelated validation order, a backtest-only branch, or a
simplified substitute (for example a single option leg instead of the user's
spread) to manufacture a fill. If an exact entry date has unusable data, keep
the no-trade result, explain it, and ask before changing the date.

## Futures and options specifics

- Futures: `get_last_price(asset)` can be `None` in backtests while bars exist.
  Fall back to the latest completed bar close and log which source was used.
- Options: use `OptionsHelper` to find expiries and contracts that actually have
  data; log `evaluate_option_market(...)` results and only trade when
  `has_actionable_price(...)` is true. See `options-strategies`.

## Metric-target loops

When the user asks to keep editing and backtesting until a metric is met (for
example "until max drawdown is under 20 percent"):

1. Inspect the latest run's evidence.
2. Make one bounded, plausible change.
3. Save, read back, and start a fresh backtest on the new revision. An old
   backtest id never validates a new revision.
4. Repeat until the target is met, the user stops, or the agreed number of
   runs is used. Report each attempt honestly, including misses.

Respect a user's stated preference not to run backtests automatically; in that
case save and read back the code and tell the user validation waits for their
go-ahead. An explicit request in the current message overrides that preference
for that run only.
