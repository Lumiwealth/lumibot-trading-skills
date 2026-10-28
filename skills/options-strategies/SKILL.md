---
name: options-strategies
title: Options Strategies in LumiBot
description: Load before writing, editing, debugging or backtesting any LumiBot strategy that trades options, including single calls or puts, covered calls, cash-secured puts, the wheel, vertical spreads, iron condors, butterflies, straddles, strangles, calendars, diagonals and ratio spreads, or when an options backtest makes no trades. Covers OptionsHelper, chains, expirations, strikes, greeks, liquidity checks, multi-leg orders, assignment and expiry handling, position management and options data on BotSpot.
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

--------------------------------------------------------------
OPTIONSHELPER COMPONENT
--------------------------------------------------------------

Keep broker reads inside their original enabling branches. Hoisting an order
read above a conditional guard can add a second account request when that
branch's existing helper already refreshes orders. Trace both enabled and
bypassed paths, including missing quotes, before reusing a phase snapshot;
avoid duplicate phase reads while retaining the required decision-time refresh.



For exits defined relative to entry cost, preserve the user's exact value/profit
formula. Quote evaluations are estimates, never the confirmed entry cost.
Track the exact owned package and actual filled quantities and execution prices,
including partial fills and each contract multiplier. Compute its signed net
entry debit or credit from that evidence; use supported fill callbacks or
reconciled owned orders (`Order.get_fill_price()` only when filled-price evidence
exists). Do not set the realized basis from bid/ask evaluations before submission
or label an estimate as entry cost. Keep quote estimates separately for entry
pricing, and wait for the required fill evidence before testing a cost-based exit.

Reconcile the owned package before a new-session or new-entry eligibility return.
On a date change, do not return solely because saved package state is not FLAT or
CLOSED: first inspect the owned order statuses and current positions through the
existing lifecycle. Retain unresolved orders/exposure; after confirmed cancellation,
closure or expiry, retire that same package and reset settled session state. A reset
guard must not make its own package-completion path unreachable or permanently
disable later valid days. A new date alone is neither terminal evidence nor
permission to discard open obligations. An EXIT_SUBMITTED branch must keep
rechecking owned orders and positions on later iterations. Retain the exact closing
Order objects before package submission, just as for the entry. Acceptance alone
does not settle them: refresh those owned exits and all original leg positions
before the early return for a submitted exit. While any exit remains active, keep
waiting without submitting a duplicate. If an exit becomes terminal but positions
remain nonzero, retain an incomplete-exit state and reconcile the remaining package
through its existing lifecycle; never label that exposure closed. The historical
next-session expiry boundary below permits daily reset, not skipping intraday exit
tracking. Use `owned_package_settled` below for the actual flat completion check. Once every owned leg
is confirmed flat and no owned order remains unresolved, retire the active package
pointer (for code using that field, `self.vars.package = None`) before the next
session's entry guard; preserve the completed operation in its history. Merely
logging that the exit was sent leaves the strategy permanently blocked. In a strictly historical pandas backtest, the framework cash-settles expired cash-settled index options and cancels their open orders at session close. A package that strictly uses same-day expiration and DAY orders, with no live path, can therefore retire that prior session's package on the next trading date. Do not retain its stale `package_legs` list as evidence of current exposure. This verified terminal boundary does not apply to live, GTC, later-dated or otherwise unresolved obligations; reconcile those through their owned orders and positions before clearing them.

For an exact entry minute, check the configured time in the Rules' timezone
before acquiring inputs AND again immediately before submission. Missing inputs
do not authorize a later-session entry. Use the same predicate at both checks;
if the second check fails, leave that session untraded rather than substitute a
later entry. Session/date resets and completion reconciliation remain separate.

```python
# owned-entry-minute
def in_entry_minute(now, configured_time):
    return (now.hour, now.minute) == (configured_time.hour, configured_time.minute)
```

Use this complete predicate after refreshing every owned entry/exit attempt and
one position observation for each original package leg. A read failure retains
the active package. Wire the result into the existing completion owner BEFORE
any daily-entry return: on True, retire that same active package pointer and
retain its history. A helper that is never called from that path is unfinished.

