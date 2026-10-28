> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-fast-order-management
description: Use when LumiBot strategy code needs fast live order handling, cancel-after-N-seconds logic, immediate hedge/pair/spread legs, manual-cancel recovery, volatile quote handling, or broker-native OTO/OCO/bracket orders.
---

# LumiBot fast order management


When the user asks for a code pattern or minimal state machine, provide a
compact, copyable Python implementation with its callbacks and reconciliation
path. Loading this internal reference does not show that implementation to the
user. Load and adapt the complete combined implementation referenced below instead of replying only with prose.

Choose the responsible mechanics owner. A coupled scan/cancel/late-fill repair
without a safe controller uses the complete fast-order-example implementation;
its own short reservations protect callbacks, polling and broker I/O. An
already coherent complex operation with competing duplicate preparation callers
instead uses `lumibot-strategy-building:references/order-operation-ownership.md`.
Do not mix a new partial state machine or whole-method I/O lock into the complete
controller merely because both resources discuss hedging. Preserve the existing
strategy's actual investment policy in either route.


For a code-pattern or state-machine request, start from the complete combined implementation
referenced below and keep all of its functions: adapt assets, quantities, names and the
user's timeout, but do not write a new state machine from scratch or merge
functions in ways that drop a path. A shorter answer may drop optional
commentary, never a lifecycle path. Before replying, check the fenced Python
against this list:

- Every helper the snippet calls for submit, deadline, cancel, terminal
  clearing, reconciliation and hedging is defined in the snippet. Only the
  strategy's own scan or signal logic may stay a named placeholder, and its
  contract must be stated.
- The entry order id is recorded in the set or dict the callbacks check, and
  the absolute time.monotonic() deadline is the first value computed after
  submit_order returns. Bookkeeping comes after it.
- The wait before cancel dispatch makes no broker request: no get_order and
  no get_orders. In live trading self.sleep(..., process_pending_orders=True)
  only waits; say so in a comment. Preserve a configured full fill-wait
  interval: the optional early-dispatch margin defaults to zero. A request for
  dispatch BY a deadline may configure a measured safety margin; do not silently
  apply that margin to a request to wait the full interval. Keep waits short and
  distinguish local dispatch from later broker acknowledgment.
- cancel_order returns None, not a terminal answer. A broker reply that the
  order already filled arrives as an exception or a fill callback. Wrap the
  call: on an exception, do one exact-order self.get_order(order_id) read;
  FILLED goes to the shared hedge helper, a terminal canceled, expired or
  error state clears the entry, and anything else keeps the blocker armed. A
  successful cancel whose callback never arrives is resolved by one exact read
  on a later iteration.
- One hedge helper serves on_filled_order, the cancel-exception read and later
  reconciliation, fenced by the entry order id. Accepted/submitted/ACTIVE remains
  unresolved until a verified hedge fill fulfills the obligation; cancellation,
  expiry or rejection retains an unfulfilled recovery obligation. State this
  boundary explicitly in a structural answer too. It records a failed or rejected
  hedge as an explicit blocking state and retries it a bounded number of times
  (at least one retry). Only an explicit broker rejection is retryable. An
  exception from the hedge submit_order is UNKNOWN, because the broker may have
  accepted it: keep entries blocked and never resubmit it automatically. A
  hedge order in CANCELLING or PENDING_CANCEL stays active and blocking.
- Every state the code stores is initialized in initialize, and every state
  that can block entries has a path that later clears it or retries it.
- Every exact get_order read is wrapped so a slow, missing or rate-limited read
  becomes unresolved blocking state, never an escaped exception. After a missed
  callback, read the exact order at most once.
- After cancel_order returns, check the local order object for a fill (no
  broker read) and hedge it through the shared helper.
- Finishing a pair never deletes the processed-entry record that the hedge
  fence checks.
- The prose says plainly that sleeptime cannot preempt a running
  on_trading_iteration, and that the strategy controls cancel dispatch but
  cannot guarantee the broker's confirmation latency. It names CANCELLING and
  PENDING_CANCEL as non-terminal and Order.OrderStatus.ERROR as the portable
  rejected state.

