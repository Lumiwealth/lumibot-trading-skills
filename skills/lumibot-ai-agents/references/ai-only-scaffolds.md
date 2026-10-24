# AI-Only Strategy Scaffolds

Use this reference when the user asks for an AI-only (agent-only, no
deterministic logic) strategy for options or intraday equity patterns: iron
condor, credit spread, opening range breakout (ORB) or VWAP.

Python stays minimal: the cadence, at least one non-trading research agent,
exactly one trading agent created in `initialize()`, and an
`on_trading_iteration()` that calls every agent in order and passes the
research answer to the trader. Strategy-specific policy goes in agent prompts
and context. LumiBot's built-in runtime skills (`stock-trading`,
`options-trading`) supply the reusable stock, options and order mechanics.

Do not use LumiBot's `OptionsHelper` or any Python contract-selection code in an
AI-only build. The agent uses the built-in options tools
(`options_get_chain`, `options_find_strike_for_delta`, `options_get_greeks`,
`options_calculate_multileg_price`, `orders_submit_multileg` and so on)
directly. If the user wants deterministic options selection, that is a Python
or hybrid strategy; see the `options-strategies` skill.

Models: omit `model` to use LumiBot's current default, or pass the exact model
id the user chose. On BotSpot, AI runs use BotSpot's managed AI and credits, so
no personal model key is needed. Self-hosted LumiBot needs the provider's key.

## Shared AI-only shape

```python
from pathlib import Path

from lumibot.strategies.strategy import Strategy

RULES = Path(__file__).with_name("rules.json")


class AIOnlyStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"  # use "1H" or similar for intraday setups
        self.vars.last_research = None
        self.agents.create(
            name="researcher",
            allow_trading=False,
            system_prompt="Research the strategy setup and return a bounded evidence packet. Never trade.",
            rules_path=RULES,
        )
        self.agents.create(
            name="risk_trader",
            allow_trading=True,
            system_prompt=(
                "You are the only agent that trades, and you own risk. Apply the "
                "strategy policy below, re-check the account and prices, then trade "
                "or hold. <strategy policy and risk rules in plain sentences>"
            ),
            rules_path=RULES,
        )

    def on_trading_iteration(self):
        context = {"current_datetime": self.get_datetime().isoformat()}
        research = self.agents["researcher"].run(
            task_prompt="Research one strategy cycle and return a bounded evidence packet.",
            context={**context, "previous_research": self.vars.last_research},
        )
        self.vars.last_research = research.summary
        self.agents["risk_trader"].run(
            task_prompt="Review the evidence, manage risk, and execute or hold.",
            context={**context, "research": research.summary},
        )
```

Include `rules_path` only when the strategy has a `rules.json` beside
`main.py` (see the rules section in `SKILL.md`). LumiBot reloads and injects the
active rules before every call. Do not copy the rules ledger into the prompt.

Parameters belong in the prompt or the run context, not in Python selection
logic. Name them in the system prompt; when the user supplies numbers for the
current run, also pass them in `context` so the agent sees the active values.

Do not put reusable tool sequences in the saved prompt. The agent loads
`stock-trading` or `options-trading` itself once it knows which asset it is
handling, which also covers broad mandates where the builder cannot know in
advance whether the agent will pick a stock or an option.

## AI iron condor

Keep all four-leg selection and management inside the agents. Document these
parameters in the trader's prompt even when defaults are used:

- underlying symbol (often SPY or QQQ)
- short-leg delta target or delta band for the put and call shorts
- wing width in dollars or long-leg delta band
- target DTE or DTE window
- maximum contracts or buying-power budget
- minimum entry credit (skip if the credit is too small)
- profit-take as a percent of credit
- stop-loss as a multiple of credit or a maximum loss
- management DTE for a forced exit or roll decision
- whether rolls are allowed
- one condor at a time, no duplicate condor exposure

The researcher gathers selection evidence. The trader owns execution and
management. Neither prompt restates the generic chain, exact-contract,
liquidity, atomic-order, signed-position or verification steps; those live in
LumiBot's `options-trading` runtime skill.

Do not simplify an iron condor request into a single credit spread or a
deterministic build unless the user explicitly asks for that.

## AI credit spread

Same shape. The saved prompt owns only:

- bull put versus bear call direction rule
- short-leg delta and long-leg wing width
- DTE window
- minimum credit
- profit-take and stop-loss
- maximum spreads and no duplicate spread

Atomic two-leg submission, signed close sides, pending-order reconciliation
and post-submit verification come from the runtime options skill.

## AI opening range breakout (ORB)

Use a cadence that can observe the range without needless model calls. An
hourly cycle can still read minute bars when the setup allows. Python only
creates and runs the agents. The trader's prompt owns:

- symbol universe (keep it tiny for the first test)
- opening-range window (for example the first 5 or 15 regular-session minutes)
- breakout confirmation (close beyond the range, buffer, volume filter)
- session VWAP or other confirmation only if the user asked for it
- stop at the opposite side of the range, or an ATR-style stop described in
  words
- profit target or time-of-day flatten
- no re-entry rules when requested
- regular session only, unless the user asks for extended hours

The agent retrieves bars, computes the range, places orders and manages the
trade. Reusable evidence and order-verification mechanics come from the
`stock-trading` runtime skill.

## AI VWAP

Choose a practical intraday cadence. The trader's prompt owns:

- symbol universe
- session VWAP defined from regular-session bars
- the reclaim, reject or fade rule the user asked for
- confirmation bars after a reclaim
- stop and target, or end-of-day flatten
- one-position or maximum-position rules
- no duplicate orders

Do not add pandas-ta or Python indicator code in an AI-only VWAP strategy. The
agent reads bars and indicators through built-in tools and applies the rule.

## Keeping the first test practical

Allowed simplifications for a first backtest:

- one symbol or a tiny universe
- one compact research agent plus exactly one trading agent
- shorter prompt wording that still contains the full decision policy
- daily cadence when the idea does not need intraday structure

Not allowed:

- `OptionsHelper` or other deterministic options selection
- Python-computed ORB or VWAP levels that then drive orders
- fake `if self.is_backtesting:` proof trades
- hybrid "parse the summary, then `submit_order`" execution layers
