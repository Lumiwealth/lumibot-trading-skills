> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Complete scanner performance repairs

For an accepted implementation, source inspection must lead to the scoped save,
not another feasibility-only answer. Prior replies that did not implement the
user's proposed optimization do not make the current request advice-only.
Read the full conversation; preserve a genuinely explanation-only request as
read-only. Do not require another permission merely to edit the saved code when
the user already asked you to perform that change.

## Choose the repair from the saved causal path

A short request about slow trading does not determine the bottleneck. First identify the slow phase from the saved callers and available runtime evidence. Repeated quote or account reads while traversing the basket before choosing an entry belong to the acquisition-only branch below. The mere presence of timed entry and hedge methods does not turn that scan repair into a controller replacement. Preserve those later methods and their deadline boundaries while saving the demonstrated acquisition optimization. One structural chain lookup per symbol does not establish repeated quote/account work.

Use the mechanical lifecycle branch when the requested or demonstrated slowdown concerns an already accepted entry, its cancellation or its fill/hedge continuation. A continuing scan after an accepted entry, lost cancellation ownership or discarded authoritative fill is then the causal repair. Do not substitute faster pre-entry acquisition for that execution defect. Choose the demonstrated phase, rather than requiring every unrelated lifecycle rewrite before a useful scoped scan edit.

## Repair execution mechanics independently of fill-price choices

A broad request to fix slow trading authorizes demonstrated scan, cancellation and fill-handling defects while preserving the existing entry price. A low limit can explain unfilled orders; it does not explain away these independent defects:

- Continuing a basket scan after accepting a timed entry can overwrite its tracked identity and delay its cancellation service. Retain the accepted order, stop that scan, and service its monotonic deadline.
- Clearing the entry on cancel dispatch loses unresolved cancellation and late-fill ownership. Retain it until authoritative reconciliation and the related hedge obligation are resolved.
- Re-fetching an order inside its authoritative fill callback can discard a real fill when the mutable snapshot is late or missing. Process that callback through the same entry-keyed idempotent hedge owner used by recovery.

When this accepted-entry execution phase is the requested or demonstrated repair, complete and read back the coherent saved-file repair using the maintained `deadline-order-example.py` lifecycle. Keep its original price, signals, quantities and instruments. Explain separately that price aggressiveness is unchanged and may still limit fills. An optional question about a different price is not a prerequisite to those already authorized mechanical corrections. Do not substitute that question for making the demonstrated repair. Do not promise faster broker fills or submit live orders. For a compact saved file with connected initialize/iteration/callback changes, use one complete `replace_file` from the current readback instead of hand-counting an entire-file `replace_range`. Retain unrelated content. A mechanical repair preserves existing Rules meaning; discover optional files with `list_files` before reading them, and do not create a Rules ledger as a new prerequisite.

Before saving and again after readback, trace the accepted entry through elapsed deadline, cancel requested, cancel terminal or late full fill, one hedge claim, submitted/failed hedge outcome and next-entry eligibility. The saved methods must implement every transition, not merely mention them in prose. A remaining wall-clock deadline, cancel-dispatch reset, callback gated on a later mutable order fetch, or untracked hedge submission means this lifecycle repair is unfinished. Continue the authorized correction; do not final-answer that scanning alone fixed the speed issue. The maintained `deadline-order-example.py` supplies this complete operation; adapt its methods while retaining the strategy's actual entry selection and price policy.


## Explain the causal repair in the final handoff

After a verified saved repair, explain the OLD cause and the corresponding NEW behavior, not just a list of added methods or "a lifecycle problem was fixed." For each demonstrated defect, identify the lost boundary: a long basket iteration could defer the pending cancel; clearing entry ownership when cancellation was merely requested could admit a conflicting entry before confirmation or a late fill; re-reading a mutable order snapshot inside the fill callback could discard that authoritative fill. Explain which of those existed in the inspected file and how the saved changes now preserve the deadline, ownership and one hedge obligation. Keep the original pricing rule and the limit of unverified broker fill latency separate. State what was saved/read back and what execution validation was actually performed. Do not claim a backtest, live deployment or faster fill without that evidence.

## Acquisition-only repair: demonstrated quote/account hot paths