```python
# owned-package-settlement
from decimal import Decimal, InvalidOperation

def owned_package_settled(owned_orders, owned_positions):
    if not owned_orders or not owned_positions:
        return False
    terminal = {"fill", "filled", "canceled", "cancelled", "expired", "error"}
    for order in owned_orders:
        status = getattr(order, "status", None)
        status = str(getattr(status, "value", status)).lower()
        if status not in terminal:
            return False
    try:
        return all(position is None or Decimal(str(position.quantity)) == 0
                   for position in owned_positions)
    except (AttributeError, InvalidOperation, TypeError, ValueError):
        return False
```


An option-selection or liquidity repair does not authorize a once-only or
once-per-day latch, a blanket held-position gate, new exits or new sizing.
For a selection repair spanning imports, initialization and the entry method,
prepare one coherent complete-file replacement from the literal current file
and use replace_file with its exact fresh editHandle. Do not reconstruct a
large replace_range expectedOldText from memory. Read the saved revision back.
Preserve every original legitimate entry opportunity. Only a demonstrated
duplicate submission of the same unresolved order needs a scoped technical fence.
At readback, compare each early return with the original entry method. A new
return for any held position or any open order changes entry capacity; remove
it unless that exact gate already existed or the user requested it. A fence
for this same unresolved submission must not block other legitimate entries.


Before beginning a new options strategy build, identify whether the requested
leg topology is complete. A ratio-spread wing direction is material: "buy one
and sell two options ten points apart" does not say whether the long strike is
above or below the short strike. If that direction is absent and cannot be
resolved from the user's own explicit context, ask one precise clarification
before `create_plan` and before `create_strategy`. Do not silently infer the
direction from a convention, example, or market view.

**CRITICAL: You MUST use OptionsHelper for ALL options strategies. Do NOT attempt to manually select options from chains.**
OptionsHelper validates that options have tradeable data during backtesting and handles the complexities of option selection.
If the user asks to fix an options no-trade, chain, expiry/expiration, strike,
leg, spread, liquidity, bid/ask, or option-pricing problem, this skill is the
focused skill and must be loaded before the edit. `lumibot-api-reference` can
supplement API semantics, but it is not sufficient by itself for options fixes.
For options no-trade, liquidity, expiration, strike, chain, or multi-leg rescue,
this focused skill is mandatory. A generic strategy or API skill alone is not
enough. Inspect the saved code and available artifacts/logs, then make the
smallest normal executable change that uses OptionsHelper/evaluate-option-market
semantics; do not add fake fills, dummy legs, hardcoded proof trades, or fixture-dependent
behavior. Preserve an explicitly requested historical-only/live-order boundary.

OptionsHelper is a utility component for constructing and managing various options strategies.

The complete accounting implementation is `references/package-cost.py`. Load
that existing resource when implementing confirmed package cost. Use its complete
`PackageSessionState` owner in the saved strategy. Call its actual
`begin_historical_day(today, ...)` at the beginning of every iteration, before
any daily entry flag or active-package early return. Compare its previous and
new session dates to reset the strategy's daily flags even when yesterday had
no submission (missing data, skipped entry, or an empty package). Do not replace
this method with a custom rollover that returns immediately for a missing
package date: that leaves a skipped day's entry latch set forever. Retain its
verified expiry/terminal safeguards for a real outstanding package. Retain legs with
`prepare_submission("entry" or "exit", built_orders)` BEFORE execute_orders,
then pass its actual bool to `observe_submission`. False is rejection, not an
accepted order. On every later iteration refresh those retained exit orders and
every original leg's position, call `reconcile_exit(positions)` BEFORE an EXIT_*
early return, and keep incomplete/unknown exposure visible. A saved helper that
is never called from main.py does not implement this behavior. The normal
sourceResourceKey file option can copy the loaded resource losslessly to an
ordinary saved helper; connect its complete owner, do not copy only its docstring. The other API
examples are in this SKILL.md; do not invent `references/options-helper.md`.
The general API reference is a DIFFERENT skill. If its broad component overview
is needed, the exact call is
`skills reference get(skill_name="lumibot-api-reference", file_path="references/components-overview.md")`.
That `references/components-overview.md` path belongs to `lumibot-api-reference`,
not `options-strategies`. This focused skill already
contains the OptionsHelper methods, so do not load a broad overview merely to
verify a method documented below. There is no `references/options.md` resource.

