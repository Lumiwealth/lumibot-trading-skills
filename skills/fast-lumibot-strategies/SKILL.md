---
name: fast-lumibot-strategies
description: Load when a LumiBot strategy is slow, scans many symbols or option contracts, needs fast order handling (cancel after N seconds, immediate hedge or pair legs, OTO/OCO/bracket), or when backtests take too long. Covers sleeptime choice, batched data calls, caching, self.indicators, chunked scanners, bounded quote batching and order state machines.
license: MIT
metadata:
  title: "Fast and Responsive LumiBot Strategies"
---
# Fast and Responsive LumiBot Strategies

A LumiBot strategy is slow for a small number of reasons: it runs more
iterations than it needs, it recomputes the same thing every iteration, it reads
data one symbol at a time, or it blocks the iteration while waiting on the
broker. This skill shows how to find which one applies and fix it without
changing what the strategy trades.

The rule that governs everything here: **speed changes how data is acquired and
when work happens, never the trading policy.** Keep the same universe order,
thresholds, quantities, formulas, cooldowns, order guards and fallbacks. A
"faster" version that skips symbols, drops a guard or suppresses eligible trades
is a different strategy, not an optimization.

Related skills: `lumibot-api-reference` for exact signatures,
`lumibot-strategy-building` for the overall build and backtest workflow,
`options-strategies` for options-specific logic, `lumibot-indicators` for
indicator details, `lumibot-ai-agents` for AI-agent strategies.

## References in this skill

Load a reference with the `skills` tool (action=get,
name=fast-lumibot-strategies, reference=references/<file>):

| Load | When |
|---|---|
| `references/scanner-performance.md` | A scan over many symbols or option contracts is slow; you need to batch quotes, cut repeated account/order reads, and keep every guard and price fallback intact. Includes the full two-level scan pattern and a verification checklist. |
| `references/quote-snapshot-example.py` | You are adding batched bid/ask reads with `get_quotes`. A complete, bounded, failure-isolating reader to adapt into the strategy file (it is not an installed LumiBot module). |
| `references/fast-order-management.md` | Cancel-after-N-seconds, immediate hedge or pair legs after a fill, late fills during cancellation, duplicate hedge prevention, manual-cancel and restart recovery, broker-native OTO/OCO/bracket. Includes a complete state-machine pattern and the cases to test. |

## Step 1: find where the time goes

Do not guess. Before changing code:

1. Read the strategy (`get_file` on BotSpot) and list what each iteration does:
   how many symbols, how many `get_historical_prices`, `get_quote`,
   `get_last_price`, `get_chains`, `get_greeks`, `get_orders`, `get_positions`
   and `get_cash` calls, and any loops, sleeps or retries.
2. Check the cadence: `self.sleeptime` and the backtest window. Iterations times
   per-iteration work is the total cost.
3. Look at the logs of a real run (`get_backtest_logs`) for repeated work,
   timeouts, retries and skipped-entry reasons.
4. Classify the problem:
   - too many iterations (cadence), go to Step 2;
   - repeated computation, go to Step 3;
   - serial data reads, go to Step 4 and the scanner reference;
   - blocking order handling or missed deadlines, go to Step 6 and the order
     reference.

After the change, run the same backtest window again and compare (Step 8).

## Step 2: choose the right cadence

- Default to `self.sleeptime = "1D"` unless the strategy genuinely makes intraday
  decisions. A minute cadence runs hundreds of times more iterations than daily,
  and every iteration pays for its data reads. Use `"1M"`, `"5M"` or `"15M"` only
  when the logic needs it, and seconds (`"10S"`, `"1S"`) only for live order
  management.
- Minute-level history is limited (often about two years), so minute backtests
  must use shorter windows anyway.
- `sleeptime` is the gap after an iteration finishes. It never interrupts a
  running iteration. A one-second sleeptime does nothing for a scan that takes
  six seconds; the scan itself has to get shorter or be split (Step 5).
- Work that only needs to happen once a day belongs in `before_market_opens`
  (watchlists, chain lookups, daily resets), with the results stored in
  `self.vars`. It should not run on every intraday iteration.
- Crypto strategies run around the clock with `set_market("24/7")`, which also
  multiplies iterations. Pick the slowest cadence the logic tolerates.

## Step 3: stop recomputing the same thing

**Indicators.** Hand-rolled rolling windows recompute the entire history every
iteration:

```python
# Slow: recomputes the whole series on every iteration
df = self.get_historical_prices(asset, 300, "day").df
sma = df["close"].rolling(200).mean().iloc[-1]

# Fast: computed once over the series, cached, looked up per bar
sma = self.indicators.sma(asset, length=200, timestep="day")
if sma is None or pd.isna(sma):
    return
```

