> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

## Critical Order-Readiness Contract

When editing an existing AI trading team, investment committee, or saved
strategy that uses ``self.agents.create`` because the user mentions blind
orders, order readiness, safe order placement, or letting the AI place trades
safely, rely on the current LumiBot runtime skills for the reusable readiness
and verification sequence. Avoid copying that sequence into every strategy
prompt. Keep only user-specific readiness constraints in the policy. Load
`references/ai-only-order-verification.md` to audit the runtime boundary and to
identify whether the saved strategy is incorrectly duplicating generic
mechanics in Python or prompt text.

If the edited strategy has no successful filled-trade backtest yet, or the
current workflow context says this is first-cycle validation, the saved-code
readback is not completion. Start a fresh validation backtest on the newest
revision and record the external wait before final-answering, unless the user
explicitly disabled automatic backtests or a real blocker appears.

When the user asks for an AI trading team, AI investment committee, pod
structure, Ray Dalio/Buffett/Ackman/Citadel-style AI team, or multiple AI roles
that debate before trading, load:

- `references/ai-trading-teams.md` for the team-building contract;
- `references/ai-trading-team-examples.md` for example shapes.

For a new AI trading-team build, code generation is not complete after
`create_strategy`, `replace_file`, or readback. After the saved readback,
start the first validation backtest on the newest revision unless the user
explicitly disabled automatic backtests or a real tool blocker prevents it. If
the plan tool rejects or the visible plan is stale, fix the plan or continue to
the validation action; do not final-answer that the build is saved while
validation has not started.

For a new AI trading-team first build, do not call `saved_env_vars(action="list")` as a
precondition for the initial smoke backtest unless the current user explicitly
asked to use or diagnose a saved key. Empty saved-key inventory is not a blocker
before validation starts. Call `start_backtest` on the newest saved revision and
handle any actual failed start result from that tool.

Do not call `set_runtime_secret_requirements` as a prerequisite for that first
validation run. Strategy code and revision analysis own runtime-secret
requirements. After saved-code readback and the implementation-to-launch plan
handoff above, call `start_backtest` directly; treat only its actual result as validation
evidence. A missing scope or failure
from a secret-metadata tool is not permission to skip the required start.

For a new AI trading-team build, use the full first-build flow from
`lumibot-strategy-building`: create/maintain the visible plan, create the neutral
workspace, read the returned `strategyId`/`revisionId`, replace
`main.py` with the real AI-team implementation, read back the new edited
revision, then start validation. A `create_strategy` result with
`workspaceStatus="neutral_starter"` is not implemented code. Do not call
`start_backtest` from that neutral starter revision, and do not treat a plain
starter `get_file` read as a saved-code readback.

For this attached workspace, omit optional strategy/revision IDs on supported
file tools, including `create_file(path="rules.json", ...)`: attachment follows
the latest successful write. Use the fresh file edit handle where required.
For `start_backtest`, or an explicit historical/different target, copy only the
complete exact IDs required by that tool from its latest authoritative result.
Never manually reconstruct a UUID. A write to `rules.json` also advances the
whole strategy revision; read back the final active revision before validation.

When the first permitted trade is on the requested backtest's first date and it
depends on historical bars or option quotes, start validation with one prior relevant market session
when the product's date range allows it. Keep the saved
strategy gated to the user's actual eligibility window and describe the earlier
session as data warmup, not an extra trading day. If the requested start cannot
be extended, preserve missing first-day evidence as missing rather than moving
an exact trade to a later date.

For run-only AI trading-team requests that mention a saved Gemini key, the
required sequence is: load this skill, call `saved_env_vars(action="list")`, select/rely
on saved metadata containing `GEMINI_API_KEY`, then call `start_backtest` for
the requested window. If `start_backtest` fails immediately with missing runtime
secrets, invalid/missing key metadata, or another fixable saved-secret issue,
that failed call is not a running backtest. Inspect saved env-var metadata,
correct the request when possible, and retry once before final-answering. Only
a later `start_backtest` result with a real backtest id and external wait may
be described as waiting/running.

For AI trading-team revision checks asking whether saved environment variables
are required, inspect the saved code first with `get_file` and identify the
requested credential mode. Ordinary BotSpot-managed inference does not require
a saved personal provider key, even when the selected model is Gemini, OpenAI,
Anthropic, or xAI. Explicit BYOK/local execution does require the matching
provider key even if the code does not directly read `os.environ`. Availability
tools such as `saved_env_vars(action="list")` show what the user has saved; they do not
prove either credential mode. Do not final-answer with "I can inspect the code
next" when the current request is already asking you to check the revision.

