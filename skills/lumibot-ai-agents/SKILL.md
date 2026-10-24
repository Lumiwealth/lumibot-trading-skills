---
name: lumibot-ai-agents
description: Load when someone wants an AI-powered trading strategy, an AI trading bot, an LLM agent that trades, an AI trading team or investment committee, or any LumiBot strategy built with self.agents (research agents plus one trading agent). Covers the agent API, the one-trader team pattern, prompts, tools, rules.json, cadence and cost, backtesting AI strategies, and the BotSpot build and validation workflow.
license: MIT
metadata:
  title: "AI-Powered LumiBot Strategies (LLM Agents That Research and Trade)"
---
# AI-Powered LumiBot Strategies

An AI-powered strategy is a LumiBot strategy where large language model agents
inside the strategy do the thinking. Research agents gather and weigh evidence.
Exactly one trading agent reads that research, checks the live account, and
places or skips the orders itself. Python only sets the cadence, creates the
agents, and calls them in order.

This is a different design from a Python-rules strategy. If the user wants
fixed if/else signals and Python-placed orders, use the
`lumibot-strategy-building` skill instead (see "When the user wants Python to
place the orders" below).

Examples in this skill are illustrations of code structure. They are not
investment advice and say nothing about future performance.

## Which reference to load

Load a reference with the `skills` tool: `action="get"`, `name="lumibot-ai-agents"`,
`reference="references/<file>"`.

| You are building | Load |
|---|---|
| A multi-role team (committee, bull/bear debate, sector pods, macro regime team) | `references/ai-trading-teams.md` and `references/ai-trading-team-examples.md` |
| An AI-only iron condor, credit spread, opening range breakout or VWAP strategy | `references/ai-only-scaffolds.md` |
| Auditing what the trading agent does around orders, or a strategy that duplicates order mechanics in Python or prompts | `references/ai-only-order-verification.md` |

Related public skills: `lumibot-strategy-building` (general strategy structure
and Python strategies), `lumibot-api-reference` (Strategy methods),
`options-strategies`, `stock-etf-strategies`, `lumibot-indicators`,
`fast-lumibot-strategies`, `using-botspot-mcp` (the BotSpot tools).

## The core rules (read first)

Every AI-owned trading strategy follows these rules, whether it has two agents
or ten.

1. **AI and AI only.** The agents make the decisions. There is no Python in
   between that fetches or parses data, filters filings or news, computes
   indicators or weights, picks symbols, sizes positions, parses agent text into
   orders, or skips agents with `if` statements. Python sets `self.sleeptime`,
   creates the agents in `initialize()`, and calls every agent on every
   `on_trading_iteration()`.
2. **Exactly one trading agent.** One agent has `allow_trading=True`. It places
   the trades and owns risk management. Name it by its job, for example
   `trader`, `risk_trader` or `portfolio_manager`. Immediately before acting it
   re-checks current positions, open orders and prices (and, for options, the
   exact contracts and package price). LumiBot's built-in trading skills already
   teach it those mechanics.
3. **At least one research agent, and any number of them.** Every other agent
   has `allow_trading=False`: researchers, specialist pods, bull and bear
   debaters, a devil's advocate critic. A critic may comment on risk, but that
   is advice; the trader still owns risk. A single agent that researches and
   trades at once makes more mistakes, so a one-agent AI trading strategy is not
   a valid design even for a simple single-asset bot.
4. **Agents hand work to each other only through their answers.** Python passes
   an earlier agent's `result.summary` to later agents through the `context`
   argument. That is the whole hand-off.
5. **`self.vars` may carry an agent's last answer forward**, so it does not redo
   old work next iteration. Store the answer and pass it back in as context.
   Do not parse it.
6. **Let the agent find its own way.** Agents can browse, download and read
   documents, query market data, and look up filings with built-in tools. A
   short hint about where to look may go in the prompt ("SEC filings and recent
   Alpaca news are good starting points"). Parsing code, availability code or
   pre-fetched data may not.
7. **The trading agent places the trades, not Python.** Order code tends to miss
   edge cases (a rebalance that sells the wrong amount, a symbol with a dot such
   as `BRK.B`). A trading agent reasons around them, and LumiBot's runtime skills
   make it re-check positions, open orders, prices and the returned order. Do not
   copy those mechanics into prompts or Python.
8. **The trader's own `system_prompt` states its risk rules in plain sentences.**
   At least two concrete rules: how much of the account may go into one position,
   when to hold cash, when to trim or cut a loser, how many holdings it normally
   keeps, plus any strategy rule. When the user said "safe" or gave no limits,
   choose sensible limits and tell the user what you chose. When the user
   rejected caps ("fully unrestricted"), follow that instead (see "Explicit
   mandates" below).
9. **Diversification is guidance, never a hard rule.** A single-asset bot (for
   example "in BTC or in cash") is fine. Do not add other assets or lecture. Its
   prompt still states how much of the account may go into that asset and when
   to cut or exit a losing position.
10. **Every capability is a tool, not strategy code.** Built-in tools cover the
    account, market prices and history, indicators, orders, options, news, SEC
    filings, FRED macro data and memory. Network tools go only to research
    agents that need them, via `allow_network=True`, never to the trader. Write
    an `@agent_tool` only when the user names a real provider LumiBot does not
    cover.
11. **A plain "I want an AI that trades for me" is a build request.** Do not quiz
    a beginner. Build a small team on a liquid, diversified ETF universe (for
    example SPY, QQQ, IWM, TLT, GLD) with beginner-friendly risk rules in the
    trader's prompt, explain in plain words what it will do, start a short
    validation backtest, and invite changes. Ask only when a missing choice
    would make the build unsafe or impossible.

If the user explicitly asks for a single agent, explain that an AI trading
strategy keeps a separate research agent and one trading agent, and offer a
Python or hybrid design if they need exactly one model call.

## Minimal working shape

```python
from lumibot.strategies.strategy import Strategy


class AIResearchTraderStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"  # one AI decision cycle per trading day
        self.vars.last_research = None

        self.agents.create(
            name="researcher",
            allow_trading=False,
            allow_network=True,  # research may search and read the web
            system_prompt=(
                "You research a small ETF universe: SPY, QQQ, IWM, TLT, GLD. "
                "Use market history, indicators and recent news. Return a short "
                "evidence packet: your view on each ETF, the observed prices you "
                "used, the main risks, what would change your mind, and any "
                "evidence you could not find. Never trade."
            ),
        )
        self.agents.create(
            name="trader",
            allow_trading=True,
            system_prompt=(
                "You are the only agent that trades, and you own risk. Read the "
                "research, check the account, then place or skip the orders "
                "yourself. Only trade SPY, QQQ, IWM, TLT and GLD. Never put more "
                "than 40% of the account in one ETF. Hold cash when the research "
                "is weak or mixed. Sell a position when the reason you bought it "
                "no longer holds. Say which research points you accepted or "
                "rejected and why."
            ),
        )

    def on_trading_iteration(self):
        context = {"current_datetime": self.get_datetime().isoformat()}
        research = self.agents["researcher"].run(
            task_prompt="Research today's setup and return your evidence packet.",
            context={**context, "previous_research": self.vars.last_research},
        )
        self.vars.last_research = research.summary
        self.agents["trader"].run(
            task_prompt="Review the research and the account, then trade or hold.",
            context={**context, "research": research.summary},
        )
```

Important details:

- **`allow_trading` defaults to `True` in LumiBot.** Always pass
  `allow_trading=False` explicitly on every research, critic and pod agent.
- Create each agent once in `initialize()`. Never recreate agents per iteration.
- `model` is optional. Omit it to use LumiBot's current default model, or pass
  the exact model id the user chose. See "Models and API keys".
- Keep `on_trading_iteration()` to agent calls and context passing. No
  indicators, watchlists, fallback rules, manual order code, chart markers or
  extra logging unless the user asked for them.

## Agent API reference

### Imports

```python
from lumibot.components.agents import BuiltinTools, MCPServer, agent_tool
```

### `self.agents.create(...)`

Keyword arguments (all keyword-only):

| Argument | Meaning |
|---|---|
| `name` | Unique agent name; access later with `self.agents["name"]`. |
| `system_prompt` | The agent's job description and strategy policy. |
| `model` (alias `default_model`) | Model id. Omit for LumiBot's default. Pass only one of the two. |
| `allow_trading` | Defaults to `True`. Set `False` on every non-trading agent. |
| `allow_network` | Grants outbound network tools (web search, HTTP, document reader, RSS, browser). Off by default. Give it to research agents only. |
| `tools` | Extra tools: `@agent_tool` methods or `BuiltinTools` entries. Built-in tools stay included. |
| `mcp_servers` | List of `MCPServer` objects for hosted data sources. |
| `rules_path` | Path to the strategy's `rules.json`; active rules are reloaded and injected before every call. |
| `output_schema` | JSON Schema dict or pydantic model; the validated answer appears on `result.parsed`. |
| `reasoning_effort` | One of `none`, `low`, `medium`, `high`, `xhigh`, `max`, where the model supports it. |
| `max_output_tokens` | Leave unset; set only when the user explicitly wants to cap answer length. |
| `run_timeout_seconds`, `model_request_timeout_seconds` | Optional time limits per run or per model request. |
| `include_builtin_tools`, `include_builtin_skills` | Default `True`. Leave them on. |
| `skill_dirs` | Extra folders of user-written agent skills (advanced). |

### `self.agents["name"].run(...)`

```python
result = self.agents["researcher"].run(
    task_prompt="What to do this cycle.",
    context={"key": "value"},   # JSON-friendly values: dates, earlier summaries
)
```

`run()` also accepts `model=` and `output_schema=` overrides for a single call.

### `AgentRunResult`

- `result.summary`: the agent's short final answer. This is what you pass on.
- `result.text`: all text the agent produced, joined.
- `result.parsed` / `result.parse_error`: the validated structured answer when
  `output_schema` is set, or why it did not match.
- `result.cache_hit`: whether a backtest replayed a recorded decision.
- `result.tool_calls`, `result.tool_results`: the tool-call trace.
- `result.warning_messages`: observability warnings.
- `result.payload`: run bookkeeping such as `trace_path`. Never the answer.
- `result.model`, `result.usage`, `result.latency_ms`: run metadata.

Never parse `result.summary` or `result.text` with string searches or regexes.

## Built-in tools and runtime skills

Every agent gets LumiBot's built-in tools automatically, even when you pass a
`tools` list. The main groups (tool names as the agent sees them):

- **Account:** `account_portfolio`, `account_positions`.
- **Market data:** `market_last_price`, `market_last_prices`,
  `market_historical_prices`, `market_load_history_table`, `scan_bars`.
- **Indicators:** `list_indicators`, `get_indicator`, `get_indicators`.
- **Orders (trading agent only):** `orders_submit_order`,
  `orders_submit_multileg`, `orders_open_orders`, `orders_get_status`,
  `orders_wait_for_terminal`, `orders_modify_order`, `orders_cancel_order`,
  `risk_calculate_stock_quantity`.
- **Options:** `options_get_chain`, `options_find_expiration`,
  `options_get_strikes`, `options_find_strike_for_delta`, `options_get_greeks`,
  `options_calculate_multileg_price`, `options_check_spread_profit`,
  `options_evaluate_market`.
- **News:** `alpaca_news` (when Alpaca news credentials are available).
- **SEC filings and fundamentals:** `get_filings`, `search_filing`,
  `get_filing_document`, `list_filing_sections`, `get_filing_section`,
  `get_company_facts`, `get_income_statement`, `get_balance_sheet`,
  `get_cash_flow`.
- **Macro (FRED):** `list_fred_series`, `get_fred_series`, `get_fred_latest`,
  `get_fred_snapshot`.
- **Memory and theses:** `remember`, `search_memory`, `remember_decision`,
  `remember_proposal`, `remember_risk_note`, `remember_lesson`, `open_thesis`,
  `update_thesis`, `close_thesis`.
- **Data analysis:** `duckdb_query`.
- **Network (only with `allow_network=True`):** `web_search`, `http_request`,
  `read_document`, `rss_fetch`, and the `browser_*` tools.

LumiBot also gives every agent built-in runtime skills: `stock-trading`,
`options-trading`, `research-data` and `web-documents`. The agent loads the
matching skill itself when an asset becomes relevant, so you do not need to
predict whether a broad agent will trade a stock or an option. Those skills own
the generic mechanics: fresh evidence before an order, exact-contract checks,
multi-leg construction, pending-order reconciliation, atomic submission and
post-submit verification. Keep that out of saved prompts.

A missing news, FRED or other data key never blocks a build. Build with the
tools that work, and tell the user once which saved key would add that data.

### News with `alpaca_news`

`alpaca_news` uses the active Alpaca broker connection when the broker is
Alpaca. With another broker, it uses news-specific keys `ALPACA_NEWS_API_KEY`
and `ALPACA_NEWS_API_SECRET`, kept separate so news access does not change
broker routing. It searches by symbol and date window, not keyword. Useful
guidance for a news-reading agent's prompt:

- Scan headlines first with `include_content=False` (about 10 to 20 items for
  one symbol, 30 to 50 for a broad scan), then re-read important stories with
  `include_content=True` and usually `exclude_contentless=True`.
- Use `page_token` when `next_page_token` is returned and more is needed.
- For broad or sparse searches use ETF proxies: market `SPY,QQQ,DIA,IWM`; tech
  `QQQ,XLK,SMH`; financials `XLF,KRE`; energy `XLE,USO`; healthcare `XLV,XBI`;
  rates `TLT,IEF,SHY`; commodities `GLD,SLV,DBC`.
- Do not act on one weak article; compare several and their timestamps.
- In backtests, future end times are clamped to the simulated time and flagged
  `lookahead_clamped`, which protects against look-ahead.

## Writing good prompts

**Research agents** get a crisp role and return a bounded evidence packet:
thesis, exact candidates, observed prices, risks, what would change the view,
and missing evidence. Tell them which kinds of sources to inspect (prices and
positions, news, filings, macro indicators, risk regime). Writing "never
trade" in the prompt is not enough; also set `allow_trading=False`.

**The trading agent** gets the strategy's own policy, and only that:

- objective and valid instruments
- entry and exit policy
- position and risk limits, written as sentences
- cadence-related rules ("only open new positions between 10:00 and 11:30
  New York time; otherwise manage or hold")
- any user-specific constraint
- "say which upstream advice you accepted or rejected and why", so the
  per-agent backtest output is useful later

Do not restate generic stock, options or order-tool mechanics. LumiBot's runtime
skills and tool descriptions supply them, and they improve over time.

**Hard dates.** When the user says an entry may happen only on one exact date,
put that boundary in the trader's prompt and in `rules.json`. If data or quotes
are missing that day, the trader holds rather than trading on a later date. A
broader fallback window is a strategy change the user must approve.

**Explicit mandates.** When the user states a broad mandate ("fully
unrestricted", "no artificial risk caps", "no forced stop-losses"), encode it in
the trader's prompt and `rules.json`. Do not override it with safer defaults or
argue about it. You may still keep the first test small (fewer symbols, shorter
prompts, fewer agents) so it can run quickly.

## Strategy rules: `rules.json`

BotSpot strategies can keep the user's rules in plain English in a
`rules.json` file beside `main.py`. Bind it with `rules_path` on every agent and
LumiBot reloads it and injects the active rules before every agent call. Do not
paste the rules ledger into the system prompt.

```python
from pathlib import Path

RULES = Path(__file__).with_name("rules.json")
self.agents.create(name="trader", allow_trading=True, system_prompt="...", rules_path=RULES)
```

LumiBot validates the file before any model call:

- top level is a JSON object with a numeric `version` and a `rules` array
- each rule has a unique non-empty `id`, a `status` of `active`, `disabled` or
  `deleted`, and a non-empty plain-English `interpretation`
- optional `title` and `raw_quote` (the user's exact words) must be strings
- no machine checks or verdicts: keys such as `check`, `verdict`, `overall` or
  `audit` are rejected

BotSpot's rules editor also tracks `source`, `created_by`, `last_edited_by` and
`edit_history` on each rule. Include them when you create the file so the
editor shows a clean history:

```json
{
  "version": 1,
  "rules": [
    {
      "id": "max-position-size",
      "title": "Position size limit",
      "status": "active",
      "raw_quote": "never more than 40% in one ETF",
      "interpretation": "Never let one ETF exceed 40% of total account value.",
      "source": "user",
      "created_by": "user",
      "last_edited_by": "user",
      "edit_history": []
    }
  ]
}
```

Only `active` rules are runtime instructions. Disabled and deleted entries are
history. Validate the whole JSON before saving it. Rules carry the user's
instructions into the AI; they do not make decisions deterministic and do not
guarantee any result.

## Cadence and cost

Each agent call is a model call, so cadence drives cost and speed.

- Default new AI strategies to one decision cycle per day (`sleeptime = "1D"`).
- For intraday ideas, use the coarsest cadence that can see the setup, normally
  no more often than hourly. An hourly agent can still read minute bars.
- Faster AI cycles (`30M`, `10M` or less) are a deliberate choice, not a
  default. A regular US session has about 390 minutes, so a two-agent team at
  `1M` makes at least 780 model calls per day before retries. Explain the
  credit, latency and provider rate-limit cost and get the user's explicit
  confirmation once before saving it. After that, build what they asked.
- Every agent is called on every iteration. If you want fewer AI decisions, use
  a slower `sleeptime`, not `if` statements that skip agents. Put time-of-day
  entry windows in the trader's prompt.
- If the AI is too slow, reduce the number of research agents, the universe and
  the prompt size before anything else. Keep at least one researcher and the one
  trader.
- If the strategy truly needs sub-minute reaction, it is not a good fit for an
  AI-only design. Recommend a Python or hybrid design and explain the tradeoff.

## Custom tools with `@agent_tool`

Use a custom tool only when the user names a real provider or API LumiBot does
not already cover, uploads reference code, or explicitly asks for an
integration. Never invent placeholder APIs, fake URLs or new key requirements
to satisfy "give it news" or "give it more tools".

The decorator registers a strategy method as a tool, builds its schema from type
hints and the docstring, and includes the function's source in the description
the model sees. Always write a Google-style docstring with an `Args` section.

```python
import os
import requests
from lumibot.components.agents import agent_tool


@agent_tool(
    name="get_economic_indicator",
    description="Fetch a US economic indicator series from Alpha Vantage.",
)
def get_economic_indicator(self, indicator: str) -> dict:
    """Fetch a US economic indicator.

    Args:
        indicator: Alpha Vantage function name, for example REAL_GDP or CPI.

    Returns:
        The provider's JSON response.
    """
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": indicator, "apikey": os.environ.get("ALPHAVANTAGE_API_KEY")},
        timeout=15,
    )
    return resp.json()

# in initialize():
self.agents.create(
    name="macro_researcher",
    allow_trading=False,
    system_prompt="Use economic data to describe the current macro regime. Never trade.",
    tools=[self.get_economic_indicator],
)
```

The tool returns raw provider data to the agent. It must not filter, score or
decide; the agent interprets the data. FRED is already built in, so prefer the
built-in FRED tools over a custom FRED wrapper.

### Hosted MCP servers (advanced)

```python
from lumibot.components.agents import MCPServer

MCPServer(
    name="my-data-source",
    url="https://my-mcp-server.example.com/mcp",
    exposed_tools=["tool_a", "tool_b"],
    timeout_seconds=120,
)
```

Pass the list with `mcp_servers=[...]` in `self.agents.create(...)`. Built-in
tools stay included. Keep credentials out of source code: read them from saved
environment variables (the `MCPServer` also accepts `headers` and
`auth_token_env`).

## Structured answers (optional, rarely needed)

By default agents talk to each other in plain language and the trader places
trades itself. Use `output_schema` only when Python must read an agent's answer
as data, for example a research-only report the user wants as a table. It never
changes who places orders.

```python
VERDICT = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "VETO"]},
        "reason": {"type": "string"},
    },
    "required": ["symbol", "verdict", "reason"],
}

self.agents.create(
    name="analyst",
    allow_trading=False,
    system_prompt="Review one stock and give a PASS or VETO verdict.",
    output_schema=VERDICT,
)

result = self.agents["analyst"].run(task_prompt="Review AAPL.")
if result.parsed is None:
    self.log_message(f"No usable verdict: {result.parse_error}", color="red")
else:
    self.vars.last_verdict = result.parsed
```

A pydantic `BaseModel` class also works; `result.parsed` is then an instance.

## Models and API keys

- **On BotSpot**, AI strategies run through BotSpot's managed AI in backtests and
  live bots, billed in BotSpot credits. The user does not need a personal model
  provider key, whatever provider prefix the model id has. If a backtest or bot
  start reports missing secrets, that list is the authority on what is needed.
- **Self-hosted LumiBot** (outside BotSpot) needs the model provider's own API
  key for the chosen model, even when the strategy code never reads it.
- Use current models. Omit `model` to get LumiBot's default, or use the exact id
  the user picks. Avoid very old model generations; if the user insists on one,
  mention once that it is old, then use what they asked for.
- Data keys (Alpaca news, an Alpha Vantage key for a custom tool) are separate
  from model keys. On BotSpot, save them with `saved_env_vars` and attach them
  with `envVarSetIds` on `start_backtest` or `start_deployment`. Never print raw
  key values.

## Backtesting AI strategies

- **Keep the first test short.** Every simulated iteration may call models. A
  week is a good first window for a daily strategy, one or two days for an
  intraday one. Warn the user about cost before long or expensive runs.
- **Point-in-time evidence only.** Do not present current web or news results as
  historical evidence. LumiBot clamps built-in news and data tools to the
  simulated time. Web pages fetched during a backtest may be newer than the
  simulated date; tell the agent to prefer dated sources and to treat undated
  pages carefully, and disclose that limitation to the user.
- **Replay cache.** Backtests can replay recorded agent decisions
  (`result.cache_hit`). A replay tests that recorded path; fresh model calls may
  decide differently and cost credits.
- **Check `agent_health` before trusting results.** Provider rate limits
  (HTTP 429) are retried. If a bar still gets no AI decision, the log says
  `BACKTEST INCOMPLETE`, the parameters show `agent_<name>_skipped_runs`, and
  `settings.json` has `agent_health` with `complete: false`.
- **A hold is a valid result.** A holiday, missing evidence or "no signal" hold
  is not a failure. Never add a fake trade (for example an
  `if self.is_backtesting:` order) to make a test show a fill, and never change
  quantities, signals or budgets just to get a fill.
- **If the first run is slow**, shrink the universe, the number of research
  agents and the prompts. Do not add more roles or a bypass trade.
- **Data warmup.** If the first allowed trade is on the backtest's first date and
  needs historical bars, start the backtest one session earlier and describe
  that as warmup, not an extra trading day.
- **Read the agent output.** The backtest artifacts include per-agent detail
  (for example `agent_detail.parquet`) showing each role's output and the
  trader's reasoning. Inspect it with `get_backtest_artifact` or `query_csv`
  where available, and `get_backtest_logs` for provider or runtime errors.

## Building it on BotSpot (public MCP tools)

1. **Create the workspace:** `create_strategy` with a name and a short
   description that says what the agents do and any first-version
   simplifications. It returns neutral starter files and ids.
2. **Read before writing:** `get_file` on the returned `main.py`. Use
   `list_files` to learn whether `rules.json` exists before reading or creating
   it.
3. **Write the full implementation:** use `replace_file` for the first complete
   AI-team `main.py` (the starter is placeholder code, so a whole-file replace
   is cleaner than patching it). Include `rules_path` from the start if you will
   add `rules.json`. Use `patch_file` later for targeted edits to real code.
4. **Rules:** if `list_files` shows no `rules.json` and the user gave rules,
   `create_file`; if it exists, `get_file` then `replace_file`.
5. **Read back:** `get_file` on the newest revision and confirm the file is
   complete (imports, class, both agents, `allow_trading` set correctly).
6. **Validate:** `start_backtest` on the newest revision with a short date range,
   then `backtest_status` with the returned id. Use `get_backtest_logs` and
   `get_backtest_artifact` to diagnose. A missing personal model key is not a
   reason to skip validation on BotSpot.
7. **Iterate:** `list_revisions` and `set_strategy_revision` to move between
   versions.
8. **Go live only with the user.** `start_deployment` starts a real bot; the user
   reviews and approves deployments and trades on botspot.trade. Never start one
   on your own initiative, and always state whether the account is paper or real
   money.

Copy every strategy, revision and backtest id exactly from the latest tool
result. Never retype or reconstruct an id from memory.

To learn from public examples, `marketplace_strategies` and `clone_strategy`
let the user start from a published strategy.

## When the user wants Python to place the orders

Follow the user. If they explicitly want code-owned signals and orders, build
that: every agent `allow_trading=False`, and Python owns signals and orders by
the user's rules. That is a hybrid or Python strategy, not an AI-only one, so
use `lumibot-strategy-building` for the Python side. When you describe the saved
design, include one plain sentence on the tradeoff: an AI trading agent usually
places the orders because order code tends to miss edge cases (for example a
symbol like `BRK.B`), and this build keeps orders in Python because the user
chose that. Do not refuse, nag or repeat it. Do not force existing Python
strategies to become AI strategies either.

## Common mistakes

- Forgetting `allow_trading=False` on research agents (LumiBot defaults to
  `True`), which creates several order owners.
- One agent that researches and trades.
- Python that fetches data, computes indicators, filters a universe or sizes
  positions before handing a "pre-digested" packet to the agent.
- Parsing `result.summary` and then calling `create_order` or `submit_order`.
- `if` statements that skip an agent on some iterations.
- Copying generic order mechanics (check positions, then price, then submit,
  then verify) into every saved prompt.
- Giving network tools to the trading agent.
- Inventing data APIs or key requirements the user never asked for.
- A one-minute AI loop the user never confirmed.
- A fake proof trade in backtests.
- Treating current web content as historical evidence.
