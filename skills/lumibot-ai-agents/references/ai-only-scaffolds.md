> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# AI-Only Strategy Scaffolds

Use this reference when the user asks for an explicit AI-only, agent-only, or
no-deterministic-logic strategy for options or intraday equity patterns.

Python stays minimal: cadence, at least one non-trading research/setup agent,
exactly one terminal trading/risk agent in `initialize()`, and
`on_trading_iteration()` that passes a bounded upstream packet to the terminal
agent. Put the strategy-specific policy in agent prompts and context. LumiBot's
built-in runtime skills supply reusable stock, options, and order mechanics.
Never load
`options-strategies` for these builds. Never import `OptionsHelper`.

Default model for new AI-only agents: the model marked (default) in the CURRENT
AI MODELS table (its exact id) through BotSpot-managed inference (no saved personal provider key),
unless the user picks another model from the CURRENT AI MODELS list. Explicit
BYOK/local execution requires the matching key.

## Preserve the requested trade before choosing a scaffold

Before writing role policies or Rules, identify the user's opening direction
and verify it against the actual leg actions and premium flow. A holding-period
request does not reverse a named structure. Use the requested economics in BOTH
the research policy and terminal trading mandate; a correctly labeled class
cannot compensate for an opposite policy. After readback, compare those saved
mandates and Rules against the request before starting validation.

Preserve both cash flow and leg direction. With put strikes below call strikes,
the opening directions from lowest to highest strike are:

| Requested orientation | Opening legs from lowest to highest strike |
| --- | --- |
| Long / net debit | Sell outer put, buy inner put, buy inner call, sell outer call |
| Short / net credit | Buy outer put, sell inner put, sell inner call, buy outer call |