Constructor: OptionsHelper(strategy: Strategy)

Use only the documented method names below. Do not invent OptionsHelper
methods for chain/expiration lookup. In particular,
`get_chains_expirations_with_data` does not exist and generated code that calls
it will crash. To find a usable expiration, call `self.get_chains(...)`, then
`get_expiration_on_or_after_date(...)` with `underlying_asset`, and then
`find_next_valid_option(...)` for the strike/contract.

Basic Utility Functions:
1. find_next_valid_option(underlying_asset, rounded_underlying_price, expiry, put_or_call="call") -> Optional[Asset]
   - **ALWAYS USE THIS** - Finds a valid option, checking quote data first then last_price (last trade; can be stale) as fallback
2. get_strike_deltas(underlying_asset, expiry, strikes, right, stop_greater_than=None, stop_less_than=None) -> Dict[float, Optional[float]]
3. get_delta_for_strike(underlying_asset, underlying_price, strike, expiry, right) -> Optional[float]
4. find_strike_for_delta(underlying_asset, underlying_price, target_delta, expiry, right) -> Optional[float]
   - Use keyword arguments. `underlying_price` is required and must be a float (do not pass `expiry` as arg #2).
5. calculate_multileg_limit_price(orders, limit_type) -> Optional[float]
6. evaluate_option_market(option_asset, max_spread_pct=None) -> OptionMarketEvaluation
   - Returns a dataclass with: bid, ask, last_price, spread_pct, spread_too_wide, missing_bid_ask, missing_last_price, buy_price, sell_price, used_last_price_fallback, max_spread_pct, data_quality_flags. Always log the evaluation and only place orders if OptionsHelper.has_actionable_price(evaluation) returns True; otherwise log the flags and skip.
   - Legacy helper check_option_liquidity(...) still exists but generated code should migrate to evaluate_option_market.
7. has_actionable_price(evaluation) -> bool
   - Convenience helper to confirm evaluation.buy_price is finite, positive, and not blocked by spread filters.
8. get_order_details(order) -> Dict[str, Optional[Union[str, float, date]]]
9. get_expiration_on_or_after_date(dt, chains, call_or_put, underlying_asset=None) -> Optional[date]
   - **ALWAYS PROVIDE underlying_asset** - Gets expiration on/after date, validating option has tradeable data when underlying_asset provided

Order Building Functions (build orders but do not submit them):
10. build_call_orders(underlying_asset, expiry, call_strike, quantity_to_trade, wing_size) -> Tuple[Optional[Order], Optional[Order]]
11. build_put_orders(underlying_asset, expiry, put_strike, quantity_to_trade, wing_size) -> Tuple[Optional[Order], Optional[Order]]
12. build_call_vertical_spread_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity) -> List[Order]
13. build_put_vertical_spread_orders(underlying_asset, expiry, upper_strike, lower_strike, quantity) -> List[Order]
14. build_calendar_spread_orders(underlying_asset, strike, near_expiry, far_expiry, quantity, right) -> List[Order]
15. build_butterfly_spread_orders(underlying_asset, expiry, lower_strike, middle_strike, upper_strike, quantity, right) -> List[Order]
16. build_straddle_orders(underlying_asset, expiry, strike, quantity) -> List[Order]
17. build_strangle_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity) -> List[Order]
18. build_diagonal_spread_orders(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity, right) -> List[Order]
19. build_ratio_spread_orders(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right) -> List[Order]

Order Execution Functions (build orders and then submit them):
20. execute_orders(orders, limit_type=None) -> bool
21. execute_call_vertical_spread(underlying_asset, expiry, lower_strike, upper_strike, quantity, limit_type=None) -> bool
22. execute_put_vertical_spread(underlying_asset, expiry, upper_strike, lower_strike, quantity, limit_type=None) -> bool
23. execute_calendar_spread(underlying_asset, strike, near_expiry, far_expiry, quantity, right, limit_type=None) -> bool
24. execute_butterfly_spread(underlying_asset, expiry, lower_strike, middle_strike, upper_strike, quantity, right, limit_type=None) -> bool
25. execute_straddle(underlying_asset, expiry, strike, quantity, limit_type=None) -> bool
26. execute_strangle(underlying_asset, expiry, lower_strike, upper_strike, quantity, limit_type=None) -> bool
27. execute_diagonal_spread(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity, right, limit_type=None) -> bool
28. execute_ratio_spread(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right, limit_type=None) -> bool

