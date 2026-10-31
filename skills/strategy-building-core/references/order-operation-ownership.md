> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: order-operation-ownership
description: Use when callback, polling, fallback or queue paths can submit the same obligation more than once.
---

# One owner for each order operation

## Repair mutable order identity as well as duplicate submission

Retain the exact created Order object BEFORE dispatch. In LumiBot's Schwab
adapter, `_submit_order` assigns the broker ID onto that SAME object's
`identifier` before returning. The old UUID and the current broker ID can
therefore differ with NO fill callback and NO change of operation.

Do not use `saved_id != order.identifier` as a post-submit completion guard.
That mistakes normal broker acceptance for completion and leaves the saved
UUID forever active. Guard with the original operation/attempt OBJECT (or its
immutable generation token) and its explicit completed flag. Then bind the
returned order. Poll and cancel using the retained object's CURRENT identifier;
match fill callbacks by that exact object or its known aliases. Apply this to
EVERY option and stock hedge path, not just the entry. A retained Order that
is never used by polling/callbacks does not repair the bug.

The complete `publish_hedge_attempt` / `accept_hedge_return` /
`observe_hedge_fill` / `reconcile_hedge_attempt` functions below demonstrate
these connected paths. Use their object-identity guard, not a scalar-ID
inequality substituted during adaptation. Preserve queue-leg quantity ownership
and all unrelated trading policy.

Finish the saved repair through its final readback. Save-only forbids starting
backtests, deployments or trades; it does not limit the number of necessary
file edits. A known repairable race, orphaned preparation flag or disconnected
helper is unfinished work, not a final verification disclaimer.

Preserve the original trading policy: symbols, signals, prices, quantities,
entry eligibility, cancellation/deadline/cooldown rules and session behavior.
Repair their causal ownership mechanics without substituting an example's
business rules. When the user confines edits to the existing file, keep the
controller and helpers in that file. Do not create another file. If this turn
already created an unused helper, delete ONLY that newly created unused file
with the ordinary file tool and current revision, then read back the file set.
Keep every pre-existing file and one-time dependency initialization.

This route repairs an existing coherent queue/operation. For that routing
choice, an existing entry -> hedge preparation/queue -> reconciliation ->
completion -> next-entry flow is an existing operation, even when its ID aliases,
claims or locks are defective. Incorrect synchronization does not mean that
this architecture is absent. Repair those connected methods in place. Do not
switch to the full-controller copy route merely because this operation has a
callback race; that would replace an already defined lifecycle and can leave
an unused helper beside the actual bug. Use the complete
reentrant whole-method owner below. Do not then load the separate fast-order
controller as another candidate or mix its short reservations into this owner.
If the saved architecture genuinely lacks a coherent controller, use the
separate complete tested controller with its business hooks instead; do not
invent a partial hybrid. Preserve the user's actual broker-I/O deadline policy.

## Connect all callers before editing individual branches

Read the saved code and identify the actual method names for EVERY row:

| State transition | Required common ownership |
| --- | --- |
| Next entry | Scan/reservation, order creation, all pending-field publication and submit |
| Entry fill | Exact attribution, one-time claim and hedge-operation initialization |
| Hedge preparation | Option/stock selection, fallback and queue append/pop |
| Hedge execution | Create/submit, polling, fill/cancel callbacks and queue continuation |
| Completion | All-leg completion, reset and next-entry resumption |

Initialize one process-local `threading.RLock` on the strategy instance. Copy
this tested decorator into the saved file and apply it to the existing methods
in ALL rows, including entry-scan and polling methods. A callback-only decorator
or lock only around an ID set/slot claim leaves the original race alive. The
same owner covers remaining quantity, position-based side selection, order
construction, publication and dispatch. Nested calls use the same reentrant
lock. Keep one state authority and derive legacy fields from it.

~~~python
from functools import wraps


def serialized_hedge_state(method):
    @wraps(method)
    def invoke(self, *args, **kwargs):
        with self._hedge_state_lock:
            return method(self, *args, **kwargs)
    return invoke
~~~

The lock also covers queue completion and next-entry resumption. A completion
callback and an already running scan must not both start the next entry. A stale
preparer must recheck its ORIGINAL operation under the owner; an empty slot does
not mean that its old obligation still exists. This complete generation check
is executable, and completion uses the same lock:

