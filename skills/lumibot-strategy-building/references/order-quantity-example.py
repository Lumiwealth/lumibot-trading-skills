# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""IO-free example: one operation's fills across multiple order attempts.

Adapt inside the strategy's existing state owner, not as a replacement strategy.
The caller serializes registration, observation, submit and completion together.
No broker read, trading policy, automatic retry or order submission occurs here.
"""
from decimal import Decimal, InvalidOperation
from typing import Any, Literal, TypedDict


def quantity(value: Any) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Invalid execution quantity") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Invalid execution quantity")
    return result


def long_position_quantity(value: Any) -> Decimal:
    """Long inventory available to sell; signed positions are not fill quantities."""
    try:
        signed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Invalid position quantity") from exc
    if not signed.is_finite():
        raise ValueError("Invalid position quantity")
    return max(Decimal(0), signed)


held_long_quantity = long_position_quantity


class Attempt(TypedDict):
    objects: list[Any]
    aliases: set[str]
    requested: Decimal
    filled: Decimal
    terminal: bool
    order: Any
    lookup_order: Any
    cancel_requested: bool
    provisional_id: str


class Step(TypedDict):
    action: Literal["submit", "cancel", "wait", "complete", "reconcile"]
    token: int | None
    quantity: Decimal


class OperationFills:
    def __init__(self, target: Any) -> None:
        self._target = quantity(target)
        if self.target <= 0:
            raise ValueError("Target must be positive")
        self.attempts: list[Attempt] = []

    @property
    def target(self) -> Decimal:
        return self._target

    @property
    def filled(self) -> Decimal:
        return sum((a["filled"] for a in self.attempts), Decimal(0))

    @property
    def remaining(self) -> Decimal:
        return max(Decimal(0), self.target - self.filled)

    @property
    def execution_excess(self) -> Decimal:
        return sum((max(Decimal(0), a["filled"] - a["requested"])
                    for a in self.attempts), Decimal(0))

    @property
    def complete(self) -> bool:
        return (self.execution_excess == 0 and self.filled == self.target
                and all(a["terminal"] for a in self.attempts))

    def _attempt(self, order: Any) -> Attempt | None:
        identifier = str(order.identifier) if order.identifier is not None else None
        return next((a for a in self.attempts if any(o is order or (
                         identifier is not None and o.identifier is not None
                         and str(o.identifier) == identifier) for o in a["objects"])
                     or identifier is not None and identifier in a["aliases"]), None)

    def register(self, order: Any) -> int:
        if self.execution_excess:
            raise ValueError("Observed execution requires reconciliation before another attempt")
        if self._attempt(order) is not None:
            raise ValueError("Attempt is already registered")
        if any(not a["terminal"] for a in self.attempts):
            raise ValueError("Prior attempt remains unresolved")
        requested = quantity(order.quantity)
        if order.identifier is None or not 0 < requested <= self.remaining:
            raise ValueError("Untrackable or excessive replacement quantity")
        self.attempts.append({"objects": [order], "aliases": {str(order.identifier)},
                              "requested": requested, "filled": Decimal(0),
                              "terminal": False, "order": order, "lookup_order": order,
                              "cancel_requested": False, "provisional_id": str(order.identifier)})
        return len(self.attempts) - 1

    def accepted(self, token: int, returned_order: Any) -> None:
        # One stable local token survives broker assignment/mutation of its ID.
        # It is not a second attempt and must not create a second fill bucket.
        attempt = self.attempts[token]
        if returned_order.identifier is None:
            raise ValueError("Acceptance remains untrackable; retain reservation")
        other = self._attempt(returned_order)
        if other is not None and other is not attempt:
            raise ValueError("Broker identity belongs to another attempt")
        attempt["aliases"].add(str(returned_order.identifier))
        if not any(o is returned_order for o in attempt["objects"]):
            attempt["objects"].append(returned_order)
        # A callback may already have observed the broker-assigned identity.
        # A stale synchronous return is still an attribution alias, never a
        # reason to downgrade that canonical lookup or reopen completion.
        current_id = attempt["lookup_order"].identifier
        stale_return = (str(returned_order.identifier) == attempt["provisional_id"]
                        and current_id is not None
                        and str(current_id) != attempt["provisional_id"])
        if not stale_return:
            attempt["lookup_order"] = returned_order
            if not attempt["terminal"]:
                attempt["order"] = returned_order

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

    def observe(self, order: Any) -> bool:
        attempt = self._attempt(order)
        if attempt is None:
            return False
        # Pinned LumiBot Order.transactions contains execution quantities.
        # These are cumulative records for this order, not a fresh delta each read.
        reported = sum((quantity(fill.quantity) for fill in order.transactions), Decimal(0))
        # Record authoritative evidence even when it exceeds the request. Never
        # clamp it away; next_step surfaces reconciliation instead of trading on.
        attempt["filled"] = max(attempt["filled"], reported)
        attempt["order"] = order
        if order.identifier is not None:
            attempt["aliases"].add(str(order.identifier))
        status = getattr(order.status, "value", order.status)
        # A stale working report cannot reopen an already confirmed terminal attempt.
        attempt["terminal"] |= status in {"fill", "canceled", "expired", "error"}
        return True

    def excess_live_orders(self) -> list[Any]:
        # Newly observed fills for a retired attempt can invalidate a replacement.
        # Dispatch cancel; do not resize in place or replace until terminal confirmed.
        return [a["lookup_order"] for a in self.attempts if not a["terminal"]
                and (self.execution_excess > 0
                     or a["requested"] - a["filled"] > self.remaining)]

    def unresolved_tokens(self) -> list[int]:
        # An old terminal observation never releases another attempt's slot.
        # In particular, cancel_requested remains unresolved until confirmed.
        return [i for i, a in enumerate(self.attempts) if not a["terminal"]]

    def request_cancel(self, token: int) -> bool:
        attempt = self.attempts[token]
        if attempt["terminal"] or attempt["cancel_requested"]:
            return False
        attempt["cancel_requested"] = True
        return True

    def cancel_dispatch_failed(self, token: int) -> None:
        # A failed dispatch permits a bounded retry, never another submission.
        # Whether broker acceptance was uncertain still needs reconciliation.
        self.attempts[token]["cancel_requested"] = False

    def next_step(self) -> Step:
        # Call after observing all required attempts under the SAME state owner.
        # No mutable "remaining queue" exists: every decision derives from the
        # original target minus confirmed cumulative fills, exactly once.
        for token in self.unresolved_tokens():
            attempt = self.attempts[token]
            if ((self.execution_excess > 0
                    or attempt["requested"] - attempt["filled"] > self.remaining)
                    and not attempt["cancel_requested"]):
                return {"action": "cancel", "token": token, "quantity": Decimal(0)}
        if self.unresolved_tokens():
            return {"action": "wait", "token": None, "quantity": Decimal(0)}
        if self.filled > self.target or self.execution_excess > 0:
            return {"action": "reconcile", "token": None, "quantity": Decimal(0)}
        if self.complete:
            return {"action": "complete", "token": None, "quantity": Decimal(0)}
        return {"action": "submit", "token": None, "quantity": self.remaining}


class RetainedOperations:
    """Retain attribution after completion; caller owns locking and trading policy.

    Completing an entry releases its active slot, not its fill history. Callback
    observers use this registry even when another entry is active. It performs
    no historical polling, submission, compensation, or automatic completion.
    """

    def __init__(self) -> None:
        self.operations: dict[str, OperationFills] = {}
        self.completion_claims: set[str] = set()
        self.reconciliation_required: dict[str, Decimal] = {}

    def for_entry(self, entry_id: str, target: Any) -> OperationFills:
        # A duplicate original-entry callback cannot reset its immutable target.
        if entry_id not in self.operations:
            self.operations[entry_id] = OperationFills(target)
        return self.operations[entry_id]

    def observe(self, order: Any) -> tuple[str, OperationFills] | None:
        for entry_id, operation in self.operations.items():
            if operation.observe(order):
                # Run on EVERY matched observation, including completed entries.
                # Merely archiving a higher fill total silently loses the alert.
                excess = max(operation.filled - operation.target, operation.execution_excess)
                if excess > 0:
                    self.reconciliation_required[entry_id] = excess
                return entry_id, operation
        return None

    def claim_completion(self, entry_id: str) -> bool:
        if entry_id in self.completion_claims:
            return False
        if not self.operations[entry_id].complete:
            return False
        self.completion_claims.add(entry_id)
        return True
