# AI Trading Teams

Use this reference when the user asks for an AI trading team, AI investment
committee, pod-style strategy, investor-style agent team, macro regime agent,
sector pods, or any strategy where several AI roles specialize or debate before
one trading decision.

## Core contract

Every AI-owned trading strategy follows "The core rules" in this skill's
`SKILL.md`. In short:

- exactly one trading agent (`allow_trading=True`) that places the orders and
  owns risk, with plain-language risk rules in its own prompt
- at least one research agent, each with `allow_trading=False` set explicitly
  (LumiBot defaults it to `True`)
- agents hand work to each other only through their answers, passed in
  `context`; `self.vars` may carry an answer forward to the next iteration
- every agent is called every iteration, in order
- no Python that fetches or parses data, filters, scores, sizes or places orders
- built-in tools instead of strategy helpers

Team-specific guidance:

- Build a real LumiBot strategy, not a prose proposal.
- Give each role a crisp prompt and a bounded job.
- The trading agent says which upstream advice it accepted or rejected and why,
  so the per-agent backtest output is useful later.
- Default to daily decisions; intraday teams normally no more often than
  hourly. A one-minute US-session loop is about 390 cycles and, for even two
  agents, at least 780 model calls per day. Explain the credit, latency and
  rate-limit cost and get explicit confirmation before saving a cadence that
  fast.

## Team shapes

Reusable shapes, not fixed names:

- **Research pods:** several non-trading agents, each covering an asset class,
  sector, regime, valuation view, catalyst or risk.
- **Debate committee:** bull, bear and neutral researchers, then a
  disagreement agent that names conflicts and missing evidence.
- **Critic:** a non-trading devil's advocate that challenges concentration,
  drawdown, leverage and liquidity. Its view is advice; the trader still owns
  risk.
- **Trader:** one final trading agent (`portfolio_manager`, `risk_trader`,
  `trader`) that reads the upstream summaries plus live account state, applies
  its risk rules and places the orders itself.

For a first build keep the team small enough to validate quickly: one to three
researchers, an optional critic, one trader, a compact universe, daily cadence
and short prompts.

## Example: debate committee

```python
from lumibot.strategies.strategy import Strategy

UNIVERSE = "SPY, QQQ, IWM, TLT, GLD, SHV"


class AIDebateCommitteeStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
        self.vars.last_decision = None

        self.agents.create(
            name="bull_researcher",
            allow_trading=False,
            system_prompt=(
                f"Build the strongest evidence-based case for owning ETFs in: {UNIVERSE}. "
                "Use prices, indicators, news and macro data. Return candidates, the "
                "prices you observed, and the evidence. Never trade."
            ),
        )
        self.agents.create(
            name="bear_researcher",
            allow_trading=False,
            system_prompt=(
                f"Build the strongest evidence-based case for caution in: {UNIVERSE}. "
                "Name the risks, weak signals and missing evidence. Never trade."
            ),
        )
        self.agents.create(
            name="critic",
            allow_trading=False,
            system_prompt=(
                "Compare the bull and bear cases. Name where they conflict, what "
                "evidence is missing, and any concentration or drawdown concern. "
                "Never trade."
            ),
        )
        self.agents.create(
            name="portfolio_manager",
            allow_trading=True,
            system_prompt=(
                "You are the only agent that trades, and you own risk. Weigh the "
                "research and the critic, then place or skip the orders yourself. "
                f"Only trade {UNIVERSE}. Hold at least three of the ETFs when risk "
                "is on. Never put more than 40% of the account in one ETF. Move to "
                "SHV or cash when the research is weak or mixed. Say which advice "
                "you accepted or rejected and why."
            ),
        )

    def on_trading_iteration(self):
        context = {
            "current_datetime": self.get_datetime().isoformat(),
            "previous_decision": self.vars.last_decision,
        }
        bull = self.agents["bull_researcher"].run(
            task_prompt="Make today's bull case.", context=context
        )
        bear = self.agents["bear_researcher"].run(
            task_prompt="Make today's bear case.", context=context
        )
        critique = self.agents["critic"].run(
            task_prompt="Compare the two cases.",
            context={**context, "bull": bull.summary, "bear": bear.summary},
        )
        decision = self.agents["portfolio_manager"].run(
            task_prompt="Review the debate and the account, then rebalance or hold.",
            context={
                **context,
                "bull": bull.summary,
                "bear": bear.summary,
                "critique": critique.summary,
            },
        )
        self.vars.last_decision = decision.summary
```

Keep order placement agent-owned. Do not parse `result.summary` and submit the
same order in Python afterward. That creates two execution paths and turns the
AI team into commentary.

## Keys and secrets

On BotSpot, AI strategies use BotSpot's managed AI in backtests and live bots,
billed in BotSpot credits; no personal model provider key is needed. The keys a
BotSpot run needs are exactly the ones its missing-secrets result names.
Self-hosted LumiBot outside BotSpot needs the model provider's own key. For a
Gemini model that key is named `GEMINI_API_KEY`. Never print raw key values.

## Diagnosing a team backtest

When an AI-team backtest fails or makes surprising trades:

- use `list_backtests` to find the run and `backtest_status` for its state and
  attached saved-variable metadata (names only, never values);
- read `get_backtest_logs` for provider errors, rate limits and runtime
  failures;
- read the per-agent artifact (for example `agent_detail.parquet`) with
  `get_backtest_artifact` to see each role's output and the trader's reasoning;
- check `agent_health` in the run settings before trusting the numbers;
- do not conclude a key is invalid from a loose log text match, and never
  disable or delete a user's saved keys on your own.
