> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: crypto-strategies
description: Use for spot crypto, BTC/EUR, crypto quote assets, crypto symbol construction, and crypto first-cycle rescue work.
---

--------------------------------------------------------------
CRYPTO STRATEGIES
--------------------------------------------------------------

Use this skill when generating, refining, or rescuing spot crypto strategies.

First-cycle rules:
- BTC/USD, ETH/USD, BTC/USDT, ETH/USDT, BTC/EUR, ETH/EUR, and similar pairs with a proven runner/data path are supported first-cycle targets.
- Strategy code should use base-coin assets, such as `Asset("BTC", asset_type=Asset.AssetType.CRYPTO)`, with a separate quote asset where the API requires one.
- Do not use pair strings such as `BTC-USD`, `BTC/USD`, `BTCUSD`, `BTC/EUR`, or `BTCEUR` as the crypto base asset symbol.
- Do not silently convert BTC/EUR to BTC/USD. Preserve the requested quote asset unless a fresh capability check proves that exact pair is unavailable.

Common failure causes:
- The pair string is incorrectly used as the base asset, producing symbols like `BTC-USD/USD`.
- The test window is too short for long-lookback rules, or ML/RL warmup history was not requested before the window.
- The strategy waits for indicators that cannot compute on available bars.
- Data download latency makes the first day much slower than later simulated days.

Rescue guidance:
- Inspect logs for missing crypto data, symbol construction, and quote asset errors.
- Preserve the requested signals, thresholds, warmups, sizing, risk, and option structure. Repair technical defects in data availability, indicator computation, API usage, and state handling. If a trading-rule change is necessary, propose the exact change and obtain user approval before saving it; a smoke trade is not permission to weaken the strategy.
- If a specific pair truly lacks data, explain the exact pair limitation and offer a supported crypto pair.