COMBINED MULTI-LEG PACKAGES

When one strategy decision requires several related structures to fill as one
package, build every leg first and call `execute_orders(...)` exactly once with
the combined list. For example, a same-day put ratio spread plus call ratio
spread should concatenate the two lists returned by
`build_ratio_spread_orders(...)`, then pass that one combined list to
`execute_orders(...)`. Do not execute each ratio spread separately.

For a combined exit, close all remaining owned exposure in one package. Retain
every original asset, side and filled quantity. At exit, obtain a successful
current position observation for EVERY original asset, then build opposite-side
orders for all its nonzero held quantities and submit that complete list once.
A successfully observed flat leg needs no closing order; do not require the
closing list to have the original leg count. Three remaining held legs can be
the complete remaining package after a fourth is confirmed flat. A failed read
or unexplained ownership/quantity discrepancy remains unknown: retain the
package and reconcile it rather than invent a zero or send an unverified subset.
Retain the actual closing orders and observe their terminal states and every
original position. Mark closed only when all owned exposure is confirmed flat;
do not close nonzero legs independently or treat submission as completion.

Strike selection uses listed strikes. To choose the strike at or nearest a
reference price, read the listed strikes for that expiration and right
(`chains.strikes(expiry, "CALL")` or `"PUT"`) and take the one with the smallest
absolute distance, with a stated tie rule. Never round the price to an assumed
strike grid. A fixed-width wing strike must also be listed; if it is not, hold
and log instead of substituting another width.

Compute the requested long strike once, validate that exact value, then reuse
the returned pair in `build_ratio_spread_orders`. Do not validate an opposite
wing with separately written arithmetic; that can suppress a valid package.
The signed offset is chosen from the user's actual leg relationship, not from
a conventional spread assumption. This helper returns `(buy_strike, sell_strike)`:

```python
# listed-ratio-leg-strikes
def listed_ratio_leg_strikes(short_strike, long_offset, listed_strikes):
    short_strike = float(short_strike)
    long_strike = short_strike + float(long_offset)
    listed = {float(strike) for strike in listed_strikes}
    if short_strike not in listed or long_strike not in listed:
        return None
    return long_strike, short_strike
```

CONFIRMED PACKAGE COST AND EXIT

Use the actual native Order fields; there is no `filled_quantity` property.
The tracked Order can receive authoritative fills in place. Reconcile through
callbacks or exact owned lookups when needed, and calculate from its confirmed
transactions or its authoritative full-fill/average-price snapshot:

```python
# confirmed-leg-fill
def confirmed_leg_fill(order):
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
```

For combined package accounting, load `references/package-cost.py` and keep
its complete confirmed-leg and confirmed-package functions. Retain the actual
built order list; contract quantity is not order-list length. The returned
signed cost is positive for a debit and negative for a credit; never flip it.

Retain every submitted leg and apply that evidence to every leg before setting
package cost. A missing field defaulted to zero must not silently leave the
package in ENTRY_SUBMITTED forever. `execute_orders` supplies package submission,
not a returned order list or fill confirmation.

Keep the actual submitted leg orders and their owned IDs. Submission acceptance
is not a fill. Reconcile each leg via on_filled_order or get_order, requiring its
full filled quantity before establishing the complete package. order.get_fill_price()
returns its weighted actual fill price; absent fills do not establish entry cost.
Compute signed package entry cash with actual fill price × filled quantity ×
contract multiplier (buy positive, sell negative). Mark the existing long legs
at actionable sell/bid and the short legs at buy/ask to obtain signed liquidation
value, retaining ratios and actual quantities. For an entry debit, value 150% of
entry cost means liquidation value >= 1.5 × actual debit, a 50% gain. Never set
entry_cost from a submit acknowledgement or leave that branch as a logging stub.
For a net credit or zero cost, preserve the user's stated accounting policy and
clarify a genuinely undefined percentage rather than dividing by zero. Use
`confirmed_debit_exit_target` from the package reference at the actual exit
decision: an undefined target remains `None` and cannot trigger a debit-target
exit. An entry-time log alone does not guard the later exit path. Construct
all closing orders from the actual held legs and submit one complete package
through execute_orders; quote availability is a technical check, not permission
to invent a new spread threshold that suppresses the requested daily entry.

