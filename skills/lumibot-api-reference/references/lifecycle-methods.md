> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-lifecycle-methods
description: Use when deciding where strategy logic belongs across initialize, trading iteration, market-open hooks, and other LumiBot lifecycle methods.
---

LUMIBOT STRATEGY LIFECYCLE METHODS

LumiBot strategies should put logic in the lifecycle callback method that matches the
moment when that logic must run. Do not put all behavior into one long
`on_trading_iteration` loop. Use hooks to separate setup, pre-market work,
recurring scans, order-state reconciliation, fill handling, shutdown summaries,
and crash diagnostics.

These hooks are lifecycle callback methods: LumiBot invokes them in response to
scheduled strategy work or broker/backtest events. An order callback reports an
observation; it does not initiate the broker action named by the callback. In
particular, `on_canceled_order` does not initiate cancellation. Code must call
`cancel_order`; `on_canceled_order` runs only after LumiBot observes terminal
cancellation.

General rules:

- Keep `initialize` deterministic and fast. It should configure state, assets,
  parameters, components, and cadence. It should not place orders.
- Keep each live trading iteration short. Fetch fresh broker/order state only
  when needed, act on it, then return. Do not block scans with long sleeps,
  polling loops, unbounded retries, or waiting for fills.
- Treat live broker state as the source of truth for orders and positions. In
  live trading, stale local order objects can happen after reconnects, broker
  delays, manual cancels, partial fills, or bot restarts.
- Backtests replay simulated events in-process. Live trading depends on broker
  APIs, broker clocks, account permissions, order propagation delays, and
  exchange/session state. Add guards for `self.is_backtesting` when live-only
  APIs, sleeps, external data, or broker-specific behavior are involved.
- Strategy logic should be broker-agnostic unless the user explicitly asks for
  broker-specific behavior. Prefer LumiBot methods such as `get_orders`,
  `get_positions`, `submit_order`, `cancel_order`, and `get_last_price`.

ORDER STATE AND HEDGE FLOW PLACEMENT

Order callbacks, reconnect snapshots, and exact-order reconciliation are three
inputs to one idempotent order-state reducer. A typical pattern is:

1. Persist stable broker order ids and the strategy's processed quantity/state.
2. Feed callback observations to the reducer as the fast path.
3. On reconnect, restart, or suspected missed callback, reconcile the exact
   tracked order and any related position/open hedge orders.
4. Treat a missing read, timeout, or rate limit as unknown, not terminal.
5. Only unblock the affected risk unit after broker-terminal evidence and any
   required hedge reconciliation.

Do not put stale-order reconciliation only in `initialize`; it will run once
and miss state changes later. Do not put it only in fill callbacks; a stale
order may disappear without a fill callback. Do not hide it behind long sleeps.

Hedge-after-fill, second-leg, and spread-completion logic belongs in fill
callbacks when the logic is a direct reaction to a fill:

- `on_filled_order` for fully filled first legs that require an immediate hedge
  or second side.
- `on_partially_filled_order` for strategies that hedge partial fills or update
  remaining quantities.

If the broker or backtest engine may not deliver a callback for every edge
case, keep a reconciliation fallback in `on_trading_iteration` that checks
filled/open order state and repairs missing hedges. The callback should react
quickly; the iteration fallback should make the strategy resilient.

Avoid blocking scans:

- `self.sleeptime` controls delay after a completed iteration; it does not
  preempt a running `on_trading_iteration`. Keep worst-case iteration wall time
  well below the shortest strategy-managed order deadline.
- Reconcile pending-order deadlines before starting fresh market scans. After
  submitting an order with a short deadline, store its id/deadline and return
  immediately; do not continue option-chain scans, serial quote loops, or hedge
  precomputation in that iteration.
- Use bulk price APIs such as `get_last_prices(assets)` and
  `get_historical_prices_for_assets(...)` instead of serial per-asset calls.
- Cache slow session-level data such as option chains, selected expiries, and
  candidate contracts with a bounded TTL. Refresh on session/date, universe,
  or material-input changes instead of every iteration.
- Chunk unavoidable scans. Persist a resume cursor, check a monotonic
  wall-clock budget and nearest order deadline between chunks, then return and
  resume next iteration. Bound provider retries per call and per iteration.