For AI trading-team key diagnosis on a failed backtest, do not scrape logs as
the primary key source. Use `list_backtests` to find the run and
`backtest_status` to inspect attached saved env-var set metadata. Report only
safe metadata such as env-var set id, display name, key names, and status; never
print raw key values or delete/disable keys. Do not final-answer after
`list_backtests` alone, even if it includes `runtimeSecrets`; call
`backtest_status` for the exact chosen backtest id first.

IMPORTANT: Every model in the CURRENT AI MODELS table runs through BotSpot's managed AI on BotSpot (backtests and bots), billed in BotSpot credits, and needs no personal provider key, whatever its provider prefix. A provider prefix in ``model=`` never means provider-direct. A personal provider key applies only when the strategy runs outside BotSpot (self-hosted LumiBot needs that provider's own key) or when the saved code itself reads the key; for a BotSpot run, the missing-secrets list a start or backtest returns is the authority. Write model ids exactly as in CURRENT AI MODELS, including any ``-preview`` suffix (some have no provider prefix).

Choosing a model: take exact ids only from the CURRENT AI MODELS table at the end
of the system prompt (the BotSpot AI model picker, with each model's price and
benchmark score). Unless the user picks one, write the model marked (default)
and recommend it; the table, not this skill, says which model that is today and
how the others compare on score and price. GPT-3.5, GPT-4, GPT-4 Turbo and GPT-4o are extremely old; never
choose them yourself, and avoid any model that is not in the table. If the user
insists on an older model, even if they say they know it is old, push back once
in your final answer (one sentence: it is old, and name the model you recommend
from the table), then use exactly the model they named without waiting for
another confirmation. Never refuse an older model.

Non-Gemini ids are routed through LiteLLM (which ships with LumiBot). The replay cache keys on the model id, so swapping providers on the same backtest produces fresh runs rather than stale cross-model replays.

Use AI agents when:

- The user wants an AI to decide what to trade based on news, economic data, or market conditions
- The user wants non-deterministic trading where the AI reasons about evidence before acting
- The user describes a strategy in natural language like "buy stocks with strong momentum" or "allocate based on macro conditions"

For macro AI-agent strategies such as Ray Dalio-style allocation, Citadel-style
sector pods, Buffett value selection, or multi-agent investment committees,
make the evidence tools explicit:

- If the strategy should reason from news, rely on the built-in `alpaca_news`
  tool (on by default when Alpaca news credentials exist). Missing credentials
  never block the build: save and validate the strategy, and say once which
  saved key adds news.
- If the strategy should reason from macroeconomic data, add a real provider
  tool only when the user has or requests that provider. For FRED use
  `FRED_API_KEY`; for Alpha Vantage macro endpoints use `ALPHAVANTAGE_API_KEY`.
  Do not imply a macro agent is using Federal Reserve data unless the saved code
  exposes a working macro data tool and the required key is supplied.
- Tell the agent prompt which evidence sources to inspect before trading:
  prices/positions, news headlines/articles, macro indicators, and risk regime.
- Keep the trading agent responsible for the final order decision, but require
  it to cite or summarize which upstream agent advice it accepted, rejected, and
  why. This makes `agent_detail.parquet` useful for later analysis.
- If tools are omitted for cost or first-smoke speed, say that in the strategy
  description and test a variant later instead of pretending the tool exists.

Retain Python-owned execution when explicitly chosen, when editing an existing
Python strategy without conversion authorization, or when the user chooses it
for latency or inference-cost requirements. When the user explicitly chose Python-owned
orders for a new build, follow convention 9 above, including its one-sentence
recommendation in the final reply. Rules expressible as if/else,
precise indicator thresholds, and absence of the word AI do not imply Python.

Historical AI testing records the model, Rules revision, configuration and
source limitations. Keep the researcher's web and document tools available in
backtests; `is_backtesting` alone is not a reason to disable `allow_network`.
Prefer sources dated on or before the simulated decision. Exclude known future
information. Missing original publication timestamps or vintage metadata do
not automatically disqualify all research: use reasonable date approximations
when supported, describe the evidence and uncertainty, and never claim exact
point-in-time fidelity or relabel current news as historical evidence. Replaying
recorded decisions tests that trajectory; fresh model decisions may differ and
incur new inference cost. A valid holiday,
missing-evidence or no-signal hold is not a failure requiring a manufactured
trade. Never change quantities, signals or budgets just to obtain a smoke fill.

