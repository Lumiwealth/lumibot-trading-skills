> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: breakout-strategy
description: Use for breakout, opening-range-breakout, channel, Donchian, momentum-breakout, and breakout first-cycle rescue work.
---

--------------------------------------------------------------
BREAKOUT STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing breakout, opening-range-breakout, channel breakout, Donchian, support/resistance, or momentum-breakout strategies.

First-cycle rules:
- Use a liquid market and the user's exact breakout window and filters. Choose the first backtest window to fit them (First test window in `backtest-rescue`): intraday rules stay short (about a week or less), daily multi-week breakouts on one symbol may need 1 to 3 months.
- For opening-range strategies, make sure the selected date range includes market sessions and that the entry clock logic uses compatible timezone-aware datetimes.

Common no-trade causes:
- The test window is too short for how rarely the breakout fires.
- Session window or timezone logic skips the trading period (a code bug).
- The order is placed too late in the day and rejected by the close guard (a code bug).
- Breakout, volume, or ATR filters never all agree in an adequate window (rules).

Rescue guidance:
- Check the window first; if it was too short, rerun the same saved revision over the right window without editing.
- Inspect indicator/decision artifacts for the first blocked condition and fix code-level blockers (session, timezone, close guard) without changing rules.
- If the user's own thresholds never fire in an adequate window, explain why plainly and offer specific choices before changing any threshold, volume multiple, trading window, or universe.

## Trailing protection is state for the held position

Use the complete tested price policy in
`lumibot-strategy-building:references/trailing-stop-policy.py`. Save it as a normal
helper through `create_file(sourceResourceKey=...)` and import that saved module.
It supplies a stop price; the existing protection owner still reconciles actual
orders, position-wide quantity, partial fills and cancellations.

Recomputing `highest_price - multiple * current_ATR` can lower a long stop when
ATR expands, even when the highest price never falls. Preserve the previous stop
as well as the high-water reference. The short-position counterpart retains the
lowest reference and the minimum accepted stop. Apply this ratchet to a requested
trailing policy, not to unrelated fixed or deliberately resetting stop rules.

Keep one policy dictionary in `self.vars` per owned position. Feed observations
on every relevant iteration and fill callback; reset it only for an actual
confirmed zero position. A cancellation, partial exit, session boundary, missing
read or restart does not mean a new position. Preserve distinct owners for
different positions, including opposite directions when the account supports them.

The first entry fill needs protection immediately. Its price reference is the
actual fill basis; have the disclosed ATR/distance available before entry, and
call the same protection owner from the actual partial/full-fill callbacks.
Later references use completed observations from the held position's lifetime,
not pre-entry highs or lows or an incomplete future bar. Do not wait for tomorrow's
signal evaluation to initialize the stop. An unavailable initial distance is
missing protection data, not permission to invent a stop or claim verification.

```python
# A price-policy example; retain the existing single order/protection owner.
self.vars.trailing = getattr(self.vars, "trailing", {})
self.trailing_price = TrailingStopPolicy(self.vars.trailing, direction="long")

# At the first actual fill, using its actual current aggregate basis:
stop = self.trailing_price.observe(position.quantity, position.avg_fill_price, atr_distance)
# Feed later completed in-position prices and the current disclosed distance.
# The protection owner consumes this stop for the whole actual held quantity.
# Supply quantity=0 only on an authoritative flat-position observation.
```

Do not reset the policy after every normal update or on an unconfirmed order
response. Check a wider
ATR, a partial entry/exit, restart and a genuinely new position in addition to
one favorable-price movement.
