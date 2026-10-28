> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# LumiBot examples: AI agents

Patterns for LumiBot AI agents: minimal agent, research plus trader team, bull/bear committee, built-in news tool, and a custom `@agent_tool`. Replace `<model id>` with the model the user picked (see `references/components-overview.md`, AI agents section, for model ids and keys). For the full design guide load the `lumibot-ai-agents` skill.

These snippets show methods from inside a `Strategy` subclass (`self` is the strategy). Imports such as `Asset`, `Order`, `TradingFee`, `timedelta` and `pd` are assumed. Examples are illustrations of the API, not trading recommendations.

```python
# Example - Minimal built-in-tools AI agent:
# This example shows the smallest useful pattern for creating and running a LumiBot AI agent
# with only built-in tools. Built-in tools are included by default -- no explicit listing needed.

def initialize(self):
    self.agents.create(
        name="research",
        default_model="<model id>",
        system_prompt="Use LumiBot tools and return a short summary.",
    )

def on_trading_iteration(self):
    self.agents["research"].run(
        context={"symbol": "SPY", "current_datetime": self.get_datetime().isoformat()}
    )


# Example - Strict minimal AI-owned trading team:
# Every AI-owned trading strategy keeps research separate from the sole terminal
# risk/trader. Do not collapse this to one trading-enabled agent.

def initialize(self):
    # Default to daily cadence for backtest speed/cost unless the user explicitly asks for intraday.
    self.sleeptime = "1D"
    self.agents.create(
        name="researcher",
        default_model="<model id>",
        allow_trading=False,
        system_prompt="Research opportunities and return a bounded evidence packet. Never trade.",
    )
    self.agents.create(
        name="risk_trader",
        default_model="<model id>",
        allow_trading=True,
        system_prompt="Revalidate evidence and account risk, then trade or hold.",
    )

def on_trading_iteration(self):
    research = self.agents["researcher"].run()
    self.agents["risk_trader"].run(context={"research": research.summary})


# Example - Simple leveraged ETF AI trading team:
# Use this shape when the user asks for an AI trading team that should actively
# pick among a defined universe. The universe includes bullish and inverse
# leveraged ETFs, so the team can express risk-on or risk-off views without
# short selling. Keep on_trading_iteration thin: agents debate, then the trader
# agent handles orders.

parameters = {
    "universe": ["TQQQ", "SQQQ", "UPRO", "SPXU", "UDOW", "SDOW", "TNA", "TZA", "TECL", "TECS", "SOXL", "SOXS", "WEBL", "WEBS", "FAS", "FAZ", "LABU", "LABD", "ERX", "ERY", "GUSH", "DRIP", "DRN", "DRV", "TMF", "TMV", "NUGT", "DUST"],
}

def initialize(self):
    self.sleeptime = "1D"
    self.agents.create(
        name="researcher",
        default_model="<model id>",
        allow_trading=False,
        system_prompt="Rank the ETFs by upside. Be direct.",
    )
    self.agents.create(
        name="bull",
        default_model="<model id>",
        allow_trading=False,
        system_prompt="Argue for the strongest money-making trade.",
    )
    self.agents.create(
        name="bear",
        default_model="<model id>",
        allow_trading=False,
        system_prompt="Point out the biggest risk, briefly.",
    )
    self.agents.create(
        name="trader",
        default_model="<model id>",
        allow_trading=True,
        system_prompt="Buy one ETF from the universe aggressively. Use nearly all cash.",
    )

def on_trading_iteration(self):
    context = {
        "date": self.get_datetime().date().isoformat(),
        "universe": self.parameters["universe"],
    }
    research = self.agents["researcher"].run(
        task_prompt="Pick the strongest ETF.",
        context=context,
    )
    bull = self.agents["bull"].run(
        task_prompt="Make the bull case.",
        context={**context, "research": research.summary},
    )
    bear = self.agents["bear"].run(
        task_prompt="Make the bear case.",
        context={**context, "research": research.summary, "bull": bull.summary},
    )
    self.agents["trader"].run(
        task_prompt="Sell anything that is not the pick, then buy the best ETF with nearly all available cash.",
        context={**context, "research": research.summary, "bull": bull.summary, "bear": bear.summary},
    )


# Example - Multi-agent investment committee:
# Use this shape when the user asks for a committee, debate, bull/bear agents,
# or multiple agents working together. The research agents can inspect account
# state and data, but only the portfolio manager can mutate orders.

def initialize(self):
    self.sleeptime = "1D"
    self.agents.create(
        name="evidence_researcher",
        default_model="<model id>",
        allow_trading=False,
        system_prompt=(
            "Gather market data, indicators, news, SEC fundamentals, SEC filings, "
            "and FRED macro context. Return a compact evidence pack with sources, "
            "top candidates, risks, and missing data."
        ),
    )
    self.agents.create(
        name="bull_case",
        default_model="<model id>",
        allow_trading=False,
        system_prompt=(
            "Build the strongest long-only case from the evidence pack. "
            "Focus on upside, catalysts, fundamentals, technical setup, and invalidation points."
        ),
    )
    self.agents.create(
        name="bear_case",
        default_model="<model id>",
        allow_trading=False,
        system_prompt=(
            "Attack the long case. Find red flags, downside risks, filing concerns, "
            "valuation risk, weak technicals, and reasons to avoid or reduce size."
        ),
    )
    self.agents.create(
        name="portfolio_manager",
        default_model="<model id>",
        allow_trading=True,
        system_prompt=(
            "Review the evidence, bull case, and bear case. Check cash, positions, "
            "open orders, prices, and risk limits. Place orders only when justified."
        ),
    )

def on_trading_iteration(self):
    context = {"current_datetime": self.get_datetime().isoformat()}
    evidence = self.agents["evidence_researcher"].run(context=context)
    bull = self.agents["bull_case"].run(context={**context, "evidence": evidence.summary})
    bear = self.agents["bear_case"].run(context={**context, "evidence": evidence.summary, "bull_case": bull.summary})
    self.agents["portfolio_manager"].run(
        context={
            **context,
            "evidence": evidence.summary,
            "bull_case": bull.summary,
            "bear_case": bear.summary,
        }
    )


# Example - AI agent with built-in Alpaca/Benzinga news:
# Use this when the user asks for news access and they can provide Alpaca credentials.
# This avoids fake NewsAPI wrappers. The tool searches by symbols and date windows,
# not keywords. The agent should scan headlines/summaries first, then fetch full
# article content only when it needs to read deeper.

from lumibot.components.agents import BuiltinTools

def initialize(self):
    # Built-in tools (positions, portfolio, last_price, load_history_table,
    # duckdb.query, docs.search, orders) are ALWAYS included automatically.
    # The Alpaca news tool is added alongside them.
    self.agents.create(
        name="news_research",
        default_model="<model id>",
        system_prompt=(
            "Use Alpaca news and market tools to make trading decisions. "
            "For news, first scan with include_content=False and limit 30 for broad market context. "
            "If an article matters, call alpaca_news again with include_content=True and exclude_contentless=True. "
            "If next_page_token is returned and the first page is not enough, call again with page_token. "
            "Use article timestamps and avoid look-ahead bias."
        ),
        tools=[BuiltinTools.news.alpaca_news()],
    )

def on_trading_iteration(self):
    result = self.agents["news_research"].run(
        context={
            "current_datetime": self.get_datetime().isoformat(),
            "news_search_guidance": (
                "Use SPY,QQQ,DIA,IWM for broad market news, or sector ETFs "
                "such as XLK,SMH, XLF,KRE, XLE,USO, XLV,XBI when single-stock news is sparse."
            ),
        }
    )
    trace_path = (result.payload or {}).get("trace_path")
    if trace_path:
        self.log_message(f"Trace: {trace_path}", color="blue")


# Example - AI agent with @agent_tool wrapping a REST API:
# @agent_tool wraps any REST API as an agent tool. This is the most reliable approach
# for explicit custom data sources. Do not invent generic APIs for strict minimal
# AI-agent requests. Always include Google-style docstrings with Args sections.
# The source code is auto-included in the tool description sent to the agent.

import os
import requests

from lumibot.components.agents import agent_tool

@agent_tool(
    name="get_economic_indicator",
    description="Fetch a US economic indicator (e.g. REAL_GDP, CPI, FEDERAL_FUNDS_RATE).",
)
def get_economic_indicator(self, indicator: str) -> dict:
    '''Fetch a US economic indicator value from a data provider.

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
        name="liquidity_research",
        default_model="<model id>",
        system_prompt=(
            "Use money supply and liquidity data to decide between "
            "TQQQ and SHV. Focus on whether M2 liquidity is expanding."
        ),
        tools=[self.get_economic_indicator],
    )

def on_trading_iteration(self):
    self.agents["liquidity_research"].run()
```
