---
name: lumibot-ai-agents
title: AI-Powered LumiBot Strategies (LLM Agents That Research and Trade)
description: Load when someone wants an AI-powered trading strategy, an AI trading bot, an LLM agent that trades, an AI trading team or investment committee, or any LumiBot strategy built with self.agents (research agents plus one trading agent). Covers the agent API, the one-trader team pattern, prompts, tools, rules.json, cadence and cost, backtesting AI strategies, and the BotSpot build and validation workflow.
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

--------------------------------------------------------------
AI AGENTS COMPONENT
--------------------------------------------------------------

## Explicit Python order ownership

When the user explicitly chooses Python signals/orders and non-trading AI,
implement that choice. In the first visible progress acknowledgment, explain this tradeoff once:
 BotSpot usually lets one trading agent place orders because hand-written
order code can miss a rebalance or an instrument-identity edge case; this build
keeps orders in Python as requested. Every AI role has allow_trading=False.
Complete BUY targets against confirmed existing positions as below, rather than
skipping every held symbol. An already-held skip is not duplicate-order control;
reconcile actual pending orders separately.
At the saved-code readback, follow one qualifying held underweight through the
actual sizing and submission path. A positions-membership continue still skips
the required top-up even when a separate helper computes target weights.
For multi-leg mandates, compare the researcher prompt, trader prompt and saved
active Rules: each must preserve the requested atomic entry and atomic exit.

## Python-owned equal-weight BUY targets

For a user-selected Python BUY-target design, evaluate the user's signal and AI
PASS/VETO policy first. Include EVERY qualifying symbol in the target set,
including held underweights. Use confirmed account value, positions and spendable
cash; an unfilled sell is not available cash. This pure sizing step creates no
signal, order or additional sell rule. Apply the common factor before any
required broker quantity rounding, then reconcile reservations before submission.

```python
import math

def equal_weight_buy_quantities(prices, held_quantities, eligible, account_value, available_cash):
    eligible = list(dict.fromkeys(eligible))
    if not eligible:
        return {}
    if not math.isfinite(account_value) or account_value < 0 or not math.isfinite(available_cash):
        raise ValueError('Use verified finite account values')
    if any(not math.isfinite(prices[symbol]) or prices[symbol] <= 0 for symbol in eligible):
        raise ValueError('Each eligible asset needs its actual positive price')
    target_value = account_value / len(eligible)
    deficits = {symbol: max(0.0, target_value / prices[symbol]
                           - held_quantities.get(symbol, 0.0))
                for symbol in eligible}
    required_cash = sum(deficits[symbol] * prices[symbol] for symbol in eligible)
    common_factor = min(1.0, max(0.0, available_cash) / required_cash) if required_cash else 0.0
    return {symbol: deficit * common_factor for symbol, deficit in deficits.items()}
```

An overweight gets a zero BUY deficit, not an unauthorized sell. Retain the
user's VETO exit and other actual sell rules independently. AI-owned designs
leave this decision with their sole trader rather than adding Python orders.

## Preserve the complete policy across roles

For a requested atomic multi-leg entry and exit, the shared effective policy
must explicitly say both "enter the complete package atomically" and "close
the complete package atomically", with the actual entry/exit windows. Pass
that same policy prefix to the non-trading researcher AND sole trader; an
atomic exit clause alone omits the entry obligation. Copy all package constraints
to the active Rules as well. Do not replace this with two partial paraphrases.
When the user leaves the model unspecified or chooses the default, copy the
CURRENT AI MODELS row explicitly marked (default),
not the highest bot-recommendation rank or an older code example's model.


For a dated multi-leg policy, put this evidence requirement directly into the
shared policy prefix actually passed to BOTH roles: "Require dated bid and ask
observations for every individual leg as of the instructed decision date.
Reject later/current quotes for a historical decision; missing dated evidence
means no entry, never a later retry." Adapt the actual dates and instruments.
A generic actionable package quote or "date-appropriate" summary omits the
per-leg observation requirement. Verify the saved effective prompt strings,
including their shared prefix, after the file readback.


