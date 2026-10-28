# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Reference source to include inside a fixed-rule strategy, not an SDK import.

The caller owns signal timing and target selection. This owner finishes accepted
allocation work between signal dates, using actual positions and confirmed cash.
"""
import math
from typing import Any, Callable


class AllocationReconciler:
    def __init__(self, strategy: Any, assets: dict[str, Any], maximum_buy_price: Callable[[Any], float], *, fee_fraction: float, lock: Any) -> None:
        self.strategy = strategy
        self.assets = assets
        self.maximum_buy_price = maximum_buy_price
        self.fee_fraction = float(fee_fraction)
        if not math.isfinite(self.fee_fraction) or self.fee_fraction < 0:
            raise ValueError("Invalid configured buy fee")
        self.lock = lock
        self.publishing = False
        self.orders: dict[str, Any] = {}
        saved = getattr(strategy.vars, "allocation_intent", None)
        if saved is None:
            saved = {"generation": None, "dollars": {}, "quantities": {}, "order_ids": [],
                     "cancel_requested": [], "replacement": False, "uncertain_id": None}
            strategy.vars.allocation_intent = saved
        self.book = saved

    def accept(self, weights: dict[str, float], generation: str) -> None:
        with self.lock:
            if generation == self.book["generation"]:
                return  # Do not move the target on each price observation.
            if set(weights) - set(self.assets):
                raise ValueError("Unknown allocation asset")
            values = {key: float(value) for key, value in weights.items()}
            if any(not math.isfinite(value) or value < 0 for value in values.values()) or sum(values.values()) > 1:
                raise ValueError("Invalid long-only allocation")
            equity = float(self.strategy.get_portfolio_value())
            if not math.isfinite(equity) or equity <= 0:
                raise ValueError("Missing current portfolio value")
            # The target includes a known fee reserve, not expected sale proceeds.
            budget = equity / (1 + self.fee_fraction)
            dollars = {key: budget * values.get(key, 0) for key in self.assets}
            quantities = {}
            for key, asset in self.assets.items():
                if dollars[key] == 0:
                    quantities[key] = 0
                    continue
                price = float(self.maximum_buy_price(asset))
                if not math.isfinite(price) or price <= 0:
                    raise ValueError("Missing allocation valuation")
                quantities[key] = math.floor(dollars[key] / price)
            # Freeze this operation's target units. Later price drift is not a
            # new scheduled rebalance; a new generation accepts new targets.
            self.book.update(generation=generation, dollars=dollars,
                quantities=quantities, replacement=bool(self.book["order_ids"]))

    def _bind(self, identity: str, order: Any) -> str:
        if order.identifier is None:
            raise ValueError("Accepted allocation order has no broker identity")
        current = str(order.identifier)
        self.orders[current] = order
        if current != identity:
            self.orders.pop(identity, None)
            self.book["order_ids"] = [current if key == identity else key
                                      for key in self.book["order_ids"]]
            self.book["cancel_requested"] = [current if key == identity else key
                                             for key in self.book["cancel_requested"]]
            if self.book["uncertain_id"] == identity:
                self.book["uncertain_id"] = current
        return current

    def _active(self) -> list[Any] | None:
        active = []
        for identity in list(self.book["order_ids"]):
            # The adapter can assign the broker ID to the created object even
            # without a callback or a returned snapshot. Poll its current ID.
            local = self.orders.get(identity)
            if local is not None:
                identity = self._bind(identity, local)
            current = self.strategy.get_order(identity)
            if current is not None:
                identity = self._bind(identity, current)
                if self.book["uncertain_id"] == identity:
                    self.book["uncertain_id"] = None
            order = self.orders.get(identity)
            if order is None:
                return None  # A missing refresh does not prove cancellation/fill.
            if order.is_active():
                active.append(order)
        return active

    def _submit(self, order: Any) -> None:
        identity = str(order.identifier)
        self.orders[identity] = order
        self.book["order_ids"].append(identity)
        self.publishing = True
        self.book["uncertain_id"] = identity
        try:
            returned = self.strategy.submit_order(order)
            current = self._bind(identity, order)
            if returned is not None:
                stale = (str(returned.identifier) == identity and current != identity)
                if not stale:
                    self._bind(current, returned)
            self.book["uncertain_id"] = None
        finally:
            # Preserve an assigned ID even if acceptance raised after dispatch.
            # It remains uncertain until the normal exact-order read succeeds.
            if str(order.identifier) != identity and identity in self.book["order_ids"]:
                self._bind(identity, order)
            self.publishing = False

    def reconcile(self) -> str:
        with self.lock:
            if self.publishing or self.book["generation"] is None:
                return "waiting"
            active = self._active()
            if active is None or self.book["uncertain_id"] is not None:
                return "reconcile_required"
            if self.book["replacement"] and active:
                self.publishing = True
                try:
                    for order in active:
                        key = str(order.identifier)
                        if key not in self.book["cancel_requested"]:
                            self.book["cancel_requested"].append(key)
                            self.strategy.cancel_order(order)
                finally:
                    self.publishing = False
                return "cancel_pending"
            if active:
                return "fill_pending"
            self.book["order_ids"] = []
            self.book["cancel_requested"] = []
            self.book["replacement"] = False
            # Refresh AFTER accepted sales/cancellations, including partial fills.
            held, bounds = {}, {}
            targets = self.book["quantities"]
            for key, asset in self.assets.items():
                position = self.strategy.get_position(asset)
                held[key] = float(position.quantity) if position else 0
                if held[key] < 0:
                    raise ValueError("This example owns a long-only portfolio")
            reductions = [(key, held[key] - targets[key]) for key in self.assets if held[key] > targets[key]]
            if reductions:
                for key, quantity in reductions:
                    self._submit(self.strategy.create_order(self.assets[key], quantity, "sell"))
                return "sales_pending"
            cash = float(self.strategy.get_cash())
            if not math.isfinite(cash):
                return "missing_cash"
            shortfalls = [(key, targets[key] - held[key]) for key in self.assets if targets[key] > held[key]]
            for key, _ in shortfalls:
                bound = float(self.maximum_buy_price(self.assets[key]))
                if not math.isfinite(bound) or bound <= 0:
                    return "missing_price"
                bounds[key] = bound
            published = False
            for key, quantity in shortfalls:
                unit_cost = bounds[key] * (1 + self.fee_fraction)
                affordable = min(quantity, max(0, math.floor(cash / unit_cost)))
                if affordable:
                    # Use the SAME maximum execution price as the affordability calculation.
                    cash -= affordable * unit_cost
                    self._submit(self.strategy.create_order(self.assets[key], affordable, "buy",
                        limit_price=bounds[key], time_in_force="day"))
                    published = True
            if published:
                return "purchases_pending"
            return "cash_limited" if shortfalls else "complete"
