> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: stock-etf-strategies
description: Use for stock, ETF, index-ETF, liquid-universe, GLD/SLV, and equity first-cycle strategy generation, refinement, or rescue.
---

--------------------------------------------------------------
STOCK AND ETF STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing stock, ETF, index-ETF, or basket strategies.

First-cycle rules:
- Prefer liquid US-listed symbols such as SPY, QQQ, IWM, DIA, GLD, SLV, AAPL, MSFT, NVDA, TSLA, or the exact liquid symbols the user named.
- Implement the user's rules exactly and pick the first backtest window to fit them (First test window in `backtest-rescue`: short by default, longer only when the rules need it and the test stays cheap). Request warmup history before the window.
- If the user asks for "gold" or "silver" without requiring spot forex, use GLD/SLV or listed options/futures only after making that substitution clear.
- Avoid broad unsupported universes that need unavailable screening data. If the user asks for a competition or stock-picking strategy, start with a small liquid universe and explain that it can be expanded later.

Common no-trade causes:
- The test window is too short for daily or rare rules to fire (fix the window, not the rules).
- Indicator warmup returns early because too little history was requested (a code bug).
- Too many confirmations are required at once.
- The strategy computes signals on old history but sizes/orders using unavailable last prices.
- Entry logic only runs at a time outside the selected market/session.

Rescue guidance:
- Inspect trades/orders directly. If orders are absent, inspect the signal branches and logs.
- Check the window first; if it was too short for the rules, rerun the same saved revision over the right window without editing.
- Fix proven code blockers (history request, last-price sizing, session timing) without changing rules.
- Keep completed signal bars separate from sizing and execution prices. Inspect the supported API's timestamp and price semantics before a price repair. Do not relabel the prior signal bar's open as the current execution open, read a future daily close, or require a current-session row from an API that returns only completed history. A missing current-session historical row does not prove that all supported point-in-time price sources are unavailable.
- If the user's rules never fire in an adequate window, explain why in plain words and offer specific choices (a longer test, one exact threshold change, or dropping one named confirmation). Change nothing until the user picks.
