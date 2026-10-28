> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: options-strategies
description: Use for US options, spreads, single-leg options, wheel, covered-call, cash-secured-put, and options first-cycle rescue work.
---

--------------------------------------------------------------
OPTIONS STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing US-listed option strategies, including single-leg options, spreads, wheel strategies, covered calls, cash-secured puts, and volatility strategies.

Always also load `options-strategies` before changing options code.

First-cycle rules:
- Prefer SPY, QQQ, IWM, GLD, SLV, or the exact liquid optionable symbols the user named.
- Use `OptionsHelper` APIs and documented option entity patterns. Do not invent chain methods.
- Preserve the requested signals, thresholds, warmups, sizing, risk, and option structure. Repair technical defects in data availability, indicator computation, API usage, and state handling. If a trading-rule change is necessary, propose the exact change and obtain user approval before saving it; a smoke trade is not permission to weaken the strategy.
- For complex spreads, retain every requested leg and its liquidity/risk checks. Diagnose missing quotes and exact-contract selection before proposing any structure change.
- Never use `pd.np`; import numpy as `np`.

Common failure causes:
- Chains exist, but all spread legs fail strict price/spread checks.
- Expiration or strike helper names are invented or stale.
- Warmup/indicator gates run before a smoke option can be selected.
- The code assumes every option chain field is present.

Rescue guidance:
- Inspect logs for option-chain, expiration, strike, and quote messages.
- Query orders and trades. If orders are empty but chains/prices exist, trace each entry condition, its actual inputs, and contract availability. An unsatisfied requested condition is not itself a code defect.
- Make normal revisions only. Explain the technical defect repaired and verify that the requested trading rules and option structure remain intact.