For questions about long scans or a slow loop, the answer also covers:
pending-order deadlines run before any fresh scan; after submit_order the
iteration does nothing except the bounded deadline wait and cancel dispatch,
then returns, with no option-chain scans, serial quote loops or hedge
precomputation while that order is pending; preserving the original complete-scan policy while servicing any armed deadline; batched price reads
(get_last_prices, get_historical_prices_for_assets, or get_quotes for bid/ask);
option chains and candidate contracts cached with a bounded TTL; bounded
retries; and callback-first hedging with an exact-order
self.get_order(order.identifier) read as the idempotent missed-callback
fallback.

When saved code with a timed order is "not fast enough" or slow, the order
lifecycle is part of the speed problem, not only the scan. Check the saved code
against the list above and fix every failing item in the same edit: monotonic
deadline, yield after submit, blocker kept through cancel, callback-first
idempotent hedge. Explain the demonstrated lifecycle defects and their effect on dispatch or hedge handling. A fixed limit price alone does not prove why the reported slowdown occurred; describe fill-price limitations separately, without calling an unobserved market price the main bottleneck.
Caching or a faster scan alone is not the repair. Keep the saved timeout, prices
and sizes: shortening the timeout changes the strategy's rules and does not fix
when cancel is dispatched. A "fix it" request authorizes these lifecycle repairs:
save them without asking first. Ask only before changing entry rules or how often
the strategy trades.


For an existing-strategy speed repair, load the complete owner example before
the first saved-file edit. Audit and repair the scan, pending deadline, cancel,
fill and hedge paths together; an early return alone fixes only one symptom.
Use the saved owner integration below when the existing entry/cancel/fill
controller has those coupled defects. A two-line loop/cancel patch is unfinished
while its fill callback still polls before hedging, can hedge twice or never
releases a filled entry. Complete the helper save and entrypoint wiring before
finishing; these are the same requested repair, not optional follow-up work.
When the user requests a fix and that inspection proves a control-flow defect,
save the repair that preserves the existing trading rules. Do not make the user
choose that repair against optional changes to prices, signals or entry frequency.
Those alternatives are not missing prerequisites for fixing the observed bug.
Trace the entire scan loop before describing its entry limit: a pending-order
check before the loop does not stop later loop iterations from submitting and
overwriting that pending order. Repair that demonstrated control-flow defect
under the existing rules before asking about a different trading frequency.
Repairing cancellation and hedging does not authorize more entries. Every
entry caller, including the regular trading iteration and an immediate scan
resumed by a fill callback, must reserve the same entry slot atomically before
broker submission. A broker-list or live-order check is not a reservation: two
callers can both pass it before either publishes its new order. Keep the slot
through uncertain acceptance; release a no-candidate or rejected attempt without
leaving a permanent entry-submitted latch. Preserve a one-shot entry limit or
existing position cap independently of order-state reconciliation. Do not leave cancel/fill races in place because the strategy
has no automatic exit or re-entry policy. Retaining an unresolved entry through
cancel acceptance and fencing its hedge does not add a new trading rule.


Replacing
the broken lifecycle owner is the requested repair, while unrelated trading
policy stays intact. A request for a narrow repair limits the behavior changed;
it does not require keeping an unsafe partial state machine. If the strategy
has a different lifecycle, preserve that contract while applying the ownership
invariants below.
Read back both saved modules before finishing. A helper import without its
complete saved implementation is unfinished; do not replace the copied helper
with an abbreviated local class.

Publishing a fill and reserving its required hedge are one locked transition:
never clear the active entry before the hedge record exists. Keep an already
observed FILLED hedge terminal when `submit_order` later returns; acceptance
must not overwrite a raced fill with ACTIVE. For queue-based fallback hedges,
queue preparation and the entry-keyed submission claim share the same fence.
A later claim cannot undo an extra queue item already appended by a losing
callback. Recheck these three transitions in the final saved code, including
every callback, iteration and recovery caller.



## Preserve one operation through cancellation and hedge failures

Use the complete maintained owner in `deadline-order-example.py`, retaining
its historical entry/alias and per-entry hedge records when integrating it.
A canceled snapshot can clear the active scanning blocker only after the
required reconciliation; it must not delete the historical correlation needed
by a later authoritative fill callback. A callback for that old entry still
reaches the same entry-keyed hedge owner, never the current entry's state.

