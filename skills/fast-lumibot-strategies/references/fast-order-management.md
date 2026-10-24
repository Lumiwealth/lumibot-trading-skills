# LumiBot fast order management

Use this reference for second-level live order deadlines, immediate hedge legs,
late fills during cancellation, duplicate hedge prevention, manual-cancel
recovery, and broker-native OTO/OCO/bracket orders.

When the user asks for a code pattern or minimal state machine, give them a
compact, copyable Python implementation with its callbacks and reconciliation
path. The user cannot see this reference, so adapt the combined pattern below
into your answer or their strategy file instead of replying only with prose.

## Safety invariants

- Treat an entry, its cancellation, and any required hedge as one lifecycle for
  the risk unit that owns them. Scope blocking to the smallest risk unit allowed
  by explicit strategy and portfolio policy: order, symbol/pair, risk bucket, or
  account. Do not turn one unresolved independent symbol into a universal global
  freeze, and do not let correlated/shared-capital exposure bypass its broader
  risk constraint.
- CANCELLING and PENDING_CANCEL are not terminal. A missing order refresh,
  timeout, rate limit, or cancel exception is also not terminal. Every one of
  those states must keep the entry blocker armed.
- Use Order.OrderStatus.ERROR as LumiBot's portable rejected/error state.
  Broker text may say REJECTED, but generated code must not invent
  Order.OrderStatus.REJECTED.
- A successful cancel_order(order) call does not mean a custom
  on_canceled_order hook already ran. LumiBot queues the strategy callback, so
  it may run just after the current on_trading_iteration returns.
- on_filled_order already carries a filled order. Trust that callback object
  for the fast hedge path; do not make the hedge depend on another
  self.get_order(order.identifier) call that can be slow, missing, or
  rate-limited.
- Callback and reconciliation paths must share one idempotency fence keyed by
  the original entry order.identifier.
- A hedge submission is not a completed pair. Keep the affected risk unit
  unresolved while the hedge is active, rejected, missing, or awaiting a
  bounded retry.
- No timeout, retry count, or blocker scope is universal. Derive each from the
  strategy's stated execution contract, broker capability, and risk coupling.

## Deadline architecture

self.sleeptime = "1S" only schedules the next iteration after the current
iteration returns. It cannot preempt a slow scan. A deadline checked only on a
future iteration can therefore be many seconds late.

A synchronous scan known to occupy that same control path for six seconds
already exceeds a three-second local dispatch budget. State that demonstrated
budget violation directly. Missing broker timestamps may still prevent blaming
the broker or proving the precise cancel-dispatch or terminal-confirmation time.

For a strategy-defined timeout:

1. Finish expensive option-chain, quote, liquidity, and hedge-candidate work
   before submitting the entry.
2. Call submit_order, store the returned order.identifier, and start an
   absolute time.monotonic() deadline immediately after the broker accepts the
   order.
3. Use a deadline-capable control path that cannot be starved by the next long
   scan. Choose a measured safety margin before the user's actual dispatch
   deadline; derive it from this strategy's requirement, not a magic constant.
4. During that short resident wait, process pending events and inspect the local
   tracked order object. Do not call broker-backed get_order immediately before
   the deadline.
5. At the target, call cancel_order once and retain the blocker.
6. Return from the iteration so queued on_canceled_order or on_filled_order
   callbacks can run.
7. If no callback resolves the order, perform one exact-order
   self.get_order(order_id) reconciliation on a later iteration. Back off and
   bound cancel retries.

The strategy can control prompt cancel dispatch. It cannot guarantee the broker's
network response or broker-confirmed terminal time exactly at three seconds.

A continuous runtime window is sufficient when it spans the strategy's true
operating period and starts immediately when approved inside the window. A
scheduled one-shot process that exits after one iteration cannot own a
sub-minute deadline or callback lifecycle. Persisting ids and deadlines helps a
later reconciliation but cannot replace a live process while an order is
unresolved. On BotSpot, choose an always-on deployment or a schedule window
that keeps the process running for the whole trading window (see
`manage_schedule`); one daily invocation is not equivalent.

## Minimal combined pattern

Adapt asset, quantity, and hedge construction to the user's strategy. Preserve
the lifecycle and failure semantics.

~~~python
import time
from datetime import timedelta

from lumibot.entities import Order