- Do not use `while` loops that wait for an order to fill inside
  `on_trading_iteration`.
- Do not call `time.sleep()` for long periods in live trading loops. If a delay
  is required, store timestamps such as `self.next_scan_at`,
  `self.cancel_after_by_order_id`, or `self.cooldown_until_by_symbol`, then
  return and let the next iteration handle it.
- Do not re-scan every symbol while waiting on an existing order. Reconcile
  pending orders first, then skip only the affected symbol/contract if it is
  genuinely blocked.
- Use idempotent helper methods so retrying an iteration does not duplicate
  orders.
- For very fast live order workflows such as "cancel this option order after 4
  seconds" or "place the hedge immediately after this fill", prefer
  broker-native OTO/OCO/bracket orders when they fit the requested structure. If
  the strategy must manage the sequence itself, track the submitted order id,
  use callbacks/stream observations as the fast path, and use rate-budgeted
  exact-order reads only for healing after reconnects or missed events. Do not
  use broad `get_orders()` as the deadline hot path or assume one-second polling
  is safe for every broker/account. Treat `CANCELLING`/`PENDING_CANCEL` as
  unresolved and use an idempotency guard so `on_filled_order` plus
  reconciliation cannot place the hedge twice.

Fill quantity semantics must be verified at the adapter/framework boundary.
When an observation is cumulative, persist a per-order cumulative high-water
mark and compute `delta = max(0, observed_cumulative - processed_cumulative)`.
For cumulative observations 2, duplicate 2, then 5, the actionable deltas are
2, 0, and 3. When a broker supplies incremental executions instead, deduplicate
by stable execution id. Never combine both interpretations silently.

METHODS

`initialize(self)`

Use for one-time setup before the strategy starts:

- Set strategy parameters and defaults.
- Create `Asset` objects used throughout the strategy.
- Set cadence values such as scan interval, cooldown seconds, and cancel
  timeout seconds.
- Initialize dictionaries/sets for state: pending orders, last scan times,
  hedge state, cooldown keys, and seen order ids.
- Instantiate reusable components such as `OptionsHelper(self)`.
- Configure external clients or API keys if needed, without making slow network
  calls during startup unless the strategy cannot run without them.

Do not:

- Place live orders.
- Read positions or orders and assume they stay fresh for the whole run.
- Perform a full universe scan that could delay startup.
- Use a live broker token, account id, or broker-specific secret directly in
  code. Use the platform/broker connection and environment variables.

`before_starting_trading(self)`

Use for final startup checks after initialization and before normal trading
iterations begin:

- Validate required parameters and environment variables.
- Load cached files or long-lived model state.
- Build static symbol lists or lightweight schedules.
- Do a quick sanity check that required assets and components are configured.

Do not:

- Place first trades unless the strategy explicitly has a startup trade rule and
  the user requested it.
- Run a long scan that should happen in `on_trading_iteration`.
- Treat startup broker state as permanently fresh.

Live vs backtest:

- In live trading, external services can fail here and should produce a clear
  log message.
- In backtesting, keep this deterministic and avoid live web/API calls unless
  they are replay-safe or explicitly mocked/cached.

`before_market_opens(self)`

Use for work that should happen before the regular market session opens:

- Refresh daily watchlists.
- Load pre-market data snapshots.
- Reset daily counters, daily risk flags, and per-session state.
- Prepare orders or candidate lists without submitting unless the strategy is
  specifically intended to submit pre-market orders.

Do not:

- Place regular-session orders before the market is open unless the strategy
  supports extended-hours trading and the broker/order type supports it.
- Assume this hook runs for 24/7 markets the same way it runs for stocks.

`on_trading_iteration(self)`

Use for recurring strategy decisions. This is the main loop:

- Reconcile current broker orders and positions when order state affects the
  next decision.
- Cancel stale orders whose timeout has elapsed.
- Check cooldowns and skip symbols/contracts that are still cooling down.
- Scan the current universe, compute indicators, evaluate signals, and submit
  new orders.
- Use helper methods to keep the loop readable.
- For options, use `OptionsHelper` for expiration/strike/market evaluation
  instead of manual chain selection.

