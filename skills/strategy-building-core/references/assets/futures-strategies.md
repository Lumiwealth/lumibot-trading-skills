> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: futures-strategies
description: Use for futures, continuous futures, Nasdaq/US100/NAS100 futures, session windows, and futures first-cycle rescue work.
---

--------------------------------------------------------------
FUTURES STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing futures or continuous-futures strategies.

First-cycle rules:
- For Nasdaq/US100/NAS100 requests, prefer `NQ` or `MNQ` continuous futures, not QQQ, unless the user asks for an ETF proxy.
- Use `Asset.AssetType.CONT_FUTURE` for continuous-futures smoke tests unless the user explicitly needs dated contracts.
- Avoid comparing offset-naive datetimes with timezone-aware values from `self.get_datetime()` or bar timestamps.
- Do not require `get_last_price(asset)` to be non-None when historical bars are available. Use the latest completed bar close as a sizing/reference fallback.

Common failure causes:
- Timezone comparison errors in session windows.
- `get_last_price` is unavailable in backtest while OHLC bars exist.
- Strategy waits for a session open/close that never occurs in the tested date range.
- Contract type or symbol shape is wrong.

Rescue guidance:
- Inspect logs for datetime, price unavailable, contract, and session messages.
- If OHLC/indicator artifacts exist but no trades were placed, verify whether price/sizing gates returned before order placement.
- Preserve the requested futures market. Use a smaller/lower-margin contract such as MNQ/MES/MGC when that makes the smoke practical.
