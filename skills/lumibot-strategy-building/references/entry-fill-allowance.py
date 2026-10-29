# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Daily filled-entry allowance: use the complete lifecycle owner first.

Use EntryOrderLifecycle.for_strategy(self) once during initialization. Keep the
owner on the strategy object and only its plain state in self.vars. Include
this reference's implementation in the saved strategy; it is not an SDK import.

Wiring inside the EXISTING strategy:
  initialize: self.entries = EntryOrderLifecycle.for_strategy(self)
  iteration, BEFORE eligibility: self.entries.refresh(current_session)
  after unchanged signal/position checks, prepare the original sized order:
      self.entries.submit_new(order, current_session, configured_daily_limit)
  each partial/full-fill or canceled callback:
      self.entries.observe(order, current_session)
Use the actual trading-session key consistently, not a lifetime flag. Refresh
also reconciles terminal orders whose callback was missed.

The owner replaces the filled-entry allowance's old submission counter/reset
logic. Remove that counter from entry eligibility and submission increments;
keeping both owners can permanently block valid retries after cancellation.
submit_new returning True means ONE publication, not a fill. A confirmed no-fill
cancellation/rejection frees its reservation, while a first partial execution
consumes one logical entry. A replacement's quantity/ownership reconciliation
is separate; preserve the original position and exposure checks.

Preserve the existing imports, signal logic, sizing, and executable backtest/live
entry point when incorporating the owner. This component is not a whole-file
strategy replacement. If a placeholder lacks a runnable entry point, complete
the supported strategy scaffold before starting the requested validation; a
readiness warning is a repair task, not completion of an authorized repair.