Use signed held quantities, not absolute quantities, for the combined mark. With
complete owned fill/position evidence and supported quote evaluations, the core
calculation is:

```python
# signed-package-liquidation
from decimal import Decimal

def signed_package_liquidation(held_positions_with_quotes):
    value = Decimal("0")
    for position, evaluation in held_positions_with_quotes:
        quantity = Decimal(str(position.quantity))
        if quantity == 0:
            continue
        closing_price = evaluation.sell_price if quantity > 0 else evaluation.buy_price
        if closing_price is None:
            return None
        value += quantity * Decimal(str(closing_price)) * Decimal(str(position.asset.multiplier))
    return value
```

Only pass the exact reconciled package legs into this calculation. A missing
closing quote retains the package and waits for evidence; it is not zero value.
Longs close at the actionable sell price; shorts cost the actionable buy price.

The closing list is not one `Order`: do not pass that list to singular
`strategy.submit_order`. `OptionsHelper.execute_orders` uses the supported
`submit_orders(..., is_multileg=True)` package path.

The methods and signatures required for this pattern are fully documented in
this skill. Do not repeatedly call `LumiBot source search` or
`LumiBot source read` merely to rediscover them. Inspect source only when
an actual tool or runtime error contradicts this documented contract. A code
review can verify that the strategy requests one package, but completed
backtest evidence cannot prove broker-level atomicity unless the order and fill
artifacts include a shared package identifier.

Advanced / Risk Management Functions:
29. aggregate_portfolio_greeks(positions, underlying_asset) -> Dict[str, float]
30. check_spread_profit(initial_cost, orders, contract_multiplier=100) -> Optional[float]

USAGE

1. Import the component:
    from lumibot.components.options_helper import OptionsHelper

2. In your strategy's initialize() method, instantiate the helper:
    def initialize(self):
        self.options_helper = OptionsHelper(self)
        self.vars.options_chains = None
        self.vars.options_chain_date = None

3. In a lifecycle method (e.g., on_trading_iteration), call its functions:
    def on_trading_iteration(self):
        underlying_asset = Asset("SPY")
        today = self.get_datetime().date()
        if self.vars.get("options_chains") is None or self.vars.get("options_chain_date") != today:
            self.vars.options_chains = self.get_chains(underlying_asset)
            self.vars.options_chain_date = today
        chains = self.vars.options_chains

        # CRITICAL: ALWAYS use get_expiration_on_or_after_date with underlying_asset to find valid expiry with data
        target_date = self.get_datetime().date() + timedelta(days=21)
        expiry = self.options_helper.get_expiration_on_or_after_date(
            target_date, chains, "call", underlying_asset=underlying_asset  # REQUIRED to validate data exists
        )

        if expiry:
            # ALWAYS use find_next_valid_option to ensure the option has tradeable data
            strike = 400  # or calculate based on underlying price
            option = self.options_helper.find_next_valid_option(
                underlying_asset, strike, expiry, "call"  # Validates quote/price data exists
            )
            if option:
                self.log_message(f"Found valid option: {option}", color="green")

FIRST-CYCLE OPTIONS RESCUE

For first-cycle backtest rescue, do not make the fix wheel-specific. Complex
options includes covered calls, cash-secured puts, vertical spreads, calendar
spreads, diagonal spreads, butterflies, iron condors, straddles, strangles,
ratio spreads, and any multi-leg order that requires all legs to pass quote,
liquidity, expiration, delta, or spread-width checks before placing an order.

