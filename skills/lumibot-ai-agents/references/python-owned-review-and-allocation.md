> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Python-owned decisions with a non-trading AI reviewer

Use only when the user explicitly chose Python execution. AI-owned strategies
keep selection, sizing and orders with their sole trading agent.

## Explicit Python order ownership

When the user explicitly chooses Python signals/orders and non-trading AI,
implement that choice. Begin the final handoff with a compact **Design:** line explaining this tradeoff once; do not repeat it in progress updates:
Use one concrete example, rather than shortening the explanation to "edge cases":
"BotSpot normally lets one trading AI place orders because code can sell the
wrong quantity during a rebalance; this build keeps orders in Python as you
requested." Every AI role has allow_trading=False.
Complete BUY targets against confirmed existing positions as below, rather than
skipping every held symbol. An already-held skip is not duplicate-order control;
reconcile actual pending orders separately.
At the saved-code readback, follow one qualifying held underweight through the
actual sizing and submission path. A positions-membership continue still skips
the required top-up even when a separate helper computes target weights.

## Python-owned equal-weight BUY targets

For a user-selected Python BUY-target design, evaluate the user's signal and AI
PASS/VETO policy first. Include EVERY qualifying symbol in the target set,
including held underweights. Use confirmed account value, positions and spendable
cash; an unfilled sell is not available cash. This pure sizing step creates no
signal, order or additional sell rule. Apply the common factor before any
required broker quantity rounding, then reconcile reservations before submission.

```python
import math

def equal_weight_buy_quantities(prices, held_quantities, eligible, account_value, available_cash):
    eligible = list(dict.fromkeys(eligible))
    if not eligible:
        return {}
    if not math.isfinite(account_value) or account_value < 0 or not math.isfinite(available_cash):
        raise ValueError('Use verified finite account values')
    if any(not math.isfinite(prices[symbol]) or prices[symbol] <= 0 for symbol in eligible):
        raise ValueError('Each eligible asset needs its actual positive price')
    target_value = account_value / len(eligible)
    deficits = {symbol: max(0.0, target_value / prices[symbol]
                           - held_quantities.get(symbol, 0.0))
                for symbol in eligible}
    required_cash = sum(deficits[symbol] * prices[symbol] for symbol in eligible)
    common_factor = min(1.0, max(0.0, available_cash) / required_cash) if required_cash else 0.0
    return {symbol: deficit * common_factor for symbol, deficit in deficits.items()}
```

An overweight gets a zero BUY deficit, not an unauthorized sell. Retain the
user's VETO exit and other actual sell rules independently. AI-owned designs
leave this decision with their sole trader rather than adding Python orders.

## Complete review coverage and independent exits

When the user requests a verdict for each symbol, the reviewer prompt must
require one allowed decision for every requested symbol. State unavailable
evidence separately; do not instruct the model to omit difficult symbols.
Python must not fabricate a missing PASS/VETO. A missing review blocks a new
purchase and does not erase an already established exit intent.

Evaluate affirmative exit decisions for held positions before entry-only data
filters. Missing momentum warm-up bars cannot cancel an accepted exit. Obtain
the execution evidence needed by that close independently. If it is unavailable,
retain the exit intent and report the actual data problem. Reconcile opposite-side
pending buys and their fills without forgetting that exit or duplicating orders.

An accepted exit is durable state, not just today's verdict. A pending buy must not erase the accepted exit.
Reconcile it at each iteration and order callback: request cancellation of the
conflicting buy, wait for its actual terminal status, refresh the filled position,
then submit or retain one close for the actual remainder. A cancel request is not
a cancellation, and a later PASS does not clear an unfinished accepted exit.
Clear the intent only after confirmed flatness and reconciled pending orders.
Avoid a blanket `if any active order: skip exit`; a working close and a working
buy have different meanings.

The existing `strategy-building-core/references/protective-position-example.py`
reference (public owner: `lumibot-strategy-building`) implements this lifecycle.
Load it when building Python-owned accepted exits. Its `LongPositionProtection`
can use `stop_for=lambda position: None` when the user requested exits but no
standing stop. Keep one state dictionary per asset in `self.vars`, reconcile
before new entry decisions and on order callbacks, and request the accepted exit
without replacing the user's signals or sizing. Do not add an unrequested stop.
At saved-code review, trace a held position plus an active buy through VETO,
cancellation, a late partial fill, the next PASS and eventual flatness. The close
must survive that sequence without duplication or an unauthorized new buy.

For an equal-weight BUY target, qualifying stocks already held still belong in
the eligible set. Calculate target quantity minus confirmed held quantity and
buy its positive deficit; an unconditional already-held skip loses legitimate
underweight purchases. Apply one common confirmed-cash scaling factor to all
proposed buys. A BUY-target policy does not authorize selling overweights;
perform reductions only if the user asked for rebalancing or a stated veto exit.
This allocation math belongs in Python only when the user explicitly selected
Python-owned orders; AI-owned designs leave decisions with the sole trader.