Use the following section with the complete `quote-snapshot-example.py` only when repeated quote/account reads are the demonstrated bottleneck. It changes idle pre-entry acquisition, not the later entry/cancel/hedge owner. Existing timed-order methods alone do not make this scoped acquisition repair incomplete; retain their behavior and do not claim to have qualified their execution. Complete the whole requested operation while
preserving its trading policy. A broad speed request authorizes the coherent
multi-method refactor needed to remove both demonstrated hot paths. A small
helper improvement that leaves the main scan unchanged is unfinished work.

Collect contracts from structural chain data. Keep time-varying order and
cooldown decisions in their original decision phase. Build the quote universe
from the union required by all consumers: a buy cooldown need not exclude that
contract from selling as a hedge. Apply each consumer's own filters when using
the acquired data. A quote fetch moving earlier does not authorize moving or
weakening the order checks. Check a blocker that appears while scanning.
Preserve each original predicate literally when moving acquisition: a bid-based
strike decision must not acquire an additional ask-based filter. Bid and ask
can be crossed in a returned snapshot; batching does not authorize changing
which existing caller accepts it.


## Prepare one coherent repair

For an existing single-file scanner, make the first optimization save in that
same `main.py`: integrate the complete quote reader AND its actual scan,
price/liquidity and preparation callers in one coherent `patch_file` batch.
Include its imports and preserve every unrelated method. An isolated new
`quote_snapshot.py` followed by readbacks leaves the requested scanner unchanged;
do not stage that helper-only write before the primary repair. Preserve an
already modular file layout, but finish the connected primary caller edit in
the same request. A complete reader sitting unused is not a saved optimization.

Collect contracts from structural chain data. Keep time-varying order and
cooldown decisions in their original decision phase. Build the quote universe
from the union required by all consumers: a buy cooldown need not exclude that
contract from selling as a hedge. Apply each consumer's own filters when using
the acquired data. A quote fetch moving earlier does not authorize moving or
weakening the order checks. Check a blocker that appears while scanning.
In particular, do not build a shared snapshot from an entry-only `eligible`
list after buy-cooldown filtering and then reuse it for hedge preparation. Keep
the structural contracts needed by the original hedge cache in the read universe,
even when they cannot be bought now. Missing a still-valid hedge quote can switch
the original option hedge to a stock fallback and changes trading policy.

Before the first write, trace the full saved file and map these callers:

| Phase | Required data change | Behavior to preserve |
|---|---|---|
| Symbol admission | Keep its current observation/check once per symbol. | Original scope, exceptions, order flags and age rules. |
| Entry scan | Acquire option quotes in supported batches. | Basket order, expiry/strike selection, cooldowns and pricing. |
| Existing viable candidate admission | Refresh orders only where the original decision had an order guard; pass that list through its predicates. | Original exact-contract guard, phase and decision boundary. |
| Pre-entry preparation | Pass the same quote snapshot through every price AND liquidity helper. | Its own candidate universe, formulas and fallbacks; no newly added order filter. |
| After an entry fills | Keep the original fresh-price acquisition and validation. | Existing option-versus-stock choice and order management. |

Prepare all required caller/signature changes together. In a large existing
file, replace complete affected method bodies in one `patch_file` batch rather
than matching repeated state assignments inside them. Copy each method's exact
old body from the current readback. Include its unique `def` line in `oldText`,
or use `replace_range` with verified inclusive `startLine`, `endLine` and
`expectedOldText`. For several ranges, put the lowest method in the file first
so earlier replacements do not shift the remaining line numbers. Include every
required reader, caller and signature change; a helper-only save is unfinished.
A complete `replace_file` containing the current file plus only the scoped
changes is another valid route. Neither mechanism authorizes unrelated edits.
Keep a scan's quote snapshot local and pass it to its consumers when possible;
new persistent state, initialization and reset edits are unnecessary for that.

Cache construction is data acquisition, not a new admission decision. If the
original pre-entry preparation had no account/order read or order predicate,
do not add one there. A transient working order before the fill may disappear
before the original post-fill decision. Removing that contract from the cache
now changes the later option-versus-stock hedge choice, even if scanning is
faster. Preserve the original post-fill fresh checks in their original phase.