If a smoke backtest finds chains or option prices but still completes with zero
trades, inspect whether the strategy keeps returning because one leg is missing
quotes, bid/ask is unusable, spread width is too strict, expiration windows are
too narrow, or every leg must pass at once. Preserve the user's strategy family,
but make the saved revision tradeable:

- First broaden the complex-order search in a normal way: use the nearest valid
  expiration with data, loosen target delta/strike bands, continue searching
  after an untradeable combination, and log each rejected combination's
  `OptionMarketEvaluation.data_quality_flags`.
- If a multi-leg strategy still blocks its first backtest and the
  user's thesis is directional, simplify to a one-contract call or put
  activation path that still uses `OptionsHelper.evaluate_option_market(...)`
  and requires a real executable `evaluation.buy_price`.
- Do not add dummy fills, fake option legs, hardcoded validation orders, or
  `if backtesting` branches. The rescue revision must be a normal strategy that
  can trade because the entry/order path is practical.
- For a direct existing-strategy options edit, save and read back the complete
  result. When `strategy review` is available, resolve its supported
  in-scope findings and review the corrected saved revision before finishing.
  A successful save/readback does not discharge supported in-scope review findings.
  This does not require a backtest: do not call `start_backtest` merely to
  validate an options fix unless the user asked for one.
  For a substantial options no-trade rewrite, prefer `replace_file` over a large
  patch. If a patch returns a revision but the readback is partial, truncated,
  tail-only, missing imports, missing the strategy class, missing the complete
  OptionsHelper order path, or otherwise not a complete executable `main.py`,
  the fix is not saved correctly; immediately call `replace_file` with the
  complete options strategy and read it back before final-answering.
  If a complex `patch_file` repair fails with `Invalid editHandle`, `stale edit
  handle`, `EDIT FAILED`, or another file-tool error, no options fix was saved.
  Refresh with `get_file`, keep the editHandle paired with the strategyId and
  revisionId from that same read, and retry with `replace_file` or a corrected
  patch before final-answering. Do not end by describing the intended
  OptionsHelper rewrite when file tools are available.
  First-cycle rescue flows can still start the required next smoke backtest
  when the backtest-rescue skill says the rescue loop requires it.

## Performance edits use the complete bounded snapshot example

If the supplied profile shows many option quotes AND account-order reads, complete both reductions. Batching quotes but leaving a `get_orders()` inside each candidate predicate is an incomplete repair. The scanner-performance reference contains the phase-admission versus decision-time order-read example: keep the original phase guard, avoid repeated reads for candidates that cannot pass the unchanged price checks, and refresh the existing exact-order predicate before each viable submission. Preserve its scope and error handling; do not replace it with a broader account freeze or a stale scan-wide cache.

For a general "speed up this scanner" request, follow the measured hot path
through every entry-quote and pre-entry hedge-preparation caller. Improving a
small stock-prefetch loop does not finish a repair when per-option reads and
repeated order refreshes still dominate the supplied profile. Complete the
supported optimization, read back the saved files and resolve in-scope review
findings in the same turn. Keep user pricing and eligibility unchanged.

This skill has no supplementary reference files: skills get returned its full
content. The quote reader belongs to a different skill. Use these exact pairs:
`skills reference get(skill_name="lumibot-api-reference",
file_path="references/scanner-performance.md")` and, when implementing the
reader, `skills reference get(skill_name="lumibot-api-reference",
file_path="references/quote-snapshot-example.py")`.
A RESOURCE_NOT_FOUND result means the requested pair is wrong; inspect the
advertised catalog, correct that pair and continue. It does not mean the
user must resolve a blocker or that authorized coding must stop. Do not
request `references/components-overview.md` from options-strategies.

Call file tools using their visible input schema. Put `path`, `editHandle` and
`operations` directly in the `patch_file` arguments, or `content` in the
`replace_file` arguments. Do not wrap those fields in `parameters`, `arguments` or `payload`
unless the visible schema explicitly declares that wrapper. A tool definition's
`parameters` is a schema description, not an extra input field. A schema rejection
saves nothing: correct the input shape and continue the authorized edit.