Before hedge creation, create the owned outcome record. If creation or submit
raises, retain an explicit FAILED/UNKNOWN outcome and its obligation/recovery
policy. A set marking the entry "hedged" plus an exception log is not that
record. Do not fence the obligation away with an untracked placeholder order.

Before the final handoff, trace the original scan/entry/cancel/fill methods and
explain the demonstrated OLD lifecycle defect beside the NEW saved transition.
An acquisition optimization or rotating scan alone does not explain a repaired
cancellation/late-fill/hedge lifecycle. Preserve the original pricing policy.

Use this reference for second-level live order deadlines, immediate hedge legs,
late fills during cancellation, duplicate hedge prevention, manual-cancel
recovery, and broker-native OTO/OCO/bracket orders.

When the user asks for a code pattern or minimal state machine, provide a
compact, copyable Python implementation with its callbacks and reconciliation
path. Loading this internal reference does not show that implementation to the
user. For a new generic deadline-plus-hedge pattern, present the complete tested
class in `references/deadline-order-example.py` with all its method bodies unchanged; explain its input hooks.
Load it with the advertised tool call
`skills reference get(resource_key="lumibot-api-reference:references/deadline-order-example.py")`.
This Python file is registered in the callable resource enum. Loading it is the
same lifecycle implementation task, not an unrelated second reference. Continue
to that exact resource before answering a complete-pattern request; a timing-only
fragment or a claim that the referenced class is unavailable leaves the request
unfinished. Report unavailability only from an actual failed resource read.
A request to show a code pattern requires the actual fenced implementation;
an internal resource filename is not delivered code. Describe the resident
wait accurately: it suspends further scanning in the current iteration while
SDK events are processed; it is not a background or nonblocking worker.
In the explanation, distinguish both external limits explicitly: local cancel
dispatch can be delayed by blocking runtime calls, and Schwab broker cancellation
confirmation latency cannot be promised. A returned cancel request is not
confirmed terminal cancellation.
Do not replace it with a shorter newly invented state machine. Existing saved
strategy repairs must instead integrate only the requested change and preserve
unrelated code. A narrow hedge-observation question may show just that component
without adding new entry/cancel machinery.

Before delivering the complete pattern, audit the emitted reconciliation method
against the maintained class. A due-time check alone is not a finite attempt budget.
Keep its actual refresh counter, maximum attempts, reset/resume policy and visible
blocked exhausted state. An interval-based loop that can read forever omits that
recovery policy even when every individual read is backed off.

## Match the requested deliverable

For an existing-file repair, change only the requested behavior and its necessary
callers. The checks below do not authorize rewriting unrelated strategy logic.
If saved-file readback reveals a specific in-scope defect and editing remains
available, repair it before ending; describing an unfinished repair is honest
but does not fulfill the request. Recheck the initialization, update and reset
callers that own that state, then read back the newest revision.

For a request for a code pattern or state-machine example, minimal means one
clearly defined risk unit, not missing lifecycle code. Provide the necessary
fenced Python together. Implement generic reconciliation, terminal-state and
hedge-recovery helpers that the example calls; a comment saying "reconcile
later" or an undefined `_reconcile_exact_entry_if_due()` does not implement
recovery. Asset selection, signal calculation and strategy-specific quantities
may be explicit inputs. Do not leave the order-management behavior to those
inputs or hide it in an unspecified helper.

- Show a due-time/backoff check and one `get_order(entry_id)` in each later
  reconciliation pass, with unavailable/429/exception results retaining the
  blocker. Both the callback and the actual reconciliation code must reach the
  same entry-id idempotency fence. After cancel dispatch, inspect a locally
  updated filled order or consume its queued callback; an authoritative fill
  does not require another broker read.
- Show why a cancel-pending order remains unresolved. Handle confirmed canceled,
  expired and `Order.OrderStatus.ERROR` results separately from pending/missing
  data. A rejected hedge can be returned as an errored order without raising:
  inspect the returned order as well as catching submission exceptions. Keep
  the original entry's obligation and rejection reason. A saved repair that must
  keep trading needs its actual recovery policy. A conceptual component may
  explicitly retain a visible blocked failure for operator resolution. If you
  include recovery, implement its bounded or operator-requested attempt with
  attributable confirmed zero-fill/preparation-only evidence. Blind retries or
  silently discarded obligations are unsafe. A submitted hedge is not a
  completed pair.