Audit every pre-entry consumer of the acquired mapping. A price helper and an
option-market/liquidity evaluator can both issue their own quote request. Pass
the selected snapshot quote through BOTH, including the supported `quote=`
argument of `evaluate_option_market`. A snapshot's explicit missing/None member
must stay missing for that scan; distinguish an omitted optional argument from
a supplied None so it cannot silently trigger a singleton re-fetch.
When the entry scan calls an existing preparation method such as
`_prepare_hedge_candidate_cache`, update that CALL and the preparation method's
SIGNATURE together to carry `quotes_by_asset`. Inside its candidate loop, read
`quote = quotes_by_asset.get(option_asset)` and skip an explicit None before
calling `_get_option_mid(option_asset, quote=quote)` and passing that same
`quote=quote` to `evaluate_option_market` alongside its original arguments.
Updating only the
entry loop leaves the old nested helper on individual requests and can retry
the same acquired missing member. Keep that helper's original formulas,
candidate rules and post-fill fresh reads; this changes acquisition wiring only.

Keep the new reader's actual return type consistent through every caller.
`self.get_quotes(assets)` returns an Asset-keyed dictionary. The complete
`read_quote_snapshot` example returns a `QuoteSnapshot` whose `.quotes` is that
dictionary. Extract `quotes_by_asset = snapshot.quotes` once at acquisition and
pass the dictionary to existing price and pre-entry preparation helpers; those
consumers use `quotes_by_asset.get(asset)`. If an adapted reader itself returns a
dictionary, use it directly. A dictionary has no `.quotes` attribute. Do not mix
the two interfaces between candidate selection and pre-entry preparation.
In final readback, trace the reader's `return` statement and every consumer's
access, including a qualifying candidate that reaches preparation. Compilation
alone cannot detect that return-type mismatch. Correct alternative interfaces
are valid when all their callers agree.

Prefer injecting acquired data into existing helpers over replacing those
helpers or inlining their fields. Before writing, identify each helper's actual
rejection conditions and fallback returns; those are executable policy too.
Keep the measured repair separate from optional extra optimization. If the hot
paths are repeated option reads and per-candidate account reads, retain the
existing one-stock quote call per symbol in its original phase. Complete those
two changes without introducing a basket-wide stock prefetch or changing that
stock helper. One necessary stock read is not the repeated-contract bottleneck.

## Remove both expensive loops

For a broad speed request, inspect the complete nonqualifying path, not only
what runs after a candidate qualifies. Batching only hedge preparation or
reusing one quote after qualification leaves the normal option loop serial.
Batching stocks alone leaves per-option work unchanged.

Separate symbol/phase admission from exact-candidate admission. Retain each
symbol guard in its original position and scope; even an account-wide predicate
may be required once per symbol. Calculate non-mutating price/eligibility
conditions before EXISTING candidate order reads. An ineligible candidate needs
no additional order request. Where the original viable-candidate path had an
order predicate, pass its fresh observation through that predicate. Do not add
an admission predicate to other callers merely because this one needs it. Keep
each original phase's policy and errors unchanged.

```python
# These strategy-local callables represent the EXISTING policies, not new SDK
# methods. Add explicit `orders` arguments to existing predicates where needed.
for symbol in symbols_in_original_order:
    symbol_orders = self.get_orders(statuses=Order.ACTIVE_STATUSES)
    if existing_symbol_blocker(symbol, symbol_orders):
        continue
    # Structural contracts are collected BEFORE any buy-side cooldown/order
    # decision. Derive each consumer's universe independently from that same
    # structural set; an entry-filtered list is not a hedge quote universe.
    structural_contracts = existing_contract_selection(symbol)
    candidates = list(structural_contracts)
    hedge_candidates = existing_hedge_contract_selection(symbol)
    # A buy cooldown can reject an ENTRY without rejecting that contract as a
    # HEDGE. Acquire the union, then retain each consumer's original filters.
    quote_assets = list(dict.fromkeys([*candidates, *hedge_candidates]))
    snapshot = read_quote_snapshot(self, quote_assets, deadline=None)
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

Trace every helper that calls `get_orders`; passing a list into one predicate
is insufficient if another still refreshes it. An explicit empty list is a
valid observation: use an omitted-input check, not `orders or get_orders(...)`.
Refresh again for the next viable decision. Do not reuse a positive or negative
order observation across later decisions, remove an original guard, or add a
stronger broad-account veto where only an exact-contract guard existed.
For example, an empty order list observed before the first symbol cannot answer
the original guard for the second symbol after quote acquisition: another order
may have become visible meanwhile. Keep the first-level observation per symbol;
remove the redundant per-candidate reads only for ineligible candidates.


## Preserve the existing validation boundary

Batching changes where a quote comes from, not what makes it acceptable. If the
current stock helper requires both bid and ask, pass a supplied quote through
that same helper. Checking only that the Quote object is non-None loses policy.
For a pre-existing two-sided policy, this acquisition-injection illustration
keeps its rejection body unchanged:

```python
def existing_two_sided_quote_check(strategy, asset, *, quote=QUOTE_NOT_PROVIDED):
    quote = quote_input(strategy, asset, quote)
    if quote is None or quote.bid is None or quote.ask is None:
        return None
    return quote