For a multi-agent package with exact user constraints, put the complete policy
in one shared text variable and prefix BOTH research and sole execution/risk
agent prompts with it. Include the actual leg directions, quantities, expiry,
entry AND exit dates/windows, atomic package entry and complete-package close,
per-leg dated bid/ask evidence, and missed-entry/no-later-retry rule when requested.
Do not leave atomicity only in the exit clause or require quotes only for the
package total. Each role must retain each leg's available observation date/time;
never substitute future/current quotes for a historical decision or invent
precision. Report missing evidence. Add each role's own responsibility and a
finite research packet bound. Keep the ordinary rules_path binding; this shared
policy is not a duplicate Rules ledger. At readback, compare both actual saved
prompts and Rules against every requested constraint.

For an equal-weight BUY target, qualifying stocks already held still belong in
the eligible set. Calculate target quantity minus confirmed held quantity and
buy its positive deficit; an unconditional already-held skip loses legitimate
underweight purchases. Apply one common confirmed-cash scaling factor to all
proposed buys. A BUY-target policy does not authorize selling overweights;
perform reductions only if the user asked for rebalancing or a stated veto exit.
This allocation math belongs in Python only when the user explicitly selected
Python-owned orders; AI-owned designs leave decisions with the sole trader.

## AI-owned new automation

Define the handoff in the saved upstream agent prompt before creating the team:
name its packet fields and an explicit candidate/evidence-size bound chosen for
this strategy. Include thesis, exact candidates, observed prices, risks, invalidation
and missing evidence. A request to "research findings" or passing `result.summary`
does not by itself define that bounded packet. Python passes the answer unchanged;
the terminal trading/risk agent evaluates it and rechecks execution evidence.

After saving an AI-team build, identify the upstream research role and the sole
execution/risk owner separately in the final reply. For example: "The research
agent gathers setup evidence; the trading/risk agent alone decides and places
orders." Saying only that "AI agents handle research and trading" does not
explain the separate ownership. Then report the observed backtest state: saved
code or a queued backtest does not prove a trade or completed validation.

## Saved-file review before validation

After the final edit, compare the actual saved `main.py` and `rules.json` before
starting validation. Repair a mismatch in the file that contains it, then read
that file back. Do not treat the intended design as proof of the saved design.

- Read each saved file literally; a correct trader prompt does not correct
  contradictory Rules. For an options package, write out the ordered strikes,
  the buy/sell action of each leg, and the opening debit or credit; compare that
  same structure across the active Rules and trader policy. For example, a
  long/debit iron condor sells the outer put, buys the inner put, buys the inner
  call and sells the outer call. Long outer wings with short inner legs describe
  the inverse credit package, even when its label says "long".
- Check the actual call sites, not only sleeptime or role prose. When the request
  names decision windows, trace one iteration outside those windows: neither
  researcher nor trader should run there. Put the clock schedule around the
  whole team; asking an hourly trader to hold until the close still buys hourly
  research and trading calls. Keep market decisions and orders inside the AI.
- Keep research ownership and execution/risk ownership separate in the handoff.
  Name what the upstream researcher supplies and what only the terminal trader
  decides and executes. Report the actual returned validation state separately.

Default ordinary new automation to AI-owned decisions when it has hourly or
slower intelligent decisions and no fast-reaction requirement, using the working LumiBot
`self.agents` engine. Python supplies lifecycle, cadence and invocation, not a
competing signal or order owner. Bind canonical sibling `rules.json` through
`rules_path`; an `aiEnabled` label alone does not implement the policy. Exact
signals, quantities and budgets are valid AI instructions. Exact rules alone
do not require Python, but frequent intelligent decisions or fast reaction do
justify recommending Python or a hybrid. Do not force existing Python
strategies to migrate; explicit Python and chosen hybrid designs remain
supported. Do not claim a separate no-Python engine exists.
For an availability question, explicitly explain that exact requested rules
can be carried as active Rules into this AI runtime. That preserves the
instructions; it does not guarantee deterministic decisions or profitable trades.

