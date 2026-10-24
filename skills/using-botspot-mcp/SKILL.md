---
name: using-botspot-mcp
description: Load first in any session connected to the BotSpot MCP. Explains what BotSpot does, which tools to call in what order to build, backtest, compare, share and deploy a LumiBot trading strategy, how sign-in works, and the mistakes that waste time.
license: MIT
metadata:
  title: "Using the BotSpot MCP well"
---
# Using the BotSpot MCP well

BotSpot (https://botspot.trade) builds, backtests and runs trading strategies written with LumiBot, the open-source Python trading library (https://github.com/Lumiwealth/lumibot, docs at https://lumibot.lumiwealth.com). Through this MCP you can write a strategy, backtest it on historical data, read the results, and, with the user's approval on botspot.trade, run it with their own broker.

Nothing here is investment advice. Backtest results are simulations of the past, not a promise about the future. Say that plainly when you show results.

## 1. Signing in

- These skills and the public Marketplace browse actions (`marketplace_strategies` and `marketplace_accounts` with action=list) work without signing in.
- Every other tool needs the user to connect BotSpot. When a tool asks for sign-in, the client shows its Connect button. Connecting creates a free BotSpot account if the user does not have one.
- `get_account_status` shows the user's plan and backtest usage. If a limit is reached, `create_checkout_link` returns a checkout link the user can open. Never invent prices; read them from the tool result.

## 2. Load the right skill first

Call `skills` with action=list once, then action=get for what the task needs:

| Task | Skill |
|---|---|
| Write, edit or fix any LumiBot strategy | `lumibot-strategy-building` |
| Exact LumiBot API names, lifecycle, examples | `lumibot-api-reference` |
| Stocks and ETFs, rebalancing, rotation | `stock-etf-strategies` |
| Options, chains, spreads, the wheel | `options-strategies` |
| Indicators and charts in a backtest | `lumibot-indicators` |
| A strategy where AI agents research and trade | `lumibot-ai-agents` |
| Slow strategies, big scanners, fast order handling | `fast-lumibot-strategies` |

Skills point to reference files. Load a reference only when you need it: `skills` action=get, name=<skill>, reference=<path>.

## 3. The build loop

1. **Understand the idea.** Ask only what you cannot reasonably choose: what to trade, when to enter, when to exit, how much to risk per position, and the timeframe. Pick sensible defaults for the rest and say what you picked.
2. **Create the workspace.** `create_strategy` with a clear name and description. It returns starter files (`main.py`, `requirements.txt`).
3. **Write the code.** Read the starter with `get_file` (it returns an `editHandle`), then write the full strategy with `replace_file`. For later small changes use `get_file` then `patch_file`; for a new file use `create_file`. Every write creates a new saved revision. Always re-read before the next edit so you work on the newest revision.
4. **Pick data.** Backtests use the conversation's data provider. The default (BotSpot Auto) covers stocks, ETFs, indexes, crypto and futures. Options backtests need the user's own data source (for example a connected Alpaca account or their own Polygon key). To use another source, pass `dataProvider` (for example `alpaca` or `polygon`) on `start_backtest`; change it only when the user asks or a tool result says the current source cannot serve this strategy.
5. **Backtest.** `start_backtest` with the revision and a date range. Start with a window long enough to see several trades (often one to two years of daily data, or a few weeks of minute data). It runs in the background and returns a backtest id.
6. **Wait well.** Call `backtest_status` with that id. It reports progress, simulated date, current positions and orders. Summarize progress instead of polling in a tight loop.
7. **Read results.** `show_backtest_dashboard` gives return, drawdown, Sharpe and the equity curve. `get_backtest_logs` shows errors, tracebacks and your strategy's own log lines. `get_backtest_artifact` and `query_csv` let you inspect trades, stats and indicators with SQL.
8. **Check correctness before praising returns.** Did it trade at all? Did cash ever go negative without margin? Were exits filled? Do the trades match the rules the user asked for? The `lumibot-strategy-building` skill has the checklist.
9. **Improve.** Fix the code with `patch_file`, then backtest again. To compare settings without editing code, use `start_parameter_experiment` (2 to 10 variants on the same revision and window). `show_backtest_comparison` puts runs side by side.
10. **Go back in time.** `list_revisions` shows saved versions; `set_strategy_revision` restores one.

## 4. Running it live or on paper

- The user connects a broker on botspot.trade or through `broker_connections`. Never ask for broker passwords, API secrets or account numbers in chat. Saved keys a strategy needs go through `saved_env_vars`, whose values are never shown back.
- `start_deployment` prepares a deployment for the user's review. Nothing runs and no order is placed until the user approves it on botspot.trade. A live account can place real-money trades, so confirm the exact strategy, broker account and settings with the user first.
- `list_deployments`, `get_deployment_logs`, `get_bot_performance` and `show_bot_activity` show how a running bot is doing. `stop_deployment` prepares a stop for the user to approve.
- A one-off trade the user asks for goes through `place_trade`, which also returns an approval link. Never say a trade happened until `get_single_trade_status` confirms it.

## 5. Ideas from the Marketplace

`marketplace_strategies` action=list browses public strategies and their recorded results. With sign-in, `clone_strategy` with a listing id copies a strategy the publisher allows to be copied into the user's own account, ready to backtest or change.

## 6. Mistakes that waste time

- Writing the strategy from memory of an old LumiBot version. Load `lumibot-strategy-building` and `lumibot-api-reference` first.
- Editing a stale copy. Re-read with `get_file` after every write.
- Starting many backtests at once while debugging. Fix the first error from `get_backtest_logs`, then rerun.
- Calling a backtest a success because it finished. Check that it traded the way the user asked.
- Changing the user's rules (universe, weights, timing, risk limits) to make a backtest look better. Ask before changing any rule; explain trade-offs instead.
- Mixing up ids. A strategy id, a revision id, a backtest id and a deployment id are different things; use the one the tool asks for.
- Hiding failures. If something fails, say what failed and what you will try next.

## 7. Feedback

If something in BotSpot is broken or confusing, `send_feedback` with kind=bug or kind=feature reaches the BotSpot team.