```

This is a local helper pattern, not a LumiBot method or a new universal two-sided
requirement. Keep whatever the original helper actually validates. A supplied
quote still runs those checks; explicit None remains unavailable; omitted input
retains the original fresh-read behavior. Do not put validation only inside the
`if quote is None` acquisition branch. An object can exist with one side absent.

For a separate request or profile that actually justifies batching stocks,
retain their checks and use the bounded reader for failed requests there too.
One direct stock-batch failure must not abort healthy later symbols when the
prior singleton path could continue. That additional acquisition change is not
needed to fix an already measured option-and-account-read bottleneck.

## Preserve the existing price policy

Change acquisition while retaining the original valuation branches. Adapt the
existing price helper with `QUOTE_NOT_PROVIDED` and `quote_input` from the
complete reader. Only its acquisition/default changes; keep the existing
mid/bid/ask/last-price calculations below it. An omitted quote still fetches for
legacy and post-fill callers; an explicitly supplied `None` stays unavailable.

For an existing caller whose policy is two-sided evaluation followed by its
price-helper fallback, the batched version retains that branch. In this
call-site illustration, substitute the caller's existing spread expression for
`original_max_spread`; it is not a new SDK variable or a new limit:

```python
quote = snapshot.quotes.get(option_asset)
if quote is None:
    continue
# Keep this caller's existing spread parameter and later eligibility checks.
evaluation = self.options_helper.evaluate_option_market(
    option_asset, max_spread_pct=original_max_spread, quote=quote,
)
if evaluation is not None and evaluation.bid is not None and evaluation.ask is not None:
    option_mid = (float(evaluation.bid) + float(evaluation.ask)) / 2.0
else:
    option_mid = self._get_option_mid(option_asset, quote=quote)