First-cycle backtest rule:
- Keep the first AI-owned backtest short: about a week for ordinary daily decisions, or one to two completed sessions when the selected model or cadence makes it expensive. Explain the chosen window and credit implications. A user who explicitly selected the model and asked to start validation has already made that choice: proceed within that scope without demanding the same approval again. Ask only for a genuinely missing spending choice or an actual credit/entitlement requirement returned by the tool. Never switch models or reasoning to reduce cost without permission.
- Do not call the LLM on every smoke iteration before the first filled trade; keep the first revision practical by limiting the AI call cadence, universe, and prompt size while preserving the AI decision path.
- Preserve the user's AI-agent live behavior, but make the first revision practical: use exactly one trading-enabled terminal risk/trader and at least one compact non-trading upstream researcher; keep a tiny supported universe, bounded setup packet, and short prompts so the normal agent path can place a real order during the first AI-owned test. Use simple risk controls only when the user did not reject them; when the user asked for a fully unrestricted trader or explicitly rejected risk caps, do not invent conservative risk caps.
- Do not add an unrelated deterministic `self.is_backtesting` order that bypasses the AI-agent decision path. If the LLM path is too slow, reduce agent count, reduce universe size, cache/limit evidence, or simplify the final agent prompt instead of adding a fake proof trade.
- Run the normal agent decision path before date gates, contest-window gates, market-session gates, or strict filters that can return early. Otherwise the first-cycle strategy exists in code but never executes.
- Explain any first-revision simplifications in the description; later revisions can tighten the requested AI-agent decision flow.
- If a rescue backtest is timing out or spending most of its time inside agent calls, refine by simplifying the agent path and universe instead of adding more AI-agent roles or a bypass trade.
- For an explicit AI-only request, never simplify by adding Python-owned data,
  selection, sizing, order, or management logic. Keep the class minimal and
  refine only the complete agent prompt or generic built-in tool descriptions.

Core imports
------------

```python
from lumibot.components.agents import BuiltinTools, MCPServer, agent_tool
```

How to create an agent
----------------------

Preserve the user's explicit reasoning setting with `reasoning_effort` on each
`self.agents.create(...)`, alongside `default_model`, using the current model
catalog's supported values. Reasoning belongs in executable configuration;
mentioning it only in prose or Rules does not set it. Do not invent another
parameter or silently omit the setting. A managed gateway settings rejection
requires runtime/configuration diagnosis, not removing a supported user choice.

Create the agent once in ``initialize()``. The system prompt owns the complete
strategy policy, but it must not restate generic stock, options, or order-tool
mechanics already supplied by LumiBot runtime skills. All built-in tools
(positions, portfolio, prices, options, orders, DuckDB) and built-in runtime
skills are included automatically, even when you add custom tools or MCP
servers.

The PRIMARY pattern for adding external data is ``@agent_tool`` when the user names a real provider/API, uploads reference code, or explicitly asks for a custom integration. Do not invent placeholder APIs, generic NewsAPI calls, fake URLs, or new API-key requirements to satisfy broad requests like "give it news" or "give it more tools".

For market news, prefer LumiBot's built-in BYOK Alpaca/Benzinga tool instead of inventing a custom news API:

```python
tools=[BuiltinTools.news.alpaca_news()]
```

The tool uses the active Alpaca broker credentials when the broker connection is Alpaca. When the active broker is not Alpaca, use the news-specific BYOK env vars ``ALPACA_NEWS_API_KEY`` / ``ALPACA_NEWS_API_SECRET``. Do not tell users to set generic Alpaca broker env vars just to unlock news; generic Alpaca broker credentials are intentionally separate so news access does not confuse broker selection for Tradier, IBKR, or other brokers. It retrieves historical or live news by symbol/date window, not keyword search. Teach the agent to scan first with ``include_content=False``. Use ``limit=10`` to ``20`` for focused single-symbol checks and ``limit=30`` to ``50`` for broad market or sector scans. If a story matters, call again for the same or narrower window with ``include_content=True`` and usually ``exclude_contentless=True`` to read the full article. If ``next_page_token`` is returned and the first page is not enough, call again with ``page_token``. Full article content is not truncated unless ``content_max_chars`` is explicitly set. In backtests, the tool clamps future ``end`` timestamps to the simulated datetime and returns ``lookahead_clamped`` so the agent can avoid look-ahead bias.

