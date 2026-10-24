# One owner for each order operation

Use when competing callback, polling, fallback or queue paths can submit the
same obligation (for example a hedge for one entry) more than once.

Preserve the strategy's existing trading policy. Repair every responsible path
for the same obligation; do not replace the whole strategy with a template.
This reference is about shared state ownership, not partial-fill replacement
arithmetic (see `references/order-quantity-accounting.md`), a deadline
controller (see `fast-lumibot-strategies`) or a new trading signal.

## Find every owner first

An entry fill callback is only one caller. Before editing, list every path that
can prepare a hedge, append to or pop its queue, claim a submission, clear an
order id, mark completion or resume entries. Polling and fallback helpers are
callers too. Changing only the callback's processed-id set does not protect
those other paths.

## Serialize the whole state transition

For an operation with a shared hedge queue, a simple Python pattern preserves
existing method bodies while serializing their state changes:

```python
from functools import wraps


def serialized_hedge_state(method):
    @wraps(method)
    def invoke(self, *args, **kwargs):
        with self._hedge_state_lock:
            return method(self, *args, **kwargs)
    return invoke
```

Initialize one process-local `threading.RLock` for that risk unit in
`initialize`. A lock is runtime-only and not serializable, so it does not belong
in `self.vars`; a distinctive private attribute such as
`self._hedge_state_lock` is the narrow exception to the "no attributes on self"
rule (never a framework-like name such as `self._lock` or `self.name`).
Apply the same serialization to ALL owners of the state: entry-fill claim and
initialization, hedge selection, fallback preparation, queue continuation and
reconciliation, and completion and reset. Nested calls reuse the same reentrant
lock. Decorating only `on_filled_order`, only an initial claim helper, or only
the submit call leaves the other mutations unprotected.

Keep queue pop, clearing the active hedge id, completion and entry resumption
in one protected transition. Otherwise a late preparer can see an empty queue
and a cleared id before completion is recorded, rebuild the queue and hedge an
entry that is already complete. Recheck the current entry inside the protection
instead of trusting an earlier observation. An old callback must not borrow a
newer entry's identity.

If holding a lock across slow work would starve another deadline, use a short
atomic reservation instead: compute a private proposal, then under the same
owner recheck the operation identity or generation and publish once. Serialize
completion with that publication too. The losing path discards its proposal and
never leaves extra shared queue entries. Preserve legitimate remaining legs,
such as selling held stock before shorting the balance.

## Boundaries

- Keep preparation, submission and confirmed completion distinct. A submitted,
  missing, rejected or cancel-pending order does not fulfill the obligation.
- Keep the original entry identity, legitimate remaining legs and the original
  order duration, quantities, expiry, pricing and basket policies.
- Completing one operation must not block the next qualifying entry. A
  duplicate callback for a completed entry must not borrow a later entry's
  state.
- Use supported LumiBot calls already in the strategy. Check
  `lumibot-api-reference` or the LumiBot source for any timing or API fact you
  are unsure of. Do not invent framework methods.

## Proof

Read back the final saved functions and trace callback, polling, fallback and
queue continuation through the same protected owner, not just the existence of
a lock. Then run the saved code against competing paths and a following
independent entry. A lock's presence or one successful hedge does not prove the
repair. If a patch fails as ambiguous, use the current saved function with
unique surrounding context and finish the repair; never describe an unsaved
guard as implemented.
