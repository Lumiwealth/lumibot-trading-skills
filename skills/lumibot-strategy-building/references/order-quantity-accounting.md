> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: order-quantity-accounting
description: Use for overfills, partial or canceled hedge replacements, repeated fill observations, or late executions across order attempts.
---

# Quantity belongs to the operation, not its current order

Prepare the complete `OperationFills` and `RetainedOperations` definitions,
imports AND connected submission, callback, reconciliation and completion
method bodies before the first write. List the actual existing initialization, submission,
observation and completion methods that will use the accounting owner. A
definition has no effect until those callers instantiate and use it; repair
those method bodies together, rather than saving a class as an initial step.
When accounting spans initialization, submission, polling and callbacks, use
`replace_file` for the complete affected existing module. Preserve its original
unrelated methods, imports and runner verbatim. This keeps one coherent repair
from depending on several approximate oldText fragments in an atomic patch.
Then read back the complete saved module and correct any disconnected caller.
Audit each new persistent owner field by its exact saved name before handing off.
Trace its initialization, submission/callback reads and writes, reset and
completion paths. Initializing one attempt index and then reading a differently
named index during submission leaves the hedge unimplemented even though the
file compiles. Use the same actual initialized registry throughout; do not
introduce a second legacy-looking field name in one caller. Read the saved
initializer alongside every edited caller and correct missing or inconsistent
fields before the final answer. A catch-and-log branch reporting unresolved
submission does not compensate for a missing local field: no broker submission
occurred, so finish that local wiring repair.
 Do not stage a definitions-only or
imports-only save before the actual repair. If a complex patch fails, refresh
the current handle and recover the complete connected change; a smaller save
of only scaffolding does not recover its user-facing purpose. The failed
batch is atomic: its proposed new text is not present in the saved file. When
retrying a selected `retryOperation`, preserve its oldText AND newText fields
unchanged, adding only the returned location selection; do not use the proposed
new text as oldText or accidentally turn the replacement into a deletion. If
that correction is no longer straightforward, use the current complete readback
to save the complete connected repair with replace_file and verify it. A rejected
text edit is recoverable; continue the authorized saved-file repair. Keep the
tested `observe` implementation and common lock instead of a second handwritten
observer. Preserve the terminal, alias and high-water behavior supplied by the
complete component, and retain all unrelated code and Rules.


First identify the causal hedge methods: attempt registration, fill refresh,
replacement sizing/dispatch and confirmed completion. Preserve entry signals,
prices, eligibility and cancellation-branch outcomes. Entry-scan reservation,
pending-state publication and the one-time fill handoff are causal ownership
mechanics: repair those when needed, without changing trading policy. Keep
unrelated branch bodies intact when assembling the repaired file. In particular, do not
copy the hedge's unresolved-order policy into the separate entry-cancellation
path or change what that original path does after a missing entry-order read.
At final readback compare those untouched method bodies against the original,
as well as tracing the new hedge path. Correct an accidental entry-policy edit
before final-answering; a successful hedge repair does not excuse that drift.

Add accounting initialization to the actual original `initialize` method;
preserve its existing helper construction, caches, deadlines and scan state.
A daily reset often repeats many assignments but omits one-time dependency
setup. Never replace `initialize` with a reconstructed reset body. Compare its
complete final body to the original after adding the new fields, and retain
every original dependency still used by unchanged methods. A hedge ledger
cannot repair a file whose ordinary scanner now fails before any entry.

Honor an explicit file boundary. If the user says to keep the other files the
same, repair the affected existing file using its current operation architecture;
do not add a separate controller file. Reuse the COMPLETE tested `OperationFills`
and `RetainedOperations` implementations inside that file and wire the existing
callers to them. Adapt field names and callers, not their identity matching,
cumulative-fill accounting or terminal-state logic. An existing-file boundary
does not require reimplementing those classes as a shorter queue and one
current-order fill counter. That loses late fills from a previous canceled
attempt even if a lock protects the new queue. Preserve the original entry,
pricing, cancellation and retry policies around this accounting owner.
If this repair turn already created a helper that the final strategy does not
use, remove ONLY that newly created unused file with the ordinary delete_file
tool and current revision, then read back the final file set. Preserve every
pre-existing file and its content outside the authorized change. An unused
extra helper is unfinished cleanup, not evidence that the saved repair works.

