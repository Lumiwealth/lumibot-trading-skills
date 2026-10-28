# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Copyable confirmed native leg and package accounting; no trading policy or IO."""
from decimal import Decimal
from typing import Any
from dataclasses import dataclass, field

def confirmed_leg_fill(order: Any) -> tuple[Decimal, float] | None:
    from decimal import Decimal
    from math import isfinite
    if not order.is_filled():
        return None
    price = order.get_fill_price()
    if price is None or not isfinite(float(price)):
        return None
    fills = order.transactions
    quantity = sum((abs(Decimal(str(fill.quantity))) for fill in fills), Decimal(0))
    if not fills and order.avg_fill_price is not None:
        quantity = abs(Decimal(str(order.quantity)))
    if quantity != abs(Decimal(str(order.quantity))):
        return None
    return quantity, float(price)


def confirmed_package_cost(orders: list[Any]) -> float | None:
    from decimal import Decimal
    if not orders:
        return None
    total = Decimal(0)
    for order in orders:
        observed = confirmed_leg_fill(order)
        if observed is None:
            return None
        quantity, price = observed
        if order.is_buy_order():
            direction = Decimal(1)
        elif order.is_sell_order():
            direction = Decimal(-1)
        else:
            return None
        total += direction * quantity * Decimal(str(price)) * Decimal(str(order.asset.multiplier))
    return float(total)



def confirmed_debit_exit_target(entry_cost: Any, multiple: float) -> float | None:
    """A debit-based value target stays undefined for missing/zero/credit cost.

    Call at the actual exit decision, not only when recording the entry fill:
        target = confirmed_debit_exit_target(confirmed_entry_cost, requested_multiple)
        if target is None:
            return  # retain the package; do not invent a credit/zero-cost policy
        if signed_liquidation_value >= target:
            ...  # submit the complete owned package through its existing exit owner

    Logging an undefined target at entry while leaving OPEN plus a nonpositive
    stored cost is insufficient: the later exit branch must preserve None.
    This does not replace a separately specified credit-strategy exit policy.
    """
    from math import isfinite
    try:
        debit, factor = float(entry_cost), float(multiple)
        target = debit * factor
        return target if debit > 0 and factor > 0 and all(map(isfinite, (debit, factor, target))) else None
    except (TypeError, ValueError, OverflowError):
        return None


def confirmed_package_exit_state(exit_orders: list[Any], leg_positions: list[Any]) -> str:
    """Reconcile a retained combined exit; submission acceptance is not closure.

    Keep the exact closing Order objects BEFORE execute_orders. On every later
    iteration, refresh those owned orders (or use their authoritative callback
    updates) and read every original leg's current position, then call this
    function BEFORE an exit_sent/EXIT_SUBMITTED early return. A failed read
    retains the operation; it must not be replaced with an invented flat value.

    active: keep the same exit, never submit a duplicate.
    unresolved: retain all orders/exposure and obtain the missing observation.
    incomplete: orders are terminal but exposure remains; preserve that outcome
        and reconcile the remaining whole package through the existing exit
        owner. This is not a completed flat exit.
    closed: every exit is terminal and every leg is observed flat; retire that
        active package while preserving its history and the daily entry policy.

    Do not set an exit-completed flag merely because execute_orders returned
    True. Historical next-session expiry settlement does not replace this
    intraday reconciliation.
    """
    if not exit_orders or not leg_positions:
        return "unresolved"
    active = {"unprocessed", "submitted", "open", "new", "cancelling", "partial_fill"}
    terminal = {"fill", "filled", "canceled", "cancelled", "error", "expired"}
    statuses = [str(getattr(order.status, "value", order.status)).lower() for order in exit_orders]
    if any(status in active for status in statuses):
        return "active"
    if any(status not in terminal for status in statuses):
        return "unresolved"
    try:
        flat = all(position is None or Decimal(str(position.quantity)) == 0
                   for position in leg_positions)
    except (AttributeError, ArithmeticError, TypeError, ValueError):
        return "unresolved"
    return "closed" if flat else "incomplete"



