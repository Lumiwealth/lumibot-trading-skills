# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Complete reusable cancel/late-fill/hedge lifecycle.

Strategy subclasses supply their own investment-policy inputs. The controller
retains order identities, cancellation, callback replay and hedge recovery.
"""
# Business integration boundary: set option_asset, entry_quantity,
# entry_limit_price, stock_hedge_asset and stock_hedge_quantity before entry.
# Populate scan_cache from actual bounded, batched provider observations and
# override _prepare_candidate_from_cached_evidence with the user's selection
# policy. That pure cached-data hook is deliberately strategy-specific; this
# controller does not invent a provider feed, entry signal or investment rule.
# The hook may only inspect the supplied cached value and set prepared inputs;
# it must do finite local work, with no network calls, waits or further scans.

import math
import threading
import time
from datetime import timedelta
from lumibot.entities import Order
from lumibot.strategies.strategy import Strategy

class FastOrderStrategy(Strategy):

    def initialize(self):
        self._order_state_lock = threading.RLock()
        self.sleeptime = '1S'
        self.cancel_timeout_seconds = float(self.parameters.get('cancel_timeout_seconds', 3.0))
        # Measure/calibrate this positive dispatch margin in the actual runtime.
        # Prompt local dispatch cannot guarantee broker terminal-confirmation latency.
        self.cancel_dispatch_margin_seconds = float(self.parameters.get('cancel_dispatch_margin_seconds', 0.25))
        self.reconcile_backoff_seconds = float(self.parameters.get('reconcile_backoff_seconds', 5.0))
        if not all((math.isfinite(value) for value in (self.cancel_timeout_seconds, self.cancel_dispatch_margin_seconds, self.reconcile_backoff_seconds))) or not 0 < self.cancel_timeout_seconds <= 3.0 or (not 0 < self.cancel_dispatch_margin_seconds < self.cancel_timeout_seconds) or (self.reconcile_backoff_seconds <= 0):
            raise ValueError('Use a finite positive user deadline/backoff and a smaller positive margin')
        self.entry_order_ids = {}
        self.entry_hedge_inputs = {}
        # Transient strong references preserve exact object identity for late
        # callbacks after an entry becomes terminal and a different one starts.
        self.entry_order_objects = {}
        self.selected_entry_id_by_key = {}
        self.terminal_entry_ids = {}
        self.hedge_entry_by_order_id = {}
        self.hedge_order_by_entry_id = {}
        self.canceling_entry_ids = {}
        self.hedge_by_entry_id = {}
        self.hedge_attempts_by_entry_id = {}
        self._submitting_orders = 0
        self._reconciling_orders = 0
        self.scan_symbols = list(self.parameters.get('symbols', []))
        self.scan_cursor = 0
        self.scan_cache = {}
        self._pending_filled_callbacks = {}
        self._pending_terminal_callbacks = {}
        self.unmatched_callback_evidence = {}
        self.owner_recovery_audit = []
        self.owner_construction_retries = {}
        self.unmatched_reconcile_cursor = 0
        self.hedge_reconcile_cursor = 0
        self.reconcile_owner_cursor = 0
        self.active_entry_order_id = None
        self.active_entry_order = None
        self.cancel_deadline_monotonic = None
        self.pair_state = 'IDLE'
        self.next_reconcile_at = None
        self._reconcile_generation = 0

    def _pair_is_blocking(self):
        with self._order_state_lock:
            return self._submitting_orders > 0 or self._reconciling_orders > 0 or self.active_entry_order_id is not None or bool(self.canceling_entry_ids) or (self.pair_state in {'ENTRY_ACTIVE', 'CANCEL_PENDING', 'HEDGE_SUBMITTING', 'HEDGE_ACTIVE', 'HEDGE_FAILED', 'RECONCILE_REQUIRED'})

    def _entry_key(self, order):
        with self._order_state_lock:
            identifier = order.identifier
            key = self.entry_order_ids.get(identifier)
            remembered = self.entry_order_objects.get(id(order))
            if key is None and remembered is not None and remembered[0] is order:
                key = remembered[1]
                self.entry_order_ids[identifier] = key
            if isinstance(key, str):
                self.entry_order_objects[id(order)] = (order, key)
                if self.selected_entry_id_by_key.get(key) in {None, key}:
                    self.selected_entry_id_by_key[key] = identifier
                return key
            if key is True:
                self.entry_order_objects[id(order)] = (order, identifier)
                self.selected_entry_id_by_key.setdefault(identifier, identifier)
                return identifier
            if order is self.active_entry_order and self.active_entry_order_id is not None:
                previous = self.active_entry_order_id
                key = self.entry_order_ids.get(previous)
                key = key if isinstance(key, str) else previous
                self.entry_order_ids[identifier] = key
                self.entry_order_objects[id(order)] = (order, key)
                if identifier != key or self.selected_entry_id_by_key.get(key) in {None, key}:
                    self.selected_entry_id_by_key[key] = identifier
                self.active_entry_order_id = identifier
                return key
            return identifier

    def _refresh_pair_state(self):
        with self._order_state_lock:
            states = [row['state'] for row in self.hedge_by_entry_id.values()]
            if 'FAILED' in states:
                self.pair_state = 'HEDGE_FAILED'
            elif any((state != 'FILLED' for state in states)):
                self.pair_state = 'HEDGE_ACTIVE'
            elif self.active_entry_order_id is not None:
                self.pair_state = 'CANCEL_PENDING' if self.canceling_entry_ids else 'ENTRY_ACTIVE'
            elif self.canceling_entry_ids or any((evidence.get('risk_unit_unresolved') for evidence in self.unmatched_callback_evidence.values())):
                self.pair_state = 'RECONCILE_REQUIRED'
            else:
                self.pair_state = 'IDLE'

    def _finish_hedge(self, entry_key):
        with self._order_state_lock:
            self.hedge_by_entry_id[entry_key]['state'] = 'FILLED'
            for identifier, key in self.entry_order_ids.items():
                if (key if isinstance(key, str) else identifier) == entry_key:
                    self.canceling_entry_ids.pop(identifier, None)
                    if self.active_entry_order_id == identifier:
                        self.active_entry_order_id = None
                        self.active_entry_order = None
            self._refresh_pair_state()

    def _replay_accepted_callbacks(self, identifier):
        with self._order_state_lock:
            filled = self._pending_filled_callbacks.pop(identifier, None)
            terminal = self._pending_terminal_callbacks.pop(identifier, None)
            self.unmatched_callback_evidence.pop(identifier, None)
        if filled is not None:
            self.on_filled_order(*filled)
        if terminal is not None:
            self.on_canceled_order(terminal)

    def submit_entry(self):
        if self._pair_is_blocking():
            return None
        order = self.create_order(self.option_asset, self.entry_quantity, 'buy', order_type=Order.OrderType.LIMIT, limit_price=self.entry_limit_price)
        with self._order_state_lock:
            if self._pair_is_blocking():
                return None
            logical_entry_key = order.identifier
            self._reconcile_generation += 1
            self.active_entry_order_id = logical_entry_key
            self.active_entry_order = order
            self.entry_order_ids[logical_entry_key] = logical_entry_key
            self.entry_hedge_inputs[logical_entry_key] = (self.stock_hedge_asset, self.stock_hedge_quantity)
            self.entry_order_objects[id(order)] = (order, logical_entry_key)
            self.selected_entry_id_by_key[logical_entry_key] = logical_entry_key
            self.pair_state = 'ENTRY_ACTIVE'
            self._submitting_orders += 1
        try:
            tracked = self.submit_order(order) or order
            returned_full_fill = tracked.is_filled()
            accepted_at = time.monotonic()
        except Exception:
            observed_exception_fill = order.is_filled()
            with self._order_state_lock:
                self._submitting_orders -= 1
                mutated_id = getattr(order, 'identifier', None)
                if mutated_id is not None:
                    self.entry_order_ids[mutated_id] = logical_entry_key
                    if self.selected_entry_id_by_key.get(logical_entry_key) in {None, logical_entry_key}:
                        self.selected_entry_id_by_key[logical_entry_key] = mutated_id
                    if self.active_entry_order_id == logical_entry_key:
                        self.active_entry_order_id = self.selected_entry_id_by_key[logical_entry_key]
                if observed_exception_fill:
                    self.terminal_entry_ids[logical_entry_key] = Order.OrderStatus.FILLED
                    self._reconciling_orders += 1
                elif logical_entry_key not in self.terminal_entry_ids and logical_entry_key not in self.hedge_by_entry_id:
                    selected = self.selected_entry_id_by_key.get(logical_entry_key, logical_entry_key)
                    self.canceling_entry_ids.setdefault(selected, {'requested_at': self.get_datetime(), 'attempts': 0})
            try:
                if observed_exception_fill:
                    self._place_stock_hedge_once(order)
            finally:
                with self._order_state_lock:
                    if observed_exception_fill:
                        self._reconciling_orders -= 1
                    self._refresh_pair_state()
            raise
        with self._order_state_lock:
            returned_fill_hold = (returned_full_fill or tracked.identifier in self._pending_filled_callbacks or tracked.identifier in self._pending_terminal_callbacks)
            if returned_full_fill:
                self.terminal_entry_ids[logical_entry_key] = Order.OrderStatus.FILLED
            if returned_fill_hold:
                self._reconciling_orders += 1
            self._submitting_orders -= 1
            self.entry_order_ids[tracked.identifier] = logical_entry_key
            self.entry_order_objects[id(tracked)] = (tracked, logical_entry_key)
            if self.selected_entry_id_by_key.get(logical_entry_key) in {None, logical_entry_key}:
                self.selected_entry_id_by_key[logical_entry_key] = tracked.identifier
            active_key = self.entry_order_ids.get(self.active_entry_order_id)
            if active_key == logical_entry_key and self.active_entry_order_id == logical_entry_key:
                self.active_entry_order_id = self.selected_entry_id_by_key[logical_entry_key]
                if tracked.identifier == self.active_entry_order_id:
                    self.active_entry_order = tracked
            deadline = accepted_at + self.cancel_timeout_seconds - self.cancel_dispatch_margin_seconds
            current_key = self.entry_order_ids.get(self.active_entry_order_id)
            if current_key == logical_entry_key and logical_entry_key not in self.terminal_entry_ids and (logical_entry_key not in self.hedge_by_entry_id):
                self.cancel_deadline_monotonic = deadline
            if current_key == logical_entry_key and not returned_fill_hold:
                self._reconciling_orders += 1
                returned_fill_hold = True
        try:
            self._replay_accepted_callbacks(tracked.identifier)
            with self._order_state_lock:
                current_key = self.entry_order_ids.get(self.active_entry_order_id)
                returned_fill = returned_full_fill or tracked.is_filled()
                if returned_fill:
                    self._reconciling_orders += 1
                elif current_key != logical_entry_key or logical_entry_key in self.terminal_entry_ids or logical_entry_key in self.hedge_by_entry_id:
                    return tracked
                resident_order = self.active_entry_order or tracked
            if returned_fill:
                try:
                    self._place_stock_hedge_once(tracked)
                finally:
                    with self._order_state_lock:
                        self._reconciling_orders -= 1
                return tracked
            self._hold_entry_until_cancel_dispatch(resident_order, deadline)
            return tracked
        finally:
            if returned_fill_hold:
                with self._order_state_lock:
                    self._reconciling_orders -= 1

    def _hold_entry_until_cancel_dispatch(self, tracked, deadline):
        while True:
            with self._order_state_lock:
                observed_fill = tracked.is_filled()
                if observed_fill:
                    self._reconciling_orders += 1
                elif self._entry_key(tracked) in self.terminal_entry_ids:
                    return
            if observed_fill:
                try:
                    self._place_stock_hedge_once(tracked)
                finally:
                    with self._order_state_lock:
                        self._reconciling_orders -= 1
                return
            status = getattr(tracked, 'status', None)
            if tracked.is_canceled() or status in {Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED, Order.OrderStatus.ERROR}:
                self._finish_terminal_entry(tracked.identifier, status)
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            self.sleep(min(0.05, remaining), process_pending_orders=False)
        entry_id = tracked.identifier
        with self._order_state_lock:
            already_filled = tracked.is_filled() or self._entry_key(tracked) in self.hedge_by_entry_id
            if already_filled:
                self._reconciling_orders += 1
            else:
                if self._entry_key(tracked) in self.terminal_entry_ids:
                    return
                status = getattr(tracked, 'status', None)
                if tracked.is_canceled() or status in {Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED, Order.OrderStatus.ERROR}:
                    self._finish_terminal_entry(tracked.identifier, status)
                    return
                self.canceling_entry_ids[entry_id] = {'requested_at': self.get_datetime(), 'attempts': 1}
                self.pair_state = 'CANCEL_PENDING'
                reservation = self._reserve_reconcile(self.get_datetime())
        if already_filled:
            try:
                self._place_stock_hedge_once(tracked)
            finally:
                with self._order_state_lock:
                    self._reconciling_orders -= 1
            return
        cancel_started = time.monotonic()
        try:
            # Do not clear state here; cancel dispatch is not terminal evidence.
            self.cancel_order(tracked)
        except Exception:
            self._refresh_pair_state()
            return
        finally:
            completed_at = self.get_datetime()
            elapsed = max(0.0, time.monotonic() - cancel_started)
            with self._order_state_lock:
                self._complete_reconcile(reservation, completed_at + timedelta(seconds=elapsed))

    def _retain_unmatched_callback(self, order, kind, *, position=None, price=None, quantity=None, multiplier=None):
        # Called under the state lock. Snapshot callback-time facts before a
        # mutable SDK Order changes, and retain the complete original payload.
        status = Order.OrderStatus.FILLED if kind == 'filled' else str(getattr(order, 'status', 'unknown'))
        evidence = self.unmatched_callback_evidence.setdefault(order.identifier, {'source': 'callback', 'risk_unit_unresolved': False, 'callbacks': []})
        evidence['status'] = status
        evidence['risk_unit_unresolved'] |= self.pair_state != 'IDLE'
        evidence['callbacks'].append({'kind': kind, 'order_id': order.identifier, 'status': status, 'position': position, 'order': order, 'price': price, 'quantity': quantity, 'multiplier': multiplier})

    def _owner_callback_evidence(self, identifier):
        # Freeze the audit's event list before replay/removal; no broker calls.
        evidence = dict(self.unmatched_callback_evidence.get(identifier, {}))
        evidence['callbacks'] = tuple(dict(row) for row in evidence.get('callbacks', ()))
        return evidence

    def on_filled_order(self, position, order, price, quantity, multiplier):
        if order is None:
            return
        with self._order_state_lock:
            is_entry = order.identifier in self.entry_order_ids or order is self.active_entry_order or (id(order) in self.entry_order_objects and self.entry_order_objects[id(order)][0] is order)
            if is_entry:
                self._reconciling_orders += 1
        if is_entry:
            try:
                self._place_stock_hedge_once(order)
            finally:
                with self._order_state_lock:
                    self._reconciling_orders -= 1
            return
        with self._order_state_lock:
            accepted_was_known = order.identifier in self.hedge_entry_by_order_id
            entry_key = self.hedge_entry_by_order_id.get(order.identifier)
            if entry_key is None:
                entry_key = next((key for key, tracked in self.hedge_order_by_entry_id.items() if tracked is order), None)
            if entry_key is not None:
                self.hedge_entry_by_order_id[order.identifier] = entry_key
                row = self.hedge_by_entry_id[entry_key]
                if not accepted_was_known or row.get('hedge_order_id') in {None, row.get('local_order_id')}:
                    row['hedge_order_id'] = order.identifier
                self._finish_hedge(entry_key)
            else:
                self._pending_filled_callbacks[order.identifier] = (position, order, price, quantity, multiplier)
                self._retain_unmatched_callback(order, 'filled', position=position, price=price, quantity=quantity, multiplier=multiplier)

    def on_canceled_order(self, order):
        if order is None:
            return
        with self._order_state_lock:
            is_entry = order.identifier in self.entry_order_ids or order.identifier in self.canceling_entry_ids or order is self.active_entry_order or (id(order) in self.entry_order_objects and self.entry_order_objects[id(order)][0] is order)
            if is_entry:
                self._entry_key(order)
                self._reconciling_orders += 1
            accepted_was_known = order.identifier in self.hedge_entry_by_order_id
            hedge_key = self.hedge_entry_by_order_id.get(order.identifier)
            if hedge_key is None:
                hedge_key = next((key for key, tracked in self.hedge_order_by_entry_id.items() if tracked is order), None)
                if hedge_key is not None:
                    self.hedge_entry_by_order_id[order.identifier] = hedge_key
            if not is_entry and hedge_key is None:
                self._pending_terminal_callbacks[order.identifier] = order
                self._retain_unmatched_callback(order, 'terminal')
                return
        try:
            if order.is_filled():
                self.on_filled_order(None, order, None, None, None)
                return
            terminal_status = getattr(order, 'status', None)
            if terminal_status not in {Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED, Order.OrderStatus.ERROR}:
                terminal_status = Order.OrderStatus.CANCELED
            if is_entry:
                self._finish_terminal_entry(order.identifier, terminal_status)
            else:
                with self._order_state_lock:
                    row = self.hedge_by_entry_id[hedge_key]
                    if row['state'] != 'FILLED':
                        if not accepted_was_known or row.get('hedge_order_id') in {None, row.get('local_order_id')}:
                            row['hedge_order_id'] = order.identifier
                        row.update(state='FAILED', reason='Authoritative terminal unfilled hedge callback')
                        self._refresh_pair_state()
        finally:
            if is_entry:
                with self._order_state_lock:
                    self._reconciling_orders -= 1

    def retry_owner_fixed_unsubmitted_hedge(self, filled_entry):
        """Explicit owner action after fixing a local construction error.

        Never call automatically from callbacks or iterations. Only a failure
        before any hedge Order was registered is provably unsubmitted. An
        uncertain submission or terminal submitted hedge is never resent here.
        One owner-requested construction retry is allowed for this entry.
        """
        with self._order_state_lock:
            key = self._entry_key(filled_entry)
            row = self.hedge_by_entry_id.get(key)
            if (row is None or row.get('state') != 'FAILED'
                    or row.get('hedge_order_id') is not None
                    or key in self.hedge_order_by_entry_id
                    or row.get('submission_unknown')
                    or self.owner_construction_retries.get(key, 0) >= 1):
                return False
            self.owner_recovery_audit.append({'action': 'retry_local_construction', 'entry_key': key, 'prior_state': dict(row)})
            self.owner_construction_retries[key] = 1
            self._reconciling_orders += 1
            del self.hedge_by_entry_id[key]
        try:
            self._place_stock_hedge_once(filled_entry)
            return True
        finally:
            with self._order_state_lock:
                self._reconciling_orders -= 1
                self._refresh_pair_state()

    def record_owner_verified_hedge_identity(self, entry_order_id, verified_hedge_order_id, *, expected_current_id):
        """Owner supplies a broker-verified association, never a symbol guess.

        Read the current row and independently verify this broker order belongs
        to its hedge before invoking. The expected ID prevents a stale owner
        action overwriting a newer callback identity. This only changes the
        exact read target and replays any already retained authoritative
        callback under a continuous hold. Known older aliases and IDs owned by
        another entry/hedge cannot replace the selected identity. This never
        resubmits or infers a fill; without a retained callback, normal bounded
        reconciliation must obtain the actual terminal result.
        """
        if not isinstance(verified_hedge_order_id, str) or not verified_hedge_order_id:
            return False
        with self._order_state_lock:
            key = self.entry_order_ids.get(entry_order_id, entry_order_id)
            row = self.hedge_by_entry_id.get(key)
            if row is None or row.get('state') == 'FILLED' or row.get('hedge_order_id') != expected_current_id:
                return False
            known_owner = self.hedge_entry_by_order_id.get(verified_hedge_order_id)
            if (verified_hedge_order_id in self.entry_order_ids
                    or (known_owner is not None and (known_owner != key or verified_hedge_order_id != expected_current_id))):
                return False
            self.owner_recovery_audit.append({'action': 'verified_hedge_read_identity', 'entry_key': key, 'prior_state': dict(row), 'verified_id': verified_hedge_order_id, 'callback_evidence': self._owner_callback_evidence(verified_hedge_order_id)})
            row['hedge_order_id'] = verified_hedge_order_id
            self.hedge_entry_by_order_id[verified_hedge_order_id] = key
            self._reconciling_orders += 1
        try:
            # The association can resolve a callback already retained before
            # this accepted ID was known. Do not wait for a redundant read.
            self._replay_accepted_callbacks(verified_hedge_order_id)
            return True
        finally:
            with self._order_state_lock:
                self._reconciling_orders -= 1
                self._refresh_pair_state()

    def record_owner_verified_entry_identity(self, entry_order_id, accepted_id, *, expected_current_id):
        """Replay a retained callback after the owner verifies its entry alias.

        The caller independently proves the broker association; symbols alone
        are insufficient. This explicit action performs no broker write/read,
        never adopts an ID already belonging to another known owner, and keeps
        a temporary hold through callback replay into the shared hedge fence.
        """
        if not isinstance(accepted_id, str) or not accepted_id:
            return False
        with self._order_state_lock:
            if entry_order_id not in self.entry_order_ids:
                return False
            key = self.entry_order_ids[entry_order_id]
            current = self.selected_entry_id_by_key.get(key, key)
            if current != expected_current_id or accepted_id in self.hedge_entry_by_order_id:
                return False
            if accepted_id in self.entry_order_ids and (self.entry_order_ids[accepted_id] != key or accepted_id != current):
                return False
            self.owner_recovery_audit.append({'action': 'verified_entry_identity', 'entry_key': key, 'prior_id': current, 'verified_id': accepted_id, 'callback_evidence': self._owner_callback_evidence(accepted_id)})
            self.entry_order_ids[accepted_id] = key
            self.selected_entry_id_by_key[key] = accepted_id
            if self.entry_order_ids.get(self.active_entry_order_id) == key:
                self.active_entry_order_id = accepted_id
            self._reconciling_orders += 1
        try:
            self._replay_accepted_callbacks(accepted_id)
            return True
        finally:
            with self._order_state_lock:
                self._reconciling_orders -= 1
                self._refresh_pair_state()

    def record_owner_verified_unrelated_callback(self, callback_id):
        """Archive only after the owner proves this ID belongs outside this pool.

        No asset/symbol match establishes that proof. Keep the original unknown
        evidence in the audit, and never discard an ID now linked to an owned
        entry or hedge. This state-only operation performs no broker action.
        """
        with self._order_state_lock:
            evidence = self.unmatched_callback_evidence.get(callback_id)
            if evidence is None or callback_id in self.entry_order_ids or callback_id in self.hedge_entry_by_order_id:
                return False
            self.owner_recovery_audit.append({'action': 'verified_unrelated_callback', 'callback_id': callback_id, 'evidence': self._owner_callback_evidence(callback_id)})
            self.unmatched_callback_evidence.pop(callback_id, None)
            self._pending_filled_callbacks.pop(callback_id, None)
            self._pending_terminal_callbacks.pop(callback_id, None)
            self._refresh_pair_state()
            return True

    def _place_stock_hedge_once(self, filled_entry):
        with self._order_state_lock:
            entry_id = self._entry_key(filled_entry)
            self.terminal_entry_ids[entry_id] = Order.OrderStatus.FILLED
            for identifier, key in self.entry_order_ids.items():
                if (key if isinstance(key, str) else identifier) == entry_id:
                    self.canceling_entry_ids.pop(identifier, None)
                    if self.active_entry_order_id == identifier:
                        self.cancel_deadline_monotonic = None
            self.canceling_entry_ids.pop(filled_entry.identifier, None)
            existing = self.hedge_by_entry_id.get(entry_id)
            if existing and existing.get('state') in {'SUBMITTING', 'ACTIVE', 'FILLED', 'FAILED'}:
                return
            self.pair_state = 'HEDGE_SUBMITTING'
            self.hedge_by_entry_id[entry_id] = {'state': 'SUBMITTING', 'hedge_order_id': None}
            hedge_asset, hedge_quantity = self.entry_hedge_inputs.get(entry_id, (self.stock_hedge_asset, self.stock_hedge_quantity))
        hedge = None
        submitting = False
        try:
            hedge = self.create_order(hedge_asset, hedge_quantity, 'sell', order_type=Order.OrderType.MARKET)
            with self._order_state_lock:
                self.hedge_by_entry_id[entry_id]['hedge_order_id'] = hedge.identifier
                self.hedge_by_entry_id[entry_id]['local_order_id'] = hedge.identifier
                self.hedge_entry_by_order_id[hedge.identifier] = entry_id
                self.hedge_order_by_entry_id[entry_id] = hedge
                self._submitting_orders += 1
                submitting = True
            submitted_identifier = hedge.identifier
            hedge = self.submit_order(hedge) or hedge
            returned_hedge_full_fill = hedge.is_filled()
            with self._order_state_lock:
                self._submitting_orders -= 1
                submitting = False
                self.hedge_entry_by_order_id[hedge.identifier] = entry_id
                row = self.hedge_by_entry_id[entry_id]
                if row.get('hedge_order_id') in {None, row.get('local_order_id', submitted_identifier)}:
                    row['hedge_order_id'] = hedge.identifier
                    self.hedge_order_by_entry_id[entry_id] = hedge
                if returned_hedge_full_fill or hedge.is_filled():
                    self._finish_hedge(entry_id)
            self._replay_accepted_callbacks(hedge.identifier)
        except Exception as exc:
            with self._order_state_lock:
                if submitting:
                    self._submitting_orders -= 1
                row = self.hedge_by_entry_id[entry_id]
                if hedge is not None and getattr(hedge, 'identifier', None) is not None:
                    self.hedge_entry_by_order_id[hedge.identifier] = entry_id
                    if row.get('hedge_order_id') in {None, row.get('local_order_id')}:
                        row['hedge_order_id'] = hedge.identifier
                        self.hedge_order_by_entry_id[entry_id] = hedge
                if row['state'] != 'SUBMITTING':
                    return
                row.update(state='FAILED', submission_unknown=hedge is not None, reason=str(exc))
                self.pair_state = 'HEDGE_FAILED'
                return
        with self._order_state_lock:
            state = self.hedge_by_entry_id[entry_id]
            if hedge.is_filled():
                self._finish_hedge(entry_id)
                return
            if state['state'] != 'SUBMITTING':
                return
            if hedge.is_canceled() or getattr(hedge, 'status', None) in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                state.update(state='FAILED', reason='Broker returned a terminal unfilled hedge; reconcile fills before retry')
                self.pair_state = 'HEDGE_FAILED'
                return
            state.update(state='ACTIVE')
            self.pair_state = 'HEDGE_ACTIVE'

    def _read_tracked_order(self, identifier, *, entry_key=None, hedge_key=None):
        with self._order_state_lock:
            self._reconciling_orders += 1
            selected_before = self.selected_entry_id_by_key.get(entry_key) if entry_key is not None else None
            hedge_before = dict(self.hedge_by_entry_id[hedge_key]) if hedge_key is not None else None
        try:
            observed = self.get_order(identifier)
            observed_full_fill = observed is not None and observed.is_filled()
            with self._order_state_lock:
                if observed is not None:
                    if entry_key is not None:
                        if observed_full_fill:
                            self.terminal_entry_ids[entry_key] = Order.OrderStatus.FILLED
                        known_alias = self.entry_order_ids.get(observed.identifier) == entry_key
                        self.entry_order_ids[observed.identifier] = entry_key
                        self.entry_order_objects[id(observed)] = (observed, entry_key)
                        current_id = self.selected_entry_id_by_key.get(entry_key)
                        if current_id in {None, entry_key} or (current_id == selected_before and observed.identifier != entry_key and (not known_alias)):
                            self.selected_entry_id_by_key[entry_key] = observed.identifier
                    if hedge_key is not None:
                        known_alias = self.hedge_entry_by_order_id.get(observed.identifier) == hedge_key
                        self.hedge_entry_by_order_id[observed.identifier] = hedge_key
                        row = self.hedge_by_entry_id[hedge_key]
                        selected_unchanged = row.get('hedge_order_id') == hedge_before.get('hedge_order_id')
                        if row.get('hedge_order_id') in {None, row.get('local_order_id')} or (selected_unchanged and (not known_alias)):
                            row['hedge_order_id'] = observed.identifier
                            self.hedge_order_by_entry_id[hedge_key] = observed
                        if observed_full_fill:
                            self._finish_hedge(hedge_key)
                        elif selected_unchanged and row['state'] == hedge_before['state'] and (row['state'] != 'FILLED') and (observed.is_canceled() or getattr(observed, 'status', None) in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}):
                            row.update(state='FAILED', reason='Exact owned read observed terminal unfilled hedge')
                            self._refresh_pair_state()
            if observed is not None:
                self._replay_accepted_callbacks(observed.identifier)
                if entry_key is not None and (observed_full_fill or observed.is_filled()):
                    self._place_stock_hedge_once(observed)
                elif hedge_key is not None and (observed_full_fill or observed.is_filled()):
                    self._finish_hedge(hedge_key)
            return observed
        finally:
            with self._order_state_lock:
                self._reconciling_orders -= 1

    def _reconcile_hedge_or_hold_blocker(self, now):
        step_started_monotonic = time.monotonic()
        with self._order_state_lock:
            if self.next_reconcile_at is not None and now < self.next_reconcile_at:
                return
            pending = [(key, row) for key, row in self.hedge_by_entry_id.items() if row['state'] != 'FILLED']
            reconnect_entry = not pending and self.active_entry_order_id is not None and (self.active_entry_order_id not in self.canceling_entry_ids)
            recovery_entry = None
            if not reconnect_entry and self.unmatched_callback_evidence:
                known_keys = list(dict.fromkeys((key if isinstance(key, str) else identifier for identifier, key in self.entry_order_ids.items())))
                known_entries = [self.selected_entry_id_by_key.get(key, key) for key in known_keys]
                if known_entries:
                    recovery_entry = known_entries[self.unmatched_reconcile_cursor % len(known_entries)]
                    self.unmatched_reconcile_cursor += 1
                    self._reconciling_orders += 1
                    reservation = self._reserve_reconcile(now)
            hedge_id = None
            if reconnect_entry:
                selected_entry = self.active_entry_order_id or recovery_entry
                self.canceling_entry_ids.setdefault(selected_entry, {'requested_at': now, 'attempts': 2 if recovery_entry else 0})
            elif not pending and recovery_entry is None:
                self._refresh_pair_state()
                return
            if pending:
                entry_key, row = pending[self.hedge_reconcile_cursor % len(pending)]
                self.hedge_reconcile_cursor += 1
                hedge_id = row.get('hedge_order_id')
                reservation = self._reserve_reconcile(now)
                before_read = dict(row)
                if hedge_id is None:
                    row.update(state='FAILED', reason='Unknown hedge identity; owner recovery required')
                    self._refresh_pair_state()
        if recovery_entry is not None:
            try:
                logical_key = self.entry_order_ids.get(recovery_entry, recovery_entry)
                if not isinstance(logical_key, str):
                    logical_key = recovery_entry
                observed = self._read_tracked_order(recovery_entry, entry_key=logical_key)
                if observed is not None:
                    self._replay_accepted_callbacks(observed.identifier)
                if observed is None:
                    pass
                elif observed.is_filled():
                    self._place_stock_hedge_once(observed)
                elif observed.is_canceled() or getattr(observed, 'status', None) in {Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED, Order.OrderStatus.ERROR}:
                    self._finish_terminal_entry(observed.identifier, observed.status)
                else:
                    with self._order_state_lock:
                        if logical_key not in self.terminal_entry_ids and logical_key not in self.hedge_by_entry_id:
                            self.canceling_entry_ids.setdefault(observed.identifier, {'requested_at': now, 'attempts': 2})
                        self._refresh_pair_state()
            except Exception:
                pass
            finally:
                with self._order_state_lock:
                    self._reconciling_orders -= 1
                    elapsed = max(0.0, time.monotonic() - step_started_monotonic)
                    completed_at = max(now + timedelta(seconds=elapsed), self.get_datetime())
                    reservation = self._complete_reconcile(reservation, completed_at)
            if not pending:
                return
        if reconnect_entry:
            self._reconcile_canceling_entry(now)
            return
        if hedge_id is None or reservation is None:
            return
        try:
            observed = self._read_tracked_order(hedge_id, hedge_key=entry_key)
        except Exception:
            return
        finally:
            with self._order_state_lock:
                elapsed = max(0.0, time.monotonic() - step_started_monotonic)
                completed_at = max(now + timedelta(seconds=elapsed), self.get_datetime())
                self._complete_reconcile(reservation, completed_at)
        with self._order_state_lock:
            row = self.hedge_by_entry_id[entry_key]
            if observed is None:
                return
            accepted_id = observed.identifier
            if observed.is_filled():
                self._finish_hedge(entry_key)
            elif row != before_read or row['state'] == 'FILLED':
                return
            before_replay = dict(row)
        self._replay_accepted_callbacks(accepted_id)
        with self._order_state_lock:
            row = self.hedge_by_entry_id[entry_key]
            if row != before_replay or row['state'] == 'FILLED':
                return
            if observed.is_filled():
                self._finish_hedge(entry_key)
            elif observed.is_canceled() or getattr(observed, 'status', None) in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                row.update(state='FAILED', reason='Hedge terminal without confirmed full fill; owner recovery required')
                self._refresh_pair_state()

    def _reconcile_canceling_entry(self, now):
        with self._order_state_lock:
            if not self.canceling_entry_ids:
                return
            if self.next_reconcile_at is not None and now < self.next_reconcile_at:
                return
            previous_id = next(iter(self.canceling_entry_ids))
            logical_key = self.entry_order_ids.get(previous_id, previous_id)
            if not isinstance(logical_key, str):
                logical_key = previous_id
            entry_id = self.selected_entry_id_by_key.get(logical_key, previous_id)
            aliases = [identifier for identifier in self.canceling_entry_ids if identifier == previous_id or self.entry_order_ids.get(identifier, identifier) == logical_key]
            states = [self.canceling_entry_ids.pop(identifier) for identifier in aliases]
            pending = dict(states[0])
            pending['attempts'] = max((state.get('attempts', 0) for state in states))
            self.canceling_entry_ids[entry_id] = pending
            reservation = self._reserve_reconcile(now)
            self._reconciling_orders += 1
        started_monotonic = time.monotonic()
        try:
            try:
                logical_key = self.entry_order_ids.get(entry_id, entry_id)
                tracked = self._read_tracked_order(entry_id, entry_key=logical_key)
            except Exception:
                self._refresh_pair_state()
                return
            if tracked is None:
                self._refresh_pair_state()
                return
            with self._order_state_lock:
                logical_key = self.entry_order_ids.get(entry_id, entry_id)
                self.entry_order_ids[tracked.identifier] = logical_key
                selected_id = self.selected_entry_id_by_key.get(logical_key, entry_id)
                active_key = self.entry_order_ids.get(self.active_entry_order_id)
                if active_key == logical_key:
                    self.active_entry_order_id = selected_id
                    if tracked.identifier == selected_id:
                        self.active_entry_order = tracked
                state = self.canceling_entry_ids.pop(entry_id, None)
                if state is not None:
                    self.canceling_entry_ids.setdefault(selected_id, state)
                entry_id = selected_id
            self._replay_accepted_callbacks(tracked.identifier)
            if tracked.is_filled():
                self._place_stock_hedge_once(tracked)
                return
            status = getattr(tracked, 'status', None)
            if tracked.is_canceled() or status in {Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED, Order.OrderStatus.ERROR}:
                self._finish_terminal_entry(entry_id, status)
                return
            with self._order_state_lock:
                state = self.canceling_entry_ids.get(entry_id)
                if state is None:
                    return
                if state['attempts'] >= 2:
                    self._refresh_pair_state()
                    return
                state['attempts'] += 1
            try:
                # Do not clear state here; cancel dispatch is not terminal evidence.
                self.cancel_order(tracked)
            except Exception:
                self._refresh_pair_state()
        finally:
            with self._order_state_lock:
                elapsed = max(0.0, time.monotonic() - started_monotonic)
                self._complete_reconcile(reservation, now + timedelta(seconds=elapsed))
                self._reconciling_orders -= 1

    def _reserve_reconcile(self, now):
        self._reconcile_generation += 1
        self.next_reconcile_at = now + self._broker_reconcile_backoff()
        return (self._reconcile_generation, self.next_reconcile_at)

    def _complete_reconcile(self, reservation, completed_at):
        if reservation is None or reservation[0] != self._reconcile_generation or self.next_reconcile_at != reservation[1]:
            return None
        self.next_reconcile_at = max(self.next_reconcile_at, completed_at + self._broker_reconcile_backoff())
        return (self._reconcile_generation, self.next_reconcile_at)

    def _broker_reconcile_backoff(self):
        return timedelta(seconds=self.reconcile_backoff_seconds)

    def _run_one_ordered_acquisition_step(self, acquire_original_candidate):
        """One original-priority provider step, with no unresolved risk pair.

        The strategy supplies its original acquisition/selection rules. This
        helper owns only search progress and the obligation checks around them.
        """
        if not self.scan_symbols or self._pair_is_blocking():
            return False
        index = self.scan_cursor % len(self.scan_symbols)
        symbol = self.scan_symbols[index]
        value = acquire_original_candidate(symbol)
        if self._pair_is_blocking():
            return False
        prepared = self._prepare_candidate_from_cached_evidence(symbol, value)
        if self._pair_is_blocking():
            return False
        self.scan_cursor = 0 if prepared else (index + 1) % len(self.scan_symbols)
        return bool(prepared)

    def _run_one_bounded_scan_step(self):
        deadline = time.monotonic() + 0.05
        for _ in range(min(8, len(self.scan_symbols))):
            if self._pair_is_blocking() or time.monotonic() >= deadline:
                return False
            symbol = self.scan_symbols[self.scan_cursor % len(self.scan_symbols)]
            self.scan_cursor = (self.scan_cursor + 1) % len(self.scan_symbols)
            cached = self.scan_cache.get(symbol)
            if not cached or not math.isfinite(cached['expires_at']) or cached['expires_at'] <= time.monotonic():
                continue
            prepared = self._prepare_candidate_from_cached_evidence(symbol, cached['value'])
            if time.monotonic() >= deadline:
                return False
            if prepared:
                return True
        return False

    def on_trading_iteration(self):
        now = self.get_datetime()
        if self.canceling_entry_ids:
            with self._order_state_lock:
                other_recovery = any((row['state'] != 'FILLED' for row in self.hedge_by_entry_id.values())) or bool(self.unmatched_callback_evidence and self.entry_order_ids)
                if self.next_reconcile_at is not None and now < self.next_reconcile_at:
                    return
                recover_other = other_recovery and self.reconcile_owner_cursor % 2 == 1
                if other_recovery:
                    self.reconcile_owner_cursor += 1
            if recover_other:
                self._reconcile_hedge_or_hold_blocker(now)
                return
            self._reconcile_canceling_entry(now)
            return
        if self.active_entry_order is not None and self.cancel_deadline_monotonic is not None:
            self._hold_entry_until_cancel_dispatch(self.active_entry_order, self.cancel_deadline_monotonic)
            return
        if self.pair_state in {'HEDGE_SUBMITTING', 'HEDGE_ACTIVE', 'HEDGE_FAILED', 'RECONCILE_REQUIRED'}:
            self._reconcile_hedge_or_hold_blocker(now)
            return
        if self.active_entry_order_id is not None:
            self.pair_state = 'RECONCILE_REQUIRED'
            self._reconcile_hedge_or_hold_blocker(now)
            return
        if self.unmatched_callback_evidence and self.entry_order_ids:
            self._reconcile_hedge_or_hold_blocker(now)
            if self._pair_is_blocking():
                return
        if self._run_one_bounded_scan_step():
            self.submit_entry()
        return

    def _finish_terminal_entry(self, entry_id, status):
        with self._order_state_lock:
            logical_key = self.entry_order_ids.get(entry_id)
            logical_key = logical_key if isinstance(logical_key, str) else entry_id
            if self.terminal_entry_ids.get(logical_key) == Order.OrderStatus.FILLED:
                return
            self.terminal_entry_ids.setdefault(logical_key, status)
            resolved_active = False
            for alias, key in self.entry_order_ids.items():
                if (key if isinstance(key, str) else alias) == logical_key:
                    self.canceling_entry_ids.pop(alias, None)
                    if self.active_entry_order_id == alias:
                        self.active_entry_order_id = None
                        self.active_entry_order = None
                        resolved_active = True
            if resolved_active or self.active_entry_order_id is None:
                self.cancel_deadline_monotonic = None
                if not self.canceling_entry_ids and (not self.unmatched_callback_evidence) and (not any((row['state'] != 'FILLED' for row in self.hedge_by_entry_id.values()))):
                    self.next_reconcile_at = None
                    self._reconcile_generation += 1
            self._refresh_pair_state()