~~~python
def reserve_prepared_operation(self, operation, attempt):
    with self._hedge_state_lock:
        if self._current_operation is not operation:
            return False
        if operation["completed"] or operation["attempt"] is not None:
            return False
        operation["attempt"] = attempt
        return True
~~~

Claim each canonical original entry only once under that same owner. Initialize
its completed-entry history once and retain it across session resets. The
claim starts its existing operation; subsequent reconciliation continues that
operation rather than trying to claim the entry again.

~~~python
def claim_original_entry(self, entry_id):
    with self._hedge_state_lock:
        if entry_id in self._claimed_entry_ids:
            return False
        self._claimed_entry_ids.add(entry_id)
        # Initialize/publish this entry's operation here under the same owner.
        return True
~~~

## Publish before dispatch, then preserve callback completion

For ENTRY orders, perform this sequence inside the common owner:

1. Reserve the next-entry scan BEFORE quote/chain preparation or order creation.
   Preserve eligibility and pricing; the reservation is lifecycle bookkeeping.
   Every scan path must observe it, including completion-triggered resumption.
2. Before an entry identifier becomes recognizable to callbacks, publish ALL
   pending-entry fields and retain the exact created Order object. Do this
   BEFORE `submit_order`, not after it returns.
3. A fill callback atomically records the original entry's claim and hands it
   to its hedge operation once. Missing identifiers are never wildcards; match
   a retained object or a known alias of that exact entry.
4. When submit returns, bind its snapshot ONLY if the same entry is still
   current and unresolved. Never restore a pending-buy ID or overwrite fields
   after its callback already completed the handoff. A processed-entry fence
   cannot clear a pending ID that the submitter incorrectly resurrected.

Wrapping entry submission to fix this publication race is not permission to
change its signals, prices or cancellation branches. Keep unrelated original
method bodies intact, and preserve every original helper construction, cache,
deadline and scanner field in `initialize`. A daily reset omits one-time setup;
it is not a replacement initialize body.

For HEDGE preparation, reserve ownership BEFORE appending shared queue legs,
position reads or order creation. A losing claimant changes no queue state.
Keep the existing original-entry obligation available for reconciliation; its
one-time entry claim prevents duplicate initialization, not retrying a failed
preparation of that SAME operation.

Separate two error paths explicitly. If quote/position lookup or `create_order`
fails BEFORE dispatch, release that operation's preparation reservation under
its owner and preserve its unfulfilled obligation for the normal retry path.
Do not leave a processed entry plus a busy flag with no attributable attempt.
If `submit_order` may have reached the broker, retain its exact published Order
and unresolved ownership. Never clear that uncertain attempt or blindly submit
another. Finish these connected error exits before final-answering.

## Retain current hedge identity and connect its fill callback

The following identity pattern belongs INSIDE the existing operation, not in a
second ledger. Adapt names and callers; preserve the strategy's quantity and
retry owner. Its original serialized preparation method still covers queue
preparation, creation and dispatch together. Call `publish_hedge_attempt` before
submit and `accept_hedge_return` afterward. The saved attempt object is the
post-submit guard: the broker may have changed its identifier during submit,
so comparing its current ID to a pre-submit scalar is incorrect. A submit exception retains the
published attempt. This pattern does not replace the preparation-error handling
above.

Connect BOTH hedge-fill callbacks and hedge polling to this same operation.
The entry callback keeps its separate entry-attribution handoff. Do not add
these functions while leaving the old scalar-ID polling path active.
`_complete_hedge` is the existing confirmed-fill queue/quantity owner; it alone
advances legs or completes the whole operation.

~~~python
def publish_hedge_attempt(self, operation, order):
    with self._hedge_state_lock:
        if self._current_operation is not operation or operation["completed"]:
            return False
        if operation["attempt"] is not None:
            return False
        operation.update(attempt=order, accepted=None, attempt_filled=False,
                         provisional=order.identifier, aliases={order.identifier})
        return True


def accept_hedge_return(self, operation, created, returned):
    with self._hedge_state_lock:
        if self._current_operation is not operation or operation["completed"]:
            return
        if operation["attempt"] is not created or operation.get("attempt_filled"):
            return
        if returned is not None:
            operation["accepted"] = returned
            operation["aliases"].add(returned.identifier)