`self.indicators` caches per asset, timestep and parameters, and refreshes
automatically when new bars arrive. For custom math, pass the function to
`self.indicators.custom("label", fn, asset, timestep="day")`; `fn(df)` receives
the full history and returns a Series (scalar result) or a DataFrame
(IndicatorRow result). On indicator-heavy daily backtests this change alone
often cuts runtime substantially. Make the migration behavior-preserving: same
algorithm, smoothing, warmup and decision timing; compare values on a few bars
before replacing an existing calculation.

**Option chains and contracts.** `get_chains` is slow. Cache it once per day (or
per session) in `self.vars`, keyed by date:

```python
today = self.get_datetime().date()
if getattr(self.vars, "chains_date", None) != today:
    self.vars.chains = self.get_chains(underlying)
    self.vars.chains_date = today
chains = self.vars.chains
```

Store the full selected `Asset` objects (strike, expiry, right included), not just
symbols, so later iterations do not refetch or rebuild them. Cache the selected
expiry and strikes and recompute only when the underlying has moved materially
or the date changed.

**Delta hunting.** Never loop `get_greeks()` over a strike list to find a target
delta. Each call is a data request, so a 100-strike loop is 100 requests per
iteration. Use `OptionsHelper.find_strike_for_delta(...)` (keyword arguments,
`underlying_price` required) and `get_expiration_on_or_after_date(...)` with
`underlying_asset=...`.

