> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: moving-average-strategy
description: Use for SMA, EMA, crossover, trend-filter, moving-average warmup, and moving-average first-cycle rescue work.
---

--------------------------------------------------------------
MOVING AVERAGE STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing SMA, EMA, crossover, trend-following, or moving-average filter strategies.

## Complete the execution owner before writing the strategy

This pattern supplies signals; it does not implement position protection. A
daily moving-average decision does not turn a requested loss limit into a
daily-close-only exit. For a requested protective stop, load
`lumibot-strategy-building:references/protective-position-example.py` before
writing the order lifecycle. Its complete owner connects standing protection
to actual filled position size/basis and keeps an accepted exit outstanding
through cancellation, rejection and later signal changes. Keep the signal,
sizing and fresh-crossover re-entry policy separate from that execution owner.

Make the implementation plan cover both the signal and the requested risk
behavior. Before calling the strategy complete, inspect whether the saved
owner protects the position between signal evaluations and retains unfinished
exits. A daily price check followed by a market sell does not implement that
standing protection, even if the backtest happens to sell at a similar price.

First-cycle rules:
- Implement the user's exact lookbacks and crossover rules. Choose the first backtest window to fit them (First test window in `backtest-rescue`): a daily 20/50-day crossover usually needs 1 to 3 months to fire once; a 50/200-day cross is rarer, so say plainly when an affordable test may show no trade. Request enough history before the window for warmup.
- Do not return before order placement just because one optional moving average is unavailable.

Common no-trade causes:
- The test window is too short: a daily crossover happens only a few times a year, so a 7-day or 1-month test of daily rules usually has zero trades. Fix by testing the right window, never by changing the rules.
- The code requests fewer bars than the longest lookback, so the long average is never computed (a code bug: request enough history and rerun the same window).
- A crossover check that compares against values that are never stored, so no cross is ever detected (a code bug).

Rescue guidance:
- Check the window first. If it was too short for the rules, rerun the same saved revision over the right window without editing.
- Inspect indicator artifacts and logs to see whether moving averages are NaN/unavailable (code or data) or simply did not cross in an adequate window (rules).
- Never shorten lookbacks, swap a crossover for "already above" trend state, or add a buy-now entry to make a test trade unless the user approves that exact change.