Stale-order checks belong near the beginning when old orders can block scans,
hedges, or second legs:

```python
def on_trading_iteration(self):
    self._refresh_live_order_state()
    self._cancel_timed_out_orders()
    self._repair_missing_hedges_if_needed()

    if self._scan_is_on_cooldown():
        return

    self._scan_for_new_entries()
```

Do not:

- Perform a blocking wait for fills.
- Use long sleeps to implement timeouts.
- Recompute expensive indicators by hand when `self.indicators` can do it.
- Use stale local order lists after placing or canceling an order when the next
  decision depends on fresh state.
- Claim an order is canceled because local code marked it canceled; confirm via
  broker reads in live trading when the result matters.

Live vs backtest:

- In backtests, order and position state usually updates synchronously through
  the simulator.
- In live trading, `get_orders()` and `get_positions()` may involve broker API
  calls, propagation delays, and transient auth/connectivity failures. Handle
  empty/failed/stale results defensively and log the reason.

`before_market_closes(self)`

Use for end-of-day preparation:

- Cancel day-only stale orders if the strategy should not hold them overnight.
- Flatten or reduce risk if the strategy requires it.
- Stop placing new entries close to the bell.
- Save a final intraday state snapshot or summary.

Do not:

- Start a long scan or open a new multi-leg sequence that cannot reasonably
  complete before the close.
- Assume every asset follows the same close time. Options, equities, futures,
  crypto, and extended-hours sessions differ.

`after_market_closes(self)`

Use for post-session cleanup and reporting:

- Log daily summaries.
- Persist non-sensitive state needed tomorrow.
- Reset intraday flags.
- Run analytics or notifications that are not needed during the live loop.

Do not:

- Place normal trading orders unless the strategy is explicitly designed for an
  after-hours market/session and uses supported order types.
- Do broker-heavy reconciliation that must happen before next entries; that
  belongs in `on_trading_iteration` or `before_market_closes`.

`on_new_order(self, order: Order)`

Use for immediate bookkeeping when an order is created/submitted:

- Record order ids, symbols/contracts, timestamps, and cancel deadlines.
- Log useful order context.
- Add the order to pending state used by later reconciliation.

Do not:

- Assume the order will remain open.
- Place a hedge here unless the hedge is meant to be submitted at the same time
  as the first order and the strategy has already validated that behavior.
- Block waiting for a broker acknowledgement beyond what LumiBot already does.

`on_partially_filled_order(self, position: Position, order: Order, price: float, quantity: float, multiplier: float)`

Use when partial fills materially change risk:

- Update filled quantity and remaining exposure.
- Decide whether partial hedging is required.
- Adjust or cancel remaining orders if the strategy's rules require it.
- Route partial callbacks and reconciliation through the same quantity reducer.
- Persist the processed cumulative high-water mark when restart safety matters.

Do not:

- Ignore partial fills in multi-leg strategies where one side creates exposure.
- Submit duplicate hedge orders without checking existing hedge state and open
  orders first.

Live vs backtest:

- Backtests may fill in clean deterministic chunks.
- Live brokers may report partial fills, corrections, or state changes at
  different times. Keep this handler idempotent; duplicate and out-of-order
  observations must not create duplicate exposure or hedges.

`on_filled_order(self, position: Position, order: Order, price: float, quantity: float, multiplier: float)`

Use for actions that must happen because an order fully filled:

When an exit depends on an entry fill price or timestamp, populate that state
from confirmed fills for the expected strategy order and asset. Check order
identity and side before updating it; an unrelated fill must not overwrite it.
Use the held asset's price when evaluating the exit. Keep existing-position
management reachable even when a new-entry filter fails, and reset session-only
flags on the next session. Order submission alone is not a confirmed fill.

- Mark entry/exit state complete.
- Submit required hedge or second-leg orders for strategies where the second
  side depends on the first fill.
- Clear cancel timers for the filled order.
- Log fill details and resulting exposure.

Second-leg and hedge-after-fill logic usually belongs here. The handler should
verify the filled order is the expected first leg, then call a small helper such
as `_place_required_hedge_for_fill(order, quantity)`.