- When scanning is part of the question, show a monotonic wall-clock scan
  budget, a resumable cursor, and caller control flow that exits scanning after
  submitting a timed entry. Mention supported batching for the required data:
  `get_quotes` for bid/ask, `get_last_prices` or
  `get_historical_prices_for_assets` for trade/bar prices. Reuse option chains
  and candidates with a bounded TTL while keeping decision quotes fresh. Keep
  the filled callback fast and exact-order polling as its backed-off fallback.
  `sleeptime` cannot interrupt a running iteration; state this when explaining
  why a deadline can be missed.

For a timing diagnosis, ask for timestamps of submission acceptance, the
calculated deadline, cancel decision, cancel request start and return, the
**broker-terminal observation**, callback delivery and iteration phases. Asking
only for the final status or raw response omits when it became observable.

For an existing saved-file callback-versus-polling or duplicate-hedge repair,
load lumibot-strategy-building's `references/order-operation-ownership.md` before
editing. Start at the shared confirmed-fill initializer itself: its operation
lookup/create/publication, original-entry claim and active-operation pointer
must have the same state owner from every callback and polling caller. A lock
only around final submission cannot prevent a competing initializer from
replacing an in-flight operation. Preserve the existing causal methods and
next-entry completion behavior; do not introduce a second engine.

## Start a numerical cancellation repair here

Distinguish a full fill-wait interval from an explicitly latest cancel-request
boundary. Preserve a full interval without subtracting an unrequested margin.
For an explicit dispatch-BY boundary, include local bookkeeping/dispatch cost in
its configured safety margin; broker acknowledgment is a separate observation.
Copy/adapt this timing arithmetic in every entry submission and recovery path:

```python
# Capture this immediately after submit_order returns, before tracking/logging.
accepted_at = time.monotonic()
# Preserve the user's full fill window by default. Only an explicitly configured
# dispatch-BY allowance accounts for local overhead; it is not broker latency.
fill_window_seconds = float(self.parameters.get("entry_fill_window_seconds", 3.0))
dispatch_allowance_seconds = float(self.parameters.get("cancel_dispatch_margin_seconds", 0.0))
cancel_dispatch_at = accepted_at + max(0.0, fill_window_seconds - dispatch_allowance_seconds)
```

Use that absolute `cancel_dispatch_at` in the resident local-order wait below.
`self.sleep` is a wait plus SDK work, not a precise wake-up guarantee. Leave the
allowance before the latest dispatch time; do not postpone cancellation for a
last quote refresh, order lookup, logging, another scan or a later iteration.
For the illustrated three-second budget, `accepted_at + 3.0` with a cancel only
after expiry still misses the request budget. `accepted_at + 2.5` leaves a
half-second local allowance while preserving a meaningful fill opportunity.
Do not cancel immediately to manufacture a faster test result.

Before finishing the edit, inspect **all** assignments to the pending entry's
deadline, including initialization, normal submission and recovery/fallback.
They must agree on acceptance time and dispatch allowance. A corrected helper
does not repair a caller that still stores a raw full-timeout deadline. Preserve
cancel-pending attribution until a confirmed terminal result or a fill resolves
it, including if a fill arrives while the cancellation response is pending.

To repair saved code that sent a duplicate hedge or duplicate order, also
load `lumibot-strategy-building` resource `references/order-operation-ownership.md`
before editing. It covers every path that can submit the same obligation; this
reference covers deadlines and callbacks only.

## Bound and resume the scan itself

For a long-scan question, show the scan loop as well as the lifecycle owner.
The following override enforces the scan budget and resumes the flattened
watchlist/contract cursor. Populate `scan_candidates` from the original strategy's
cached candidates, initialize `scan_cursor = 0`, and keep the original policy in
`_inspect_original_candidate(candidate)`: it returns True only after selecting an
eligible Asset and setting the five submission inputs documented above. All
candidate/quote work happens before submission. A slow single lookup cannot be
preempted by this loop; no timed entry may already be pending during that lookup.