def observe_hedge_fill(self, operation, filled):
    with self._hedge_state_lock:
        if self._current_operation is not operation:
            return False
        retained = (operation.get("attempt"), operation.get("accepted"))
        operation.setdefault("aliases", set()).update(
            order.identifier for order in retained if order is not None)
        if not (any(filled is order for order in retained if order is not None)
                or (filled.identifier is not None
                    and filled.identifier in operation["aliases"])):
            return False
        if not operation.get("attempt_filled"):
            operation["attempt_filled"] = True
            self._complete_hedge(operation, filled)
        return True


def reconcile_hedge_attempt(self, operation):
    with self._hedge_state_lock:
        if self._current_operation is not operation or operation["completed"]:
            return
        created, accepted = operation["attempt"], operation.get("accepted")
        if created is None:
            return
        # Keep BOTH actual objects. A broker ID may appear on the original
        # created Order after submit returns, even if its return was distinct.
        identity = created.identifier
        if identity == operation["provisional"] and accepted is not None:
            identity = accepted.identifier
        operation["aliases"].update(
            order.identifier for order in (created, accepted) if order is not None)
        if identity is None:
            return  # Unresolved; retain the attempt, never blindly resubmit.
        observed = self.get_order(identity)
        if observed is not None and observed.is_filled():
            self.observe_hedge_fill(operation, observed)
~~~

Identity attribution marks only this ATTEMPT as filled. The existing quantity
owner decides whether ALL required confirmed hedge quantity is complete. It
clears the finished attempt before publishing another legitimate leg. A filled
sell-held-shares leg must not mark the original entry complete while a short-sale
remainder is queued. Terminal canceled/rejected/zero-fill is also not completion;
preserve the existing remaining-quantity retry policy.

An actual fill callback is authoritative without another broker read. Preserve
that confirmed fill over stale canceled/error reads or submit returns. Retain
BOTH actual created/returned objects and their provisional/current aliases.
Read the current retained identifier for every refresh/cancel; a submission-time
UUID can become stale after submit has returned. A missing or failed HEDGE read
remains unresolved. Preserve the original error handling and do not transplant
this hedge rule into an unrelated entry-cancellation branch.

Keep original entry identity and completion fences across daily/session resets.
An old callback must not borrow a newer entry's identity. Completion clears
only its own transient operation and permits the next qualifying entry. Scope
blocking to the strategy's actual coupled risk unit, never an invented permanent
or account-wide stop.

For partial/canceled replacements, use the complete `OperationFills` and
`RetainedOperations` reference inside the existing file. The original target
belongs to the entry across ALL attempts. Refresh retired attempts too; a late
old fill can require canceling an oversized replacement, confirming terminal
state, then resizing the remainder. Repeated reports cannot double-count fills.
An absolute account position does not prove this entry's executed quantity.
Preserve the permitted sell-held/short-rest split and every unrelated rule.

## Complete the edit and readback

Prepare the connected method changes before saving. Use one coherent atomic
patch with unique complete-method anchors, or replace the complete current file
with its fresh edit handle. Preserve unrelated bodies and constructor setup.
Read back the final saved code and trace the actual callers in the table:
reserve -> prepare -> publish -> dispatch -> observe -> complete all legs ->
resume exactly one next entry. Check the real entry-scan method, every fallback,
pre-dispatch error exit and callback/submit-return branch. A lock's definition,
one successful hedge or a broad claim of readiness is insufficient.

If an atomic patch reports ambiguity, none of that batch was saved. Choose the
intended returned match and use its exact `retryOperation` at the returned failed
operation index, retaining the other original operations. Do not guess shifted
line numbers or repeat the same ambiguous anchor. Alternatively read the current
file and replace the complete corrected file. Repair syntax and then continue
the behavioral change; a recoverable save error is not an authorization blocker.

Before ending, correct any missing connection or newly introduced unused file.
Unknown static readiness alone does not establish a missing code repair, and
static readiness PASS does not prove runtime execution. Report the actual saved
change and its verification limits truthfully. Do not claim a reproduction,
backtest, live fill or deployment that the author did not perform. A supplied
synthetic baseline may be attributed as reported, with its original limits.


## Retained release integration requirements

When a user asks to fix slow trading and the saved file exposes concrete order
ownership, cancel or scan defects, repair those defects while preserving the
existing cadence and trading policy. An unspecified desired trade frequency
does not block that authorized repair. Ask about a different frequency only
if the requested fix actually requires changing the trading policy.

