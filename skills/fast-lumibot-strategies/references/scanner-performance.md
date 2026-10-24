# Speeding up multi-symbol and options scanners

Use this reference, together with `references/quote-snapshot-example.py` in this
skill, when a strategy scans a basket of symbols or option contracts and is slow
because it reads quotes or account/order state one item at a time. The goal is
to change how data is acquired while keeping the trading policy exactly the same.

When the user asks you to make the scan faster, do the whole refactor: remove
both demonstrated hot paths (serial option quote reads and repeated per-candidate
account/order reads) and wire the new reader into every caller. A new helper
whose old serial callers are still in place has not made anything faster. If the
user only asked whether batching is possible, answer the question and leave
their code alone.

## Map the scan before editing

Read the full strategy file first (`get_file`) and map these phases:

| Phase | Data change | Behavior to preserve |
|---|---|---|
| Symbol admission | Keep its current observation/check once per symbol. | Original scope, exceptions, order flags and age rules. |
| Entry scan | Acquire option quotes in supported batches. | Basket order, expiry/strike selection, cooldowns and pricing. |
| Viable candidate admission | Refresh orders only where the original decision had an order guard; pass that list through its predicates. | Original exact-contract guard, phase and decision boundary. |
| Pre-entry preparation | Pass the same quote snapshot through every price AND liquidity helper. | Its own candidate universe, formulas and fallbacks; no newly added order filter. |
| After an entry fills | Keep the original fresh-price acquisition and validation. | Existing option-versus-stock choice and order management. |

Prepare all caller and signature changes together. For a large existing file on
BotSpot, replace complete affected method bodies in one `patch_file` call rather
than matching repeated statements inside them: copy each method's exact old body
from the current `get_file` readback and include its unique `def` line in
`oldText`, or use a `replace_range` operation with verified `startLine` and
`endLine`. When several ranges are replaced, edit the method lowest in the file
first so earlier replacements do not shift later line numbers. A complete
`replace_file` with the current file plus only the scoped changes also works.
After saving, read the new revision back with `get_file`. If a patch fails
because the anchor text is ambiguous, nothing was saved: read the file again and
use a unique method body, a verified range or `replace_file`.

Keep a scan's quote snapshot local and pass it to its consumers; new persistent
state is not needed for that.

Cache construction is data acquisition, not a new admission decision. If the
original pre-entry preparation had no account/order read or order predicate, do
not add one there. A transient working order before the fill may disappear
before the original post-fill decision. Moving that check earlier changes the
later option-versus-stock hedge choice, even if scanning is faster. Keep the
original post-fill fresh checks in their original phase.

Audit every pre-entry consumer of the acquired mapping. A price helper and an
option-market/liquidity evaluator can each issue their own quote request. Pass
the selected snapshot quote through BOTH, including the `quote=` argument of
`OptionsHelper.evaluate_option_market` on versions that support it. A snapshot
member that is explicitly missing (None) must stay missing for that scan;
distinguish an omitted optional argument from a supplied None so it cannot
silently trigger a singleton re-fetch.

Keep the reader's return type consistent through every caller.
`self.get_quotes(assets)` returns an Asset-keyed dictionary. The
`read_quote_snapshot` example returns a `QuoteSnapshot` whose `.quotes` is that
dictionary. Extract `quotes_by_asset = snapshot.quotes` once and pass the
dictionary to existing price and preparation helpers, which use
`quotes_by_asset.get(asset)`. A dictionary has no `.quotes` attribute, and
compiling the file will not catch that mismatch, so trace the reader's `return`
and every consumer's access when you read the saved file back.

Prefer injecting acquired data into existing helpers over replacing those
helpers or inlining their fields. Before writing, list each helper's rejection
conditions and fallback returns; those are executable policy too. Keep the
measured repair separate from optional extra optimization: if the hot paths are
repeated option reads and per-candidate account reads, keep the existing single
stock quote call per symbol where it is. One necessary stock read is not the
repeated-contract bottleneck.