For broad or sparse news searches, use ETF proxies rather than random tickers: broad market ``SPY,QQQ,DIA,IWM``; tech/AI/semis ``QQQ,XLK,SMH``; financials/banks ``XLF,KRE``; energy/oil ``XLE,USO``; healthcare/biotech ``XLV,XBI``; rates/bonds ``TLT,IEF,SHY``; gold/commodities ``GLD,SLV,DBC``. Do not trade from a single weak article; compare several articles and their timestamps.

For strict minimal AI-agent requests (for example: "only AI", "no watchlist", "no indicators", "minimal on_trading_iteration", "just tell it to make money"), do not add custom tools, REST calls, trace logging, or result-summary logging. Use built-in agent tools only and keep ``on_trading_iteration`` to the agent call.

```python
import os
import requests
from lumibot.components.agents import agent_tool

@agent_tool(
    name="get_economic_indicator",
    description="Fetch a US economic indicator (e.g. REAL_GDP, FEDERAL_FUNDS_RATE, CPI).",
)
def get_economic_indicator(self, indicator: str) -> dict:
    '''Fetch a US economic indicator value.

    Args:
        indicator: The indicator function name (e.g. REAL_GDP, CPI, FEDERAL_FUNDS_RATE).

    Returns:
        A dict with the indicator data from the API.
    '''
    resp = requests.get("https://www.alphavantage.co/query", params={
        "function": indicator, "apikey": os.environ.get("ALPHAVANTAGE_API_KEY")
    }, timeout=15)
    return resp.json()

def initialize(self):
    self.agents.create(
        name="research",
        system_prompt=(
            "Use economic data to decide whether capital should be in "
            "TQQQ or a defensive asset like SHV. This is a binary allocator."
        ),
        tools=[self.get_economic_indicator],
    )
```

How ``@agent_tool`` works
-------------------------

Decorate any strategy method with ``@agent_tool``. The decorator:
- Registers the function as a tool the agent can call
- **Auto-includes the function's source code** in the tool description sent to the model, so the agent understands exactly what the tool does
- Uses the function's type hints and docstring to build the tool schema

Always write Google-style docstrings with an ``Args`` section for every ``@agent_tool`` function. This is critical because the docstring becomes part of the tool description the agent sees.

```python
@agent_tool(
    name="get_watchlist_bias",
    description="Return a structured bias payload for one symbol.",
)
def get_watchlist_bias(self, symbol: str) -> dict:
    '''Look up the current bias for a symbol from the watchlist.

    Args:
        symbol: The ticker symbol to look up (e.g. AAPL, MSFT).

    Returns:
        A dict with symbol and bias keys.
    '''
    return {"symbol": symbol, "bias": "neutral"}
```

Then pass the decorated method in ``tools=[...]``:

```python
self.agents.create(
    name="research",
    system_prompt="...",
    tools=[self.get_watchlist_bias],
)
```

Built-in tools are ALWAYS included automatically, even when you pass a ``tools`` list. Your custom tools are added alongside the built-in ones.

How to run an agent
-------------------

```python
def on_trading_iteration(self):
    result = self.agents["research"].run()
```

``AgentRunResult`` fields
-------------------------

- ``result.summary``: short final summary from the agent
- ``result.text``: concatenated text output
- ``result.cache_hit``: whether the result came from replay cache during backtesting
- ``result.warning_messages``: list of observability warnings
- ``result.tool_calls``: structured tool-call trace events
- ``result.tool_results``: structured tool-result trace events
- ``result.payload``: trace metadata, including ``trace_path`` when available. It is run bookkeeping, never the answer.
- ``result.parsed``: the validated structured answer when ``output_schema`` is set (LumiBot 4.6.5+)
- ``result.parse_error``: why the answer did not match ``output_schema`` (``None`` when it did)

```python
trace_path = (result.payload or {}).get("trace_path")
if trace_path:
    self.log_message(f"Agent trace saved to {trace_path}", color="blue")
```

Structured answers (LumiBot 4.6.5+)
-----------------------------------

Optional, rarely needed. By default agents talk to each other in plain language
and the trading agent places trades itself. Only when Python code must read an
agent's answer (a research-only report the user wants as data, or a hybrid
strategy where the user asked for a deterministic execution layer), give the
agent an ``output_schema`` and read ``result.parsed``. Never
parse ``result.summary`` or ``result.text`` with string searches or regexes, and
never treat ``result.payload`` as the answer. LumiBot tells the model the exact
format, strips markdown code fences, validates the JSON, and returns ``None``
plus ``result.parse_error`` when the answer does not match. Agent-owned trading
still submits orders through the agent's own tools; ``output_schema`` does not
change that rule.