Use BotSpot-managed inference and BotSpot credits by default. Provider key
requirements below apply only to explicitly chosen BYOK/local execution, not
managed BotSpot execution. Do not add any model-provider API key as a
user prerequisite for managed inference. Preserve explicit BYOK choices.

## AI trading team conventions

Every AI-owned trading strategy follows these conventions, whether it has two
agents or ten. The running reference examples are LumiBot's
`ai_trading_team_ray_dalio_idea_meritocracy.py` and
`ai_trading_team_citadel_sector_pods.py` (see
`references/ai-trading-team-examples.md`).

1. **Exactly one terminal trading and risk agent.** One agent has
   `allow_trading=True`. It places the trades AND owns risk management. Name it
   by that job, for example `risk_trader` or `portfolio_manager`. It is the
   sole order owner; immediately before acting it must revalidate current
   positions, account state, open orders, executable prices, liquidity and risk,
   and for options the exact option contracts and package pricing
   (LumiBot's runtime trading skills supply those
   mechanics). Why: one agent that researches, trades and manages risk at once,
   especially on a cheaper model, makes far more trading mistakes.
2. **At least one upstream non-trading researcher, and any number of them.**
   Every other agent has `allow_trading=False`: researchers, specialist pods, bull and bear
   debaters, a devil's advocate. A non-trading critic may comment on risk, but
   that is advice; the trading agent still owns risk.
   A one-agent AI-owned trading strategy is invalid, even when the strategy is
   simple, trades one asset, or the user did not say "team".
3. **The agents talk to each other; Python only passes the messages.** Python
   sets `self.sleeptime`, creates the agents in `initialize()`, and in
   `on_trading_iteration()` runs them in order, passing earlier agents'
   `result.summary` to later agents through `context`. Python does not fetch or
   parse data, compute indicators or signals, pick symbols, size positions,
   parse agent text into trades, or create and submit orders. A research agent
   returns a bounded setup packet: thesis, exact candidates, observed prices,
   risks, what would change its mind, and missing evidence. The one allowed
   exception is a cheap Python watcher for setups that need fast reaction
   (for example an iron condor stop): it only checks a condition on a short
   `sleeptime` and wakes the trading agent when the condition appears; it never
   sizes or places orders itself (see AI decision cadence and usage).
4. **The trading agent places the trades, not Python.** Code misses edge cases: a rebalance
   that sells the wrong amount, or a symbol with a dot such as `BRK.B` breaking
   the code. A trading agent reasons around them. LumiBot's runtime trading
   skills supply the detailed position, open-order, price and returned-order
   workflow. Keep the short role obligation in the saved trader prompt, as in
   the minimal example below; do not copy the full tool workflow into prompts
   or Python.
5. **The trading agent's own `system_prompt` states its risk rules in plain
   sentences.** At least two concrete rules, written as sentences, not Python
   and not "apply the active Rules": how much of the account may go into one
   position, when to hold cash, when to trim or cut a loser, how many holdings
   the strategy normally keeps, plus any strategy rule (an All Weather trader
   keeps money spread across stocks, long bonds, medium bonds, gold and
   commodities). This is the trader's job description, so write it even when
   `rules.json` also carries the user's rules. When the user said
   "safe" or gave no limits, choose sensible limits and say so in the reply.
   When the user rejected caps ("unrestricted"), follow that mandate
   instead (see Explicit Design Mandate Compliance).