## Keep the active slot consistent with the retained ledger

A confirmed terminal attempt can remain in history while its legacy active-order
pointer is cleared. Otherwise the manager can select `submit` for the remainder
and then call a submitter whose `active_order_id is not None` guard rejects that
same canceled order forever. Conversely, an old terminal observation must never
clear another unresolved replacement. Derive the active slot from the CURRENT
operation's unresolved attempts, rather than retaining a second ownership
decision in a scalar. This executable integration uses the IO-free example:

~~~python
def operation_action(self, operation):
    with self._hedge_state_lock:
        if self._current_operation is not operation:
            return None
        step = operation.next_step()
        unresolved = operation.unresolved_tokens()
        self._active_order_id = (
            operation.current_order_id(unresolved[0]) if unresolved else None
        )
        return step
~~~

Adapt these field names inside the existing file. Call after the required
observations while the existing whole-method owner still covers selection,
preparation, registration and dispatch. Keep every attempt and its fill history.
When `submit` has no unresolved attempt, clear only that operation's obsolete
active ID BEFORE invoking a legacy submitter that checks it; do not mark its
target complete, forget the old attempt, or reset its filled total. Once the
replacement is registered, its current Order ID again projects into that slot.
A missing current identity raises and keeps ownership; it is not an empty slot.
Trace this whole path in final readback: partial fill -> confirmed cancel ->
remaining-quantity dispatch -> late old fill -> excess replacement cancellation
-> confirmed terminal outcome -> recalculated remainder -> completion.

For this existing-owner route, use the shared reentrant whole-method pattern in
the ownership reference through the entire preparation/dispatch transition.
The separate complete controller's short broker-I/O reservations are a different
complete design. A comment saying not to hold a lock during I/O does not supply
the missing fill-generation revalidation for an otherwise partial reservation.
A request to **save the repair only** authorizes completing the saved-code repair
through as many necessary edit/readback steps as it takes; it does not authorize
starting a backtest or deployment. It does not mean "make one write and stop."
Work through the complete loop: read current owners → prepare their connected
changes → save → read back every changed owner → correct any missing connection.
When readback reveals a missing method or disconnected ledger, the next action
is the corrective file edit. When a save is rejected for ambiguity, the next
action is its explicit selected-match retry or a complete-file replacement.
Finish this loop before the final answer. Then report the saved repair and its
actual verification limits without claiming execution that was not requested.

For this save-only handoff, distinguish the completed source change from runtime
readiness. A returned readiness of `unknown` is not evidence that the saved
quantity repair is incomplete or unsafe. When the current readback implements
the requested accounting, cancellation and continuation paths, describe those
actual saved corrections and separately report unknown readiness and execution
not performed. Do not invent a remaining race or say a demonstrated path is
absent merely because it has not been backtested or deployed. If a concrete
current code path still loses fills, sizes excess quantity or blocks continuation,
finish that authorized repair instead of ending with a general warning.
For example, when supported by the readback: "Saved the requested quantity
repair and read it back. The saved code retains each attempt's confirmed fills,
sizes a replacement from the remaining obligation and preserves the next entry.
Execution readiness is unknown; no backtest, deployment or trade was run."
This describes inspected source, not proven live safety or a ready status.

Read the complete saved implementation and its Rules first. Preserve its signal,
basket, target per NEW entry, prices, duration and deadline policies. Repair all
paths that submit, reconcile, cancel and complete the affected operation.
Load `references/order-operation-ownership.md` BEFORE writing the repair and
apply its common atomic owner to the quantity repair as well.

