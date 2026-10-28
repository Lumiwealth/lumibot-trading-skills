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