For a connected multi-method repair, prepare the complete corrected current
file and use `replace_file` with its fresh handle. This preserves the original
methods without a chain of fragile substring edits. If an atomic patch is
rejected, none of its changes exist: after reading the current file, finish the
complete replacement rather than ending with the known defect still saved.

Before that save, audit these connected transitions in the actual final file:


The submitted Order is mutable: the broker may replace its identifier on the
same object, including after `submit_order` returns. Comparing
`returned.identifier` with `original.identifier` then compares two aliases,
not the accepted ID with the provisional value. Capture the provisional scalar
before submission and retain the actual Order reference for this operation.
Before each later broker lookup, reconcile its current identifier under the
same owner and query that current ID. Bind provisional/current aliases to the
same retained operation for callback matching; do not repeatedly query a stale
UUID and mistake its absence for an unresolved broker outage. The existing
`OperationFills.current_order_id` example demonstrates this dynamic identity.


Preserve the existing confirmed-fill handler's complete entry-state transition
when sharing it with callbacks. Starting the hedge must also consume that
entry's pending ID, asset and deadline; adding a parallel initializer that
leaves them active lets polling rediscover the same filled order after completion.
Retire matching active pointers once, without clearing a newer entry. Retain
the original operation and its cumulative fills for late reconciliation, but
do not reactivate a completed operation or repeat completion bookkeeping when
its old callback or filled-order snapshot is observed again. Trace completion
through a subsequent independent qualifying entry, not only the first hedge.


A fallback preparer or submitter must also return when it has no originating
entry operation. After completion clears the active pointer, checking only
`active_id in completed_ids` does not fence a late request: the active ID is now
None. Carry the initiating entry's identity into the shared owner, look up that
retained operation, and reject absent or completed obligations before preparing
the queue. Do not substitute a newer active entry for the request's original
entry. Preserve the distinct next entry and every legitimate remaining hedge leg.

The NEXT entry needs its own atomic scan/submission reservation too. A callback
and an iteration must not both pass the "no pending entry" check while the first
is still scanning or waiting for submit to return. Claim before that work under
the existing shared owner; release on a confirmed no-order/pre-dispatch failure,
and retain the owned pending Order through uncertain dispatch. Publish all
pending fields together and preserve callback completion when submit returns.
Keep the existing trading eligibility rules; do not permit an extra concurrent
entry merely because hedge completion has cleared its own fields.

An entry callback is only one caller. Before editing, list every path that can
prepare a hedge, append or pop its queue, claim a submission, clear an order ID,
mark completion, or resume entries. Polling and fallback helpers are callers too.
An existing processed-entry-ID set is a valid per-entry claim when its check
and add, the complete shared initializer and every continuation/completion path
use the same state owner, and the claim is not cleared before the obligation
settles. A second dictionary, registry class or new persistence system is not
required just to rename that existing record. Check the actual callers before
claiming a completed saved repair still lacks a per-entry record; identify a
reachable bypass or lost claim, not merely the absence of another container.
Changing only the callback's processed-ID set still does not protect those other paths.

Trace the winning path as well as duplicate rejection: idle → claim → prepare
→ submit → observe → complete → next independent entry. If a caller sets
`preparing` and then calls a helper that rejects every `preparing` operation,
the winner blocks itself. Acquire the reservation once and pass its operation
identity into the helper that continues it, or let that helper alone claim it.
The same owner must protect queue publication: claim before appending shared
legs. A losing caller leaves the queue unchanged. An entry-ID guard around
only the callback cannot repair a queue that fallback or polling mutates first.

For an operation with a shared hedge queue, prefer one reentrant lock around
the existing state-changing methods as the simplest complete repair. Preserve
their trading behavior; do not add separate competing claim/state machines to
each caller. This supported Python pattern serializes the entire transition:

Protecting only a submission helper leaves the other mutations unprotected. In particular,
clearing the hedge ID/queue and publishing an idle stage must remain protected
through retirement of the old entry and the completion/resume call. Returning
from a lock before calling completion exposes the old filled entry to another
iteration. Both regular iteration and immediate resumed scans must use the same
entry reservation before submission; broker snapshots cannot reserve that slot.

