> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: wheel-strategy
description: Use for wheel strategies, covered calls, cash-secured puts, assignment/roll logic, and wheel first-cycle rescue work.
---

--------------------------------------------------------------
WHEEL STRATEGY
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing wheel, covered-call, or cash-secured-put strategies.

First-cycle rules:
- Use liquid optionable underlyings such as SPY, QQQ, IWM, GLD, SLV, or the user's named optionable symbol.
- A wheel needs enough buying power for at least one cash-secured put or covered call. If account size is too small, choose a smaller underlying only when the user accepts it.
- For first-cycle smoke, start with one contract and near-dated liquid expirations.
- Do not require assignment to prove the first backtest works; a filled put or call order is enough for activation.

Common failure causes:
- Strict delta/IV/expiration filters find no contracts in the tested window.
- Buying power checks reject every contract.
- The strategy waits for assignment before any order can be placed.
- Covered-call logic assumes stock ownership that the backtest does not have.

Rescue guidance:
- Inspect chains, selected contracts, orders, buying-power logs, and trade artifacts.
- If no contract qualifies, loosen one filter at a time and explain the change.
- Keep assignment/roll logic for later behavior, but ensure the first cycle can place a legitimate option trade.