## Remove both expensive loops

Inspect the complete non-qualifying path, not only what runs after a candidate
qualifies. Batching only hedge preparation, or reusing one quote after
qualification, leaves the normal option loop serial. Batching stocks alone
leaves per-option work unchanged.

Separate symbol admission from exact-candidate admission. Keep each symbol guard
in its original position and scope; even an account-wide predicate may be
required once per symbol. Evaluate non-mutating price/eligibility conditions
before candidate order reads, so an ineligible candidate needs no order request.
Where the original viable-candidate path had an order predicate, pass a fresh
observation through that predicate.

```python
# These strategy-local callables represent the strategy's EXISTING policies, not
# LumiBot methods. Add explicit `orders` arguments to existing predicates as needed.
for symbol in symbols_in_original_order:
    symbol_orders = self.get_orders(statuses=Order.ACTIVE_STATUSES)
    if existing_symbol_blocker(symbol, symbol_orders):
        continue
    candidates = existing_contract_selection(symbol)
    snapshot = read_quote_snapshot(self, candidates, deadline=None)
    for candidate in candidates:
        quote = snapshot.quotes.get(candidate)
        if quote is None or not existing_price_and_eligibility_checks(candidate, quote):
            continue
        decision_orders = self.get_orders(statuses=Order.ACTIVE_STATUSES)
        if existing_candidate_blocker(candidate, decision_orders):
            continue
        submit_using_existing_logic(candidate, quote, snapshot)
        return
```

Trace every helper that calls `get_orders`; passing a list into one predicate is
not enough if another still refreshes it. An explicit empty list is a valid
observation: test for an omitted input, not `orders or get_orders(...)`. Refresh
again for the next viable decision. Do not reuse an order observation across
later decisions, remove an original guard, or add a broader account-wide veto
where only an exact-contract guard existed. For example, an empty order list seen
before the first symbol cannot answer the original guard for the second symbol:
another order may have appeared since.

Collect contracts from structural chain data. Keep time-varying order and
cooldown decisions in their original phase. Build the quote universe from the
union required by all consumers (a buy cooldown need not exclude a contract from
being sold as a hedge), then apply each consumer's own filters. Moving a quote
fetch earlier does not justify moving or weakening order checks.

## Preserve the existing validation boundary

Batching changes where a quote comes from, not what makes it acceptable. If the
current helper requires both bid and ask, pass a supplied quote through that
same helper; checking only that the Quote object is non-None loses policy.

```python
def existing_two_sided_quote_check(strategy, asset, *, quote=QUOTE_NOT_PROVIDED):
    quote = quote_input(strategy, asset, quote)
    if quote is None or quote.bid is None or quote.ask is None:
        return None
    return quote
```

This is a local helper pattern (using `QUOTE_NOT_PROVIDED` and `quote_input`
from the example file), not a LumiBot method or a new universal two-sided rule.
Keep whatever the original helper actually validates. A supplied quote still
runs those checks; explicit None stays unavailable; an omitted quote keeps the
original fresh-read behavior. Do not put validation only inside the
`if quote is None` acquisition branch, because a quote can exist with one side
missing.

If you separately batch stock quotes, keep their checks and use the bounded
reader there too, so one failed stock batch cannot abort healthy later symbols.

## Preserve the existing price policy

Change acquisition and keep the original valuation branches. Adapt the existing
price helper with `QUOTE_NOT_PROVIDED` and `quote_input`; only its
acquisition/default changes, and the mid/bid/ask/last-price calculations below
it stay the same. Omitted quotes still fetch for legacy and post-fill callers.

For a caller whose policy is two-sided evaluation followed by a price-helper
fallback, keep that branch. Substitute the caller's existing spread setting for
`original_max_spread`:

```python
quote = snapshot.quotes.get(option_asset)
if quote is None:
    continue
evaluation = self.options_helper.evaluate_option_market(
    option_asset, max_spread_pct=original_max_spread, quote=quote,
)
if evaluation is not None and evaluation.bid is not None and evaluation.ask is not None:
    option_mid = (float(evaluation.bid) + float(evaluation.ask)) / 2.0
else:
    option_mid = self._get_option_mid(option_asset, quote=quote)
```

Use this only where it matches the original pricing policy, and keep each
caller's later finite/actionability and eligibility checks. Do not replace a
prior fallback with None, or derive a value only from bid/ask when the original
helper accepted another usable field. For example, with some data sources a
quote with a positive last price and no bid or ask can still have
`Quote.mid_price` and an actionable evaluation.

Skip a known-missing quote before calling a helper whose `quote=None` default
would fetch again. After the entry fills, keep the original fresh-price recheck;
do not carry the earlier snapshot indefinitely. Audit every caller when you
change a shared helper's signature.

## Use the complete bounded reader

`quote-snapshot-example.py` is a complete data-read example to adapt into the
strategy file. It is not an installed LumiBot module. It preserves exact Asset
keys and quote objects and uses the public `get_quotes` method (LumiBot 4.6.19
or newer).

- Use the full reader, including its support types, imports, failure isolation
  and diagnostics. `try: get_quotes(batch); except: continue` can discard a
  healthy contract when another member of the same batch makes parsing fail.
- Schwab accepts up to 50 symbols per batch request; other data sources may fall
  back to individual reads. For an idle pre-entry scan, pass `deadline=None` and
  omit `max_requests`. The reader computes a finite default from the number of
  unique contracts: at most `2*N-B` requests to fully isolate N members across B
  initial batches.
- A returned None stays unavailable for this snapshot. A failed request or an
  omitted requested key enters bounded isolation and recovery. Do not refetch
  returned missing values through an old helper's implicit singleton fallback.
- `get_quote` catches quote-read and parser failures and returns None, while
  direct `get_quotes` can raise. Handle that boundary for every newly batched
  asset type. A `ConnectionError` means one request failed, not that the whole
  provider is down.
- Missing quotes, failed requests and unread work are different outcomes. An
  exhausted request budget is not an empty market or a completed no-trade scan.
  Do not add an unbounded serial fallback or reorder the basket to hide
  incomplete acquisition.

The reader cannot interrupt a blocking network call. If an order deadline is
armed, service it before starting more acquisition (see
`references/fast-order-management.md`). If scanning happens only before any
order is submitted, a finite idle scan needs no artificial deadline.

Reuse structural chain information for a bounded lifetime. Price freshness is
separate: acquisition time does not prove the provider's quote is current. Keep
existing freshness checks, take a new snapshot for a later decision phase, and
do not add a new quote-age filter during a speed-only change. Fetch lazily by
underlying or in bounded steps so loading the whole basket does not delay the
first valid opportunity.

## Verify before reporting

Read the saved file back and trace the full non-qualifying path plus a
qualifying final symbol. Check that:

- both the quote change and the account-read change are present in the saved
  callers, including every pre-entry consumer and the later fresh-price callers;
- basket priority, expiry policy, thresholds, quantities, formulas, cooldowns,
  rules and unrelated files are unchanged;
- old and new helper bodies agree on rejection and fallback branches (try a
  missing quote, a one-sided quote and a newly visible order mentally);
- failure handling surrounds acquisition and keeps healthy members; a bare batch
  call or `except: return` is not the original tolerant read policy.

Then measure. On BotSpot, run the same backtest window before and after with
`start_backtest`, compare runtime with `backtest_status`, and check the logs
(`get_backtest_logs`) for request counts and skipped-entry reasons. Report only
what you actually measured. A faster-looking change that skips symbols,
suppresses eligible trades or leaves the hot loops unchanged is not a successful
performance fix.

Describe each changed data path precisely. A quote snapshot supplies market
prices; order-state checks use their own order observation. If those checks
still read fresh orders once per symbol, say so rather than claiming they were
moved to candidate-only reads. Describe the code that was saved, not the plan.