"Inner" means nearer the center of the package. Long outer wings protecting
short inner options describe the credit structure; labeling it debit does not
reverse its economics. The terminal agent still selects the exact contracts and
constructs the order through the runtime options skill. Use the applicable row
as the saved policy/Rules mandate, never a Python order-building shortcut.
Reference: [Options Institute long iron condor guide](https://www.fidelity.com/learning-center/investment-products/options/options-strategy-guide/long-iron-condor-spread).


## Shared AI-Only Trading Shape

Use the coarsest practical cadence that can observe each requested decision
window. The example uses five minutes, not one-minute model polling. Adapt that
illustrative interval to the actual strategy; preserve explicitly requested
faster behavior and keep all configured agents on the chosen trading cycle.
A finer clock must not silently become repeated one-minute AI calls throughout
a wider entry or exit window.

Run every configured research agent and the sole trading agent on every trading iteration, including exit/management cycles. Pass that iteration's actual research answer to the trader in every branch; do not bypass the researcher for exits. Keep entry, hold and exit policy in their prompts. A daily clock cannot reach both an afternoon entry and a following-morning exit. Select a cadence fine enough for every requested window, and put current clock/session context and the named windows in both agents' prompts so the trader can act only in the correct window. Do not copy a daily cadence into an intraday mandate.

```python
from pathlib import Path

from lumibot.strategies.strategy import Strategy


class AIOnlyStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "5M"  # Illustrative intraday cadence; match the requested windows.
        self.agents.create(
            name="researcher",
            model="<default model id from CURRENT AI MODELS>",
            allow_trading=False,
            system_prompt="""Research the strategy setup and return a bounded evidence packet. Never trade.""",
            rules_path=Path(__file__).with_name("rules.json"),
        )
        self.agents.create(
            name="risk_trader",
            model="<default model id from CURRENT AI MODELS>",
            allow_trading=True,
            system_prompt="""You are the sole trading owner. Apply the strategy policy and
use the matching runtime trading skill before acting. Independently refresh
current account state, positions and open orders; for options verify the exact
contracts, executable package price and liquidity immediately before the action.
Researcher recommendations are advice, not execution authority. Preserve the
requested defined-risk atomic package rather than substituting unhedged legs.
Inspect the actual returned order status and resulting positions before claiming
execution; an accepted request or proposed trade is not a confirmed fill.""",
            rules_path=Path(__file__).with_name("rules.json"),
        )

    def on_trading_iteration(self):
        context = {"current_datetime": self.get_datetime().isoformat()}
        research = self.agents["researcher"].run(
            task_prompt="Research one strategy cycle and return a bounded evidence packet.",
            context=context,
        )
        self.agents["risk_trader"].run(
            task_prompt="Revalidate the evidence, manage risk, and execute or hold.",
            context={**context, "research": research.summary},
        )
```

Parameterization belongs in the prompt or run context, not in Python selection
logic. Prefer named parameters in the system prompt, and when the user supplies
numbers for the current run, pass them again in the run prompt so the agent
sees the active values.

Keep BotSpot's canonical `rules.json` beside `main.py` and pass it through
`rules_path`. LumiBot reloads and injects active rules before every call. Do not
copy the rules ledger or disabled history into the system prompt.

Do not put reusable tool sequences in the saved prompt. The LumiBot agent can
load `stock-trading` or `options-trading` through its runtime `SkillToolset`
after the relevant asset becomes known. This also covers broad mandates where
the builder cannot know in advance whether the agent will choose a stock or an
option.

## Parameterized AI Iron Condor

When the user asks for an AI-only iron condor, keep all four-leg selection and
management inside the agent prompt. Document these parameters in the prompt
even when defaults are used:

- opening cash flow: preserve the requested net debit or net credit structure,
  including which inner and outer legs are long or short; do not substitute the
  other orientation because an example uses it
- underlying symbol (often SPY or QQQ)
- relevant long/short-leg delta target or delta band
- wing width in dollars or the corresponding leg delta band
- target DTE or DTE window
- max contracts / buying-power or margin budget
- debit ceiling for a debit package or credit floor for a credit package
- profit-taking and loss limits in units appropriate to that package, when requested
- management DTE for forced exit or roll decision
- whether rolls are allowed
- one-condor-at-a-time / no duplicate iron-condor exposure


The upstream agent owns research and selection evidence. The terminal risk/trader
owns execution and management. Its saved role contract must require current
account/order/contract/price evidence, the user's atomic defined-risk structure,
and verification of the returned outcome, as in the shared scaffold. Exact tool
sequences, chain mechanics and signed-side implementation remain defined once
in LumiBot's `options-trading` runtime skill; do not reimplement them in Python
or duplicate those full workflows in every prompt. Their prompts must not restate the generic chain
retrieval or order-tool sequence; naming the trader's ownership and current
execution facts does not reimplement that runtime workflow.

Do not simplify an iron-condor request into a single credit spread or a
deterministic OptionsHelper build unless the user explicitly asks for a hybrid
or rules-based design.

## AI-Only Credit Spread

Same AI-only shape. The saved prompt owns only:

- bull put vs bear call direction rule
- short delta / long wing width
- DTE window
- credit floor
- profit-take and stop-loss
- max spreads and no-duplicate-spread policy

Atomic two-leg submission, signed close sides, pending-order reconciliation,
and post-submit verification come from the runtime options skill.

## AI-Only ORB (Opening Range Breakout)

Use a cadence that can observe the requested range without needless model
calls. Hourly decisions may analyze minute bars when the setup permits it.
Python still only creates and runs the agent. The prompt owns:

- symbol universe (keep tiny for first smoke)
- opening-range window (for example first 5 or 15 regular-session minutes)
- breakout confirmation rule (close beyond range, buffer, volume filter)
- session VWAP or other confirmation only if the user asked for it
- stop at opposite side of range or ATR-style stop described in prose
- profit target or time-of-day flatten
- no mid-session re-entry rules when requested
- regular-session only; skip premarket/after-hours unless asked

The agent still owns bar retrieval, opening-range calculation, order placement,
and trade management. Reusable evidence and order-verification mechanics come
from LumiBot's `stock-trading` runtime skill rather than the saved prompt.

## AI-Only VWAP

Choose a practical intraday cadence. The prompt owns:

- symbol universe
- session VWAP definition from regular-session bars
- reclaim / reject / fade rule the user requested
- confirmation bars after reclaim
- stop and target or end-of-day flatten
- one-position or max-position rules
- duplicate-order prevention

Do not add pandas-ta or Python indicator code for an explicit AI-only VWAP
request. The agent reads bars through built-in tools and applies the VWAP rule
in its policy.

## First-Smoke Practicality Without Breaking AI-Only

Allowed simplifications for the first AI-owned test:

- one symbol or a tiny universe
- one compact non-trading upstream researcher plus exactly one trading-enabled terminal risk/trader
- shorter prompt wording that still contains the full decision policy
- daily cadence only when the strategy idea does not require intraday structure

Forbidden simplifications:

- OptionsHelper or other deterministic options selection
- Python-owned ORB/VWAP calculations that then place orders
- fake `is_backtesting` proof trades
- hybrid parse-summary-then-`submit_order` execution layers