The polling path must refresh EVERY attempt of the current operation, including
retired/canceled attempts, before deciding to wait on its active replacement.
A late fill on the canceled original can make a still-working replacement too
large. Aggregate those updated high-water marks, cancel the excess unresolved
replacement, confirm its terminal state, then recompute the remainder. Updating
old fills only inside callbacks does not cover a missed callback. In the final
readback, trace a retired attempt through the actual polling caller; refreshing
only `stock_hedge_order_id` leaves this repair incomplete.

## Keep the complete component in the existing file layout

Preserve the strategy's existing file layout. For a self-contained strategy,
integrate the COMPLETE accounting reference into that saved file, including its
imports, exact class/function names and every method. Adapt the existing caller
wiring instead of inventing or renaming a smaller accounting implementation.
The reference is component source; it is not an installed LumiBot import.

Wire the existing submission and polling callers to the same actual book:

~~~python
registry = self.vars.hedge_operations
book = registry.for_entry(original_entry_id, original_target)
token = book.register(created_order)  # under the shared operation owner
book.accepted(token, self.submit_order(created_order) or created_order)
# On each later reconciliation, resolve the current ID from the retained native
# object, including ID assignment that happened AFTER submit_order returned.
for token in book.unresolved_tokens():
    observed = self.get_order(book.current_order_id(token))
    if observed is not None:
        registry.observe(observed)
        # This registry includes archived entries, not only the current one.
        # Surface retained excess BEFORE any active-entry-only continuation guard.
        for entry_id, excess in registry.reconciliation_required.items():
            self.log_message(
                f"Entry {entry_id}: confirmed hedge excess {excess}; reconcile exposure",
                color="red",
            )
# Missing/unavailable reads retain the unresolved attempt and its reservation.
~~~

A string copied into `stock_hedge_order_id` before submission is not the later
broker lookup ID. Even adding the returned ID to an alias set does not repair a
poller that still queries that stale string. Route the real `_manage_*` caller
through `current_order_id` on EVERY read. Keep the retained native object and
original-entry registry; do not recreate an entry's book on a repeated callback.
The methods above are from the complete tested classes, not a second ledger.

A fill callback can settle the current attempt before the iteration monitor
runs. Inspect `book.next_step()` and perform the completion handoff below even
when `book.unresolved_tokens()` is empty. An empty unresolved list on a complete
book is settled state, not a missing broker identity or broker outage. Never
raise before completion merely because `next(...unresolved_tokens(), None)`
is None while an old cached stock-order ID remains set. Query only genuinely
unresolved current attempts in this monitor; preserve the separate retained
history/callback observation path for late reports on terminal older attempts.
Those old observations still go through `registry.observe` and the excess
reporting above, regardless of which entry is now active.

Connect the first confirmed ENTRY to its original complete fill initializer,
not merely to the new ledger and stock submission helper. That initializer owns
the existing transition out of pending-entry state as well as hedge setup:

~~~python
# Inside the existing shared state owner, once per original confirmed entry:
with self._hedge_state_lock:
    registry = self.vars.hedge_operations
    if original_entry_id not in registry.operations:
        registry.for_entry(original_entry_id, original_target)
        self.vars.active_hedge_entry_id = original_entry_id
        self._handle_confirmed_buy_fill(order)  # preserve the original full body
~~~

Here `_handle_confirmed_buy_fill` denotes the original strategy's existing
full fill-initialization method; keep its actual name and callers. Do not replace
that call with only `_use_stock_hedge_fallback` or `_sell_stock_fallback`.
Preserve its pending-entry cleanup, filled-entry data, active-order release and
normal hedge transition. In particular, retaining the old pending-buy key,
active-buy ID or pending deadline after its hedge completes can keep every later
iteration on the already filled entry, so no second entry is possible. Keep the
existing `_clear_pending_buy_state` behavior and all fields it clears. Invoke
the original initializer only on the first confirmed entry; a late report from
an archived hedge must never reset a newer entry's pending state.

Wire completion as well as initialization. The registry keeps old books for
late reports; it does not clear a strategy's separate active-entry pointer.
Inside that same existing state lock, the completion handoff is:

~~~python
with self._hedge_state_lock:
    if registry.claim_completion(observed_entry_id):
        if self.vars.active_hedge_entry_id == observed_entry_id:
            self.vars.active_hedge_entry_id = None
            self.vars.stock_hedge_order_id = None
            self.vars.stock_hedge_submitted_at = None
            self.vars.stock_hedge_state = "idle"
            self.vars.stock_hedge_symbol = None
            self.vars.hedge_stage = "idle"
            self._mark_pair_complete()  # preserve its original body and call arguments
~~~

Use the saved strategy's actual completion method. Retire the matching active
pointer and completed hedge stage BEFORE calling that method, while retaining
the old book and completion claim. The original completion method may itself
return early while `hedge_stage == "stock_hedge"`; leaving that old stage set
silently skips its completion count and entry-resumption work. Preserve the
original caller's resumption arguments and its normal entry policy. Otherwise a new entry can fill and still be rejected because
`active_hedge_entry_id` belongs to the completed old entry. A repeated old report
must neither run completion twice nor clear a different newer active entry.


After wiring the callers and before the final handoff, trace every accounting-method
call to its actual class body in the complete saved file. In particular, a caller of `book.current_order_id`
requires this method INSIDE the complete `OperationFills` class. Keep its alias
registration as well as its broker lookup; do not leave the method out or put
it outside the class:

~~~python
    def current_order_id(self, token: int) -> str:
        # Native dispatch may mutate the object ID after submit returns.
        # Old aliases identify fills; they are NOT a broker-query selector.
        attempt = self.attempts[token]
        identifier = attempt["lookup_order"].identifier
        if identifier is None:
            raise ValueError("Broker identity unavailable; retain reservation")
        current = str(identifier)
        attempt["aliases"].add(current)
        return current
~~~

This method is part of the full executable reference, not a substitute for its
other methods. Keep the complete `OperationFills` and `RetainedOperations`
implementations, then verify every constructor and method the strategy invokes
exists on the actual saved object. Read the complete saved file back and retain
all initialization, trading rules, locking and normal review steps.

Use the component as the actual owner, not an unused class beside another
handwritten dictionary ledger. The strategy's operation registry must be the
`RetainedOperations` instance; create/get books through `for_entry`, and route
both callback and polling observations through its `observe(order)` method
under the common lock. Adapt names and callers, not the reference's matching
algorithm. Do not define the tested classes and then bypass them with a second
manual fill observer.

An incoming replacement report must update THAT replacement's attempt. With an
original attempt filled40 and a replacement filled60, the original stays40 and
the replacement becomes60; a repeated report leaves the total100. Comparing a
stored order's identifier with its OWN alias set always matches that stored
attempt and is not a test of the incoming order. The reference's `_attempt(order)`
compares the incoming object/identifier against each attempt and is already used
by `observe`. Keep that tested route instead of recreating its nested search.

Keep the tested quantity helper's numeric initialization when integrating it.
An unfilled order normally has an empty `transactions` list. If using Decimal
arithmetic, initialize its accumulator with `Decimal(0)` or use
`sum(converted_quantities, Decimal(0))`; an integer `0` has no
`to_integral_value()` method. Observe a confirmed canceled order's terminal
state even when its cumulative execution is zero, so that safe reconciliation
can size the remaining obligation. Inspect this zero-fill path in the saved
helper as well as paths that contain a partial or complete execution.
A readable terminal `fill` observation may contain no NEW transaction records.
Keep its prior cumulative high-water and still mark that attempt terminal; do
not set a permanent `quantity_unknown` blocker merely because this list is
empty. This does not mean an unreadable or missing order is terminal, and it
does not permit inventing filled quantity from the requested quantity. The
reference's unchanged `observe` implements this distinction and retains late
reports against their original attempt.

