> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: mean-reversion-strategy
description: Use for RSI, Bollinger Band, z-score, oversold/overbought, pairs, and mean-reversion first-cycle rescue work.
---

--------------------------------------------------------------
MEAN REVERSION STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing RSI, Bollinger Band, z-score, oversold/overbought, pairs, or mean-reversion strategies.

First-cycle rules:
- Use liquid assets and implement the user's exact thresholds and filters. Choose the first backtest window to fit them (First test window in `backtest-rescue`); extreme thresholds on daily bars may need months to fire, so check plausibility and say so plainly when an affordable test may show no trade.
- For options mean reversion, load both this skill and the options skills before revising.

Common no-trade causes:
- The test window is too short for how rarely the thresholds fire.
- Warmup history is not requested before the window (a code bug).
- Entry requires several rare confirmations at once, or conditions that conflict.
- Pair/spread data is missing for one leg (a data problem).

Rescue guidance:
- Check the window first. If it was too short, rerun the same saved revision over a longer window without editing.
- Inspect indicators to find whether the signal never computed (code or data) or never crossed in an adequate window (rules).
- When the rules themselves never fire in an adequate window, explain why in plain words and offer specific choices (a longer test, one exact threshold change, or dropping one named filter). Wait for the user's pick before editing.
- Do not add unrelated artificial orders, and do not turn a mean-reversion request into trend following unless the user approves.