**Static values.** Levels that should not change once detected (support,
resistance, a pattern's anchor) belong in `self.vars` the first time they are
found. Recomputing them every iteration costs time and makes charts jagged.

**Date math and charting.** Avoid unnecessary date calculations inside tight
loops. Plot price with one `add_ohlc` per bar and indicators with `add_line`; add
markers only for rare events. Markers on every iteration bloat the output and can
break the chart.

## Step 4: batch data calls

Replace per-symbol loops with the batched methods:

| Instead of | Use |
|---|---|
| `get_historical_prices` in a loop | `get_historical_prices_for_assets(assets, length, timestep)` returns `{asset: Bars or None}` and fetches in parallel |
| `get_last_price` in a loop | `get_last_prices(assets)` (trade prices only) |
| `get_quote` in a loop (bid/ask decisions) | `get_quotes(assets)` (LumiBot 4.6.19+), returns `{asset: Quote or None}` |

```python
bars_by_asset = self.get_historical_prices_for_assets(assets, 60, "day")
for asset in assets:
    bars = bars_by_asset.get(asset)
    if bars is None or bars.df.empty:
        self.log_message(f"{asset.symbol}: no bars, skipping", color="yellow")
        continue
    ...
```

Things to know about batching quotes:

- `get_last_prices` returns last trades. It is not a bid/ask snapshot and cannot
  replace a bid/ask or midpoint formula.
- Native batching depends on the data source. Some sources send one request per
  batch (Schwab accepts up to 50 symbols per request); others fall back to
  individual reads. Check before claiming fewer network requests.
- `get_quote` swallows read errors and returns None; direct `get_quotes` can
  raise for the whole batch when one member is malformed or a request fails.
  Wrapping it in `try/except: continue` silently drops healthy contracts. Use the
  bounded, failure-isolating reader in `references/quote-snapshot-example.py`.
- A missing quote stays missing for that scan. Do not let an old helper refetch
  it one by one, which brings the serial loop back.
- Pass the snapshot quote into every consumer that would otherwise fetch again,
  including `OptionsHelper.evaluate_option_market(option, max_spread_pct=..., quote=quote)`.

For live freshness, `get_last_price` and `get_quote` return the latest tick and
are faster than requesting historical bars, which are at best one-minute bars and
can lag. If a live strategy feels sluggish because it calls
`get_historical_prices` for the current price, switch the current-price read to
`get_quote` or `get_last_price` and keep history for indicators.

## Step 5: scanners over many symbols

For a basket scan, split the work into two levels and make each read only where
the original decision needed it:

1. Per symbol, in the original order: keep the symbol-level guard (for example
   an active-order check) exactly where it was.
2. Select candidate contracts from cached chain data, then read their quotes in
   one bounded batch.
3. Evaluate price and eligibility from the batch first. Only for a candidate that
   is still viable, refresh orders and run the original exact-contract guard.
4. Submit using the existing logic and stop or continue as the original did.

This removes both common hot paths (serial option quotes and per-candidate
account reads) without moving guards. The full pattern, the validation and price
fallback rules, and a verification checklist are in
`references/scanner-performance.md`. Read it before editing a real scanner.

When a scan cannot finish quickly (very large universe, slow provider, or an
order deadline in flight), chunk it with a resumable cursor and a wall-clock
budget instead of scanning everything in one iteration:

```python
import time

def _run_one_bounded_scan_step(self):
    universe = self.parameters["symbols"]
    cursor = getattr(self.vars, "scan_cursor", 0)
    budget_seconds = float(self.parameters.get("scan_budget_seconds", 2.0))
    started = time.monotonic()

    while cursor < len(universe):
        if time.monotonic() - started > budget_seconds:
            break                        # resume here on the next iteration
        symbol = universe[cursor]
        cursor += 1
        if self._handle_symbol(symbol):  # existing per-symbol logic; True if it traded
            break
    if cursor >= len(universe):
        cursor = 0                       # full pass complete
        self.vars.last_full_scan_at = self.get_datetime().isoformat()
    self.vars.scan_cursor = cursor
```

Use `time.monotonic()` for elapsed-time budgets. Bound every provider retry per
call and per iteration, and log when a pass was incomplete so nobody mistakes an
unfinished scan for "no opportunities".

## Step 6: fast and safe order handling

The iteration must never block waiting for the broker. Core rules:

- Do not `while`-loop until an order fills, and never use `time.sleep()` (use
  `self.sleep(...)` only for short, bounded waits). Store deadlines and order ids
  in `self.vars` and check them next iteration, or use the resident wait pattern
  in the order reference for second-level deadlines.
- Reconcile pending orders and deadlines **before** starting a fresh scan. After
  submitting an order with a short deadline, return instead of continuing a long
  scan in the same iteration.
- React to fills in `on_filled_order` / `on_partially_filled_order` (the fast
  path), and keep a reconciliation fallback in `on_trading_iteration` for missed
  callbacks. Share one idempotency record keyed by the original order identifier
  so the callback and the fallback cannot both place a hedge.
- Use `self.get_order(order.identifier)` for an exact order. Do not poll it in a
  tight loop, and do not use broad `get_orders()` scans on a deadline-critical
  path. On rate-limit errors (HTTP 429) back off, honoring `Retry-After`.
- `cancel_order` is a request. `CANCELLING`/pending-cancel, a missing read, a
  timeout or a cancel exception are all unresolved, not terminal. Keep the
  affected symbol or pair blocked until the broker confirms a terminal state and
  any required hedge is resolved.
- Use `Order.OrderStatus.ERROR` for rejections; there is no `REJECTED` status.
- Prefer broker-native OTO/OCO/bracket orders when the relationship fits (for
  example take-profit plus stop-loss). Use a strategy-managed state machine only
  for flows a native order class cannot express, such as a custom stock hedge
  after an option fill or a strict cancel-after-N-seconds.
- Second-level deadlines need a continuously running process. On BotSpot, use an
  always-on deployment or a schedule window that covers the whole trading
  period; a one-shot scheduled run cannot own a sub-minute deadline.

`references/fast-order-management.md` has the complete cancel-after-N-seconds
plus immediate-hedge state machine, the deadline architecture, restart
recovery, and the list of cases to test before trusting it with real money.

## Step 7: backtest speed

- Start with a short window (a few months of daily bars) to prove the strategy
  runs and trades, then extend. Long minute-level backtests are the slowest kind.
- Keep the universe as small as the idea allows while iterating; widen it once
  the logic is right.
- Use daily cadence for daily logic. An intraday cadence on a daily idea only
  multiplies work.
- Use `self.indicators`, cached chains and batched reads (Steps 3 and 4). They
  help backtests as much as live trading.
- Avoid live web or API calls in backtests unless they are replay-safe or cached.
- AI-agent strategies call a model on every simulated iteration. They are the
  slowest backtests: keep the first run to about a week of daily iterations and a
  small universe (see `lumibot-ai-agents`).
- Options backtests depend on per-contract data; selecting contracts through
  `OptionsHelper` and caching them avoids requesting data for contracts that do
  not exist or are never traded.
- Log decisions and reasons, but avoid dumping large DataFrames every iteration.

## Step 8: measure and report honestly

On BotSpot:

1. Save the change (`patch_file` or `replace_file`) and read it back with
   `get_file` to confirm every caller uses the new path.
2. Run the same window as before with `start_backtest`, track it with
   `backtest_status`, and compare runtimes.
3. Check `get_backtest_logs` and the trade output (`get_backtest_artifact`,
   `query_csv`) to confirm the strategy still makes the same decisions on the
   same data. Any change in trades needs an explanation.

Report what you measured (runtime, number of requests if logged, iterations) and
describe the saved code accurately. If a hot path is still unchanged, say so. Do
not claim a speedup you did not measure, and never present speed as evidence that
the strategy will make money.

Live deployment and any real-money order always need the user's explicit
approval on botspot.trade. Nothing in this skill is investment advice.