def initialize(self):
    self.sleeptime = "1S"
    self.cancel_timeout_seconds = float(self.parameters.get("cancel_timeout_seconds", 3.0))
    self.cancel_dispatch_margin_seconds = float(
        self.parameters.get("cancel_dispatch_margin_seconds", 0.25)
    )
    self.reconcile_backoff_seconds = float(
        self.parameters.get("reconcile_backoff_seconds", 5.0)
    )

    # JSON-safe containers survive scheduled-state persistence. If older state
    # can contain sets, normalize it before callbacks or iteration logic.
    self.entry_order_ids = {}
    self.canceling_entry_ids = {}
    self.hedge_by_entry_id = {}
    self.hedge_attempts_by_entry_id = {}

    self.active_entry_order_id = None
    self.active_entry_order = None
    self.cancel_deadline_monotonic = None
    self.pair_state = "IDLE"
    self.next_reconcile_at = None


def _pair_is_blocking(self):
    return (
        self.active_entry_order_id is not None
        or bool(self.canceling_entry_ids)
        or self.pair_state
        in {
            "ENTRY_ACTIVE",
            "CANCEL_PENDING",
            "HEDGE_SUBMITTING",
            "HEDGE_ACTIVE",
            "HEDGE_FAILED",
            "RECONCILE_REQUIRED",
        }
    )


def submit_entry(self):
    if self._pair_is_blocking():
        return None

    # Complete slow chain/quote/candidate work before this point.
    order = self.create_order(
        self.option_asset,
        self.entry_quantity,
        "buy",
        order_type=Order.OrderType.LIMIT,
        limit_price=self.entry_limit_price,
    )
    tracked = self.submit_order(order) or order

    self.active_entry_order_id = tracked.identifier
    self.active_entry_order = tracked
    self.entry_order_ids[tracked.identifier] = True
    self.pair_state = "ENTRY_ACTIVE"

    # Start after submit_order returns. The margin is strategy-configured and
    # validated against the user's timeout; it is not a shared magic constant.
    dispatch_after = max(
        0.0,
        self.cancel_timeout_seconds - self.cancel_dispatch_margin_seconds,
    )
    deadline = time.monotonic() + dispatch_after
    self.cancel_deadline_monotonic = deadline
    self._hold_entry_until_cancel_dispatch(tracked, deadline)
    return tracked


def _hold_entry_until_cancel_dispatch(self, tracked, deadline):
    while True:
        if tracked.is_filled():
            self._place_stock_hedge_once(tracked)
            return

        status = getattr(tracked, "status", None)
        if (
            tracked.is_canceled()
            or status in {
                Order.OrderStatus.CANCELED,
                Order.OrderStatus.EXPIRED,
                Order.OrderStatus.ERROR,
            }
        ):
            self._finish_terminal_entry(tracked.identifier, status)
            return

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break

        # Let live stream events update the tracked object. No broker GET is
        # allowed in this deadline-critical wait.
        self.sleep(min(0.05, remaining), process_pending_orders=True)

    entry_id = tracked.identifier
    self.canceling_entry_ids[entry_id] = {
        "requested_at": self.get_datetime(),
        "attempts": 1,
    }
    self.pair_state = "CANCEL_PENDING"

    try:
        self.cancel_order(tracked)
    except Exception:
        # A fill can win the race with cancel. Reconcile once, but never clear
        # or scan merely because cancel raised or the read is unavailable.
        refreshed = self.get_order(entry_id)
        if refreshed is not None and refreshed.is_filled():
            self._place_stock_hedge_once(refreshed)
        else:
            self.pair_state = "RECONCILE_REQUIRED"
        return

    # Do not clear state here and do not assume on_canceled_order already ran.
    # Yield so the queued strategy callback can resolve the terminal event.


def on_filled_order(self, position, order, price, quantity, multiplier):
    if order is None or order.identifier not in self.entry_order_ids:
        return

    # Fast path: use the callback's filled order directly.
    self._place_stock_hedge_once(order)


def on_canceled_order(self, order):
    if order is None or order.identifier not in self.canceling_entry_ids:
        return

    self._finish_terminal_entry(order.identifier, Order.OrderStatus.CANCELED)