def package_with_time_in_force(orders: list[Any], selected_time_in_force: str) -> list[Any]:
    """Apply the selected order policy to every exact owned leg, before submit.

    Verified SDK detail: OptionsHelper.build_ratio_spread_orders calls
    Strategy.create_order without a time_in_force argument. That strategy
    method defaults to GTC (the lower-level Order constructor's DAY default
    does not apply). A built ratio package is therefore NOT implicitly DAY.

    When the strategy chooses DAY and relies on the historical DAY expiry
    boundary below, prepare the complete entry package explicitly:
        combined_orders = package_with_time_in_force(put_orders + call_orders, "day")
        options_helper.execute_orders(combined_orders)
    Keep that same list/objects/IDs for fill and later-session reconciliation.
    Apply the selected policy to complete closing packages as well.

    Preserve an explicitly requested GTC policy instead of overwriting it;
    those packages need observed terminal order/position reconciliation and
    cannot use an unqualified next-date reset. This helper does not submit,
    clone, cancel, discard or mark any order filled.
    """
    for order in orders:
        order.time_in_force = selected_time_in_force
    return orders


def historical_day_package_settled(
    leg_assets: list[Any], owned_orders: list[Any], session_date: Any,
    *, historical_pandas_backtest: bool, cash_settled: bool,
) -> bool:
    """Recognize the verified historical expiry boundary before daily entry.

    The native pandas backtesting owner cash-settles expired cash-settled
    options and expires DAY orders at session close. A later session therefore
    must not remain blocked by that prior package's OPEN, OPEN_UNPRICED,
    ENTRY_SUBMITTED or EXIT_SUBMITTED label. Call before those early returns.
    Both flags must describe the actual selected execution/instruments.

    On True, retire the entire prior package together: package_state=FLAT,
    package_orders=[], exit_orders=[], package_legs=[], entry_debit=None, plus
    the normal per-day entry/exit flags. Preserve completed history. Then
    capture this session's open and apply its original entry-minute policy.
    Resetting only the date/open price while retaining the old active package
    silently disables later days. Net-credit packages and expired unfilled
    DAY entries need this same terminal cleanup.

    False retains the operation for actual order/position reconciliation. Never
    use this historical boundary for live trading, GTC, later expirations,
    noncash-settled options or a different execution owner. Intraday exit
    reconciliation remains required before this boundary has occurred.
    """
    if not historical_pandas_backtest or not cash_settled or not leg_assets or not owned_orders:
        return False
    try:
        for asset in leg_assets:
            expiry = asset.expiration
            if hasattr(expiry, "date"):
                expiry = expiry.date()
            if expiry is None or expiry >= session_date:
                return False
        return all(str(getattr(order.time_in_force, "value", order.time_in_force)).lower() == "day"
                   for order in owned_orders)
    except (AttributeError, TypeError, ValueError):
        return False