After reading an existing scanner that needs faster market-data acquisition,
load `lumibot-api-reference` and its `references/fast-order-management.md` and
`references/quote-snapshot-example.py` before replacing per-contract reads.
This is a performance/API-contract edit, not merely a parameter change. The
snapshot example preserves the singleton API's error boundary and retains
explicit missing members. Before saving, trace every quote-consuming caller:
entry candidate selection, liquidity evaluation and pre-entry hedge preparation.
Acquire once for that decision and pass the same snapshot through those callers;
changing only entry selection leaves the other serial network loop intact.
Copy the complete bounded reader into the saved files rather than replacing it
with a try/except that marks a whole failed batch missing. Distinguish a returned
missing member from an exception before any member was returned. A raw bulk call plus a helper whose None default
refetches does not implement that contract. Preserve actual provider behavior
and validate the installed API rather than copying a healthy-data-only example.

Initialize every new cache field before its first trading use. A daily reset
hook is not its only initialization path: a bot can start mid-session or restore
state saved before that cache existed. Initialize in `initialize()` and use
`self.vars.get(...)` defaults when old restored state can omit a new field.

Preserve each consumer's actual quote requirements. If an existing entry uses
the stock bid, an absent stock ask must not become a new blanket entry exclusion
merely because another hedge path uses the ask. Preserve the original optional
side and last-price fallbacks at their own consumers; do not substitute zeroes.
Trace the preceding helpers too: preserve an existing two-sided stock guard
when it is part of that entry path. Repeating an already enforced guard does
not by itself change the strategy's eligibility.

The prefetch universe must contain every candidate the original decision path
could evaluate. Derive any early filter from the same operands and predicates
as that path; a bid-based eligibility test cannot become ask-based in a batch
comprehension. Adapters can return sparse or crossed quote sides, so assuming
ask is always at least bid can silently exclude a previously eligible contract.
Acquiring a harmless superset is valid; tightening eligibility or introducing
new quote-validity requirements is a strategy change. Trace missing snapshot
members back through the acquisition filter before treating them as unavailable.

A requested common quote snapshot moves quote acquisition ahead of candidate
selection. Keep the existing contract-order predicate and its scope; this does
not authorize adding a broad account blocker. A later contract's order may now
be observed sooner because its quote was acquired in the batch. That changed
observation history alone is not a new financial policy. Do not ignore a known
working order to reproduce an earlier stale absence. Distinguish this quote-only
change from replacing order reads with a cached order snapshot, which needs its
own freshness and revalidation policy.

## Reuse an acquired option quote without an accidental second request

`evaluate_option_market(asset, max_spread_pct=policy_limit, quote=quote)`
accepts an already acquired `Quote` for that exact Asset on supported LumiBot
4.6.19+. It applies the normal price checks without fetching another quote or
using the helper's per-datetime cache. The quote's finite last-price field remains
available to its normal fallback; an explicit snapshot disables an additional
network last-price fallback. Preserve the strategy's existing pricing policy.

```python
# First load the complete bounded reader from lumibot-api-reference's
# references/quote-snapshot-example.py; adapt it into this saved strategy.
# This example is before order submission, with a contract-derived finite budget.
snapshot = read_quote_snapshot(
    self, contracts, deadline=None, max_requests=max(1, 2 * len(contracts))
)
for contract in contracts:
    quote = snapshot.quotes.get(contract)
    if quote is None:
        continue  # Unavailable in this snapshot, not a request to refetch it.
    evaluation = self.options_helper.evaluate_option_market(
        contract, max_spread_pct=policy_limit, quote=quote
    )
```

An omitted or None `quote` has the helper's normal fetching meaning. Do not pass
a missing batch slot into a helper whose None default fetches, including during
pre-entry hedge preparation. Pass the existing snapshot through those callers
and distinguish an absent quote from a caller intentionally requesting a fresh
post-fill observation. Adding stricter bid/ask eligibility is not a speed fix. A cached evaluation and a fresh
price observation are different inputs. If a later phase previously consumed a
cached evaluation plus a fresh numeric mid/last price, keep that data flow;
re-running evaluation at that point can add a new eligibility check even when
the original comparison still passes. Replace the price acquisition, not the
caller’s trading policy. Trace whether finite zero is an existing accepted price
rather than treating every falsey numeric value as a missing quote. Do not add
new `has_actionable_price` decisions where none existed before the edit.