Execution quantities are nonnegative; `position.quantity` is signed and is
normally negative for an existing short position. Preserve the strategy's
existing long-versus-short allocation. Copy and use the tested
`held_long_quantity` input adapter from the executable reference for positions;
reserve `quantity` for nonnegative execution/order counts. Passing a short
position to `quantity` before clamping rejects a legitimate holding and blocks
the next replacement. Keep position allocation separate from cumulative fills.
Keep both reference functions' names and bodies instead of combining them into
a new generic `hedge_quantity` parser. In the final saved code, inspect EVERY
position-quantity read and its caller. No holding maps to zero, a long holding
of 25 maps to 25, and a short holding of -40 maps to zero held-long inventory
and still reaches the normal short-order branch. `max(0, quantity(-40))` is
incorrect: Python evaluates the rejecting parser before calling `max`.
Declaring `held_long_quantity` without wiring these callers does not fix that
path. Check these concrete signed inputs before claiming the repair complete.
If the existing strategy sells held inventory before opening a short, retain
its position read and both allocation branches. Pass the operation remainder
into that existing policy; do not replace it with unconditional `SELL_SHORT`.
For a `submit` step, its preserved allocation has this numeric boundary:

~~~python
position = self.get_position(asset)
held_long = held_long_quantity(position.quantity if position is not None else 0)
close_quantity = min(step["quantity"], held_long)
quantity_to_submit = close_quantity if close_quantity > 0 else step["quantity"]
side = Order.OrderSide.SELL if close_quantity > 0 else Order.OrderSide.SELL_SHORT
~~~

Register that permitted leg with the same operation before dispatch, then
reconcile its confirmed fills before selecting the next leg. Keep the existing
asset, order type, duration and other trading-policy arguments.


An account position is NOT this entry's executed hedge quantity. It can include
earlier entries, another bot, manual trades or a stale snapshot. Never declare
this operation complete or size its replacement from an absolute account
position. Use positions only for the existing permitted split between selling
held shares and shorting the rest, after computing the operation remainder.
A short position has a legitimate NEGATIVE quantity. Do not pass it through the
nonnegative execution-quantity validator before taking its positive part: that
would throw before a replacement could be submitted. Parse the signed position
as a finite Decimal first, then use `long_position_quantity(position.quantity)`
from the example for the available long inventory. Zero long inventory is not
zero account exposure. Fill quantities and requested order quantities remain
nonnegative; unavailable or nonfinite positions remain errors, not zero.


Create one operation tied to the exact original entry identity. Its target is
the original requested exposure for that entry. Keep EVERY attributable order
attempt, its stable local identity, broker-ID aliases, submitted quantity and
confirmed execution high-water mark, including retired/canceled attempts.
Do not use the currently active order as the operation identity. A replacement
is another attempt at the SAME target, never a new target.

Load `references/order-quantity-example.py` for the tested, IO-free accounting
implementation. For an authorized repair of multi-attempt fill accounting,
integrate its complete `OperationFills`, `RetainedOperations`, `quantity` and
`held_long_quantity` bodies into the saved strategy. Retain their arithmetic, broker-ID/object
matching, current-order lookup, selector and once-only completion methods.
`RetainedOperations.observe()` must receive owned reports even when their entry
is no longer active; connect its `reconciliation_required` state to the existing
diagnostic path. A reduced active-entry-only ledger loses that protection.
Use the returned ORIGINAL entry identity before writing active state. A report
for a completed older entry can update that entry's archived quantities and
reconciliation diagnostic, but must return before changing the current entry's
phase, target, queue or completion path. Gate every completion counter increment,
blocker release and resumed scan with `claim_completion(entry_id)` under the same
owner. Even a terminal snapshot at target cannot complete an entry twice.
Save the complete tested accounting module and use these methods rather than
translating them into another collection of global fill/completion flags.
Adapt the existing caller wiring and state names; do not paste a second trading
engine or rewrite unrelated selection/entry logic. All readers/writers that can
submit or complete share the same lock/reservation owner. A read-only identity
gate outside that owner is not itself quantity synchronization; recheck the
current operation inside it before changing quantities or submitting.