```python
# bounded-resumable-scan
def _run_one_bounded_scan_step(self):
    candidates = self.scan_candidates
    if not candidates:
        return
    stop_at = time.monotonic() + self.scan_budget_seconds
    visited = 0
    while visited < len(candidates) and time.monotonic() < stop_at:
        if self.active_entry_order_id is not None or self._pair_is_blocking():
            return
        index = self.scan_cursor % len(candidates)
        candidate = candidates[index]
        self.scan_cursor = (index + 1) % len(candidates)
        visited += 1
        if self._inspect_original_candidate(candidate):
            self.submit_entry()
            return  # also yield after uncertain acceptance; never scan onward
```

This budget limits fresh scanning, not a model/test execution. The inherited
iteration still services owned pending entries and hedge obligations before this
override, and its shared submission fence reserves the entry atomically.

## Safety invariants

- Treat an entry, its cancellation, and any required hedge as one lifecycle for
  the risk unit that owns them. Scope blocking to the smallest risk unit allowed
  by explicit strategy and portfolio policy: order, symbol/pair, risk bucket, or
  account. Do not turn one unresolved independent symbol into a universal global
  freeze, and do not let correlated/shared-capital exposure bypass its broader
  risk constraint.
- CANCELLING and PENDING_CANCEL are not terminal. A missing order refresh,
  timeout, rate limit, or cancel exception is also not terminal. Every one of
  those states must keep the entry blocker armed.
- Use Order.OrderStatus.ERROR as LumiBot's portable rejected/error state.
  Broker text may say REJECTED, but generated code must not invent
  Order.OrderStatus.REJECTED.
- A successful cancel_order(order) call does not mean a custom
  on_canceled_order hook already ran. LumiBot queues the strategy callback, so
  it may run just after the current on_trading_iteration returns.
- on_filled_order already carries a filled order. Trust that callback object
  for the fast hedge path; do not make the hedge depend on another
  self.get_order(order.identifier) call that can be slow, missing, or
  rate-limited.
- Callback and reconciliation paths must share one idempotency fence keyed by
  the original entry order.identifier.
- A hedge submission is not a completed pair. Keep the affected risk unit
  unresolved while the hedge is active, rejected, missing, or awaiting a
  bounded retry.
- No timeout, retry count, or blocker scope is universal. Derive each from the
  strategy's stated execution contract, broker capability, and risk coupling.

## Deadline architecture

self.sleeptime = "1S" only schedules the next iteration after the current
iteration returns. It cannot preempt a slow scan. A deadline checked only on a
future iteration can therefore be many seconds late.

A synchronous scan known to occupy that same control path for six seconds
already exceeds a three-second local dispatch budget. State that demonstrated
budget violation directly. Missing broker timestamps may still prevent blaming
the broker or proving the precise cancel-dispatch or terminal-confirmation time.

For a strategy-defined timeout:

1. Finish expensive option-chain, quote, liquidity, and hedge-candidate work
   before submitting the entry.
2. Capture `accepted_at = time.monotonic()` immediately after submit_order
   returns, before bookkeeping, logging or reads. Derive the absolute dispatch
   target from that acceptance time and the user's timeout, subtracting a
   measured local dispatch margin. Store the returned order.identifier.
3. Use a deadline-capable control path that cannot be starved by the next long
   scan. Choose a measured safety margin before the user's actual dispatch
   deadline; do not hard-code one user's timeout into shared guidance.
4. During that short resident wait, process pending events and inspect the local
   tracked order object. Do not call broker-backed get_order immediately before
   the deadline.
5. At the target, call cancel_order once and retain the blocker.
6. Return from the iteration so queued on_canceled_order or on_filled_order
   callbacks can run.
7. If no callback resolves the order, perform one exact-order
   self.get_order(order_id) reconciliation on a later iteration. Back off and
   bound cancel retries.

The timeout is the latest **request dispatch**, not the time to begin waking
up, inspecting state or logging. Waiting the entire timeout and only then calling
cancel_order is already late: local event processing, logging and dispatch take
additional time. Keep a small measured dispatch allowance inside that budget.
For example, a 3.0-second budget with a measured 0.5-second allowance targets
2.5 seconds after acceptance. This is an example, not a new shared trading
policy; preserve the user's fill opportunity and choose the allowance from the
actual path. Do not cancel immediately or hide a missed deadline by skipping an
eligible trade. Include tracking work in the budget rather than resetting the
clock after it. Verify request-start time separately from response-return time.

