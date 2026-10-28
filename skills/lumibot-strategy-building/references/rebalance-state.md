> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Finish accepted allocation work before declaring success

Use `references/rebalance-example.py` as a complete, tested reference for an
ordinary long-only, whole-unit cash portfolio. Save the complete registered source as a normal strategy helper file with
`create_file(sourceResourceKey="lumibot-strategy-building:references/rebalance-example.py")`,
using the actual strategy/revision identity and a fresh path. Import that saved
module from the existing strategy; never import a private skill path or transcribe
a shorter controller. If an existing-file-only edit forbids a new helper, keep
that boundary and integrate the same complete owner in the permitted file. Other account modes,
shorting, leverage, fractional increments and explicitly required market orders
retain their own supported execution contracts; this example does not restrict
the platform or authorize changing the user's policy.

The strategy still chooses when to rebalance and what the weights should be.
Accept targets once for that signal generation. Run `reconcile()` on every
normal iteration and after actual fill/cancel observations, including between
weekly or monthly signal dates. A date marker records target acceptance, not
successful execution. Do not place reconciliation behind a Monday-only return.

Use the SAME existing execution lock and order publisher as the strategy's
other execution paths. This example assumes that owner controls the portfolio's
orders. Integrate it into that owner; do not add a second independent publisher
or ignore other outstanding cash obligations. Preserve the user's signal,
ranking universe, weights, other exits and schedule.

The supplied maximum buy price is the actual accepted order limit. Confirm that
bounded execution fits the requested policy and disclose its unfilled-order
risk. Never pass an old quote as an alleged bound for an unrestricted market
order. The fee fraction must cover the configured proportional buy fees;
flat fees and other costs need their corresponding actual cost calculation.

`accept(weights, generation)` freezes a dollar target against observed equity.
`reconcile()` submits necessary reductions, waits for their actual terminal
states, refreshes holdings/cash and then submits affordable purchases. It
reserves each purchase's bound and fees before sizing the next. Partial fills,
cancellations and rejections retain the shortfall. A changed target cancels
previous owned attempts before acting on refreshed state. An uncertain submit
is not retried until the exact broker observation establishes its state.

`fill_pending`, `cancel_pending`, `sales_pending`, `purchases_pending`,
`cash_limited`, missing-data states and `reconcile_required` are unfinished.
Only `complete` establishes this owner's currently accepted whole-unit target.
A future price move can require a different target; do not silently recompute
one while the current accepted operation is executing.

Verify actual allocations after later rotations as well as the first purchase.
A run can select the right two instruments and still hold cash because it
forgot to buy after sales completed. Inspect the full account and trade history;
positive returns or an initial correct fill cannot prove all rebalances.

Freeze the accepted target quantities for that scheduled operation. Continue
reconciling their actual unfilled remainder, not a newly recomputed allocation
from each later quote. Price movement after completion must not silently cause
daily rebalancing of a weekly or monthly strategy. Only a newly accepted signal
generation selects and values new targets. Fresh buy price bounds still govern
affordability of the remaining units; a price increase can leave a visible
cash-limited shortfall instead of authorizing borrowing.

The scheduling branch only accepts a new signal generation. Reconciliation is
outside that branch on every normal iteration. A minimal integration shape is:

```python
# initialize: use the same execution owner as the other order paths
self.allocation_execution = AllocationReconciler(
    self, self.allocation_assets, self.maximum_buy_price,
    fee_fraction=self.configured_buy_fee_fraction, lock=self.execution_lock,
)

# on_trading_iteration: signal calculation remains the original strategy's job
with self.execution_lock:
    signal = self.new_allocation_signal()  # None between accepted signal dates
    if signal is not None:
        generation, weights = signal
        self.allocation_execution.accept(weights, generation)
    outcome = self.allocation_execution.reconcile()  # also runs between dates
```

A fill/cancel observer may call `reconcile()` under that same owner. Keep these
calls out of code that chooses a fresh signal or applies a second publisher.
`maximum_buy_price` supplies the actual current allowed buy limit, not a fee-free
market price. Configure the simulation/live fees consistently with this helper's
fee fraction and disclose a cash-limited remainder. The source tracks the current
broker ID even when submission mutates the original object and returns nothing
or raises after acceptance. A missing exact-order read retains uncertainty.
