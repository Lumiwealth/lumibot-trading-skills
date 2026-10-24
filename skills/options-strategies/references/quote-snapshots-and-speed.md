# Fast and Correct Option Scanners

Part of the `options-strategies` skill. Use this when a strategy evaluates many
option contracts per iteration and is slow, or when you are asked to speed one
up without changing its trading behavior.

## Where the time goes

Measure first (backtest logs often show timing). The usual hot spots:

- One quote request per contract inside a loop.
- `get_greeks` on every strike in a chain.
- `self.get_orders()` called inside a per-candidate check.
- Fetching chains every iteration instead of once per day.

## Batch the quotes once per decision

`self.get_quotes(assets)` returns a dict mapping each exact Asset to a Quote
(or None when absent). Some data sources batch natively; others make one
request per asset, so the speedup depends on the source.

On LumiBot 4.6.19 and later, `evaluate_option_market` accepts an already
acquired quote and will not fetch again:

```python
quotes = self.get_quotes(contracts)
for contract in contracts:
    quote = quotes.get(contract)
    if quote is None:
        continue  # absent in this snapshot; do not refetch inside the loop
    evaluation = self.options_helper.evaluate_option_market(
        contract, max_spread_pct=policy_limit, quote=quote
    )
    if not OptionsHelper.has_actionable_price(evaluation):
        continue
    ...
```

Passing `quote=None` (or omitting it) means "fetch normally". Do not pass a
missing snapshot slot into a helper whose None default fetches, or you
silently bring back the per-contract loop.

If the batch call raises before returning anything, that is different from a
returned None for one member. Handle the error explicitly (log and skip this
decision, or use the original serial path) rather than treating the whole
universe as "no quote".

## Preserve behavior while speeding up

A speed change must not change which trades happen. Check:

- **Same universe.** The batch must contain every contract the original
  decision path could evaluate. If you pre-filter, use exactly the same inputs
  and comparisons as the original. A bid-based test must not become
  ask-based. Quotes can be one-sided or crossed; do not assume the ask is at
  least the bid. Fetching a harmless superset is fine; tightening eligibility
  is a strategy change.
- **Every consumer.** Trace every caller that reads quotes for this decision
  (candidate selection, liquidity checks, hedge preparation) and pass the same
  snapshot to all of them. Fixing only entry selection leaves the other loops
  slow.
- **Each consumer's own needs.** If one path uses the bid and another the ask,
  an absent ask must not now block the bid path. Keep each path's original
  fallbacks; do not substitute zero for a missing price. A finite zero may be
  a legitimate price in the original logic.
- **No new checks.** Do not add `has_actionable_price` gates, spread filters
  or stricter bid/ask rules where none existed. That is a rule change.
- **Fresh prices where they were fresh.** If a later step used a fresh price
  after an earlier evaluation, keep that data flow. Reusing a cached
  evaluation there changes the input.

## Broker order reads

- Keep `self.get_orders()` inside the branch that originally needed it. Moving
  it above a condition can add a request on paths that never needed one.
- Read orders once per phase where the original logic allows, but keep a
  fresh check right before each submission so a working order for the same
  contract is never duplicated.
- A quote snapshot does not justify caching orders across the whole scan.
  Order state needs its own freshness.

## State for new caches

Initialize every new cache field in `initialize()` and read it with
`self.vars.get(name, default)`. A bot can start mid-session or restore state
saved before the field existed, so a daily reset hook is not enough.

For broader speed techniques load the `fast-lumibot-strategies` skill.
