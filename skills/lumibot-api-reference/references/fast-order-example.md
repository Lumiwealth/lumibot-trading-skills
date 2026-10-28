> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Complete copyable fast-order controller

Choose this full-controller integration when the saved combined lifecycle owner
is missing/incoherent, or when the user requests the complete pattern. If the
saved strategy already has a coherent operation/queue owner and only its claims
or partial-fill arithmetic are defective, preserve it and use the focused
order-operation-ownership and order-quantity-accounting references to repair the
existing methods. Adding this helper alone cannot fix an unmodified main.py.

For a requested copyable code pattern, load the raw Python resource named below and quote it
verbatim, then explain its configurable business inputs. The length reflects
verified concurrency and recovery paths; do not regenerate a shorter controller
or remove its helper bodies for brevity. The resource is the maintained tested
implementation, not merely inspiration for a new implementation. For an actual
saved-strategy repair, transplant these protected mechanics while preserving the
existing strategy's signal, basket, price, sizing and runner. A conceptual-only
question instead uses the compact lifecycle in fast-order-management.md.


First load the parent lumibot-api-reference skill and its
references/fast-order-management.md contract when they are not already loaded.
This code resource does not implicitly load that contract.
For a code-pattern request, include the full raw file in the reply.
For a saved repair, adapt business inputs and preserve all lifecycle helpers.

Saved repair procedure when a coupled scan/cancel/hedge defect needs the complete owner:
1. Create one local helper from the COMPLETE raw Python file, preserving all
   lifecycle bodies. The size of the original strategy does not change this.
2. Read the original main.py from that new revision for its fresh editHandle.
   Replace it with its original named class subclassing the helper, its actual
   investment-policy hooks and its original executable runner.
3. Preserve entry selection, symbol order, prices, quantities and hedge inputs.
   For a first-priority search, delegate its acquisition step to the provided
   ordered-acquisition helper instead of recreating cursor or obligation logic.
4. Read both final saved files back. Lead the explanation with the old concrete
   defect, then the saved repair and its limits. A saved edit proves no fill,
   broker latency or live deployment.
When integrating this complete owner, keep these tested mechanics in one local
Python helper module copied completely from this resource, and retain the
original main.py strategy class as a subclass with its original business rules
and runner. Use the existing create_file/replace_file tools; no SDK change or
external dependency is needed. Do not reimplement a shorter state machine in
main.py. After creating the helper, get_file main.py on the newly returned
revision for a fresh edit handle, then replace its business subclass and read
both saved files back. Preserve the complete revision, including existing files.
The business subclass calls super().initialize(), implements the actual bounded
selection/cache hooks, and supplies the original option, price, size and hedge
inputs. Retain first-eligible watchlist priority. Freeze hedge instrument and
size per canonical entry before submission, so a late fill cannot use the next
candidate's hedge inputs. The raw helper retains that snapshot across aliases.
The normal file tools may replace the complete file in one write. Its length is
necessary to retain the tested mechanisms; a short save omitting them is not a
completed repair.


Canonical source: `lumibot-api-reference:references/fast-order-controller.py`.

This wrapper contains no alternate controller. Load that resource before editing.
Save the helper with create_file(strategyId=<actual returned strategy ID>,
revisionId=<actual current revision ID>, path="order_lifecycle.py",
sourceResourceKey="lumibot-api-reference:references/fast-order-controller.py").
Omit content and attachment. This copies the full source losslessly through the
normal file owner; do not spend the turn retyping it or researching another
controller. Await the returned revision, then wire the original business class.
Copy strategyId and revisionId byte-for-byte from the latest successful tool
result; these are opaque identities, not text to reconstruct. If validation
rejects an ID, read the actual current identity again and correct the request
before another write. Repeating the same rejected ID cannot repair it.
Create the local helper with its whole returned source unchanged, then wire the
original business subclass to it. Verify the saved helper with get_file; its
contentHash should match the complete returned helper source. If it differs, read the saved file and correct
the missing or altered content before reporting completion. Keep business inputs
and selection hooks in the subclass, not in a shortened controller copy.


Delivery check after reading the implementation: when the user asks what code
pattern to use or asks to see code, include the complete raw Python file in
the final reply. Loading the resource did not show its code to the user. Keep
all helpers and verify copied identifier spellings against this source. For an
authorized saved repair, save the adapted complete controller and actual
business-input hook with the existing class identity and runner, then read it
back; the final prose may be brief after the code is saved.

## Business scan adapter: preserve first-eligible priority

The raw helper owns the cancel/fill/hedge lifecycle. Keep its on_trading_iteration
and callbacks inherited. Set scan_symbols to the original watchlist and provide
only the original acquisition/selection hooks. For an ordered independent search,
the business subclass's scan adapter delegates to the existing ordered owner:

<!-- saved-business-scan-adapter -->
```python
def _run_one_bounded_scan_step(self):
    return self._run_one_ordered_acquisition_step(self._acquire_candidate_data)
```

_acquire_candidate_data(symbol) performs the original bounded per-symbol data
acquisition and returns its observations. _prepare_candidate_from_cached_evidence
implements the original finite first-eligible selection and sets option_asset,
entry_quantity, entry_limit_price, stock_hedge_asset and stock_hedge_quantity.
It submits no order. The ordered owner advances an unfinished search and resets
its cursor to zero after selection, preserving first-watchlist priority for the
next independent pair. Do not replace this owner with a new loop, leave the
cursor on the selected symbol, or override the inherited callback/hedge methods.

After saving, explain the actual old defect and corrected ownership. Removing
lost tracking is a real mechanical repair; it does not guarantee broker latency,
fills or higher trading frequency. Keep preserved price/risk settings and any
optional policy observation separate. No pricing question is needed to finish
the already authorized mechanical repair.