def _place_stock_hedge_once(self, filled_entry):
    entry_id = filled_entry.identifier

    existing = self.hedge_by_entry_id.get(entry_id)
    if existing and existing.get("state") in {
        "SUBMITTING",
        "ACTIVE",
        "FILLED",
        "FAILED",
    }:
        return

    self.pair_state = "HEDGE_SUBMITTING"
    self.hedge_by_entry_id[entry_id] = {
        "state": "SUBMITTING",
        "hedge_order_id": None,
    }

    try:
        hedge = self.create_order(
            self.stock_hedge_asset,
            self.stock_hedge_quantity,
            "sell",
            order_type=Order.OrderType.MARKET,
        )
        hedge = self.submit_order(hedge) or hedge
    except Exception as exc:
        self.hedge_by_entry_id[entry_id] = {
            "state": "FAILED",
            "hedge_order_id": None,
            "reason": str(exc),
        }
        self.pair_state = "HEDGE_FAILED"
        return

    self.hedge_by_entry_id[entry_id] = {
        "state": "ACTIVE",
        "hedge_order_id": hedge.identifier,
    }
    self.pair_state = "HEDGE_ACTIVE"


def _reconcile_canceling_entry(self, now):
    if not self.canceling_entry_ids:
        return

    if self.next_reconcile_at is not None and now < self.next_reconcile_at:
        return

    # One exact-order read per reconciliation pass; never broad hot polling.
    entry_id = next(iter(self.canceling_entry_ids))
    tracked = self.get_order(entry_id)
    self.next_reconcile_at = now + self._broker_reconcile_backoff()

    if tracked is None:
        self.pair_state = "RECONCILE_REQUIRED"
        return

    if tracked.is_filled():
        self._place_stock_hedge_once(tracked)
        return

    status = getattr(tracked, "status", None)
    if (
        tracked.is_canceled()
        or status in {
            Order.OrderStatus.CANCELED,
            Order.OrderStatus.EXPIRED,
            Order.OrderStatus.ERROR,
        }
    ):
        self._finish_terminal_entry(entry_id, status)
        return

    state = self.canceling_entry_ids[entry_id]
    if state["attempts"] >= 2:
        self.pair_state = "RECONCILE_REQUIRED"
        return

    try:
        self.cancel_order(tracked)
    except Exception:
        self.pair_state = "RECONCILE_REQUIRED"
        return

    state["attempts"] += 1


def _broker_reconcile_backoff(self):
    # An account-level rate-budget coordinator should increase this after 429s
    # and honor Retry-After. Keep the strategy parameter broker-appropriate.
    return timedelta(seconds=self.reconcile_backoff_seconds)


def on_trading_iteration(self):
    now = self.get_datetime()

    # Deadline/order/hedge state always runs before fresh scans.
    if self.canceling_entry_ids:
        self._reconcile_canceling_entry(now)
        return

    if self.pair_state in {
        "HEDGE_SUBMITTING",
        "HEDGE_ACTIVE",
        "HEDGE_FAILED",
        "RECONCILE_REQUIRED",
    }:
        self._reconcile_hedge_or_hold_blocker(now)
        return

    if self.active_entry_order_id is not None:
        # The resident submit lifecycle normally owns this state. This branch
        # is a restart/reconnect fallback and must remain fail-closed.
        self.pair_state = "RECONCILE_REQUIRED"
        return

    self._run_one_bounded_scan_step()


def _finish_terminal_entry(self, entry_id, status):
    self.canceling_entry_ids.pop(entry_id, None)
    self.entry_order_ids.pop(entry_id, None)

    if self.active_entry_order_id == entry_id:
        self.active_entry_order_id = None
        self.active_entry_order = None

    self.cancel_deadline_monotonic = None
    self.next_reconcile_at = None
    self.pair_state = "IDLE"
~~~

The example intentionally leaves _reconcile_hedge_or_hold_blocker and
_run_one_bounded_scan_step strategy-specific. Their contract is not optional:

- Hedge retries must be bounded. If the broker rejects stock shorting or returns
  Order.OrderStatus.ERROR, record the reason, enter HEDGE_FAILED, and keep
  fresh entries blocked for user-controlled recovery.
- A filled hedge may complete the pair. A missing or active hedge may not.
- A scan step must have a monotonic wall-clock budget and a resumable cursor. Do
  not scan the entire universe in one iteration when order deadlines are armed.

## Broker calls and API budget

- Use callbacks or broker streams for the fast path and exact-order reads for
  reconnect or missed-callback reconciliation. Streaming does not replace
  reconciliation because messages can be missed across disconnects.