```

Use this pattern only where it matches the original pricing policy. Preserve
each caller's later finite/actionability and eligibility checks. Do not replace
a prior fallback with `None`, or derive a new value solely from bid/ask when the
original helper accepted another usable quote field. In the matching Schwab
parser, a quote with positive `lastPrice` and neither bid nor ask can have
`Quote.mid_price` and an actionable evaluation. Missing one side is a different
case; keep the existing evaluation checks instead of inventing a new rule.

Pass the same snapshot into every pre-entry helper, including
`OptionsHelper.evaluate_option_market(..., quote=quote)` on versions supporting
that parameter. A known missing quote must be skipped before calling a helper
whose `quote=None` default would fetch again. After the entry fills, retain the
original fresh-price recheck; do not carry the earlier snapshot indefinitely.
Audit later callers when changing a shared helper's signature.

## Use the complete bounded reader

`quote-snapshot-example.py` is a complete data-read example to adapt into the
saved module/helper. It is not an installed LumiBot import. It preserves exact
Asset keys and quote objects and uses the public `get_quotes` contract.

- Reuse the full `read_quote_snapshot` implementation rather than reimplementing
  its acquisition loop. Log each batch exception before its split/retry branch;
  a successful split does not erase the failed request. Keep `.unavailable`
  reasons scoped to their own assets: skip that candidate and continue original
  candidate traversal using recovered healthy quotes. Do not return from the
  whole scan merely because one isolated member has a non-missing error.
- Use the full reader, including its support types, imports, failure isolation
  and diagnostics. `try: get_quotes(batch); except: continue` can discard a
  healthy qualifying contract when another member makes the parser fail.
- The supported Schwab batch size is 50. For an idle pre-entry scan, pass
  `deadline=None` and omit `max_requests`. The reader computes a finite default
  from unique contracts: at most `2*N-B` requests for full binary isolation of
  N members across B initial batches. Twice the initial batch count is too
  small to recover healthy contracts after a malformed member.
- A returned `None` stays unavailable in this snapshot. A failed request or
  omitted requested key enters bounded isolation/recovery. Do not refetch
  returned missing values through an old helper's implicit singleton fallback.
- On pinned Schwab 4.6.20, `get_quote` catches quote-read/parser failures and
  returns `None`, while direct `get_quotes` can raise. Handle that boundary for
  every newly batched asset type, including underlying-stock prefetch. A
  `ConnectionError` indicates one failed request, not global provider downtime.
- Retain usable members and observable acquisition failures. A malformed or
  failed member must not hide healthy later candidates. Missing quotes, failed
  requests and unread work are distinct; exhausted budgets are not an empty
  market or a completed no-trade scan. Do not introduce an unbounded serial
  fallback or rotate basket priority to conceal incomplete acquisition.

The reader cannot interrupt a blocking HTTP call. An armed cancellation
deadline must be serviced before starting more acquisition, with an appropriate
provider timeout or bounded continuation. A tighter explicit budget may defer
work, but keep unread work explicit. If scanning happens only before submission,
finish that finite idle scan without inventing a deadline or asking the user
to design the batching algorithm.

Reuse structural chain information for a bounded lifetime. Price freshness is
separate: acquisition time does not prove the provider's quote is current.
Keep existing freshness checks and use a new snapshot for a later decision
phase. Do not add a new numeric quote-age filter during a speed-only edit.
Fetch lazily by underlying/bounded step so loading the entire basket does not
delay its first valid opportunity.

## Finish the saved repair before answering

Read the final saved files and trace the full nonqualifying path plus a
qualifying final symbol. Verify both quote and account-read changes in that
readback, every pre-entry consumer, and the later fresh-price callers. Keep
basket priority, expiry policy, thresholds, quantities, formulas, cooldowns,
Rules, dependencies and unrelated files intact. Leave inherited code/Rules
disagreements for a separate user decision.
Compare the old and saved helper bodies, especially deleted rejection and
fallback branches. Review each changed caller with a missing quote, one-sided
quote and newly visible order, rather than only looking for the new batch call.
Verify that failure handling surrounds acquisition and retains healthy members;
a bare batch call or `except: return` is not the original tolerant read policy.

If a hot path remains unchanged, continue the authorized edit. An answer saying
"the main scan is not fully optimized yet" does not complete this request when
supported APIs and ordinary editing tools remain available. Complete the
implementable refactor; report unavailable live timing separately. No live
broker login or forced backtest is needed merely to save that supported edit.

A failed exact-text patch saved nothing, including earlier operations in that
batch. An ambiguous match is an editable local problem, not a permission or API
blocker. Do not retry that same `oldText` in a larger batch. Read the current
file, identify the intended complete method and use its unique method body or
verified range as above; alternatively replace the complete current file.
Continue the authorized repair through a successful save and final readback.
Do not finish with an apology or a request for permission merely because a patch
was ambiguous. Explain a genuinely denied operation, unsupported API or external
prerequisite precisely when it prevents all supported editing routes.
A newly defined reader with its old serial callers still present is unfinished
plumbing. The entry path and pre-entry preparation must actually pass the
acquired quote to their existing helpers, while later callers that omit it
must retain their fresh-read default. Follow the call sites in the saved file;
neither the helper's presence nor an entrypoint readiness result proves wiring.

Measure complete traversal, qualifying decisions, request counts, data age and
cancellation dispatch separately from broker acknowledgment. Report only the
measurements actually observed. A faster-looking change that skips stocks,
suppresses eligible trades, or leaves the demonstrated hot loops unchanged is
not a successful performance repair.

Describe each changed data path precisely in the final answer. A quote snapshot
supplies market prices; order-state checks use their separate order observation.
If those checks still read fresh orders, say so rather than grouping them under
the reused quote snapshot. Verify each claimed change against its saved caller;
an accurate implementation can still be misrepresented by an overbroad summary.

Recommendations are not descriptions of the final saved implementation. Before
claiming when an order refresh happens, inspect its enclosing branch in the
saved caller. A read that still runs unconditionally once per symbol is not a
candidate-only read, even if candidate-only reads were the proposed plan. Say
that repeated reads were reduced unless the more precise placement is verified.
Do not copy a recommendation or revision-analysis description into the final
summary as though it proves the saved call ordering. Report each claimed
mechanism from the actual saved body, including successful alternatives.
