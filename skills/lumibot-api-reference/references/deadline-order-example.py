# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Complete tested lifecycle module; save unchanged as order_lifecycle.py.

Import and subclass FastOrderLifecycle from the original main.py. Adapt the
strategy inputs and scan hook there, retaining these lifecycle method bodies.

This is not an installed LumiBot class. Supply the documented selection inputs
and hooks. Partial/replacement quantities use the separate operation ledger.

When presenting this pattern, preserve the complete class below, including
_reconcile_entry and retry_confirmed_zero_fill_rejection. They implement the
verified cancel-exception fill path and bounded hedge recovery; replacing them
with a shorter illustrative class can leave a filled entry without its hedge.
``sleeptime`` schedules iterations; it cannot preempt a running
``on_trading_iteration``. Broker cancellation-confirmation latency is external
and cannot be guaranteed by this strategy.
"""
import time
from typing import Any
from threading import RLock

from lumibot.entities import Order  # type: ignore[import-not-found]
from lumibot.strategies import Strategy  # type: ignore[import-not-found]


class FastOrderLifecycle(Strategy):
    def initialize(self: Any) -> Any:
        self.sleeptime = "1S"  # cadence only; cannot preempt on_trading_iteration
        self.cancel_timeout_seconds = float(self.parameters.get("cancel_timeout_seconds", 3.0))
        self.cancel_dispatch_margin_seconds = float(self.parameters.get("cancel_dispatch_margin_seconds", 0.0))
        self.reconcile_backoff_seconds = float(self.parameters.get("reconcile_backoff_seconds", 5.0))
        self.fence = RLock()
        self.entry_order_ids: dict[str, Any] = {}  # exact accepted ID -> submitted object; retain history
        self.entry_key_aliases: dict[str, Any] = {}
        self.entry_reconciled_ids: set[str] = set()
        self.entry_reconciliation_attempts: dict[str, int] = {}
        self.reconcile_max_attempts = max(1, int(self.parameters.get("reconcile_max_attempts", 3)))
        self.hedge_reconcile_max_attempts = max(1, int(self.parameters.get("hedge_reconcile_max_attempts", 3)))
        self.hedge_inputs_by_entry_id: dict[str, Any] = {}  # original asset/quantity, including late fills
        self.canceling_entry_ids: dict[str, Any] = {}
        self.hedge_by_entry_id: dict[str, Any] = {}
        self.hedge_attempts_by_entry_id: dict[str, Any] = {}
        self.active_entry_order_id = None
        self.active_entry_order = None
        self.entry_submission_unknown = False
        self.cancel_requested = False
        self.cancel_deadline_monotonic = None
        self.next_reconcile_at = 0.0
        self.pair_state = "IDLE"
        self.scan_cursor = 0
        self.hedge_cursor = 0


    def _owned_entry_key(self: Any, order: Any) -> Any:
        if order is None:
            return None
        with self.fence:
            alias = self.entry_key_aliases.get(order.identifier)
            if alias in self.entry_order_ids:
                return alias
            for key, submitted in self.entry_order_ids.items():
                if order is submitted or (order.identifier is not None and
                                          order.identifier in {key, submitted.identifier}):
                    return key  # broker ID assignment is not a new entry
        return None


    def _pair_is_blocking(self: Any) -> Any:
        return self.pair_state != "IDLE" or self.active_entry_order_id is not None


    def _refresh_state(self: Any) -> Any:
        with self.fence:
            if self.entry_submission_unknown:
                self.pair_state = "RECONCILE_REQUIRED"
            elif self.active_entry_order_id is not None:
                self.pair_state = "CANCEL_PENDING" if self.cancel_requested else "ENTRY_ACTIVE"
            elif any(r["state"] == "FAILED" for r in self.hedge_by_entry_id.values()):
                self.pair_state = "HEDGE_FAILED"
            elif any(r["state"] != "FILLED" for r in self.hedge_by_entry_id.values()):
                self.pair_state = "HEDGE_ACTIVE"
            else:
                self.pair_state = "IDLE"

    def submit_entry(self: Any) -> Any:
        order = self.create_order(self.option_asset, self.entry_quantity, "buy",
                                  order_type=Order.OrderType.LIMIT,
                                  limit_price=self.entry_limit_price)
        with self.fence:
            if self._pair_is_blocking():
                return None
            key = order.identifier or f"pending:{id(order)}"
            self.entry_order_ids[key] = order
            self.hedge_inputs_by_entry_id[key] = (self.stock_hedge_asset, self.stock_hedge_quantity)
            self.active_entry_order_id = key
            self.active_entry_order = order
            self.entry_submission_unknown = True  # reserve BEFORE broker submission
            self.cancel_requested = False
            self.pair_state = "ENTRY_SUBMITTING"
            # Conservative fallback if acceptance is uncertain; never grant a new
            # full fill window merely because a slow submission response failed.
            self.cancel_deadline_monotonic = time.monotonic() + max(
                0.0, self.cancel_timeout_seconds - self.cancel_dispatch_margin_seconds)
        try:
            tracked = self.submit_order(order) or order
            accepted_at = time.monotonic()  # before bookkeeping or logging
        except Exception as exc:
            self.log_message(f"Entry submission unresolved: {exc}")
            self._refresh_state()  # retain submitted object and reservation
            # Acceptance may have succeeded before the transport failed. Keep
            # the original pre-submission deadline and use the same resident
            # dispatcher rather than waiting for a later trading iteration.
            tracked, accepted_at = order, None
        if tracked.identifier is None:
            self.log_message("Entry acceptance has no order identifier; retain the object and dispatch deadline")
        with self.fence:
            prior_key, key = key, tracked.identifier or key
            if prior_key != key:
                for records in (self.entry_order_ids, self.hedge_inputs_by_entry_id,
                                self.canceling_entry_ids, self.hedge_by_entry_id,
                                self.hedge_attempts_by_entry_id):
                    if prior_key in records:
                        records[key] = records.pop(prior_key)
                if self.active_entry_order_id == prior_key:
                    self.active_entry_order_id = key
            self.entry_key_aliases[prior_key] = key
            self.entry_key_aliases[key] = key
            self.entry_order_ids[key] = tracked
            if self.active_entry_order_id == key:
                self.active_entry_order = tracked
                self.entry_submission_unknown = accepted_at is None or tracked.identifier is None
                if accepted_at is not None:
                    self.cancel_deadline_monotonic = accepted_at + max(
                        0.0, self.cancel_timeout_seconds - self.cancel_dispatch_margin_seconds)
        self._refresh_state()
        while time.monotonic() < self.cancel_deadline_monotonic:
            if tracked.is_filled():
                self._place_stock_hedge_once(tracked)
                return tracked
            if tracked.is_canceled() or tracked.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                self._finish_terminal_entry(key, tracked.status)
                return tracked
            self.sleep(min(.025, max(0, self.cancel_deadline_monotonic-time.monotonic())),
                       process_pending_orders=True)
        # The broker may update the local object during the final wait.
        if tracked.is_filled():
            self._place_stock_hedge_once(tracked)
            return tracked
        if tracked.is_canceled() or tracked.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
            self._finish_terminal_entry(key, tracked.status)
            return tracked
        with self.fence:
            # Callback completion may have retired this operation after the
            # unlocked local-status observations above. Commit cancellation only
            # for the still-owned pending entry; never overwrite a later entry.
            if self.active_entry_order_id != key:
                return tracked
            if tracked.is_filled():
                self._place_stock_hedge_once(tracked)
                return tracked
            if tracked.is_canceled() or tracked.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                self._finish_terminal_entry(key, tracked.status)
                return tracked
            self.cancel_requested = True
            self.canceling_entry_ids[key] = True
            self.pair_state = "CANCEL_PENDING"
        try:
            outcome = self.cancel_order(tracked)  # no broker read before dispatch
            self._observe_cancel_outcome(outcome)
        except Exception as exc:
            self.log_message(f"Cancellation unresolved: {exc}")
            # The cancel may have raced a fill. Consume this entry's single
            # exact-order fallback after dispatch, never before the deadline.
            self._reconcile_entry(force=True)
        # Do not clear state here: cancellation is still unresolved.
        # Schwab may already have updated this object or queued a callback.
        if tracked.is_filled():
            self._place_stock_hedge_once(tracked)
        with self.fence:
            if self.active_entry_order_id == key:
                self.next_reconcile_at = time.monotonic() + self.reconcile_backoff_seconds
        return tracked  # caller MUST return from scanning/iteration

    def _observe_cancel_outcome(self: Any, outcome: Any) -> Any:
        observed = outcome.get("order") if isinstance(outcome, dict) else outcome
        if observed is not None and callable(getattr(observed, "is_filled", None)):
            key = self._owned_entry_key(observed)
            if key is None:
                return
            if observed.is_filled():
                self._place_stock_hedge_once(observed)
            elif observed.is_canceled() or observed.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                self._finish_terminal_entry(key, observed.status)
        elif isinstance(outcome, dict):
            status = outcome.get("status")
            if str(getattr(status, "value", status)).lower() == "filled":
                # A structured filled response triggers a verified order read;
                # do not fabricate quantities or infer fills from error prose.
                self._reconcile_entry(force=True, allow_retry=True)


    def _place_stock_hedge_once(self: Any, filled_entry: Any, *, allow_retry: Any=False) -> Any:
        with self.fence:
            key = self._owned_entry_key(filled_entry)
            if key is None:
                return False
            inputs = self.hedge_inputs_by_entry_id.get(key)
            if inputs is None:
                # Never guess an old entry's selection from today's mutable inputs.
                self.hedge_by_entry_id.setdefault(key, {
                    "state": "FAILED", "order": None, "hedge_order_id": None,
                    "reason": "Original hedge inputs require reconciliation",
                    "preparation_only": True, "confirmed_terminal": False, "failures": [],
                })
                self._refresh_state()
                return False
            hedge_asset, hedge_quantity = inputs
            previous = self.hedge_by_entry_id.get(key)
            if previous is not None:
                if (not allow_retry or previous["state"] != "FAILED"
                        or self.hedge_attempts_by_entry_id.get(key, 0) >= 2):
                    return False
                order = previous.get("order")
                if not previous.get("preparation_only") and (
                        not previous.get("confirmed_terminal") or order is None
                        or order.status not in {Order.OrderStatus.ERROR, Order.OrderStatus.CANCELED, Order.OrderStatus.EXPIRED}
                        or order.transactions):
                    return False
            elif allow_retry:
                return False  # no confirmed prior failure to recover
            failures = list(previous.get("failures", [])) if previous else []
            if previous:
                old = previous.get("order")
                failures.append({"reason": previous.get("reason"),
                                 "order_id": old.identifier if old else None})
            record = {"state": "SUBMITTING", "order": None, "hedge_order_id": None,
                      "preparation_only": True, "confirmed_terminal": False,
                      "failures": failures}
            # Atomic replacement retains a blocking record throughout recovery.
            self.hedge_by_entry_id[key] = record
            self.hedge_attempts_by_entry_id[key] = self.hedge_attempts_by_entry_id.get(key, 0) + 1
            if self.active_entry_order_id == key:
                self.active_entry_order_id = None
                self.entry_submission_unknown = False
            self._refresh_state()
        try:
            hedge = self.create_order(hedge_asset, hedge_quantity, "sell",
                                      order_type=Order.OrderType.MARKET)
            with self.fence:
                record["order"] = hedge
                record["preparation_only"] = False
            hedge = self.submit_order(hedge) or hedge
            with self.fence:
                if record["state"] != "FILLED":
                    record["order"] = hedge
                    record["hedge_order_id"] = hedge.identifier
                if record["state"] == "SUBMITTING":
                    if hedge.status == Order.OrderStatus.ERROR:
                        record.update(state="FAILED", reason=hedge.error_message,
                                      confirmed_terminal=True)
                    else:
                        record["state"] = "ACTIVE"
        except Exception as exc:
            with self.fence:
                if record["state"] != "FILLED":
                    record.update(state="FAILED", reason=str(exc))
        self._refresh_state()
        return True  # attempt claimed; this does not mean the hedge filled


    def on_filled_order(self: Any, position: Any, order: Any, price: Any, quantity: Any, multiplier: Any) -> Any:
        if order is None:
            return
        if self._owned_entry_key(order) is not None:
            self._place_stock_hedge_once(order)  # authoritative callback; no GET
            return
        with self.fence:
            for record in self.hedge_by_entry_id.values():
                hedge = record.get("order")
                if hedge is not None and (order is hedge or (hedge.identifier is not None
                                                           and hedge.identifier == order.identifier)):
                    record.update(state="FILLED", order=order, hedge_order_id=order.identifier,
                                  confirmed_terminal=True)
                    self._refresh_state()
                    return


    def _finish_terminal_entry(self: Any, key: Any, status: Any) -> Any:
        with self.fence:
            if str(getattr(status, "value", status)).lower() not in {
                    "canceled", "cancelled", "expired", "error", "rejected"}:
                return  # a callback name alone cannot prove broker-terminal status
            self.canceling_entry_ids.pop(key, None)
            # Keep entry_order_ids: a later fill still belongs to the original entry.
            if self.active_entry_order_id == key:
                self.active_entry_order_id = None
                self.active_entry_order = None
                self.entry_submission_unknown = False
                self.cancel_requested = False
            self._refresh_state()  # cannot release an unresolved hedge


    def on_canceled_order(self: Any, order: Any) -> Any:
        key = self._owned_entry_key(order)
        if key is None:
            return
        if order.is_filled():
            self._place_stock_hedge_once(order)
        else:
            self._finish_terminal_entry(key, order.status)


    def _reconcile_entry(self: Any, *, force: bool=False, allow_retry: bool=False) -> Any:
        with self.fence:
            key = self.active_entry_order_id
            if key is None:
                return
            submitted = self.entry_order_ids[key]
            recovery_cancel_due = (
                not self.cancel_requested and self.cancel_deadline_monotonic is not None
                and time.monotonic() >= self.cancel_deadline_monotonic)
            if not recovery_cancel_due and not force and time.monotonic() < self.next_reconcile_at:
                return
            attempts = self.entry_reconciliation_attempts.get(key, 0)
            if not recovery_cancel_due and key in self.entry_reconciled_ids and (
                    not allow_retry or attempts >= self.reconcile_max_attempts):
                return
            if recovery_cancel_due:
                self.cancel_requested = True
                self.canceling_entry_ids[key] = True
                self._refresh_state()
            else:
                if submitted.identifier is None:
                    return  # no identifier for a GET; retain callbacks and blocker
                self.entry_reconciled_ids.add(key)  # one read in this permitted recovery pass
                self.entry_reconciliation_attempts[key] = attempts + 1
            self.next_reconcile_at = time.monotonic() + self.reconcile_backoff_seconds
        if recovery_cancel_due:
            try:
                # A recovery cancel also dispatches BEFORE any broker read.
                outcome = self.cancel_order(submitted)
                self._observe_cancel_outcome(outcome)
            except Exception as exc:
                self.log_message(f"Recovery cancellation unresolved: {exc}")
                # Verify a possible raced fill after dispatch. Exception prose
                # alone is never fill evidence; use the common hedge owner.
                self._reconcile_entry(force=True, allow_retry=True)
            self._refresh_state()
            return  # a later backed-off pass may read this exact order
        try:
            order = self.get_order(submitted.identifier)  # current broker ID, one read
        except Exception:
            return  # unavailable/429 is not a terminal result
        if order is None:
            return
        with self.fence:
            self.entry_order_ids[key] = order
            if self.active_entry_order_id == key:
                self.entry_submission_unknown = False
        if order.is_filled():
            self._place_stock_hedge_once(order)
        elif order.is_canceled() or order.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
            self._finish_terminal_entry(key, order.status)
        else:
            self._refresh_state()  # CANCELLING/PENDING_CANCEL remain blocking


    def _reconcile_hedge_or_hold_blocker(self: Any, *, allow_retry: bool=False) -> Any:
        if time.monotonic() < self.next_reconcile_at:
            return
        self.next_reconcile_at = time.monotonic() + self.reconcile_backoff_seconds
        with self.fence:
            pending = [(key, record) for key, record in self.hedge_by_entry_id.items()
                       if record["state"] != "FILLED"]
        if not pending:
            self._refresh_state()
            return
        key, record = pending[self.hedge_cursor % len(pending)]
        self.hedge_cursor += 1
        if allow_retry and record["state"] == "FAILED" and (
                record.get("preparation_only") or record.get("confirmed_terminal")):
            # The common owner still requires confirmed zero fill (or proof no
            # submission happened), and permits at most two hedge attempts.
            self.retry_confirmed_zero_fill_rejection(key)
            return
        tracked = record.get("order")
        if tracked is None:
            return  # preparation/uncertain response requires explicit recovery evidence
        exhausted_now = False
        with self.fence:
            if record["state"] == "FILLED":
                return
            attempts = record.get("reconciliation_attempts", 0)
            if attempts >= self.hedge_reconcile_max_attempts:
                exhausted_now = not record.get("reconciliation_exhausted", False)
                record["reconciliation_exhausted"] = True
                record["reconciliation_reason"] = "Automatic exact-order read budget exhausted; explicit resumption required"
            else:
                record["reconciliation_attempts"] = attempts + 1
                record["reconciliation_total_attempts"] = record.get("reconciliation_total_attempts", 0) + 1
        if record.get("reconciliation_exhausted"):
            if exhausted_now:
                self.log_message(record["reconciliation_reason"])
            return  # retain native order, original failure and blocking obligation
        try:
            observed = self.get_order(tracked.identifier)  # one exact hedge per pass
        except Exception:
            return
        if observed is None:
            return
        reason = None
        with self.fence:
            if record["state"] == "FILLED":
                return  # a full-fill callback may have arrived during this GET
            record["order"] = observed
            record["hedge_order_id"] = observed.identifier
            if observed.is_filled():
                self.on_filled_order(None, observed, None, None, None)
            elif observed.is_canceled() or observed.status in {Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                reason = observed.error_message or str(observed.status)
                record.update(state="FAILED", reason=reason, confirmed_terminal=True)
                self._refresh_state()
        if reason is not None:
            self.log_message(f"Hedge unresolved: {reason}")


    def resume_hedge_reconciliation(self: Any, key: Any) -> bool:
        """Explicit recovery request grants another bounded read batch, never a submission."""
        with self.fence:
            record = self.hedge_by_entry_id.get(key)
            if (record is None or record["state"] == "FILLED"
                    or record.get("order") is None or not record.get("reconciliation_exhausted")):
                return False
            record["reconciliation_attempts"] = 0
            record["reconciliation_exhausted"] = False
            record["reconciliation_reason"] = "Explicitly resumed exact-order verification"
        return True


    def retry_confirmed_zero_fill_rejection(self: Any, key: Any) -> Any:
        with self.fence:
            entry = self.entry_order_ids.get(key)
            if entry is None:
                return False  # retain the failed obligation when attribution is absent
            previous = self.hedge_by_entry_id.get(key)
            attempts_before = self.hedge_attempts_by_entry_id.get(key, 0)
        # The common owner checks recovery evidence and atomically replaces the
        # failed record before releasing the fence. Broker I/O remains outside it.
        if self._place_stock_hedge_once(entry, allow_retry=True):
            return True
        with self.fence:
            # Another recovery pass may have claimed the same bounded attempt
            # while this request was entering the common owner. Report that
            # existing claim without submitting again or declaring a fill.
            return (self.hedge_by_entry_id.get(key) is not previous and
                    self.hedge_attempts_by_entry_id.get(key, 0) > attempts_before)


    def _run_one_bounded_scan_step(self: Any) -> Any:
        """Override with the original strategy's selection and pricing rules.

        Select an Asset, not a quote mapping. Assign option_asset,
        entry_quantity, entry_limit_price, stock_hedge_asset and
        stock_hedge_quantity, call submit_entry(), then return immediately.
        The inherited iteration handles pending orders before this hook.
        """
        raise NotImplementedError('Implement selection from the original strategy')


    def on_trading_iteration(self: Any) -> Any:
        if self.active_entry_order_id is not None:
            # A failed/missing/nonterminal observation does not consume recovery
            # forever. Later iterations may make one backed-off read, up to the
            # configured finite budget; exhaustion never clears the blocker.
            self._reconcile_entry(allow_retry=True)
            return
        if self._pair_is_blocking():
            self._reconcile_hedge_or_hold_blocker(allow_retry=True)
            return
        self._run_one_bounded_scan_step()
