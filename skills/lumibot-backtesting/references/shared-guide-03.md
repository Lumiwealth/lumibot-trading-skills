> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

- If an options backtest has chains and option prices but still completes with zero trades, inspect whether the code only tries a complex order and returns when any leg has missing quotes, unusable bid/ask, a wide spread, missing Greeks/delta, missing expiration, or too-strict liquidity.
- Complex options includes covered calls, cash-secured puts, vertical spreads, calendar spreads, diagonal spreads, butterflies, iron condors, straddles, strangles, ratio spreads, and any multi-leg order that requires every leg to pass quote/liquidity checks before placing an order. Do not make rescue guidance wheel-specific.
- Load `options-strategies` before editing options code. Use `OptionsHelper` for chain, expiration, strike, quote, and multi-leg helper operations; do not manually select contracts from raw chains when the helper has the needed operation.
- For options strategies, technical quote, chain, expiration, and order-construction repairs may proceed when they preserve the requested structure. Changing a multi-leg spread into a single leg, widening an expiration window, changing delta or strike targets, or loosening a spread limit changes user intent and requires approval before saving.
- Do not solve this by tightening option filters. A first-cycle options smoke that finds chains and buy prices but logs only "one or more option legs had unusable prices or spreads" is invalid because complex-order validation blocked the activation smoke.
- Do not add dummy fills, fake option legs, hardcoded proof-only orders, or `if backtesting` branches. The rescue revision must be understandable as a normal strategy that can trade because the entry/order path was made practical.

When to edit:
- If a structured `STRATEGY_EXECUTION_NOT_READY` or other readiness failure
  contains `issues[].filePaths`, legacy `issues[].files`, or `referencedFiles`
  naming more than one file, treat that file list as
  machine evidence. Call `list_files`, then inspect every relevant named file
  before editing. Repair the actual multi-file execution structure and preserve
  the trading idea; do not guess from `main.py` alone or merely explain the
  readiness error.
- If the readiness issue is `missing_executable_runner`, put the executable
  runner in the file that defines the strategy class, normally `main.py`, so
  the saved project has one importable and directly executable entrypoint.
  Editing only a sidecar such as `runner_settings.py` does not repair this
  readiness issue.
- Edit when the failure is caused by generated code, wrong API shape, wrong asset/data handling, or order plumbing that can be repaired without changing user rules.
- Make the smallest useful revision that addresses the proven cause.
- For first-cycle no-trade failures, do not loosen thresholds, broaden the universe, add fallback entry behavior, or change order structure without user approval. Propose the smallest exact change and wait when a rule change is required.
- Save rescue fixes as normal strategy revisions. Do not silently mutate an existing revision in place.
- After a successful rescue file edit, immediately run `start_backtest` on the returned revision over the same first-test window. Do not end the turn after the edit unless `start_backtest` itself fails or a blocker above applies.
- Never invent or reuse a backtest id to validate a rescue revision. A rescue validation id must come from the `start_backtest` result for the just-created revision.

When not to edit:
- Do not edit just to hide missing provider credentials, invalid API keys, expired data access, billing/quota blocks, or broker authorization problems. Explain the required setup.
- Do not keep retrying unsupported or unreliable first-cycle asset paths. BotSpot does not currently support forex trading as a first-class path, spot gold/silver as forex-style markets, or Indian index options such as Nifty, Bank Nifty, Sensex, NSE options, or BSE options as a first-class build/backtest path. For unsupported or mixed market requests, explain the limitation and suggest supported alternatives such as supported crypto pairs, GLD/SLV, gold or silver futures, US-listed stocks/ETFs, US options, or supported futures.
- Do not run a filled-trade smoke backtest for an alerts-only strategy unless you first convert it into a tradeable strategy with the user's consent. Alerts-only strategies do not place filled trades, so they cannot satisfy the first-backtest success metric as written.
- Do not rewrite a strategy into a different idea without telling the user. If the needed change materially changes the user's intent, ask one concise clarification.

Long-running backtests:
- `start_backtest` is asynchronous. During first-cycle smoke/rescue, it is acceptable to monitor progress because validation is part of the task.
- For first-cycle smoke/rescue, after `start_backtest` returns a backtest id with `agentRunStatus="waiting_on_external"`, record the wait in the plan and end the turn; do not poll `backtest_status` for that new run. BotSpot wakes this conversation with the terminal result. Poll only when the newest user message explicitly asks you to keep checking until it finishes.
- For first-cycle smoke/rescue, do not end with optional check-later wording while a new validation run is still active. If the runtime must yield before terminal completion, update or add the validation/rescue plan item to `waiting` with `waitReason=waiting_for_external_event` and generic evidence containing `externalKind="backtest"`, `externalId=<backtestId>`, and `revisionId`, say that the validation run is still active, and say the server-side rescue flow will continue automatically when it reaches a terminal result.
- Backtest ETA is noisy. The first simulated day can be much slower than later days because the runner starts infrastructure, imports LumiBot, and loads data. Say that plainly when reporting ETA.

Success response:
- Keep the architecture rationale from `lumibot-strategy-building` in the final
  handoff, including when validation is queued: fixed fast rules run in Python
  because calling an AI model in the trading loop adds variable latency and
  model-credit cost. Separately disclose feed, broker and order-fill limits;
  those execution limits do not replace the model-latency/cost explanation.
- Report the final revision id/version, smoke date range, data provider, filled trade count, and the main change that made it work.
- If the user approved looser filters or changed order behavior, say exactly what changed and preserve that approval in the visible plan evidence.
- If no working revision is possible, state the exact blocker and the best supported alternative.