The strategy can control prompt cancel dispatch. It cannot guarantee Schwab's
network response or broker-confirmed terminal time exactly at three seconds.

A continuous runtime window is sufficient when it spans the strategy's true
operating period and starts immediately when approved inside the window. A
scheduled one-shot process that exits after one iteration cannot own a
sub-minute deadline or callback lifecycle. Persisting ids and deadlines helps a
later reconciliation but cannot replace a live process while an order is
unresolved. If the product has no continuous-window mode yet, `always_on` is the
truthful fallback, not a claim that one daily invocation is equivalent.

## Complete combined implementation

Inspect the saved architecture before choosing the repair. When an existing
strategy already has a coherent operation/queue owner, repair its demonstrated
ownership or remaining-quantity defect in place using the maintained
order-operation-ownership and order-quantity-accounting references. Retain its
entry/cancel policy, method connections, class and runner. Do not introduce an
unconnected alternative controller or require a wholesale business-code port.

For a missing/incoherent combined scan/cancel/late-fill/hedge owner or an explicit
copyable implementation, load `lumibot-api-reference:references/fast-order-example.md`.
It supplies the complete unit-tested controller. Copy its protected lifecycle
into one ordinary strategy-owned helper and connect the original main.py business
subclass and runner. Preserve every helper body and the requested price,
quantity, basket order and entry policy. Read both saved files back.
Do not regenerate a shorter state machine, hold a state lock across broker I/O,
or leave a second callback/polling owner alongside the controller. Neither route
is complete until the actual saved strategy reaches the repaired owner and its
success, failure, reconciliation and next-entry paths remain connected.
A conceptual explanation may use the lifecycle above without copying code.

## Broker calls and API budget

- Use callbacks or broker streams for the fast path and exact-order reads for
  reconnect or missed-callback reconciliation. Streaming does not replace
  reconciliation because messages can be missed across disconnects.
- Do not poll self.get_order every 250 ms. A broker call can itself take longer
  than the polling interval, consume the deadline, and trigger HTTP 429.
- Do not call get_order twice for the same decision.
- Do not use broad get_orders() scans on the deadline-critical path.
- Coordinate an aggregate broker request budget across active orders and
  endpoints. On HTTP 429, honor `Retry-After` when present; otherwise use
  bounded exponential backoff with jitter. A missing/429 read retains
  unresolved state rather than synthesizing a terminal result.
- Batch independent price reads with get_last_prices(assets) or
  get_historical_prices_for_assets(...) when the decision uses trade/bar prices.
  Bid/ask decisions need `get_quotes(eligible_assets)` on LumiBot 4.6.19 or newer;
  `get_last_prices` is not a bid/ask snapshot. Verify the installed data source's
  native batching support before claiming fewer HTTP requests.
- Cache option chains and candidate contracts with a bounded TTL.
- Bound every broker retry loop and expose the final broker reason.

### Scanner latency

For slow basket scans or quote batching, load the focused
`lumibot-api-reference` resource `references/scanner-performance.md` before
editing. It owns the complete two-level scan example, quote/error handling and
account-read optimization. Keep the deadline and lifecycle contracts in this
reference when scanning overlaps an existing order.

## Broker-native orders

Prefer broker-native OTO/OCO/bracket orders when the requested relationship maps
cleanly to a supported broker-native trigger. Use the strategy-managed pattern
when the user's three-second cancellation or custom stock hedge cannot be
expressed by that native order class.

## Manual cancel and restart recovery

- A manual broker cancel is terminal only when the exact tracked order reports a
  terminal state or on_canceled_order delivers it.
- If an exact read is missing or rate-limited, keep the blocker and retry later.
- Persist exact entry, cancel, and hedge ids. Use JSON-safe dict/list state, or
  normalize restored lists before calling set-only methods such as discard().
- A one-shot scheduled runner is invalid for a live sub-minute deadline.
  Choose a continuous runtime window for the strategy's timezone/days/windows,
  or `always_on` until that generalized product mode exists.

## Required regression coverage

Keep production-gated coverage for:

- cancel dispatch under the target without a pre-cancel broker read;
- fill before the deadline;
- fill winning the cancel race;
- cancel exception with unavailable reconciliation;
- callback arriving after cancel_order returns;
- missed callback resolved by one later exact-order read;
- missing/429 reads retaining unresolved state;
- duplicate callback plus polling hedge paths submitting one hedge;
- rejected stock hedge with bounded retries and blocked new entries;
- second/third watchlist symbols preserving the same lifecycle;
- restart-state JSON round trip;
- scheduled one-shot rejection for sub-minute live deadlines.

## Anti-patterns

- A future on_trading_iteration as the only owner of a three-second deadline.
- self.get_datetime() + timedelta(seconds=3) for an exact elapsed-time deadline.
- Broker polling immediately before cancel dispatch.
- Clearing or moving aside the blocker because cancel was requested.
- Treating CANCELLING, missing, 429, or cancel exception as terminal.
- Calling get_order from the filled callback before hedging.
- Marking the pair complete immediately after hedge submission.
- Unbounded rejected-hedge retries.
- Broad order-history scans in the hot path.
- Background threads that call strategy/broker methods outside LumiBot's normal
  lifecycle.


## Observation basis and failure timeline

Before proposing fill arithmetic, establish whether this broker-facing source
reports cumulative filled quantity, a per-fill delta, or position snapshots.
Verify it from the adapter contract or observations first. If unavailable, say
what must be verified and make the reducer conditional; never apply a cumulative
high-water mark to per-fill deltas. For a confirmed cumulative source, process
only max(0, observed_total - prior_high_water) and retain the high-water mark
across duplicate or out-of-order events and reconnects. Track entry identity,
hedged quantity and terminal status separately; position changes are not fills.

For a missed dispatch deadline, separate synchronous work, network request time
and callback delivery. Request reconstructable timestamps for submit acceptance,
absolute deadline, cancel decision, request start/end, broker-terminal observation,
callback delivery and each iteration phase. A scan that occupies the whole
available interval prevents dispatch even when the configured sleeptime is short.
Explain that causal timing and gather the complete timeline before tuning it.

When an failure cannot be explained, keep several causes open (deployment,
process lifetime, saved versus deployed revision, broker order state, strategy
control flow) and collect evidence in that order. Then name the telemetry that
would explain the next failure automatically. Cover each item:

- Process and session lifetime: process start, stop and restart, session or
  run identity, and the exact deployed revision.
- Order lifecycle: submit acceptance, the absolute deadline, the cancel
  decision, cancel request start and end, the broker-terminal observation and
  its source, and callback delivery time.
- Fills: cumulative filled quantity per observation, partial fills, and which
  path (callback, exact-order read or restart reconciliation) resolved them.
- Hedge: decision, submission, broker response and terminal state.
- Loop health: duration of each iteration phase, broker reconnects, rate-limit
  responses, and every backoff with its delay.
- Correlation: tie every record to one opaque or hashed order, session and
  account id. Never log raw account numbers, tokens or credentials.

## Explain the saved repair accurately

After final-file readback, describe the observable behavior in plain language.
State the configured latest-dispatch budget and the actual earlier dispatch
target separately when a local allowance is used. A target of 2.5 seconds
inside a three-second budget is not a promise of a full 3.0-second fill window.
Broker acknowledgment/terminal timing remains outside that local guarantee.

Do not invent a structural claim about the saved code. A filled callback can
use one idempotent fill helper while the canceled callback separately clears
confirmed zero-fill state; that can be correct. Only say both callbacks call
one shared helper if you verified that they actually do. Prefer the useful
behavioral explanation: the entry remains tracked until a fill or confirmed
terminal cancellation, with repeated fills handled once. Do not add new code
or rename functions merely to make a polished explanation true. Report the
saved implementation and unresolved findings as they are.

## Final code-pattern completeness check

A reference the agent read is not code delivered to the user. Do not end with
"the reference also covers recovery" or "provide a recovery action" when the
answer itself leaves that transition unimplemented. Include the actual callback,
exact-order fallback, hedge terminal reconciliation and explicit recovery
functions used by the shown code. Explain the example scope, then give those
functions together. Concise prose is useful; omitting a responsible function is
not a shorter correct implementation.

