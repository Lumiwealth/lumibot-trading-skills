> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# AI Trading Teams

Use this reference when the user asks for an AI trading team, AI investment
committee, pod-style strategy, named-investor agent team, macro agent, sector
pod, or any strategy where several AI roles debate or specialize before a final
trading decision.

## Core Contract

Every AI-owned trading strategy follows "AI trading team conventions" at the
top of `SKILL.md`. In short: exactly one terminal trading and risk agent
(`allow_trading=True`) with plain-language risk rules in its own prompt; at
least one upstream non-trading researcher (`allow_trading=False`) that returns
a bounded setup packet; agents passing summaries through `context`; no
business-logic Python; built-in tools instead of strategy helpers; the model
marked (default) in CURRENT AI MODELS unless the user picks another model. The trader is the sole order owner and
must revalidate current positions, open orders, prices, and for options the
exact option contracts and package pricing, before it acts. This file only adds
team-specific shapes.

- Build a real LumiBot AI-agent strategy, not a prose proposal.
- Use AI roles for research, disagreement and critique; each role gets a crisp
  prompt and a bounded evidence set.
- The final trading agent must say which upstream advice it accepted or
  rejected and why, so `agent_detail.parquet` is useful later.
- Default AI decisions to daily and normally no more frequently than hourly for
  intraday workflows. Gate agent calls to named decision windows. Before saving
  an explicitly requested cadence below 10 minutes, quantify that a one-minute
  US-session loop is about 390 cycles and at least 780 initial model calls for
  the minimum two-agent topology, warn about credits, latency and provider
  limits, and require explicit confirmation.

Clock scheduling surrounds the whole decision cycle, including for AI-only
requests: run every upstream role and the terminal trader inside each requested
window. A coarse `sleeptime` alone does not implement multiple named windows.
Use native lifecycle scheduling or a clock-only check before the whole team;
never inspect research or market data in Python to decide which role runs.

## Recommended Team Shapes

Reusable shapes, not hard-coded names:

- Research pods: several non-trading agents specialize by asset class, sector,
  regime, valuation, catalyst or risk.
- Debate committee: bull, bear and neutral researchers, then a disagreement
  agent that names conflicts and missing evidence.
- Critic: a non-trading devil's advocate or "risk critic" that challenges
  concentration, drawdown, leverage and liquidity. Its view is advice; risk
  ownership stays with the trader.
- Trader: one final trading-enabled agent (`portfolio_manager`,
  `risk_trader`) that reads the upstream summaries plus live broker state,
  applies its plain-language risk rules, and places the orders itself.

For first builds keep the team small enough to validate: one to three
researchers, an optional critic, one trader, a compact universe, a daily
cadence and short prompts.

## Agent-Owned Order Rule

```python
self.agents.create(
    name="portfolio_manager",
    model="<default model id from CURRENT AI MODELS>",
    allow_trading=True,
    system_prompt=(
        "You are the only agent that trades, and you own risk. Weigh the research "
        "and the critic, then place or skip the orders yourself. Independently refresh current "
        "account state, positions and open orders immediately before acting; revalidate exact "
        "contracts, executable prices, liquidity and risk. Preserve the requested atomic "
        "structure. Inspect the actual returned order status and resulting positions before "
        "claiming execution. Risk rules: hold "
        "at least three of the ETFs when risk is on; never put more than 40% of the "
        "account in one ETF; move to SHV or cash when the research is weak or mixed."
    ),
)
```

Keep order placement agent-owned. Do not parse `result.summary` and submit the same order in Python afterward.
That creates duplicate execution paths and turns the AI team into commentary.

## Secret Requirements

On BotSpot, every model in the CURRENT AI MODELS table runs through BotSpot's
managed AI with BotSpot credits; a BotSpot backtest or bot never needs a
personal model-provider key for it, whatever the provider prefix. The keys a
BotSpot run needs are exactly the ones BotSpot's missing-secrets list names.
Only self-hosted LumiBot outside BotSpot needs the model provider's own key,
even if strategy code does not read it directly. When diagnosing such a run
that uses a Gemini model, name its key `GEMINI_API_KEY`, not a "Google API key".

## Backtest Diagnosis

When an AI-agent backtest fails or returns surprising trades:

- inspect `list_backtests` or `backtest_status` runtime secret metadata first;
- verify which saved env-var set ids and key names were attached;
- inspect hosted runtime logs logs for provider errors and runtime failures;
- inspect `agent_detail` artifacts for role outputs and final trade reasoning;
- do not infer invalid keys from regex-only log scans, and do not disable keys
  automatically.