@dataclass
class PackageSessionState:
    """One owner for all active package fields and their verified day rollover.

    Keep package operation state HERE rather than splitting date flags from
    separate strategy.vars.package_state/entry_orders/assets/cost variables.
    A partial daily reset leaves the old OPEN/ENTRY_PENDING package blocking
    the new day's capture and entry. Clearing only the date is not a reset.

    Initialize strategy.vars.package = PackageSessionState(). At the start of
    each iteration, before any active-package early return:
        package = self.vars.package
        prior_day = package.session_date
        if not package.begin_historical_day(today,
                historical_pandas_backtest=actual_pandas_backtest,
                cash_settled=actual_cash_settled_instruments):
            return  # retain and reconcile the still-unresolved old operation
        if prior_day != package.session_date:
            ...  # reset this strategy's daily open/cadence/marker variables

    Use package.state, package.assets, package.entry_orders, package.exit_orders
    and package.entry_cost throughout the executed entry/exit paths. Do not keep
    a second independent set of active-package fields beside this owner.
    Record complete DAY-policy entry/exit lists with package_with_time_in_force
    when relying on this historical DAY boundary. Trading rules, entry times,
    valuation, target choice and actual submission remain the strategy's job.
    """
    session_date: Any = None
    state: str = "FLAT"
    assets: list[Any] = field(default_factory=list)
    entry_orders: list[Any] = field(default_factory=list)
    exit_orders: list[Any] = field(default_factory=list)
    entry_cost: float | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def begin_historical_day(self, today: Any, *, historical_pandas_backtest: bool, cash_settled: bool) -> bool:
        if self.session_date == today:
            return True
        empty = self.state in {"FLAT", "CLOSED"} and not (self.assets or self.entry_orders or self.exit_orders)
        # Retained entry identity does not depend on a positive debit. A credit,
        # zero cost or unknown price cannot erase the expiry of owned orders.
        owned_assets = self.assets or [getattr(order, "asset", None) for order in self.entry_orders]
        if not empty and not historical_day_package_settled(
                owned_assets, self.entry_orders + self.exit_orders, today,
                historical_pandas_backtest=historical_pandas_backtest, cash_settled=cash_settled):
            return False
        if self.assets or self.entry_orders or self.exit_orders or self.entry_cost is not None:
            self.history.append({"session_date": self.session_date, "state": self.state,
                "assets": owned_assets.copy(), "entry_orders": self.entry_orders.copy(),
                "exit_orders": self.exit_orders.copy(), "entry_cost": self.entry_cost})
        self.session_date, self.state, self.assets, self.entry_orders, self.exit_orders, self.entry_cost = (
            today, "FLAT", [], [], [], None)
        return True

    def prepare_submission(self, phase: str, orders: list[Any]) -> None:
        """Retain the exact built legs BEFORE calling execute_orders once."""
        if phase not in {"entry", "exit"}:
            raise ValueError("phase must be entry or exit")
        if not orders:
            raise ValueError("retain the complete nonempty package")
        if phase == "entry":
            self.entry_orders = list(orders)
            self.assets = [getattr(order, "asset", None) for order in orders]
        else:
            self.exit_orders = list(orders)
        self.state = phase.upper() + "_PENDING"

    def observe_submission(self, phase: str, accepted: Any) -> None:
        """The OptionsHelper bool is acceptance, never an order list or fill.

        After prepare_submission, call execute_orders with the retained list,
        then pass its literal return here. For a thrown/uncertain dispatch,
        pass None and reconcile the same retained attempt instead of resending.
        A callback-observed fill/completion during dispatch remains authoritative.
        """
        if phase not in {"entry", "exit"}:
            raise ValueError("phase must be entry or exit")
        if self.state != phase.upper() + "_PENDING":
            return
        suffix = "SUBMITTED" if accepted is True else "REJECTED" if accepted is False else "UNKNOWN"
        self.state = phase.upper() + "_" + suffix

    def reconcile_exit(self, owned_positions: list[Any]) -> str:
        """Call every iteration before any EXIT_* return, after refreshing IDs.

        Pass a current observation for EVERY original asset. Read failures keep
        the attempt unresolved; never supply a fabricated flat position. Retain
        incomplete terminal exits and let the existing strategy choose recovery.
        This method neither submits nor retries orders and changes no policy.
        """
        outcome = confirmed_package_exit_state(self.exit_orders, owned_positions)
        self.state = {"active": "EXIT_SUBMITTED", "unresolved": "EXIT_UNKNOWN",
                      "incomplete": "EXIT_INCOMPLETE", "closed": "CLOSED"}[outcome]
        if outcome == "closed" and not any(row.get("exit_orders") == self.exit_orders
                and row.get("outcome") == "closed" for row in self.history):
            self.history.append({"session_date": self.session_date, "outcome": "closed",
                "entry_orders": self.entry_orders.copy(), "exit_orders": self.exit_orders.copy(),
                "assets": self.assets.copy(), "entry_cost": self.entry_cost})
        return outcome