The recovery operation is already implemented as the class method
`retry_confirmed_zero_fill_rejection` above. Reuse it with its retained entry
history, confirmation checks and shared claim rather than inventing another
partial recovery function. The combined example is one Strategy subclass; its
methods are bound normally and all method calls use `self` consistently.

Common adaptation mistakes to check in the actual emitted code:

- A counter stored only in a failed row is erased when that row is deleted.
  For automatic retries, retain the per-entry attempt counter and enforce its
  maximum. An explicit operator-requested operation may make one attempt per
  request without inventing a lifetime cap.
- A helper whose first action is "return if claim exists" cannot retry a row
  that the caller has just changed to SUBMITTING. Atomically replace a confirmed
  zero-fill failed claim under the same fence; never leave an empty unblocked gap.
- Recording an entry is not permission to submit it. The same risk unit needs a
  checked, reserved entry slot before submit_order, held through unresolved
  hedge work and released after confirmed completion. Keep unrelated independent
  risk units independent when the user's policy permits them.

Preserve these working mechanisms from the combined implementation rather than
inventing a shortened replacement. Show all the responsible functions together.

Keep the original entry record in retained history for recovery. The current
active-entry pointer may already be cleared after a fill and cannot stand in for
that history. Check original attribution and all other recovery preconditions
before removing the failed claim. If recovery cannot proceed, retain the failed
claim and its blocker; do not erase the obligation and return False.

Keep callback inputs attributable to the submitted entry: store the chosen hedge
asset and quantity in its retained record, then read that record in the hedge
callback. Arguments accepted by the submit helper do not initialize unrelated
instance fields automatically. For an entry submission with uncertain acceptance,
keep the conservative attempt-start deadline. A later exact read that finds the
order active after that deadline must dispatch recovery cancellation rather than
leave an active order indefinitely; this does not prove the original acceptance
time or promise an unavailable three-second guarantee.

Resolve the observed entry state independently of duplicate-submission fencing.
An authoritative full-fill callback or exact-order observation makes that entry
terminal before it calls the shared hedge helper. If the helper returns because
a hedge claim already exists, the terminal observation must still be retained.
Otherwise a later confirmed hedge fill can leave the entry slot blocked forever.
For a scanner, service an undispatched owned deadline before a fresh scan; after
a resident cancel dispatch, continue callback/reconciliation ownership rather
than restarting an initial deadline or treating cancellation request as terminal.

Audit the actual next-entry predicate, not just the status labels. For example,
if it blocks on `self._entry is not None`, marking that record FILLED and later
marking its hedge FILLED will not release the slot. Either release the entry
pointer on authoritative entry termination while the separate hedge record
continues blocking, as the combined example does, or explicitly release it when
both entry termination and hedge completion are confirmed. Apply the same
completion transition to filled callbacks and exact-order reconciliation, retain
historical records, and never clear a newer operation's active slot.

A retry is an atomic state transition: the common claim method validates the
failed attempt and replaces it with a new SUBMITTING reservation under one lock.
It never removes the only blocking record and leaves a gap before re-claiming.
It releases the lock before broker I/O, retains earlier failure reasons, and the
external attempt counter survives replacement. Recheck the locally tracked
entry after the last deadline wait before sending cancel; a fill or terminal
observation in that final wait must be handled without an unnecessary cancel.

For a hedge-only component, retain the newly created native hedge Order in its
entry record BEFORE calling submit_order. An exception may follow acceptance;
keep that object and its current identifier for later exact-order reconciliation.
Poll an outstanding hedge independently of whether its entry is already FILLED.
An entry-ACTIVE filter must not make the hedge follow-up unreachable. If this
minimal component leaves a FAILED or submission-unknown outcome blocked, say
plainly that an operator must resolve that outcome before authorizing another
attempt. Do not imply that an unused next-check timestamp implements recovery.

For timestamp diagnosis, first list the observations already supplied. A method
call timestamp, HTTP request start, response return and terminal callback are
different observations. Do not ask again for an already supplied submit-return
or cancel-method-entry timestamp as if it were absent. If the broker's internal
acceptance time is unknown, distinguish it from the supplied submit-return proxy.
Calculate the elapsed dispatch interval and the missed-budget interval; request
only the finer phase, actual HTTP-start or broker-terminal evidence still absent.