The lower-level EntryFillAllowance is for an EXISTING equivalent order owner:
reserve the logical entry BEFORE IO, keep replacement attempts under that same
entry identity, and observe every actual execution and terminal transition.
Do not combine half of that adapter with a second submission-based allowance.
LumiBot Order.transactions contain quantity/price, not an execution timestamp.
When an exact first-fill date is unavailable, first observation is an UPPER
bound; reserve that session and disclose the bound, rather than inventing a
historical date or consuming every future session forever. Persist across
restart. Unknown dispatch retains its reservation until actual reconciliation.
"""


from threading import RLock
from typing import Any, NotRequired, TypedDict, cast


class EntryRecord(TypedDict):
    first_fill_session: str | None
    fill_seen: bool
    attempts: dict[str, str]
    first_fill_upper_session: NotRequired[str]


class AllowanceState(TypedDict, total=False):
    entries: dict[str, EntryRecord]
    order_aliases: dict[str, str]
    order_lookups: dict[str, str]


class EntryFillAllowance:
    TERMINAL = frozenset({"filled", "canceled", "cancelled", "rejected", "expired", "error"})

    def __init__(self, state: AllowanceState) -> None:
        self._lock = RLock()
        self.state = state
        self.state.setdefault("entries", {})

    def reserve(self, entry_id: str, order_id: str) -> None:
        with self._lock:
            entry = self.state["entries"].setdefault(
                str(entry_id), {"first_fill_session": None, "fill_seen": False, "attempts": {}})
            entry["attempts"].setdefault(str(order_id), "pending")

    def observe(self, entry_id: str, order_id: str, *, status: str, first_fill_session: str | None = None,
                observed_session: str | None = None, has_execution: bool = False) -> None:
        with self._lock:
            self.reserve(entry_id, order_id)
            entry = self.state["entries"][str(entry_id)]
            normalized = str(getattr(status, 'value', status)).lower()
            normalized = {'fill': 'filled', 'partial_fill': 'partially_filled',
                          'cancelled': 'canceled'}.get(normalized, normalized)
            prior_status = entry['attempts'][str(order_id)]
            if prior_status not in self.TERMINAL or normalized in self.TERMINAL:
                entry["attempts"][str(order_id)] = normalized
            if normalized in {"filled", "partially_filled"} or first_fill_session is not None or has_execution:
                entry["fill_seen"] = True
            if entry['fill_seen'] and observed_session is not None:
                prior_upper = entry.get('first_fill_upper_session')
                entry['first_fill_upper_session'] = min(prior_upper, str(observed_session)) if prior_upper else str(observed_session)
            if first_fill_session is not None:
                prior = entry["first_fill_session"]
                entry["first_fill_session"] = min(prior, str(first_fill_session)) if prior else str(first_fill_session)

    def observe_order(self, entry_id: str, order: Any, *, observed_session: str,
                      first_fill_session: str | None = None) -> None:
        """Use actual Order status/transactions; never guess an execution date."""
        self.observe(entry_id, str(order.identifier), status=order.status,
                     observed_session=observed_session, first_fill_session=first_fill_session,
                     has_execution=any(float(fill.quantity) > 0 for fill in order.transactions))

    def used_or_reserved(self, session: str) -> int:
        with self._lock:
            session = str(session)
            count = 0
            for entry in self.state["entries"].values():
                first = entry["first_fill_session"]
                if first == session:
                    count += 1
                elif first is None:
                    attempts = entry["attempts"].values()
                    # An unresolved old attempt may first fill in this session.
                    # A filled status without its execution date is unresolved
                    # evidence, never permission to reopen capacity after restart.
                    upper = entry.get('first_fill_upper_session')
                    unknown_execution = entry.get("fill_seen") and (upper is None or session <= upper)
                    if unknown_execution or (not entry.get('fill_seen') and any(status not in self.TERMINAL for status in attempts)):
                        count += 1
            return count

    def can_submit(self, session: str, maximum_new_entries: int) -> bool:
        """Diagnostic only; publish only after try_reserve_new_entry succeeds."""
        return self.used_or_reserved(session) < maximum_new_entries

    def try_reserve_new_entry(self, entry_id: str, order_id: str, session: str, maximum_new_entries: int) -> bool:
        with self._lock:
            if str(entry_id) in self.state["entries"]:
                return False
            if not self.can_submit(session, maximum_new_entries):
                return False
            self.reserve(entry_id, order_id)
            return True


class EntryOrderLifecycle:
    """Complete submission/observation wiring; caller supplies the trading decision.

    Use ``self.entries = EntryOrderLifecycle.for_strategy(self)`` once, then use:
      iteration: lifecycle.refresh(current_session) before eligibility checks
      eligible: lifecycle.submit_new(prepared_order, current_session, daily_cap)
      partial/full/cancel callback: lifecycle.observe(order, current_session)
    submit_new returns False if there is no allowance, otherwise submits once.
    Do not wrap its exception with a reservation release: acceptance can be
    unknown. Reconcile through actual orders. This owner retains ID aliases
    and state on restart; order quantities and signal policy stay with caller.
    """

    @classmethod
    def for_strategy(cls, strategy: Any, state_name: str = "entry_lifecycle_state") -> "EntryOrderLifecycle":
        # Vars has get/set and attributes; it is not a dict. Persist only plain
        # state there, never this owner, its locks or the Strategy reference.
        state = strategy.vars.get(state_name)
        if state is None:
            state = {}
            strategy.vars.set(state_name, state)
        if not isinstance(state, dict):
            raise ValueError("Entry lifecycle state must be a plain persistent mapping")
        return cls(strategy, cast(AllowanceState, state))

    def __init__(self, strategy: Any, state: AllowanceState) -> None:
        self.strategy, self.state = strategy, state
        self.allowance = EntryFillAllowance(state)
        self.aliases: dict[str, str] = state.setdefault('order_aliases', {})
        self.lookups: dict[str, str] = state.setdefault('order_lookups', {})
        self._objects: dict[str, list[Any]] = {}
        self._lock = RLock()

    def _bind(self, entry_id: str, order: Any) -> None:
        identifier = str(order.identifier)
        self.aliases[identifier] = entry_id
        prior = self.lookups.get(entry_id, entry_id)
        if prior == entry_id or identifier != entry_id:
            self.lookups[entry_id] = identifier
        objects = self._objects.setdefault(entry_id, [])
        if not any(o is order for o in objects):
            objects.append(order)

    def observe(self, order: Any, session: str) -> None:
        with self._lock:
            entry_id = self.aliases.get(str(order.identifier))
            if entry_id is None:
                entry_id = next((key for key, values in self._objects.items()
                                 if any(o is order for o in values)), None)
            if entry_id is None:
                return  # an unrelated owned order, never an inferred entry
            identity = str(order.identifier)
            canonical = self.lookups.get(entry_id)
            has_execution = any(float(fill.quantity) > 0 for fill in order.transactions)
            if canonical is not None and canonical != identity and self.aliases.get(identity) == entry_id:
                # An older alias can carry a late execution, but its status
                # cannot retire or displace the current broker attempt.
                current_status = self.allowance.state['entries'][entry_id]['attempts'].get(entry_id, 'unknown')
                self.allowance.observe(entry_id, entry_id, status=current_status,
                    observed_session=session, has_execution=has_execution)
                return
            self._bind(entry_id, order)
            self.allowance.observe(entry_id, entry_id, status=order.status,
                observed_session=session, has_execution=has_execution)

    def refresh(self, session: str) -> None:
        with self._lock:
            for entry_id, record in list(self.allowance.state['entries'].items()):
                # Terminal status can precede execution details. Keep polling
                # unfilled records; one later fill still consumes its entry slot.
                if record['fill_seen'] and all(
                        s in self.allowance.TERMINAL for s in record['attempts'].values()):
                    continue
                order = self.strategy.get_order(self.lookups.get(entry_id, entry_id))
                if order is not None:
                    self.observe(order, session)

    def submit_new(self, order: Any, session: str, maximum_new_entries: int) -> bool:
        with self._lock:
            entry_id = str(order.identifier)
            if not self.allowance.try_reserve_new_entry(entry_id, entry_id, session, maximum_new_entries):
                return False
            self._bind(entry_id, order)
            try:
                returned = self.strategy.submit_order(order)
            except Exception:
                self._bind(entry_id, order)
                raise  # retain UNKNOWN acceptance, never fabricate rejection
            self._bind(entry_id, order)
            if returned is not None:
                self._bind(entry_id, returned)
                self.observe(returned, session)
            else:
                self.observe(order, session)
            return True