Include existing lifecycle reset hooks in that audit. In live execution the
framework drains fill/cancel callbacks on a separate queue thread; its lifecycle
decorator is not a shared state lock. If `before_market_opens` or another hook
resets hedge identifiers, submission flags, retained operations or fill claims,
protect that complete transition with the same instance lock. A copy of retained
claims, reset, and restore must be one critical section; copying outside the
lock can lose a callback's intervening claim. Do not recreate the lock during a
daily reset. A new date does not prove an owned order or hedge obligation is
terminal: keep its blocker, identity and reconciliation state until resolved,
while preserving the strategy's ordinary reset policy for settled state.

Start the integration at the SHARED confirmed-entry-fill handler itself.
Protect its lookup/create/publication of the per-entry operation AND assignment
of the active-operation pointer with this same owner, before it starts a hedge.
A callback's outer lock does not protect the resident monitor's direct call to
that handler. Protect the original-entry check-and-add there too, or in a shared
claim helper used by every caller. A lock only around replacement submission
cannot stop a competing initializer from replacing the operation while an
attempt is being appended. Prefer decorating these existing causal methods so
their complete current bodies remain intact; do not add an unrelated engine.
On final readback, trace callers INTO each state-mutating method. Verify the
callee itself is protected or EVERY caller supplies the same owner, including
the iteration monitor, callback, terminal handler and fallback. The presence of
a new lock somewhere in the file is not this audit.

In particular, keep queue-pop, clearing the active hedge ID, completion and
entry resumption in one protected transition. A late preparer must not observe
an empty queue and cleared ID before completion is recorded, rebuild the queue,
and hedge an already completed entry. Recheck the current entry/operation INSIDE
the protection instead of trusting an earlier caller's phase observation. An
old callback must not borrow a newer entry's identity.

The entry-submission path owns shared state too. Publish its entry identity and
active-entry pointer together under the same lock BEFORE a callback can observe
that identity. A fill callback can run inside or immediately after submission.
When the broker returns, rebind any returned identifier under that owner only
if the same operation is still pending; never set an active-entry pointer again
after the callback completed and cleared it. Keep original-ID aliases for late
callbacks, but use the accepted returned ID as the canonical operation key.
Audit this submit/accept transition alongside queue and fallback transitions;
locking only hedge methods cannot prevent a completed entry being reactivated.


Integrate new state into the strategy's EXISTING `initialize`: initialize every
new set, dictionary, pointer and instance lock before its first callback or
iteration can use it. A daily reset hook is not initialization. Preserve the
existing initialization and unrelated methods. Read back `initialize`, reset
hooks and every new state's readers/writers together. A submission followed by
an AttributeError can leave a real order accepted without its blocker; publish
the complete initialized operation before submission, not after fallible setup.

## Boundaries and proof

Keep preparation, submission and confirmed completion distinct. A submitted,
missing, rejected or cancel-pending order does not fulfill the obligation.
An order's client identifier may change when submission assigns its broker
identifier. Keep the submitted Order object and operation generation linked:
an identifier change on that same attempt is not evidence of a newer order.
Do not abandon the accepted broker ID because it differs from the provisional
ID stored before submit. Retain the created/returned Order object as the attempt's
lookup owner; read its CURRENT `identifier` for each refresh/cancel. Saving only
`self.vars.order_id = order.identifier` before/after `submit_order` can still go
stale when native asynchronous submission assigns the broker ID later. Keep
historical IDs only as aliases for attribution, never as the current lookup
source. A callback for the same object may supply its new ID before submit
returns; recognize that object/attempt instead of rejecting the callback as an
unrelated ID. Conversely, do not overwrite completion or another operation
observed by a callback while submit was in flight. Trace both cases.

A terminal hedge status does not establish zero fills. Preserve the existing
retry policy; before any whole-leg retry, verify the authoritative terminal
order's actual filled quantity is exactly zero. Missing quantity is unknown,
not zero. For a partial fill, retain the claim and account for the already
filled quantity through the operation ledger; never clear the claim and resubmit
the full queued leg. A log message calling a terminal order "zero-fill" is not
that check. If safe remaining-quantity recovery is unavailable, retain a visible
blocked obligation rather than silently overhedging or enabling new entries.
Retain the exact original entry identity, legitimate remaining legs and the
original order duration, quantities, expiry, pricing and basket policies.
Completion of one operation must not prevent the next qualifying entry.
A duplicate callback for a completed entry must not borrow a later entry's state.
