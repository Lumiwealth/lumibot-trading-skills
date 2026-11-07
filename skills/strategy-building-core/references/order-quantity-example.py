# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Retained accounting plus its normal Strategy/Vars integration.

Integrate both OperationFills and RetainedOperations inside the existing owner.
Keep the registry for the strategy lifetime, including after active work clears.
The caller serializes registration, observation, submit and completion together.
OperationFills/RetainedOperations are IO-free. StrategyOrderLedger at the end
wires them to ordinary reads/submission; it adds no trading policy or retry.
"""
from decimal import Decimal, InvalidOperation
from threading import RLock
from types import SimpleNamespace
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
    leg: int | None


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
        self._legs: tuple[tuple[Any, Decimal], ...] | None = None

    @property
    def legs_prepared(self) -> bool:
        return self._legs is not None

    def prepare_legs(self, legs: list[tuple[Any, Any]]) -> None:
        """Keep the caller's original side allocation, independently of fill state."""
        if self.legs_prepared:
            return
        prepared = tuple((side, quantity(target)) for side, target in legs)
        if not prepared or sum((target for _, target in prepared), Decimal(0)) != self.target:
            raise ValueError("Leg targets must cover the original operation")
        if self.attempts:
            raise ValueError("Prepare the allocation before registering an attempt")
        self._legs = prepared

    def _leg_filled(self, index: int) -> Decimal:
        return sum((a["filled"] for a in self.attempts if a["leg"] == index), Decimal(0))

    def _next_leg(self) -> tuple[int, Any, Decimal] | None:
        if self._legs is None:
            raise ValueError("Original side allocation has not been prepared")
        for index, (side, target) in enumerate(self._legs):
            remaining = min(max(Decimal(0), target - self._leg_filled(index)), self.remaining)
            if remaining > 0:
                return index, side, remaining
        return None

    def next_leg(self) -> tuple[Any, Decimal] | None:
        """Select a permitted leg only when the common operation allows dispatch."""
        if self.next_step()["action"] != "submit":
            return None
        leg = self._next_leg()
        return (leg[1], leg[2]) if leg is not None else None

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
        attempt_excess = sum((max(Decimal(0), a["filled"] - a["requested"])
                              for a in self.attempts), Decimal(0))
        leg_excess = sum((max(Decimal(0), self._leg_filled(i) - target)
                          for i, (_, target) in enumerate(self._legs or ())), Decimal(0))
        return max(attempt_excess, leg_excess)

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
        leg_index = None
        if self.legs_prepared:
            leg = self._next_leg()
            side = getattr(order.side, "value", order.side)
            if (leg is None or requested > leg[2]
                    or side != getattr(leg[1], "value", leg[1])):
                raise ValueError("Order must satisfy the current original allocation leg")
            leg_index = leg[0]
        self.attempts.append({"objects": [order], "aliases": {str(order.identifier)},
                              "requested": requested, "filled": Decimal(0),
                              "terminal": False, "order": order, "lookup_order": order,
                              "cancel_requested": False, "provisional_id": str(order.identifier),
                              "leg": leg_index})
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
    Read an existing entry with get(); only for_entry() creates an operation.
    """

    def __init__(self) -> None:
        self.operations: dict[str, OperationFills] = {}
        self.completion_claims: set[str] = set()
        self.reconciliation_required: dict[str, Decimal] = {}

    def get(self, entry_id: str) -> OperationFills | None:
        """Read retained history without creating an entry or changing its target."""
        return self.operations.get(entry_id)

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


class StrategyOrderLedger:
    """Wire the accounting above to normal Strategy APIs and managed Vars.

    Save this complete file in the strategy; this is not an SDK import.
    initialize: self.order_ledger = StrategyOrderLedger.for_strategy(self)
    iteration: refresh() before interpreting fills()/pending() and entry risk
    submission: order_ledger.submit(self.create_order(...))
    partial/full/cancel callback: order_ledger.observe(order)

    This owner records attempts, not signals, exposure limits or trade policy.
    A successful submit is not a fill; False from refresh means unresolved
    broker evidence. Callers retain exit intent and defer affected new entries.
    fills() includes original asset/side and actual cumulative quantity. Match
    that full asset identity with normal LumiBot Asset APIs when sizing or
    comparing account holdings. Never adopt an unrelated account position.
    """

    @classmethod
    def for_strategy(cls, strategy: Any, state_name: str = "owned_order_attempts") -> "StrategyOrderLedger":
        state = strategy.vars.get(state_name)
        if state is None:
            state = {"next_id": 0, "operations": {}}
        if not isinstance(state, dict):
            raise ValueError("Order accounting requires plain managed state")
        return cls(strategy, state_name, state)

    def __init__(self, strategy: Any, state_name: str, state: dict[str, Any]) -> None:
        self.strategy, self.state_name = strategy, state_name
        self.lock = RLock()
        self.registry = RetainedOperations()
        self.metadata: dict[str, dict[str, Any]] = {}
        self.next_id = int(state.get("next_id", 0))
        for key, saved in state.get("operations", {}).items():
            operation = self.registry.for_entry(key, saved["target"])
            self.metadata[key] = {"asset": saved["asset"], "side": saved["side"]}
            for item in saved["attempts"]:
                # A checkpoint reference is only a lookup selector. It carries
                # no invented broker status or executions; refresh reads those.
                lookup = SimpleNamespace(identifier=item["current_id"])
                operation.attempts.append({
                    "objects": [lookup], "aliases": set(item["aliases"]),
                    "requested": quantity(item["requested"]),
                    "filled": quantity(item["filled"]),
                    "terminal": bool(item["terminal"]),
                    "order": lookup, "lookup_order": lookup,
                    "cancel_requested": bool(item.get("cancel_requested", False)),
                    "provisional_id": item["provisional_id"], "leg": None,
                })
        self._checkpoint()

    def _checkpoint(self) -> None:
        operations = {}
        for key, operation in self.registry.operations.items():
            attempts = []
            for token, attempt in enumerate(operation.attempts):
                try:
                    current = operation.current_order_id(token)
                except ValueError:
                    current = None  # Unknown selector, never permission to free the attempt.
                attempts.append({
                    "current_id": current, "aliases": sorted(attempt["aliases"]),
                    "requested": str(attempt["requested"]),
                    "filled": str(attempt["filled"]), "terminal": attempt["terminal"],
                    "cancel_requested": attempt["cancel_requested"],
                    "provisional_id": attempt["provisional_id"],
                })
            operations[key] = {**self.metadata[key], "target": str(operation.target),
                               "attempts": attempts}
        self.strategy.vars.set(self.state_name, {"next_id": self.next_id, "operations": operations})

    def submit(self, order: Any, operation_id: str | None = None) -> Any:
        """Register before dispatch; an unknown dispatch never frees ownership."""
        with self.lock:
            if operation_id is None:
                while f"owned-{self.next_id}" in self.registry.operations:
                    self.next_id += 1
                operation_id = f"owned-{self.next_id}"
                self.next_id += 1
            metadata = {"asset": order.asset.to_dict(),
                        "side": str(getattr(order.side, "value", order.side))}
            if operation_id in self.metadata:
                from lumibot.entities import Asset
                original = self.metadata[operation_id]
                if Asset.from_dict(original["asset"]) != order.asset or original["side"] != metadata["side"]:
                    raise ValueError("A replacement must retain its original asset and side")
            operation = self.registry.for_entry(operation_id, order.quantity)
            token = operation.register(order)
            self.metadata[operation_id] = metadata
            self._checkpoint()
            try:
                returned = self.strategy.submit_order(order)
                operation.accepted(token, returned if returned is not None else order)
                return returned
            finally:
                # Includes synchronous callbacks and an ID changed just before
                # a connection error. No automatic second submit occurs here.
                self._checkpoint()

    def observe(self, order: Any) -> bool:
        with self.lock:
            matched = self.registry.observe(order)
            if matched is None:
                return False
            self._checkpoint()
            return True

    def refresh(self) -> bool:
        """Query canonical IDs only; missing evidence retains pending attempts."""
        with self.lock:
            known = True
            for operation in self.registry.operations.values():
                for token in operation.unresolved_tokens():
                    try:
                        current = operation.current_order_id(token)
                        observed = self.strategy.get_order(current)
                        if observed is None:
                            known = False
                            continue
                        operation.accepted(token, observed)
                        self.registry.observe(observed)
                    except Exception as exc:
                        known = False
                        self.strategy.log_message(f"Owned order read unresolved: {exc}")
            self._checkpoint()
            return known

    def fills(self) -> list[dict[str, Any]]:
        """Actual quantities, including excess; the caller decides position policy."""
        with self.lock:
            return [{"operation_id": key, **self.metadata[key], "quantity": operation.filled}
                    for key, operation in self.registry.operations.items() if operation.filled > 0]

    def pending(self) -> list[dict[str, Any]]:
        with self.lock:
            pending = []
            for key, operation in self.registry.operations.items():
                for token in operation.unresolved_tokens():
                    attempt = operation.attempts[token]
                    try:
                        current = operation.current_order_id(token)
                    except ValueError:
                        current = None
                    pending.append({"operation_id": key, "token": token, **self.metadata[key],
                                    "order_id": current, "requested": attempt["requested"],
                                    "filled": attempt["filled"]})
            return pending