```python
VERDICT = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "VETO"]},
        "confidence": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "reason": {"type": "string"},
    },
    "required": ["symbol", "verdict", "confidence", "reason"],
}

self.agents.create(
    name="analyst",
    default_model="<default model id from CURRENT AI MODELS>",
    system_prompt="Review one stock and give a PASS or VETO verdict.",
    output_schema=VERDICT,
)

result = self.agents["analyst"].run(task_prompt=f"Review {symbol}.")
if result.parsed is None:
    self.log_message(f"{symbol}: no usable verdict ({result.parse_error})", color="red")
else:
    self.vars.verdicts[symbol] = result.parsed
```

A pydantic ``BaseModel`` class also works as ``output_schema``; then
``result.parsed`` is an instance of that model.

Leave ``max_output_tokens`` unset. By default LumiBot sends no output length, so
the model answers as long as it needs (Anthropic models get their real limit
because Anthropic requires one). Set it only when the user explicitly asks to
cap answer length; LumiBot caps any value at the model's real limit.

Rate limits and skipped bars (LumiBot 4.6.5+): a provider rate limit (HTTP 429)
is retried up to 6 times, waiting for the provider's Retry-After. If a backtest
bar still has no AI decision, the backtest says so: the log shows
``BACKTEST INCOMPLETE``, the parameters show ``agent_<name>_skipped_runs``, and
``settings.json`` has ``agent_health`` with ``complete: false``. When explaining
backtest results, check ``agent_health`` before trusting the numbers.

Using MCP servers (optional, advanced)
--------------------------------------

MCP servers connect external data sources (news, economic data, research, etc.) to the agent via a hosted URL. ``@agent_tool`` is the recommended primary pattern, but MCP servers are available when you need a pre-built hosted service.

```python
from lumibot.components.agents import MCPServer

MCPServer(
    name="my-data-source",
    url="https://my-mcp-server.example.com/mcp?api_key=...",
    exposed_tools=["tool_a", "tool_b"],
    timeout_seconds=120,
)
```

Pass MCP servers via ``mcp_servers=[...]`` in ``self.agents.create(...)``. Built-in tools are always included alongside MCP tools.

Key rules
---------

- ``@agent_tool`` is the PRIMARY pattern for adding external data sources only when the user names a real provider/API, uploads reference code, or explicitly asks for a custom integration. Do not invent generic news APIs, placeholder URLs, or new API-key requirements.
- Always write Google-style docstrings with an ``Args`` section for ``@agent_tool`` functions. The source code and docstring are auto-included in the tool description.
- Built-in tools are ALWAYS included automatically, even when you pass custom ``tools`` or ``mcp_servers``.
- System prompts should be concise for simple agents and complete about the
  user's strategy policy for complex AI-only strategies. The runtime skills own
  generic data, execution, duplicate-prevention, and verification mechanics.
- Do not duplicate generic readiness call sequences in a new saved prompt.
  LumiBot's matching runtime skill and built-in tool descriptions require fresh
  evidence, reconcile pending orders, and verify submissions. Keep extra prompt
  instructions only when they express a user-specific policy.
- Create the agent once in ``initialize()``. Do not recreate it every iteration.
- Keep ``on_trading_iteration`` thin. Usually it should only call ``self.agents["name"].run(...)``. Only store/log ``result.summary`` if the user explicitly asks for chat-visible summaries.
- Do not add indicators, watchlists, fallback rules, manual order orchestration, markers, lines, or extra logging around an AI-agent strategy unless the user explicitly asks for them.
- For agent-owned trading, the final trading-enabled agent inspects broker state
  and submits orders itself through LumiBot tools. The strategy must not parse
  the agent summary and then call ``get_cash()``, ``get_last_price()``,
  ``create_order()``, or ``submit_order()``. Use a deterministic Python
  execution layer only when the user explicitly asks for rules-based or hybrid
  execution.
- Explicit BYOK/local AI agents require exactly one model-provider API key:
  the provider's own key for the ``default_model``, and only when the strategy
  runs outside BotSpot (self-hosted LumiBot). BotSpot-managed inference uses
  platform credits for every model in CURRENT AI MODELS and
  must not request any of those personal keys.