Use ONE quantity owner. The example's read-only `target`, per-attempt high-water
marks and `next_step()` derive submit/cancel/wait/complete from the same ledger.
Keep those tested accounting bodies when integrating them; adapt their callers
instead of inventing a smaller replacement ledger. Do not import a development
resource path. Remove obsolete full-size/remainder queue
arithmetic for this operation when adopting the ledger. In particular, never
subtract cumulative fills from an already reduced queue value: after target100,
fill40 and replacement60, a late original cumulative60 leaves40, not
`mutated_queue60 - total_filled60 = 0`. Repeated reconciliation of unchanged
evidence must leave the same remainder. A sell-held-shares/short-rest split may
choose the next side from the permitted position read, but every dispatch is
bounded by the SAME original target minus all attributable fills. It must not
reset the target or forget retired attempts when advancing a side/queue leg.

After collecting the required observations under the common owner, process the
selector's result: `cancel` claims that attempt's cancel request before dispatch;
`wait` retains all unresolved ownership; `submit` registers exactly the computed
remainder (or a permitted smaller side leg) before dispatch; `complete` releases
the entry exactly once and resumes its existing next-entry path; `reconcile`
surfaces actual excess exposure without inventing a compensating trade. A
separate mutable queue or stale scalar ID must not override that decision.

**The IO-free example does not supply synchronization.** Adding the ledger
alone leaves the repair incomplete. Use the SAME `threading.RLock` and
`serialized_hedge_state` decorator from the ownership reference around every
causal existing owner: original-entry claim, fill observation plus excess-order
decision, remaining-quantity calculation plus preparation/dispatch, terminal
reconciliation, and completion/reset/resumption. Nested calls use that same
reentrant lock. A callback can overlap an iteration. In particular:

- Computing a replacement quantity, then later setting `preparing`, is unsafe
  if a callback can update earlier fills between those statements. Serialize
  the entire calculation/publication/dispatch transition, not only the final
  submission or the observer individually.
- Calling the same hedge manager from both a fill callback and an iteration
  requires shared protection through clearing IDs, completing and resuming.
  Otherwise both can finish the same operation and each submit a new entry.
- Merely adding a busy flag without atomic claim/recheck is not synchronization.
  A short atomic reservation design is also valid when every observer and
  publication/completion transition respects that owner; do not use a partial
  reservation that leaves newly observed fills unhandled before dispatch.

The complete integration order is:

1. On the original owned entry fill, atomically claim that entry exactly once
   and initialize its target. Keep completed entry identities so repeated entry
   callbacks cannot initialize it again. A later independent entry gets its
   OWN new target; it must not inherit prior entries' hedge fills.
2. Before any hedge dispatch, reserve the operation. Compute target minus the
   SUM of confirmed attributable executions across all attempts. If another
   attempt is submitting, live, pending cancellation or uncertain, hold. A
   missing refresh is not confirmation. Never replay an original full-size
   queue after a partial fill or release the operation on cancel request alone.
3. Keep both the created order and returned broker order identity. Register
   an attempt BEFORE submit; acknowledge any returned/mutated broker ID as an
   alias of that same attempt. A submit exception after possible acceptance
   keeps the reservation. A known preparation-only failure can release its
   preparation reservation safely. No blind retry of uncertain acceptance.
   **Do not query or cancel using a frozen pre-submit local UUID or an arbitrary
   member of an alias set.** LumiBot can replace/mutate `order.identifier` during
   dispatch. Keep the current returned/submitted Order object and read its
   current identifier when reconciling it. The example's
   `book.current_order_id(attempt_token)` does this; the stable attempt token
   and historical aliases are for accounting/matching, not broker lookups.
   `next(iter(aliases))` can choose the obsolete UUID and permanently block the
   repair. A new snapshot reporting an old alias must not overwrite the current
   broker lookup identity. A returned Order alone is not proof of a fill or of
   completed broker acceptance; preserve uncertain state and supported recovery.