6. **Diversification is guidance, never a hard rule.** Many customers want a
   single-asset bot, such as a Bitcoin bot that is either in BTC or in cash.
   That is fine: do not add other assets, require several holdings, or
   lecture. A single-asset trader's prompt must still state, as sentences, how
   much of the account may go into that asset (for example "never put more
   than 50% of the account in BTC") and when to cut or exit a losing position
   (for example "sell BTC when it falls 15% below your entry or the reason you
   bought no longer holds").
7. **Every capability is a tool, not strategy code.** LumiBot's built-in tools
   are on by default: account, market prices and history, indicators, orders,
   options, Alpaca news, SEC, FRED and memory. The network tools (`web_search`,
   `http_request`, `read_document`, `rss_fetch`, `browser_*`) go only to the
   research agent that needs them, through `allow_network=True`, never to the
   trader. A missing news, FRED or other data key never blocks a build: build
   with the built-in tools, and say once which saved key would add that data.
   Write an `@agent_tool` only when the user names a real provider LumiBot
   does not cover; if a capability is missing, say LumiBot needs a new built-in
   tool instead of hand-writing Python helpers.
8. **Model.** Write and recommend the model marked (default) in the CURRENT AI
   MODELS table on every agent (it is chosen to be cheap and fast for agents
   inside bots) unless the user picks another model. Any current model is
   allowed.
9. **When the user wants code to place the trades, follow the user.**
   Build exactly that, without asking permission first: every agent
   `allow_trading=False`, Python owns the signals and orders by the user's
   rules. When the final reply describes the saved design, it must include one
   plain design-tradeoff sentence: BotSpot's usual design lets one trading
   agent place the orders because order code tends to miss edge cases (name
   one: a rebalance that goes wrong, or a symbol like `BRK.B` breaking the
   code), and this build keeps
   orders in Python because the user chose that. It is part of the design
   description, not an optional offer. Do not refuse, nag or repeat it.
10. **A plain "I want an AI that trades for me" is a build request.** Beginners
    often name no assets or limits. Do not quiz them: build a small team on a
    liquid, diversified ETF universe such as SPY, QQQ, IWM, TLT and GLD with
    beginner-safe risk rules in the trader's prompt, explain in plain words what
    it will do, start the validation backtest, and invite changes.

If the user explicitly requests a single agent, explain that an AI-owned
trading strategy keeps the separate terminal risk/trader boundary and offer a
deterministic or hybrid design if one model call is mandatory.
Latency-sensitive or high-frequency requirements should use a deterministic or
hybrid design rather than collapsing research and execution into one
trading-enabled agent. If the user says the AI workflow is too slow, first
reduce upstream agents, evidence size, and cadence while preserving one
upstream agent plus exactly one terminal trader.

Before validation, read back the saved role policies and active Rules together.
The terminal trader's own policy must assign its current account, positions,
open-order, exact-contract, executable-price, liquidity and risk checks;
researcher instructions alone do not assign that responsibility.
Every risk limit referenced by a saved prompt must actually exist in the active
Rules. If the user omitted a value, choose and disclose a reasonable default
rather than referring to an undefined ceiling or asking for arbitrary numbers.

## AI decision cadence and usage

Default new AI-owned strategies to daily AI decisions. When the strategy needs
intraday decisions, use the coarsest cadence that can observe the requested
setup and normally call the AI team no more frequently than once per hour.
Treat one hour as a soft recommendation, never a hard block, entitlement rule,
or validation failure. `30M`, `10M`, or faster AI can be appropriate when a
real intraday requirement needs it and the user accepts the tradeoff, but it is
a deliberate cost/latency choice rather than a silent default.
Named entry, exit, and management times are decision windows: gate the AI calls
to those windows instead of invoking every agent throughout the session. The
strategy must not call the model on every Python iteration.

Pure clock scheduling around the whole AI decision cycle is valid for AI-only
requests. It does not choose setups, interpret research, size positions or
submit orders. Every scheduled decision cycle still runs all upstream roles
and the terminal trader. A polling interval or a daily sleep alone does not
implement multiple named windows. Use the framework's scheduling/lifecycle
callbacks or a clock-and-last-window check before the whole team. Never put a
Python gate between the researcher and trader based on research content or
market/account data. The minimal daily example below illustrates one daily
cycle; adapt its scheduling when the user requests several distinct windows.

A hard date is not a retry window. When the user says an entry may occur on one
exact date or says "only" that date, put the same boundary in `rules.json` and
the terminal trader's saved prompt. If required quotes, data, or order readiness
are absent on that date, the trader must hold rather than trade on a later date.
It may inspect later dates for reporting or exit management only when the saved
rules permit that. A broader fallback window is a strategy change that requires
the user's approval; a first-cycle filled-trade target never supplies that
approval.

Never silently build a one-minute AI decision loop. A regular US session has
about 390 minutes, so one upstream researcher plus one terminal trader produces
at least 780 initial model calls per day at `1M`, before retries and tool-loop
continuations. For intelligent decisions more often than hourly, recommend
Python or hybrid and explain the resulting credit, latency, and provider-limit
risk before saving code. This warning is advisory. Proceed with frequent AI
after the user explicitly confirms it once; an earlier explicit statement accepting
the cost and frequency counts, and the Agent must not keep demanding confirmation,
block the build, or silently substitute Python.

A strategy may use a faster deterministic Python cadence for broker/order-state
reconciliation or a narrow time-window trigger without making the intelligent
decision cadence equally fast. This is the normal hybrid design: track the last
completed AI decision and invoke the team only in the intended decision
windows. Classify the design from the intelligent-decision and reaction-time
requirements, not `sleeptime` alone. If sub-minute or continuous signal
reaction is essential, recommend deterministic Python or hybrid while
retaining the terminal risk/trader boundary for any AI-owned orders. Do not
silently change an existing strategy's cadence or architecture; explain the
tradeoff and preserve the user's choice.


## Explicit Design Mandate Compliance

Encode unrestricted or broad mandates exactly when the user states them (for example
"fully unrestricted trader", "no artificial risk caps", "no forced stop-losses", or
"do not add safer constraints I did not ask for"). Put that mandate into the saved
agent `system_prompt` and `rules.json`. Do not argue, debate, lecture, or override
those constraints with safer/more conservative defaults. Preserve mandatory minima,
maxima, eligible assets, agent roles, cadence and model/reasoning in both Rules and
executable agent prompts. "At least N funded holdings after construction" remains
that minimum; do not turn it into "prefer N", "when evidence permits", or "if the
account is large enough". Genuine lack of buying power, available instruments or
authorized orders must be reported as an unmet requirement, never hidden by
weakening the mandate or manufacturing filler trades. Reasonable discretionary
selection happens within the requested constraints.

First-cycle practicality may shorten the test window and prompts. It cannot shrink
an explicitly open universe, reduce the requested agents, or relax a portfolio
requirement. Before saving, compare each mandatory user requirement with its
actual instructions and configuration; preserve it without unrequested exceptions.
Do not invent risk caps, forced stops or asset bans the user rejected.

## Critical New-Build Contract

When the current user asks to build/create/make a new AI trading team,
investment committee, sector pod, named-investor team, or Citadel-style AI
strategy, do not jump straight from this skill to `create_strategy`. First load
`lumibot-strategy-building` when visible, then create the visible first-build plan
with `create_plan`. The valid first-build shape is:

`skills get("lumibot-strategy-building")` -> `create_plan` -> first-build research
when required -> `create_strategy` -> verify its workspace attachment ->
targeted `get_file` -> `replace_file` with a complete real AI-team `main.py` ->
`get_file` readback of the edited revision -> complete the implementation row
with `update_plan_item` -> start the existing launch row with `update_plan_item`
-> `start_backtest` -> `record_external_wait_in_plan` completes the launch row
and waits the existing result-review row. Each plan transition waits for the
previous tool result; do not launch while implementation is still in progress.

When `create_strategy.conversationUpdate` attaches the returned workspace,
use conversation-scoped file calls: `get_file(path="main.py")`, then its fresh
`editHandle` for the save and `get_file(path="main.py")` for readback. Omit the
redundant strategy/revision UUIDs on supported file tools; the server resolves
the owned active revision after each write. Verify that the readback matches
the returned write revision. If attachment failed or the request targets a
historical/different workspace, use the complete exact returned IDs instead.
Never construct a revision ID by combining a remembered prefix with a new suffix.

Exception: when the request context already attaches a strategy with
`workflowContext.firstCycle=true` or `workspaceStatus="neutral_starter"`,
BotSpot already created the workspace for this build. Skip `create_strategy`;
use the attached ids for `get_file` -> `replace_file` -> `get_file` readback ->
`start_backtest`.

For `record_external_wait_in_plan`, omit unused optional `currentItemTarget`
and `waitingItemTarget` fields. These accept complete target objects, not null.
Copy each supplied target discriminator and identity from the actual plan.

When `record_external_wait_in_plan` succeeds and its result says the current
start row is completed and the validation row is waiting, that helper already
performed both plan mutations. Do not call `get_active_plan`,
`update_plan_item`, or `replace_plan_items` to repeat them. Immediately call
`backtest_status` with the exact returned backtest UUID.

If first-build web research is partial or unavailable, record that outcome on
the existing research plan item and continue to the existing workspace item.
Never call `add_plan_item`, `replace_plan_items`, or `remove_plan_item` to add,
reorder, or split out a completed research fallback/limitation row. The
original plan already contains the complete build sequence.

`remove_plan_item` is never part of a new AI-team build. If an earlier mistake
created a redundant row, leave it visible and reconcile the plan with the
permitted update tools; do not call an unavailable removal scope. Likewise,
never probe `rules.json` blindly with `get_file`. Use `list_files` first; its
returned path inventory is the authority for whether `rules.json` exists.

Plan progress is strictly sequential. Never start a later row while an earlier
row is still `in_progress`, and never emit two independent plan mutations in
one assistant action. Complete the current row with one `update_plan_item`,
wait for its returned plan, then start the next existing row with another
`update_plan_item`. Plan patches do not need a strategy `revisionId`; omit it
instead of manually copying an opaque code revision into plan metadata.
Target each existing row by the one-based position returned by `create_plan`
or the latest successful plan result. Copy that returned position exactly;
this avoids retyping and corrupting an opaque UUID. Skipped rows still occupy
their returned position, so do not infer a later target by counting completed
domain actions. Use an exact returned item id only when the relevant result
omitted the position.

Treat strategy, revision, backtest, AI-strategy, plan, order, and deployment
identifiers as copy-only values. Copy each complete value from one successful
tool result into the next call; never reconstruct it from memory or another
identifier. Do not issue multiple identifier-bearing file or revision calls in
the same assistant action. Make one call, verify its result, then make the next
call so every repeated identifier can be copied literally.

Every completed-row entry in `update_plan_items.updates[]` must use this exact
shape: `{"target": {...}, "patch": {"status": "completed", "outcome":
{"status": "satisfied|partial|unsuccessful", "summary": "...",
"evidence": {...}}}}`. Never place `evidence` directly inside `patch`, and
never omit `outcome` when setting `status` to `completed`. Re-read the complete
serialized batch for that invariant before sending it.

For a new AI trading-team build, use `update_plan_item` for ordinary progress
transitions. Emit at most one plan mutation in a model response and wait for
its returned plan before choosing the next transition. Use
`update_plan_items` only to repair an already inconsistent plan when one atomic
replacement is required. Do not add, remove, reorder, or replace plan rows
merely because a research tool returned limited evidence; record that
limitation as evidence on the existing research row.

For a new AI trading-team build, do not use `patch_file` as the first real
`main.py` implementation after reading the neutral starter. The starter can
contain placeholder imports/classes/harness code, and patching into it can leave
duplicate runner blocks or stale `BotSpotStrategy` code. Use `replace_file` for
the first full AI-team implementation. Reserve `patch_file` for later targeted
edits to an already-real saved strategy.

For the remainder of that same new-build turn, keep every `main.py` correction
on the complete-file path: after `create_strategy`, do not call `patch_file`
anywhere later in that same build turn. If a sibling Rules write advances the
revision or a readback exposes an omission, read the newest `main.py` and use
one complete `replace_file` with its current edit handle.

After that first replacement, wait for its result and read the complete saved
file before deciding whether another edit is necessary. Never issue a repair
patch from the starter's old edit handle or in parallel with the replacement.
If the readback needs a broad correction, use one complete `replace_file` with
the fresh readback handle rather than a speculative multi-operation patch.

If the user explicitly asks to build an AI trading team but does not name a
universe, do not stop for a universe clarification. Use a small, liquid,
diversified ETF universe such as SPY, QQQ, IWM, TLT, and GLD as the first
practical default, state that choice in the saved strategy description, and
continue through implementation and validation. Ask only when a missing choice
would make the requested build unsafe or impossible.

When saving `rules.json`, use the current human-readable Rules contract rather
than legacy `text`/`enabled` objects. Each rule needs `id`, `status: "active"`,
`raw_quote`, `interpretation`, `source`, `created_by`, `last_edited_by`, and
`edit_history`. Read `strategy-rules` before creating that file and validate the
whole JSON object before the first file call.
After `create_strategy`, call `list_files`. If its returned inventory contains
`rules.json`, read that exact file and use `replace_file` with the fresh edit
handle. If the inventory does not contain `rules.json` and the user requested
Rules, use `create_file`. Never call `create_file` for a path that `list_files`
or `get_file` returned.
Each file write creates a revision of the whole workspace and preserves the
other files. After a successful `create_file`, that path exists in subsequent
revisions unless it was explicitly deleted. Editing `main.py` does not remove
an existing Rules or helper file. To change a file you already created, read
it from the latest revision and use `replace_file` or `patch_file` with its
fresh edit handle; do not call `create_file` again. A listing taken before the
creation no longer establishes that the path is missing.

Saving `main.py` does not create `rules.json`. Carry the returned path inventory
forward when saving the sibling Rules file: an absent path still requires
`create_file`, not `replace_file` with an empty handle. Never send an empty or invented `editHandle`.
For an existing Rules file, first read that exact path at the latest revision
and copy its returned handle; a `main.py` handle cannot authorize a Rules edit.
After the Rules save, read back both files from its returned revision and check
that the saved role prompts and Rules agree on the requested decision windows,
trade economics and responsibilities. Do not acknowledge a known saved-code/prompt mismatch as remaining work
when the authorized correction is available: correct that mismatch, read back
the final coherent revision, and then start validation.

If a new AI trading-team build uses `patch_file` anyway and the readback is
partial, truncated, tail-only, missing imports, missing the strategy class,
missing the agent/team implementation, or otherwise not a complete executable
`main.py`, the build is not saved correctly even if the patch returned a revision
id. Immediately call `replace_file` with the complete AI-team implementation,
read that replacement back, and only then start validation or final-answer.

A `create_strategy` call before a visible plan is only valid if the current
user explicitly asked for an empty workspace/import/copy with no implementation
or validation work. For normal AI-team builds, no visible plan means the build
workflow is incomplete even if code and validation tools later run.

## AI-owned decision contract

For ordinary new automation and when the user asks for AI-only, agent-only, no
hybrid logic, or says Python should only create and run the agent, this contract takes
priority over deterministic strategy-building guidance:

- Load this skill. Do not load `options-strategies`, including for options
  or multi-leg strategies. The agent uses LumiBot's generic built-in market,
  account, options, position, and order tools directly.
- Generate a minimal strategy class with at least one upstream non-trading
  researcher and exactly one terminal trading/risk agent. `on_trading_iteration()`
  runs the upstream agent, passes a bounded evidence packet, then invokes the
  terminal trader. Normal imports and the standard backtest harness are allowed.
- Do not import or instantiate `OptionsHelper`. Do not retrieve chains, select
  contracts, calculate Greeks or prices, size positions, construct orders,
  evaluate entries or exits, parse agent output into trades, or manage positions
  in Python.
- Put only the strategy-specific trading policy in the agent's system prompt:
  objective, valid instruments, entry and exit policy, position and risk limits,
  cadence, and any user-specific constraints. Do not copy generic stock or
  options mechanics into every saved strategy prompt.
  Role ownership is explicit: the trading agent's saved prompt requires fresh
  account/position/open-order, exact-contract, executable-price, liquidity and
  risk evidence immediately before action, preserves the requested atomic risk
  structure, and verifies the returned broker outcome after submission before
  claiming execution. Refer to runtime skills for the exact workflow;
  an upstream researcher's instructions do not assign the trader's obligations.
- Preserve the user's package orientation and opening cash flow in both the
  saved role policy and active Rules: net debit and net credit are different
  requested structures. An example's default orientation never overrides the
  user's long/short mandate. Keep contract selection and order construction
  agent-owned; Python does not translate those directions into trades.
- LumiBot exposes its built-in `stock-trading` and `options-trading` skills to
  every agent through ADK `SkillToolset`. The LumiBot runtime instructs the
  trading agent to load the matching skill when an asset becomes relevant. The
  BotSpot builder does not need to predict the asset class. A broad agent may
  decide to trade an option during its run and then load `options-trading`
  itself before acting.
- Generic chain inspection, exact-contract validation, Greeks and liquidity,
  multi-leg construction, signed close sides, current-price readiness, pending
  order reconciliation, atomic submission, and post-submit verification belong
  to those LumiBot runtime skills and built-in tool descriptions. They do not
  belong in the saved strategy system prompt.
- Default new trading agents to the model marked (default) in the CURRENT AI
  MODELS table at the end of the system prompt unless the user selects another
  model. Write its exact id from that table.
- Do not simplify a complex multi-leg request into a single-leg or deterministic
  shortcut.

Minimal AI-owned trading shape:

```python
from pathlib import Path

from lumibot.strategies.strategy import Strategy


class AIOnlyOptionsStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
        self.agents.create(
            name="researcher",
            model="<default model id from CURRENT AI MODELS>",
            allow_trading=False,
            system_prompt="""Research the setup and return a bounded evidence packet. Never trade.""",
            rules_path=Path(__file__).with_name("rules.json"),
        )
        self.agents.create(
            name="risk_trader",
            model="<default model id from CURRENT AI MODELS>",
            allow_trading=True,
            system_prompt=(
                "You are the only agent that trades, and you own risk. Read the research, decide, "
                "and place or skip the orders yourself. Independently refresh current account "
                "state, positions and open orders immediately before acting; revalidate exact "
                "contracts, executable prices, liquidity and risk. Preserve the requested atomic "
                "structure. Inspect the actual returned order status and resulting positions "
                "before claiming execution. Risk rules: never put more than 40% of the "
                "account in one position; hold cash when the research is weak or mixed; cut a "
                "position when the reason you bought it no longer holds."
            ),
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

BotSpot's canonical `rules.json` belongs beside `main.py`. Pass it through
`rules_path` so LumiBot reloads and injects active rules before every agent call.
For an AI-team first build, include `rules_path` in the first complete `main.py` replacement before saving `rules.json`. The Rules write then becomes the newest
whole-strategy revision; do not return to patch `main.py` merely to add the
binding that should have been present in the initial replacement.
Do not serialize the rule ledger into the system prompt. Disabled, deleted, and
audit-only entries are not active runtime instructions.

When building an explicit AI-only iron condor, credit spread, ORB, or VWAP
strategy, also load:

- `references/ai-only-scaffolds.md` for parameterized prompt scaffolds;
- `references/ai-only-order-verification.md` for post-submit self-checks.

For a parameterized AI iron condor, preserve its opening direction: for a
long/net-debit condor, buy the inner put and call and sell the outer put and call;
the short/net-credit condor uses the opposite legs. Buying outer wings and
selling inner options remains a credit structure even if labeled long or debit.
Read back the saved policy and Rules and correct any contradictory leg directions
before validation. Put wing width, relevant leg delta, DTE window, an appropriate
debit ceiling or credit floor, profit-take, stop-loss, max contracts, roll policy,
and exposure limits in the agent prompt or run context. The LumiBot
runtime skill supplies the reusable chain, leg, atomic-order, and verification
workflow. Do not duplicate that workflow in the saved prompt, Python, or
`OptionsHelper`.

For AI-only ORB and VWAP, choose a cadence that can observe the requested setup
without needless model calls. Hourly agent decisions may still analyze minute
bars. Keep Python minimal and put opening-range or session-VWAP policy entirely
in the agent prompt. The runtime `stock-trading` skill owns reusable evidence,
order, pending-order, and verification mechanics.



The shared guide continues in the ordered resources below. Load the relevant continuation; these are complete source sections, not summaries.

- Part 2: `references/shared-guide-02.md`
