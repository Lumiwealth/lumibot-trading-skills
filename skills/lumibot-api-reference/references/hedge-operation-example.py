# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""A full-fill hedge component, copied into a Strategy rather than imported from LumiBot.

Register only entries this strategy actually submitted. No entry is submitted
by registration. Callbacks and one backed-off exact-order read share the claim.
FAILED/UNKNOWN remain blocked for an operator decision: no automatic retry is
implemented or promised. Partial fills/replacements need the quantity ledger.
Persist the records with the strategy's normal state to support restart recovery;
this in-memory example does not establish restart recovery on its own.

When saving a repair that uses this component, report execution readiness from
the LAST successful file mutation's exact revision, never an earlier revision.
If that newest result says analysis unavailable or backtest/live unknown, state
that readiness is unknown. A get_file staticCheck.ok proves syntax only and
cannot turn that result into "marked backtest-ready". The save still succeeded;
report the repaired saved behavior and any unverified execution separately.
"""
import time
from typing import Any
from threading import RLock
from uuid import uuid4

from lumibot.entities import Order  # type: ignore[import-not-found]
from lumibot.strategies import Strategy  # type: ignore[import-not-found]


class HedgeAfterFullFill(Strategy):
    def initialize(self: Any) -> Any:
        self._hedge_lock = RLock()
        self._pairs: dict[str, Any] = {}
        self._pair_cursor = 0
        self.sleeptime = "1S"

    def register_entry(self: Any, submitted_entry: Any, hedge_asset: Any, hedge_quantity: Any, hedge_side: Any='sell', **hedge_order_kwargs: Any) -> Any:
        with self._hedge_lock:
            key = self._entry_key(submitted_entry)
            if key is not None:
                return key  # registration cannot erase an existing claim
            key = str(uuid4())
            self._pairs[key] = {
                "entry": submitted_entry, "entry_filled": False,
                "asset": hedge_asset, "quantity": hedge_quantity,
                "side": hedge_side, "kwargs": dict(hedge_order_kwargs),
                "state": "WAITING", "hedge": None, "reason": None, "failures": [],
                "next_check": 0.0,
            }
        if submitted_entry.is_filled():
            self._entry_filled(submitted_entry)
        return key

    def _entry_key(self: Any, order: Any) -> Any:
        if order is None:
            return None
        with self._hedge_lock:
            for key, pair in self._pairs.items():
                entry = pair["entry"]
                if order is entry or (order.identifier is not None
                                          and order.identifier == entry.identifier):
                    return key
        return None

    def _entry_filled(self: Any, entry: Any) -> Any:
        with self._hedge_lock:
            key = self._entry_key(entry)
            if key is None:
                return
            pair = self._pairs[key]
            pair["entry"], pair["entry_filled"] = entry, True
            if pair["state"] != "WAITING":
                return
            pair["state"] = "PREPARING"  # claim before preparation or broker I/O
            asset, quantity, side, kwargs = (pair["asset"], pair["quantity"],
                                             pair["side"], pair["kwargs"])
        try:
            hedge = self.create_order(asset, quantity, side, **kwargs)
        except Exception as exc:
            with self._hedge_lock:
                pair.update(state="FAILED", reason=f"Preparation failed: {exc}")
                pair["failures"].append(pair["reason"])
            return
        with self._hedge_lock:
            # Retain the native object BEFORE submit: its identifier may change.
            pair.update(hedge=hedge, state="SUBMITTING")
        try:
            submitted = self.submit_order(hedge) or hedge
        except Exception as exc:
            with self._hedge_lock:
                if pair["state"] != "FILLED":
                    pair.update(state="UNKNOWN", reason=str(exc))
                    pair["failures"].append(pair["reason"])
                pair["next_check"] = time.monotonic() + 5.0
            return
        self._hedge_observed(pair, submitted)

    def _hedge_observed(self: Any, pair: Any, observed: Any) -> Any:
        if observed is None:
            return
        with self._hedge_lock:
            if pair["state"] == "FILLED":
                return  # a stale read cannot undo a confirmed callback
            pair["hedge"] = observed
            if observed.is_filled():
                pair["state"] = "FILLED"
            elif observed.is_canceled() or observed.status in {
                    Order.OrderStatus.ERROR, Order.OrderStatus.EXPIRED}:
                reason = observed.error_message or str(observed.status)
                pair.update(state="FAILED", reason=reason)
                if not pair["failures"] or pair["failures"][-1] != reason:
                    pair["failures"].append(reason)
            elif pair["state"] in {"SUBMITTING", "ACTIVE", "UNKNOWN"}:
                pair["state"] = "ACTIVE"
            pair["next_check"] = time.monotonic() + 5.0

    def on_filled_order(self: Any, position: Any, order: Any, price: Any, quantity: Any, multiplier: Any) -> Any:
        if order is None:
            return
        if self._entry_key(order) is not None:
            self._entry_filled(order)  # callback already supplies authoritative evidence
            return
        with self._hedge_lock:
            for pair in self._pairs.values():
                hedge = pair["hedge"]
                if hedge is not None and (order is hedge or (order.identifier is not None
                                                and order.identifier == hedge.identifier)):
                    pair.update(hedge=order, state="FILLED")
                    return

    def reconcile_pair_once(self: Any, key: Any) -> Any:
        now = time.monotonic()
        with self._hedge_lock:
            pair = self._pairs.get(key)
            if pair is None or now < pair["next_check"]:
                return
            # A filled entry must not exclude its unfinished hedge from polling.
            is_entry = not pair["entry_filled"]
            target = pair["entry"] if is_entry else pair["hedge"]
            if pair["state"] == "FILLED" or target is None:
                return
            pair["next_check"] = now + 5.0
            identifier = target.identifier
            if identifier is None:
                pair["reason"] = pair["reason"] or "Owned order identity needs operator reconciliation"
                return
        try:
            observed = self.get_order(identifier)
        except Exception:
            return  # unavailable/429 is not evidence to release or resubmit
        if observed is None:
            return
        if is_entry:
            if observed.is_filled():
                self._entry_filled(observed)
        else:
            self._hedge_observed(pair, observed)

    def on_trading_iteration(self: Any) -> Any:
        with self._hedge_lock:
            keys = list(self._pairs)
            if not keys:
                return
            key = keys[self._pair_cursor % len(keys)]
            self._pair_cursor += 1
        self.reconcile_pair_once(key)  # one backed-off exact-order read per pass
