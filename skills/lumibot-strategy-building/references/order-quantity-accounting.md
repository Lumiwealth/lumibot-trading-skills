# Quantity belongs to the operation, not its current order

Use for overfills, partial or canceled hedge replacements, repeated fill
observations, or late executions across several order attempts.

Read the complete saved implementation (and its saved Rules, if any) first. Preserve its signal,
basket, target per NEW entry, prices, duration and deadline policies. Repair all
paths that submit, reconcile, cancel and complete the affected operation.
Load `references/order-operation-ownership.md` BEFORE writing the repair and
apply its common atomic owner to the quantity repair as well.

## Save the complete causal edit

Prepare the complete changed methods before saving. An initialization field,
lock wrapper or comment is scaffolding, not a quantity repair. Prefer one atomic
patch replacing all causal methods with unique full-method anchors. If a patch
fails, re-read the current file and finish the complete save;
do not leave only scaffolding in place and stop because the larger edit remains.
Inspect the executable bodies after saving, including every terminal branch.

Initialization and session-reset code often repeat the same state assignments.
For adding initialization state, a unique `def initialize(self):` declaration
is a better insertion anchor than a block of assignments repeated in another
method. Copy that exact declaration/indentation from the current readback and
preserve the rest of its body. For replacing logic, anchor the whole actual
method from its unique declaration through the next method boundary. Do not
guess line numbers or try successively larger fragments of the same repeated
assignments. If that remains impractical, use `replace_file` with the COMPLETE
corrected current file and a fresh edit handle, preserving all unrelated bytes.
An ambiguous or mismatched text anchor is a recoverable edit mistake, not an
permission or platform blocker. Finish the save and final readback; a correct
diagnosis alone does not finish it.

An account position is NOT this entry's executed hedge quantity. It can include
earlier entries, another bot, manual trades or a stale snapshot. Never declare
this operation complete or size its replacement from an absolute account
position. Use positions only for the existing permitted split between selling
held shares and shorting the rest, after computing the operation remainder.

Create one operation tied to the exact original entry identity. Its target is
the original requested exposure for that entry. Keep EVERY attributable order
attempt, its stable local identity, broker-ID aliases, submitted quantity and
confirmed execution high-water mark, including retired/canceled attempts.
Do not use the currently active order as the operation identity. A replacement
is another attempt at the SAME target, never a new target.

Load `references/order-quantity-example.py` for an executable, IO-free accounting
example. Adapt its state to the existing strategy; do not paste a second trading
engine or rewrite unrelated selection/entry logic. All readers/writers that can
submit or complete share the same lock/reservation owner. A read-only identity
gate outside that owner is not itself quantity synchronization; recheck the
current operation inside it before changing quantities or submitting.

Use ONE quantity owner. The example's read-only `target`, per-attempt high-water
marks and `next_step()` derive submit/cancel/wait/complete from the same ledger.
Copy/adapt that tested algorithm inside the saved strategy if useful; do not
import the reference file as a module; it is not shipped with the strategy. Remove obsolete full-size/remainder queue
arithmetic for this operation when adopting the ledger. In particular, never
subtract cumulative fills from an already reduced queue value: after target 100,
fill 40 and replacement 60, a late original cumulative 60 leaves 40, not
`mutated_queue 60 - total_filled 60 = 0`. Repeated reconciliation of unchanged
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
4. Both callbacks and polling feed the SAME idempotent observer. In the LumiBot versions this was
   written against, sum `transaction.quantity` over `order.transactions` for
   that order's cumulative execution, then take its high-water mark. Do not
   repeatedly add that whole sum. `get_filled_quantity()` is not a supported
   Order method. Do not treat requested quantity, status alone or account
   position as actual partial quantity. Check your installed version's source before
   relying on this or on another documented execution field or incremental callback quantity.
5. After EVERY new execution observation, including for an old canceled order,
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
   If late evidence establishes an actual overhedge, surface unresolved exposure
   and use only the user's chosen recovery policy; never invent a new
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

```python
@serialized_hedge_state
def _observe_owned_hedge(self, order):
    match = self.vars.hedge_operations.observe(order)
    if match is None:
        return False
    entry_id, book = match
    if book.filled > book.target:
        self.log_message(
            f"Hedge entry {entry_id}: confirmed excess {book.filled - book.target}; "
            "requires reconciliation, no automatic compensating trade.",
            color="red",
        )
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
```

Use the supported callback signatures and retained broker-ID/object matching.
Adapt this routing into complete existing methods; the comments are integration
points, not a finished replacement for their unrelated bodies. A canceled 40 plus
replacement 60 operation can appear complete, then receive evidence that the
original actually executed 60 before cancel. The old operation now has 120
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