4. Both callbacks and polling feed the SAME idempotent observer. In the pinned
   LumiBot version, sum `transaction.quantity` over `order.transactions` for
   that order's cumulative execution, then take its high-water mark. Do not
   repeatedly add that whole sum. Never cap observed fills at requested quantity:
   `min(requested, reported)` discards evidence of excess execution. Retain the
   full authoritative total and surface reconciliation for an overexecuted
   attempt even when its operation total is still below target; do not continue
   submitting or mark completion on contradictory execution evidence.
   `get_filled_quantity()` is not a supported
   Order method. Do not treat requested quantity, status alone or account
   position as actual partial quantity. Inspect the version's source if using
   another documented execution field or incremental callback quantity.
   Distinguish an absent execution field from an authoritative empty execution
   list. For a fresh native broker-confirmed terminal cancellation, an available
   `Order.transactions == []` represents zero observed executions; `sum([])` is
   a valid zero. Do not require at least one fill before acknowledging that
   canceled attempt, or an unfilled canceled replacement can never release its
   slot. Preserve the attempt's previous cumulative high-water mark and continue
   refreshing retired attempts for late fills. A failed/missing order read or
   absent/malformed execution collection remains unknown, not zero. Confirm the
   selected adapter's actual cumulative-execution contract when it differs.
5. At the start of an active operation's reconciliation, refresh EVERY
   attributable attempt, including canceled/retired ones, and feed each returned
   snapshot into the common observer BEFORE choosing an unresolved attempt or
   deciding to submit. Retaining old objects without refreshing them misses late
   executions when the provider reports them through order reads. A loop over
   only `not terminal` attempts cannot discover a canceled attempt's late fill.
   Completed operations still retain their callback attribution; this does not
   require polling every historical order forever.
   After EVERY new execution observation, including for an old canceled order,
   recompute the remainder and compare it with all unresolved live leaves.
   Cancel an excessive replacement once, keep its reservation, and wait for
   terminal confirmation. Then observe any executions from that attempt too
   before calculating the next replacement. Do not wait only for the current
   replacement to fill; that cannot undo an oversized live order.
   Reconcile the CURRENT unresolved replacement as well as archived attempts.
   Do not return from an attempts loop after reading the first old order merely
   because a different active order ID exists. That starves the replacement's
   terminal read forever. Collect each required observation before deciding
   whether to hold, resize or finish; use the same lock throughout that decision.
   Mark a cancellation request once per attempt, retain its unresolved slot,
   and continue observing that exact order until confirmation. If dispatch
   fails, retain ownership and use a bounded reconciliation/retry policy.
   An old attempt's terminal report may update its fill high-water, but may clear
   a scalar active ID ONLY if that ID actually belongs to that old attempt.
   Testing `observed_id in old_attempt.aliases` alone is tautological and can
   erase a different live replacement. Prefer deriving blockers from the
   ledger's `unresolved_tokens()` instead of maintaining a second scalar owner.
6. Complete only when the target is confirmed executed and no attempt can still
   execute. Atomically clear the active operation's entry/hedge blockers and
   resume the existing next-entry path. Retain archived attribution for late
   reports rather than crediting an earlier entry's execution to a new one.
   After a late fill, compare the SUM across every attempt with the original
   target, including after completion; no single attempt needs to exceed the
   target for their aggregate to exceed it.
   If late evidence establishes an actual overhedge, surface unresolved exposure
   and use only the user's authorized recovery policy; never invent a new
   reverse trade or silently mark it complete.

**Completion does not retire attribution.** Do not clear the only ledger or
stop observing its orders when releasing the active entry. The example's
`RetainedOperations` keeps each entry's `OperationFills` after completion and
routes an observed hedge order to its ORIGINAL operation. `claim_completion`
is once-only; a late report never completes/resumes the old entry again. A
new entry receives its own book and original target, while the old book remains
reachable. Clearing an active pointer is fine; deleting its only history is not.

Connect this observer to actual `on_partially_filled_order` AND `on_filled_order`
callbacks, before the existing option-entry logic. A canceled order's new
execution can arrive as a partial-fill callback. A comment or unused history
list does not route that callback. For example, under the SAME common owner:

Put the excess detection/report-state update INSIDE the shared observer, directly
after updating its per-attempt high-water mark and BEFORE any early return for a
completed operation. A check only in the active hedge manager never runs for
archived entries. The example's `reconciliation_required` records the old entry's
exact excess during `observe()`, independently of completion or resumption.
Connect that state to the existing diagnostic/logging path. Do not merely keep
an updated history total and then claim excess is flagged when no such flag or
report runs on the late callback path.

~~~python
@serialized_hedge_state
def _observe_owned_hedge(self, order):
    match = self.vars.hedge_operations.observe(order)
    if match is None:
        return False
    entry_id, book = match
    reported = self.vars.get("reported_hedge_excess", set())
    if book.filled > book.target and entry_id not in reported:
        self.log_message(
            f"Hedge entry {entry_id}: confirmed excess {book.filled - book.target}; "
            "requires reconciliation, no automatic compensating trade.",
            color="red",
        )
        reported.add(entry_id)
        self.vars.reported_hedge_excess = reported
    # If this is the CURRENT operation, observe/cancel excess live leaves using
    # its common owner. Never credit an archived entry's fills to the current one.
    # Do not add another completion/rescan initiator here.
    return True

def on_partially_filled_order(self, position, order, price, quantity, multiplier):
    if self._observe_owned_hedge(order):
        return
    # Preserve any pre-existing unrelated partial-fill behavior here.

def on_filled_order(self, position, order, price, quantity, multiplier):
    if self._observe_owned_hedge(order):
        return
    # Preserve the existing exact option-entry attribution/claim path here.
~~~

`self.vars` is LumiBot's `Vars`, not a dictionary: use attribute assignment
and its supported `get(name, default)`, `set(name, value)` or `all()` methods.
Do not call `self.vars.setdefault`, `update`, or `pop`, or subscript it.
An actual dictionary stored in a Vars attribute keeps its ordinary dict API.
The callback above therefore reads the retained set with `get` and writes the
attribute explicitly, including on late excess reports after completion.

Use the supported callback signatures and retained broker-ID/object matching.
Adapt this routing into complete existing methods; the comments are integration
points, not a finished replacement for their unrelated bodies. A canceled40 +
replacement60 operation can appear complete, then receive evidence that the
original actually executed60 before cancel. The old operation now has120
confirmed, not the new operation. Surface that old excess once according to the
existing reporting policy; do not invent a reverse trade, change the new entry's
target, or complete the old pair twice. No code could prevent an execution the
broker had not yet reported. Retain duplicate high-water handling. This does not
require polling every archived order every second: use received callbacks and
the existing bounded reconnect/history reconciliation path.

Preserve the existing owner of next-entry scanning. If the original iteration
reconciles hedge completion and resumes the next scan, hedge callbacks can
record fills and request excess-order cancellation without also completing and
resuming there. Adding `hedge callback -> manager -> completion -> next scan`
creates a SECOND scan initiator concurrent with the existing iteration. A lock
used only by the callback/hedge manager does not serialize the outer scan. Prefer
keeping completion/resumption in the existing iteration owner. If a callback
must initiate the next entry, every initiating path needs the same atomic entry
claim and recheck at the actual entry dispatch boundary. Do not introduce that
extra caller merely to repair cumulative quantities.

For a target of 100, original execution 40 and confirmed cancel leaves 60.
A 60 replacement is valid on that knowledge. If broker history later reports
the original actually executed 60 before cancellation, the newly known 20
invalidates the still-working 60 replacement. Cancel it, observe its confirmed
outcome, then replace only the remaining 40 if it executed nothing. Repeating
that same 60 report changes nothing. This does not require knowing a fill before
the broker supplies it. Keep execution time distinct from observation time when
interpreting logs; an order's cumulative execution ledger need not deduplicate
by timestamp when the supported quantity records already establish high-water.

Read back all saved causal methods. Trace ordinary full fills as well as partial,
cancel, delayed/duplicate reports and a SECOND independent entry. A repair that
never submits again, uses the whole-account position, counts each report again,
or retains only the newest attempt does not satisfy this request. A static
review, a compiling file or one completed trade is not execution proof.



Continuation: `references/order-quantity-accounting.part-02.md`