- Do not poll self.get_order every 250 ms. A broker call can itself take longer
  than the polling interval, consume the deadline, and trigger HTTP 429.
- Do not call get_order twice for the same decision.
- Do not use broad get_orders() scans on the deadline-critical path.
- Coordinate an aggregate broker request budget across active orders and
  endpoints. On HTTP 429, honor `Retry-After` when present; otherwise use
  bounded exponential backoff with jitter. A missing/429 read retains
  unresolved state rather than synthesizing a terminal result.
- Batch independent price reads with get_last_prices(assets) or
  get_historical_prices_for_assets(...) when the decision uses trade/bar prices.
  Bid/ask decisions need `get_quotes(eligible_assets)` on LumiBot 4.6.19 or newer;
  `get_last_prices` is not a bid/ask snapshot. Verify the installed data source's
  native batching support before claiming fewer HTTP requests.
- Cache option chains and candidate contracts with a bounded TTL.
- Bound every broker retry loop and expose the final broker reason.

### Scanner latency

For slow basket scans or quote batching, read `references/scanner-performance.md`
in this skill before editing. It has the complete two-level scan example,
quote/error handling and account-read optimization. Keep the deadline and lifecycle contracts in this
reference when scanning overlaps an existing order.

## Broker-native orders

Prefer broker-native OTO/OCO/bracket orders when the requested relationship maps
cleanly to a supported broker-native trigger. Use the strategy-managed pattern
when the user's three-second cancellation or custom stock hedge cannot be
expressed by that native order class.

## Manual cancel and restart recovery

- A manual broker cancel is terminal only when the exact tracked order reports a
  terminal state or on_canceled_order delivers it.
- If an exact read is missing or rate-limited, keep the blocker and retry later.
- Persist exact entry, cancel, and hedge ids. Use JSON-safe dict/list state, or
  normalize restored lists before calling set-only methods such as discard().
- A one-shot scheduled runner is invalid for a live sub-minute deadline.
  Choose a continuous runtime window for the strategy's timezone, days and
  hours, or an always-on deployment.

## Cases to test

Before trusting this logic with real money, exercise these cases in backtests,
paper trading or unit tests of the strategy helpers:

- cancel dispatch under the target without a pre-cancel broker read;
- fill before the deadline;
- fill winning the cancel race;
- cancel exception with unavailable reconciliation;
- callback arriving after cancel_order returns;
- missed callback resolved by one later exact-order read;
- missing/429 reads retaining unresolved state;
- duplicate callback plus polling hedge paths submitting one hedge;
- rejected stock hedge with bounded retries and blocked new entries;
- second/third watchlist symbols preserving the same lifecycle;
- restart-state JSON round trip;
- scheduled one-shot rejection for sub-minute live deadlines.

## Anti-patterns

- A future on_trading_iteration as the only owner of a three-second deadline.
- self.get_datetime() + timedelta(seconds=3) for an exact elapsed-time deadline.
- Broker polling immediately before cancel dispatch.
- Clearing or moving aside the blocker because cancel was requested.
- Treating CANCELLING, missing, 429, or cancel exception as terminal.
- Calling get_order from the filled callback before hedging.
- Marking the pair complete immediately after hedge submission.
- Unbounded rejected-hedge retries.
- Broad order-history scans in the hot path.
- Background threads that call strategy/broker methods outside LumiBot's normal
  lifecycle.


## Diagnosing fill arithmetic and missed deadlines

Before proposing fill arithmetic, establish whether this broker-facing source
reports cumulative filled quantity, a per-fill delta, or position snapshots.
Verify it from the adapter contract or observations first. If unavailable, say
what must be verified and make the reducer conditional; never apply a cumulative
high-water mark to per-fill deltas. For a confirmed cumulative source, process
only max(0, observed_total - prior_high_water) and retain the high-water mark
across duplicate or out-of-order events and reconnects. Track entry identity,
hedged quantity and terminal status separately; position changes are not fills.

For a missed dispatch deadline, separate synchronous work, network request time
and callback delivery. Request reconstructable timestamps for submit acceptance,
absolute deadline, cancel decision, request start/end, broker-terminal observation,
callback delivery and each iteration phase. A scan that occupies the whole
available interval prevents dispatch even when the configured sleeptime is short.
Explain that causal timing and gather the complete timeline before tuning it.