If partial-fill hedging is enabled, this callback must not blindly hedge the
full final quantity again. Feed its observed cumulative quantity to the same
high-water reducer used by `on_partially_filled_order` and restart recovery.

Do not:

- Scan a full universe from this callback.
- Assume no hedge exists. Check state/open orders to avoid duplicates.
- Claim success if the hedge submit call fails.

`on_canceled_order(self, order: Order)`

Use for bookkeeping after an order is confirmed canceled:

- Remove order ids from active/pending state.
- Clear cancel deadlines and cooldown keys.
- Decide whether the strategy should retry, fallback, or stand down.
- If a canceled first leg was part of a spread attempt, trigger the fallback
  plan in a controlled way on the next iteration rather than recursively placing
  many orders inside the callback.

Do not:

- Treat local cancel intent as confirmed cancel. This hook should represent a
  broker-observed terminal cancel event and does not initiate cancellation.
- Assume HTTP cancel acceptance means this callback has already run.
- Clear unresolved state after a missing/429 exact-order read.

RESTART AND RECONNECT RECOVERY

- Persist stable broker order ids, processed cumulative quantities, hedge order
  ids, and hedge progress in JSON-safe strategy state. In-memory sets alone are
  not restart-safe.
- Reconcile broker entry state, actual position exposure, and related open hedge
  orders before submitting a replacement hedge.
- Feed restart snapshots through the same idempotent reducer as callbacks. A
  snapshot is not a brand-new fill.
- If persisted state and broker truth disagree, keep the affected risk unit
  unresolved and reconcile conservatively; do not hedge the full order again
  merely because the process restarted.

`on_bot_crash(self, error: Exception)`

Use for crash diagnostics and cleanup:

- Log the exception and relevant safe state.
- Persist non-sensitive debug context if supported.
- Avoid leaving ambiguous local state for the next run.

Do not:

- Try to trade your way out of the crash.
- Print secrets, raw broker tokens, or account credentials.

`trace_stats(self, context: dict, snapshot_before: dict)`

Use for metrics/telemetry snapshots during strategy operation:

- Return lightweight values that help diagnose behavior over time.
- Include exposure, open order counts, signal state, cooldown state, or custom
  counters when useful.
- Keep values JSON-serializable and cheap to compute.

Do not:

- Run slow broker scans or large external API calls just to populate metrics.
- Include secrets or large DataFrames.

`tearsheet_custom_metrics(self, stats_df: pd.DataFrame | None, strategy_returns: pd.Series, benchmark_returns: pd.Series | None, drawdown: pd.Series, drawdown_details: pd.DataFrame, risk_free_rate: float)`

Use for backtest reporting metrics:

- Compute additional summary metrics for tearsheets.
- Use existing returns/drawdown inputs rather than re-running the strategy.
- Return simple named metrics that help compare strategy quality.

Do not:

- Place orders or mutate strategy state.
- Depend on live-only broker APIs.
- Perform long web calls while generating a backtest report.

`on_parameters_updated(self, parameters: dict)`

Use when runtime/user parameters change:

- Validate new values.
- Recompute derived settings such as thresholds, cooldowns, position sizes, and
  watchlists.
- Log what changed.

Do not:

- Replace the entire strategy state blindly.
- Clear pending order state unless the parameter change explicitly requires it.
- Assume parameter updates are safe for live trading without validating ranges.

COMMON MISTAKES TO AVOID

- Putting all setup, scans, order management, and reporting in
  `on_trading_iteration`.
- Placing orders in `initialize`.
- Waiting inside a loop for an order to fill, which blocks future scans and
  prevents timely cancellation.
- Using old local order objects after a broker-side cancel, manual cancel,
  reconnect, or restart.
- Handling hedge or second-leg logic only in the scan loop, so fills that occur
  between scans leave the account exposed longer than necessary.
- Handling hedge or second-leg logic only in fill callbacks, with no iteration
  reconciliation fallback for missed broker events.
- Calling live news/search/LLM APIs in backtests without deterministic replay or
  caching.
- Writing broker-specific strategy code when LumiBot has a broker-agnostic API.
- Claiming a strategy changed, order canceled, or hedge placed when the
  corresponding tool/API call failed.
