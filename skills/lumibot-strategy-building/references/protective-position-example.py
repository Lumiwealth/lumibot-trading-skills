# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Standing stop and accepted-exit reconciliation for one owned long position.

Adapt this component into the strategy, preserving its signals and sizing. The
caller owns the stop rule: stop_for(position) may use aggregate fill basis or a
signal's price level. Construct once with a dictionary kept in self.vars. Call
reconcile at EVERY iteration and from partial/full-fill and canceled callbacks;
call request_exit when a signal accepts a full exit. That intent survives a
later signal reversal, rejection, partial fill and restart. A terminal-order
callback and regular reconciliation are both needed. Entry decisions remain
outside this component. It never turns a missing position read into flatness.

Example integration (same helper/lock in every callback):
  self.vars.protection = getattr(self.vars, 'protection', {})
  self.protection = LongPositionProtection(self, asset, self.vars.protection,
      lambda position: float(position.avg_fill_price) * (1 - self.parameters['stop_pct']))
  # Iteration: reconcile first, then signals; on accepted exit: request_exit().
  # After each actual partial/full fill or cancellation: reconcile().
A daily entry signal does not change this standing broker order into a daily
price check. Broker stop/gap behavior still follows the selected venue.
"""
from collections.abc import Callable
import math
from threading import RLock
from typing import Any


class LongPositionProtection:
    def __init__(self, strategy: Any, asset: Any, state: dict[str, Any],
                 stop_for: Callable[[Any], float | None]) -> None:
        self.strategy, self.asset, self.state, self.stop_for = strategy, asset, state, stop_for
        self._lock = RLock()
        self._publishing = False
        self._orders_by_id: dict[str, Any] = {}
        self.state.setdefault('exit_requested', False)
        self.state.setdefault('order_ids', [])
        self.state.setdefault('uncertain_ids', [])

    @property
    def exit_requested(self) -> bool:
        return bool(self.state['exit_requested'])

    def request_exit(self) -> None:
        with self._lock:
            self.state['exit_requested'] = True
            self.reconcile()

    def _remember(self, order: Any, previous: str | None = None) -> str:
        identity = str(order.identifier)
        if previous is not None and previous != identity:
            self._orders_by_id.pop(previous, None)
            for field in ('order_ids', 'uncertain_ids'):
                self.state[field] = list(dict.fromkeys(
                    identity if key == previous else key for key in self.state[field]))
        self._orders_by_id[identity] = order
        if identity not in self.state['order_ids']:
            self.state['order_ids'].append(identity)
        return identity

    def _orders(self) -> list[Any] | None:
        for order in self.strategy.get_orders():
            if order.asset == self.asset and not order.parent_identifier:
                self._remember(order)
        active = []
        seen = set()
        for identity in list(self.state['order_ids']):
            local = self._orders_by_id.get(identity)
            if local is not None:
                identity = self._remember(local, identity)
            if identity in seen:
                continue
            seen.add(identity)
            current = self.strategy.get_order(identity)
            if current is not None:
                identity = self._remember(current, identity)
            order = self._orders_by_id.get(identity)
            if order is None:
                return None  # A missing read cannot retire a saved reservation.
            if identity in self.state['uncertain_ids']:
                if order.status == 'error':
                    return None  # Dispatch failure is not broker rejection.
                if not order.is_active():
                    self.state['uncertain_ids'].remove(identity)
            if order.is_active():
                active.append(order)
            else:
                self.state['order_ids'].remove(identity)
        return active

    def _publish(self, order: Any) -> None:
        original = self._remember(order)  # reserve before callback-capable IO
        self.state['uncertain_ids'].append(original)
        self._publishing = True
        try:
            returned = self.strategy.submit_order(order)
            current = self._remember(order, original)
            if returned is not None:
                stale_id = str(returned.identifier) == original and current != original
                stale_state = ((bool(order.transactions) and not returned.transactions)
                               or (not order.is_active() and returned.is_active()))
                if not stale_id and not stale_state:
                    current = self._remember(returned, current)
                if current in self.state['uncertain_ids']:
                    self.state['uncertain_ids'].remove(current)
        finally:
            if original in self.state['order_ids']:
                self._remember(order, original)
            self._publishing = False

    def _cancel(self, orders: list[Any]) -> None:
        self._publishing = True
        try:
            for order in orders:
                try:
                    self.strategy.cancel_order(order)
                except Exception:
                    self.strategy.log_message('Cancellation unconfirmed; retain order and exit intent.')
        finally:
            self._publishing = False
        if orders and all(not order.is_active() for order in orders):
            self.reconcile()

    def reconcile(self) -> None:
        with self._lock:
            if self._publishing:
                return
            position = self.strategy.get_position(self.asset)
            held = float(position.quantity) if position is not None else 0.0
            if not math.isfinite(held):
                return
            active = self._orders()
            if active is None:
                return
            stops = [o for o in active if o.side == 'sell' and o.stop_price is not None]
            if self.exit_requested:
                conflicts = [o for o in active if o.side == 'buy' or o.stop_price is not None]
                if conflicts:
                    self._cancel(conflicts)
                    return  # cancellation REQUEST is not terminal confirmation
                if active:
                    return  # keep an accepted unfinished market exit
                if held > 0:
                    self._publish(self.strategy.create_order(self.asset, held, 'sell'))
                else:
                    self.state['exit_requested'] = False
                return
            if held <= 0:
                self._cancel(stops)
                return
            stop = self.stop_for(position)
            if stop is None or not math.isfinite(float(stop)) or stop <= 0:
                return  # caller must expose unavailable basis/price, never invent one
            remaining = sum(float(o.quantity) - sum(float(t.quantity) for t in o.transactions)
                            for o in stops)
            if len(stops) == 1 and math.isclose(remaining, held) and math.isclose(float(stops[0].stop_price), stop):
                return
            if stops:
                self._cancel(stops)
                return
            self._publish(self.strategy.create_order(self.asset, held, 'sell',
                          stop_price=stop, time_in_force='gtc'))
