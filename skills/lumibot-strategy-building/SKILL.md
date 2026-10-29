---
name: lumibot-strategy-building
title: "Building LumiBot Strategies on BotSpot"
description: "Use as the main direct-edit strategy-building skill for new BotSpot strategies and substantial strategy rewrites. Choose the decision owner first, preserving explicit architecture choices and the ordinary hourly/daily AI-owned default. It owns the build, plan, validation and final handoff. A fast Python/hybrid recommendation explains avoided AI round-trip latency and credit use. Load supported LumiBot API references only as needed."
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

# Strategy Building Core

Choose the decision owner before writing the first file. Ordinary hourly/daily
new builds default to AI-owned decisions, even when the user describes exact
indicators without saying AI. Load `lumibot-ai-agents`: exactly one agent may
trade, research/planning agents cannot trade, and every configured agent runs
each trading iteration. Preserve an explicit Python/hybrid choice and use the
cadence/latency decision rules below for faster signals. A no-auto-backtest
preference changes validation permission, not this architecture choice.

## Preserve the user intent across files

For an existing strategy, add the requested behavior to its existing working
state owner before considering a replacement. If a new exit condition can set
accepted exit intent, add the trigger to that existing intent path. Preserve its
pending-order and callback handling. In particular, protective orders and discretionary closing orders have different roles:
cancelling every sell before a new exit can cancel the market close you are
already waiting to fill. An added trigger does not by itself require changing
which existing orders are cancelled or replacing their reconciliation.

Defensive changes outside the requested operation are still behavior changes.
Keep a reconciliation repair within its affected operation; do not transplant
it into sibling entry blockers, deadlines, sizing or scheduling. Compare each
changed method against the request-start file. If a sibling method needs no
change to fulfill the request, retain its original behavior, including its
existing handling of missing data. Report an unrelated concern separately
instead of silently repairing it in a narrow edit.

RULES LEDGER CONTRACT: User-authored strategy behavior is durable by default,
even when the user never says `rule`, `remember`, `lasting`, `always`, `add`,
or `remove`. Entry and exit conditions, symbols and universes, indicators and
timeframes, sizing and risk, order placement, cadence and frequency, options
construction and delta/DTE/premium constraints, holding behavior, and explicit
allowed or forbidden actions belong in `rules.json`. Load `strategy-rules` for
ledger shape, create/edit/disable history, readback, exact backtest review, and
mixed-turn precedence. Follow that contract on every strategy build or edit,
including requirements embedded in advice, result discussion, backtest
requests, rescue, and AI-only work. Keep executable behavior and the Rules
ledger aligned in the same conversational edit. A manual Rules-tab save is a
ledger-only operation and does not authorize a Python edit.

For a behavior edit with existing Rules, make the task's completion criterion
cover both the executable change and the matching active Rule interpretation.
"Only change this setting" does not mean leaving its operative Rule at the old
value. After the code save, read Rules from that returned revision, reconcile
the requested intent while retaining original quotes and history, then read
both saved files from the final revision before validation. A code-only readback
does not establish that the requested behavior is coherently saved.

Use the same requested intent change in both saved representations:

| User's change | Executable behavior | Existing active Rules |
| --- | --- | --- |
| Replace a setting | Change that setting and required consumers | Update its interpretation and history; retain the original quote |
| Add a condition or exit | Add only that behavior | Append a separate active requirement when an existing broad mandate does not conflict |
| Remove a condition | Remove its enforcement | Disable/delete the removed Rule; do not add an active inverse |

A ledger may contain one broad original-mandate Rule rather than separate
conditions. Keeping that Rule unchanged does not record an added behavior:
append the new active requirement with the current request as provenance; preserve the entire existing interpretation, including setup and validation requirements,
unless the existing interpretation must be amended to resolve a real conflict.
"Don't touch anything else" preserves unrelated behavior; it does not omit the
requested behavior from Rules. "Just save" permits both necessary file saves,
without a backtest, deployment or trade. Before the final response, verify two
facts in the final revision: the requested executable change is present AND
the active ledger describes it. Reading Rules without recording the addition
is an incomplete edit.

## Verify the change against its starting point

Use the successful code mutation in this request as evidence of what you changed.
A common sequence is: read code A -> save code B -> save Rules C. The C-versus-B
analysis can truthfully say code did not change in that last save, because
B already contains the change made during this request. It does not mean the
code was unchanged from A. For the user, lead with the saved behavior and
what validation actually ran. Do not claim that code was already present or
left unchanged when your own successful mutation added it.

When explaining an edit, compare the final saved behavior with the starting revision read before this request's first mutation. A later readback of your own edit does not mean the behavior already existed. Describe that behavior as added or changed in this request; use "already present" only when the starting file actually contained it. The final readback verifies what is saved, while the starting read and successful mutations establish what changed. Keep the explanation short and distinguish saved changes from tests actually run. For a narrow edit, report the requested saved behavior, validation and material limitations. Do not restate unrelated Rules just to expand the handoff. When a constraint is relevant, minimums remain minimums and preferences remain preferences; do not weaken a required bound into a preference or promote a preference into a guarantee.

For a behavior edit that saved more than one file, retain the original code revision id from the first read. Finish with a consecutive comparison readback: read the code from the original request-start revision, then the final shared revision, and read final Rules. Perform no mutation between these comparison reads. This places the actual starting and saved behavior together for the handoff; a later Rules-only revision analysis compares only its immediate parent. It cannot establish that code was unchanged across the request. Report the verified saved behavior and preserved constraints; do not copy a single-save analysis's retrospective claim into the user reply.

## Select bounded indicator history

For ordinary built-in moving averages, use the matching built-in and its positive offset for the previous observation. Do not wrap ordinary built-in SMAs in a custom indicator merely to return current and prior values. In LumiBot 4.6.32, `self.indicators.sma(asset, length=N)` requests its finite window; `self.indicators.sma(asset, length=N, offset=1)` includes the prior observation. Recursive/custom calculations retain their broader initialization contract; a period alone does not justify truncating them. Preserve completed-bar timing, corporate-action adjustment and genuinely required missing-data checks. A repeated missing-session occurrence count is not the number of distinct missing sessions: inspect the actual dates, requested length and worker version before diagnosing it.

## Select the execution owner before writing order logic

For Python execution, read the applicable complete pattern BEFORE implementing
that state owner, rather than as an optional lookup after a failed run. Keep an
existing equivalent owner when it already satisfies the requirements. A narrow
parameter edit does not authorize replacing unrelated working mechanisms.

For a daily **filled-entry** limit, changing a resettable submission counter is
not the complete repair: yesterday's pending order can first fill today. Before
editing this mechanism, load `references/entry-fill-allowance.py`. Reserve new
entry intent before publication, retain every unresolved attempt across session
reset, and count its first execution once, including partial fills and retries.
Keep submission/attempt limits distinct when that is what the user requested.
The helper counts entries only; preserve position sizing and order-quantity
reconciliation. Connect the selected pattern to actual submission, partial/full
fill and terminal-order paths before launching verification. Merely loading it,
changing a constant, or disclosing missing lifecycle handling does not implement
the requested limit. Do not classify its pending reservation as a filled trade.
Prefer its complete `EntryOrderLifecycle.for_strategy(self)` factory and wiring:
keep the returned owner on the strategy object, with only its plain state in
`self.vars`. LumiBot Vars supports attributes and `get/set`, not dict subscripting
or `setdefault`. Refresh before entry eligibility,
submit the prepared order through `submit_new`, and observe actual order callbacks.
It preserves reservations on unknown submission errors. Use the lower-level
`observe_order` adapter only when preserving an existing equivalent state owner,
including polling after a missed callback. Keep existing persisted state during
initialization. An unknown historical fill date may use the first observation
as a conservative upper bound; disclose that bound instead of inventing a date
or permanently consuming every future session's allowance.

For Python strategies, preserve each requirement's timing: daily entries do not
turn a protective stop into a daily close check. Before implementing protection,
load `references/protective-position-example.py`. It connects standing stops to
whole-position fills, callback/iteration reconciliation, and retained accepted
exit intent. Adapt its stop-price policy without changing signals or sizing.
Reconcile partial fills, canceled/rejected orders and existing positions. Run
risk and accepted exits before entry-only returns; a pending entry cannot bypass
an exit. Cancel conflicting entries when policy requires cash, and confirm
protective-order cancellation before submitting a competing full exit. Retain
unfinished market exits rather than canceling/recreating them each iteration.
A later market sell based on yesterday's low is not a stop fill at the threshold.
Preserve broker/gap constraints and disclose actual data/fill-model limits.

- Before implementing portfolio order reconciliation, load `references/rebalance-state.md` and `references/rebalance-example.py`. The complete example separates accepted target generations, confirmed sales, bounded purchases and actual completion; adapt its configurable policy without changing the user's allocation.
- A target allocation is not spendable cash. For a rebalance, retain the target and outstanding order identities until fills and actual positions reconcile. A weekly/monthly signal schedules new targets; it must not prevent finishing an already accepted rebalance between signal dates. Submit reductions first, then calculate remaining buys from confirmed available cash, existing holdings and still-active orders without counting the same reservation twice. Include fees and execution-price movement: spending every dollar at an earlier signal close can borrow at the eventual fill. Use supported price-bounded execution when an unbounded market fill cannot respect the cash ceiling. Preserve the user's weights, universe and cadence; do not hide an execution shortfall by changing their allocation or enabling margin.


For a new build, hasStrategy=false means no workspace exists. After the required
research/plan, call create_strategy before get_file or list_files. Omit optional
file selectors only once an attached or newly created workspace actually exists;
an empty file inventory call cannot discover an uncreated workspace.
Wait for successful workspace creation before issuing any dependent file call;
`create_strategy` and `list_files`/`get_file` cannot share a parallel tool batch.

Before starting validation, finish the saved-file readback and mark the actual
implementation plan item completed. Then start the backtest; only its returned
wait can complete the start item and put validation in waiting. Do not complete
a later plan row while an earlier implementation row is still in progress.
For a backtest of the current workspace's newest saved files, omit the optional
revision selector so the tool resolves the current conversation revision. An
explicit historical/different revision remains allowed when actually requested.
Every saved file, including Rules, advances the revision; an earlier main.py
save is not necessarily the newest complete workspace.

For an authorized implementation or edit request, finish the smallest coherent
saved change before ending. Describing a needed refactor or inspecting source
alone does not complete that request. Missing live timing or deployment proof
limits the verification claim; it does not by itself prevent editing the owned
source with supported APIs and reading back the result. Preserve behavior,
complete the requested edit, and state the actual remaining validation gap.

## Final build handoff

Use this order in the final handoff, even when validation is queued:

1. State the selected decision owner AND why. For a fast Python/hybrid build:
   "The signal/order path uses Python to avoid an AI model round trip and
   per-call credit use." A statement that Python is deterministic or polling is
   fast does not explain that choice.
2. State the saved behavior verified in the latest readback, using its product
   revision card rather than manually copied UUIDs.
3. State the actual validation status and relevant feed/broker limitations.
   Waiting for capacity is not a test result and does not replace the first line.

Broker and scheduling latency are separate from AI model round-trip latency.
The first handoff line must explain the decision owner, rather than substituting
a general broker/feed timing disclaimer for the reason AI calls were avoided.

A new trading date resets only session counters for settled work. It does not
prove that yesterday's order, package, position or hedge obligation is terminal.
Retain and reconcile unresolved operations before clearing their identities or
starting another session's entry; an overnight position cannot disappear from
state because the calendar rolled over.
Retention also needs a completion path: consume confirmed exit fills/flatness,
retire the matching resolved package once, and allow the next eligible entry.
Run pending entry/exit reconciliation before a daily-entry/reset eligibility
return; a blocked reset must not make the code that resolves its blocker
unreachable. Preserve both unresolved obligations and ordinary daily repetition.

When the user explicitly requests historical/backtest-only behavior and forbids
live orders, enforce that choice in the saved executable entrypoint and order
path. Do not retain a live `Trader` fallback or claim live execution is disabled
when the code still permits it. This scoped request does not remove live support
from an ordinary strategy whose user authorized that capability.


Use the actual declared file-tool schema. When strategyId and revisionId are required, copy both from the latest successful owned workspace result, including for Rules writes. A schema that permits the current attached target to resolve them remains supported; never invent or shorten either identifier.


Before file tools, resolve an existing owned strategy/revision or create the
requested new workspace with create_strategy. An unbound new conversation has
no files to list yet; list_files/get_file cannot discover an unspecified target.
After start_backtest, copy the COMPLETE returned externalWaitId unchanged into
record_external_wait_in_plan. It is distinct from backtestId; never reconstruct
it by combining UUID segments. Bind that exact returned wait to existing plan
item identities. If the plan snapshot is stale, refresh it before mutating.


Before saving files, distinguish an empty file from an absent file. BotSpot's
neutral starter already contains `main.py` and an empty `requirements.txt`.
Read and replace that existing requirements file with its fresh edit handle;
never use `create_file` for it. Discover any other missing path before creating
it. After saving one file, refresh the next file's read/handle from the newest
revision rather than reusing a stale cross-file handle.


## Preserve the execution contract in saved code

An explicitly initial-capital budget is a stable baseline: persist the first
verified portfolio value in `self.vars`, then reuse it across iterations and
restarts. Capture that anchor at the first point account value is known, BEFORE
any independent price/history/quote check can return early. A missing price must
not postpone the baseline until a later, changed account value. Use an explicit
missing test, not a truthiness fallback that overwrites an existing baseline.
Do not substitute the changing current portfolio value. Current-value sizing
remains appropriate when that is what the user's Rules specify.

On an explicit repair request, an observed exception from a public initial-
budget property can be handled with this same persistent starting-value anchor,
using the original configured budget or first verified public account value.
Preserve the allocation rule and never invent a balance. A current framework
reference defining the property does not prove its backing value was available
in the failing deployed lifecycle. Keep that root cause uncertain while
preparing the narrow compatibility repair. A broker reconnect requirement is
separate: save/read back the safe revision and prepare the same deployment's
owner approval using its authoritative credential state, without guessing a
credential or claiming the prepared repair is already running.

Give entry/submission latches the lifetime required by the Rules and the owned
order lifecycle. A latch used to prevent duplicates must not silently disable
later eligible sessions or entries. Re-arm only after the relevant terminal
orders, positions and hedge obligations reconcile; preserve an explicit one-time
strategy rule when the user actually requested one. Trace the reset caller in
the saved code: setting `entry_submitted=True` with no reachable re-arm path is
a permanent shutdown, even if the smoke window only contains one trade. For a
recurrent Rule, reconcile its owned terminal order and flat/closed position,
then let the next eligible session or signal evaluate again. A per-session
allowance uses the strategy's actual trading-session key, not a lifetime flag.

A trading AI's own saved instructions must verify current account state,
positions, open orders, exact contract identities, executable package prices and
liquidity immediately before acting. Adviser output and a separate Rules file
do not perform that verification. When the requested structure is defined-risk
and atomic, preserve that submission contract and verify its returned result
before describing execution. Keep these instructions with the trading owner;
research agents advise without submitting orders.

Explain an architecture recommendation against the requested cadence: model
calls add variable latency and credit cost to a signal path. Deterministic
rules can use ordinary Python; discretionary reasoning can use AI with an
appropriate cadence. In the final recommendation, connect that choice to the
user's deadline: Python avoids a model round trip on a fixed-rule signal path;
full AI reasoning adds variable response latency and per-cycle credit use.
Quote/broker delay is a separate limitation, not that architecture explanation.
Preserve an explicit AI-only or fixed-rules choice.

## Plan transitions during creation and repair

Use the exact returned current item IDs and positions, refreshing get_active_plan
when the visible snapshot is stale. update_plan_item(s) changes existing rows;
it cannot append a future position. Never reopen a completed historical attempt.
Before appending an in_progress replacement, resolve every earlier unresolved
row with its true satisfied/partial/unsuccessful outcome. If a required step
cannot yet be done, preserve that gap and link the actual follow-up rather than
marking it successful. Use replace_plan_items with the full visible list for
an atomic transition, or resolve the current row then add_plan_item with a nested
item object. Copy the returned new identity before updating it. Creation,
saving, validation start and terminal validation are different outcomes.

## Cash-bounded stock entry and complete exits

For new Python cash-only entries or an authorized execution repair, use the complete supported pattern below. Preserve an explicitly requested order policy and unrelated behavior in a narrow edit; do not convert an existing strategy merely to copy an example. Disclose the chosen execution-price and fee assumptions.

- A submitted sell is not available proceeds. Reconcile confirmed fills, remaining positions and refreshed cash before spending its proceeds; an iteration boundary alone does not confirm settlement.

- Before marking allocation/sizing Rules verified, inspect the executed run's minimum cash, fees, order lifecycle and remaining positions with the available artifact tools. Successful completion, positive returns or a code-only Rules review cannot establish cash correctness. Negative cash without authorized borrowing is a mismatch to investigate and repair on the saved revision; do not call that Rule PASS or silently add a deposit.

For an unleveraged stock/ETF strategy, a prior signal close is not the next
market fill price. Even a fee allowance or small cash buffer cannot guarantee
that a market order fits cash after a gap. Use an execution price bound when
appropriate, or a documented broker-native cash amount order if supported.
Do not silently change an explicitly requested market-order policy. Disclose a
chosen limit-entry policy and its unfilled-order risk; never use a future close.

This complete example submits a whole-share DAY limit order within a verified
cash budget and configured fee upper bound. Supply a valid exchange price/tick,
fee rate and total fixed-fee bound for the entry. Do not invent zero fees.
`spendable_cash` already reflects the requested allocation and unresolved buy
commitments not yet deducted by the broker; do not double-reserve an amount the
broker has already deducted. Unconfirmed sell proceeds are not spendable cash.
Reconcile existing orders for this asset before calling it. The example does
not own signal conditions, allocation decisions or the order lifecycle.

```python
from decimal import Decimal, InvalidOperation, ROUND_FLOOR


def submit_cash_bounded_entry(strategy, asset, *, spendable_cash, limit_price,
                              percent_fee, fixed_fee_bound):
    try:
        balance, budget, price, fee_rate, fixed_fee = (
            Decimal(str(value)) for value in (
                strategy.get_cash(), spendable_cash, limit_price,
                percent_fee, fixed_fee_bound,
            )
        )
        if (not all(value.is_finite() for value in (balance, budget, price, fee_rate, fixed_fee))
                or price <= 0 or fee_rate < 0 or fixed_fee < 0):
            raise ValueError("Invalid cash, price or fee evidence")
    except (InvalidOperation, TypeError, ValueError):
        strategy.log_message("Entry not submitted: cash, price or fee evidence is unavailable or invalid.")
        return None
    available = min(balance, budget)
    quantity = int(((available - fixed_fee) / (price * (1 + fee_rate))).to_integral_value(rounding=ROUND_FLOOR))
    if quantity <= 0:
        return None
    order = strategy.create_order(asset, quantity, "buy", limit_price=float(price), time_in_force="day")
    return strategy.submit_order(order)


def submit_full_exit(strategy, asset, *, unresolved_orders):
    if unresolved_orders:
        return None
    return strategy.close_position(asset)
```

Keep unfilled and partially filled order IDs until their state and remaining
position are reconciled. A cancel request, `is_active() == False`, or a submitted
exit does not establish completion. Preserve accepted exit intent across a
rejection, partial fill or restart; reconcile the actual remaining quantity
before another submission. Scope this to the affected risk unit, not unrelated
symbols. For deadlines and callbacks, use `lumibot-api-reference` resource
`references/fast-order-management.md`. For a duplicate-order repair, load this
skill's `references/order-operation-ownership.md` before editing. Trace every
callback, polling, fallback and queue continuation path, and repair their shared
preparation/publication/completion owner. Preserve valid remaining legs and the
next independent entry; a callback-only guard or a lock only in submit_order
leaves queued duplicate work alive. Read back the complete causal repair.

For partial/canceled hedge replacements or late/repeated executions, load this
skill's `references/order-quantity-accounting.md` and
`references/order-quantity-example.py` before editing. Track the original
entry's obligation across ALL attempts, including retired orders; an account
position is not proof of this entry's executed quantity. Newly reported old
fills can require canceling and resizing a live replacement. Preserve the next
independent entry and every unrelated trading policy.

After several writes, use the LAST successful mutation/readback as the saved
revision. Report the saved behavior and use the product's structured revision
card for its identity. Omit manually transcribed revision UUIDs and display
versions from the final prose; an earlier base or intermediate revision is not
the saved result. Copy exact returned IDs only where a tool requires them.
If a text patch fails because its old fragment is missing, inspect the current
saved method. The desired behavior may already exist from an earlier write.
Keep that verified revision if so; otherwise repair the missing requirement
using current unique context. Do not claim a failed patch itself was saved.

The full-exit helper deliberately delegates quantity and closing side to the
supported API; never replace a fractional position with `int(position.quantity)`.

Before claiming an unleveraged backtest is correct, inspect its actual minimum
cash, submitted orders, fills and remaining positions. Positive ending cash and
a completed engine status do not excuse an earlier overdraft or abandoned exit.
Repair and retest the same requested rules; never mask debt with `adjust_cash`,
fake deposits or a changed signal. Inspect the returned artifact inventory and
schema before claiming a required historical input is missing. These Python
examples are for fixed-rule strategies, not controllers around AI-owned trading.

The conversation already has a data-provider default. Do not call
`set_data_provider` merely to select or reselect `botspot_auto`. Call it only
when the user explicitly requests a different provider or a tool result proves
that the configured provider must change. Provider selection is not a
first-build prerequisite.

After `start_backtest` returns a real `externalWaitId`, call
`record_external_wait_in_plan` before any `update_plan_item`,
`replace_plan_items`, status poll, retry, or assistant text. Do not try to mark
an item waiting directly. Pass the returned `externalWaitId` with the plan
targets; omit optional external/revision identity assertions. The helper
resolves and validates the exact backtest and revision from the owned stored wait.
When the plan has separate launch and result-review rows, pass BOTH selectors:
`currentItemTarget` is the unfinished launch row, `waitingItemTarget` is the
later result-review row. The helper completes launch and waits on review in one
mutation. For one combined launch/review row, use that same row for both targets.
Copy selector objects from the latest active plan; do not leave an earlier launch
row pending while trying to attach the wait only to a later review row.

Use this as the main direct-edit strategy-building skill for new BotSpot strategies and substantial strategy rewrites.

## Marketplace First

Marketplace first. As the first step of a new strategy build, before research, a plan, or `create_strategy`, search the BotSpot Marketplace with `marketplace_strategies(action="list", query=...)` using 2 to 4 plain key words from the request (tickers, the rule, an investor or data-source name). Skip it only when the user explicitly asks to build from scratch, is editing an existing strategy, or already picked a listing. When listings closely match, do not create anything in that turn: read the best one with `action="get"` (if several fit, name up to three, best first), then answer in a few short lines with the listing name and `marketplaceUrl`, one line on what it does, what the publisher shares, and any API key the user must supply (for a `credentialSource: "user"` key, check `saved_env_vars(action="list")` and warn when it is missing, including a paid subscription; `managed_ai` keys run on BotSpot credits). Offer the choices: copy it in one step (`clone_strategy` with its `listingId`, only when `capabilities.clone` is true), or build their own version starting from its shared code (`action="get_code"`, only when `capabilities.code` is true). Respect exactly what the publisher shared: never show, quote, paraphrase or guess code, rules, positions, orders or trades a listing does not grant, and never present your own code as the publisher's; for a private listing say its code and holdings are private and offer its Marketplace page or a fresh build of their own. If nothing matches closely, build normally without mentioning the search. Load `botspot-marketplace-reference` for the full Marketplace tool guide.

## Dependency Identity Before Editing

When the fetched file is only a neutral starter and the request needs its first
real implementation, use complete `replace_file`, even when the user says
"update this strategy". Do not patch a remembered copy of boilerplate. For an
actual targeted patch, copy `expectedOldText` byte for byte from the latest
`get_file` content and use its exact range; do not reconstruct it from a summary,
retype blank lines, or guess line boundaries. A broad module rewrite is clearer
as complete replacement with the fresh edit handle.

Once an editable workspace exists (after `create_strategy` for a first build), discover optional files with `list_files` before reading them; an absent Rules file is not a reason to probe a failing `get_file`. Do not call file tools before first-build workspace creation. For a connected lifecycle repair spanning several methods, use one complete `replace_file` based on the current full saved file, preserving every unrelated method and policy. Do not chain remembered text anchors through multiple revisions.

For a saved-file read, call `get_file`; `patch_file` is never a reader. A patch requires the fresh `editHandle` plus nonempty `operations`, not just path/strategy/revision selectors.

For one requested logical change to one file, use one `patch_file` call with all non-overlapping operations, or one complete `replace_file` when that is clearer. Inspect the related consumers before the save, then read back the saved file once and verify all requested changes and preserved behavior together. A genuine defect in readback requires a correction; do not make separate revisions for individual settings that belong to the same request.

Before a text patch, copy `oldText` byte for byte from the latest saved read, including whitespace and the actual receiver or state field. Do not construct it from the desired replacement or memory. A valid edit handle does not validate an invented text anchor. Check the exact anchor and choose a unique surrounding function/block when changing only one occurrence. In strategy code, initialization and exit cleanup can contain the same assignment; preserve the occurrence outside the requested change. For an ambiguous one-line anchor, do not use `replaceAll=true` unless every occurrence is intentionally part of the user's requested change. Include the surrounding block or compose one complete replacement that preserves all other behavior.

An existing Python strategy's bounded parameter edit starts with its saved file. Load focused API documentation only when the actual edit needs it; do not run new-strategy discovery or load every asset/AI example for a literal setting change. Do not add missing Rules scaffolding for a bounded existing-Python parameter edit; preserve and reconcile existing Rules when present, and create Rules when the user requests durable policy or when building a new strategy. A new Rules file or a distinct file change still needs its own sequential save.



For a bounded edit, inspect every use of the parameter or state being changed
before saving. A stop distance may also feed sizing, allocation, or an entry
condition. Change only the behavior the user requested; if a shared setting
couples the requested change to unrelated behavior, separate those consumers
and preserve the original sizing behavior and other unchanged rules. Preserve
behavior rather than the old expression: if sizing used
`cash / price * exit_distance / normalizer` and only the exit distance changes,
retain its old ratio as an independent sizing multiplier so cash and price can
still vary without the exit edit changing quantities. Changing that expression
is necessary to preserve sizing, not an unauthorized sizing change. Do not
restore the old coupling during Rules reconciliation or a later readback audit;
the Rules must describe the preserved behavior and the authorized exit change.
If the user explicitly requests a sizing change, apply that requested change.
Read
back the complete saved revision and check the affected consumers together.

Validation goals are acceptance criteria, not trading instructions. Keep a build/backtest request's testing objective separate from the active runtime policy. Preserve the user's original quote as provenance, but describe validation as a condition to check after execution, never as permission to override entry or exit conditions. For AI-owned strategies, write that distinction into the trading agent's system prompt as well as the Rules interpretation: Never place an order merely to satisfy a first-trade validation target. A valid no-trade decision must remain no-trade when the entry condition is false, even if validation is incomplete. Verify fresh, correctly dated signal evidence before submitting an order; do not submit first and inspect contradictory evidence afterward. Research packets are evidence, not authority to override the saved policy.

Order-side values must match the actual asset and position: stocks and ETFs use `buy`/`sell`, including `sell` to close a long position; option opening/closing sides apply only to option contracts. State this distinction in AI-owned execution prompts and use supported public order helpers. Do not add an order filter or manufacture a trade to enforce this guidance.

Each trading agent run must satisfy order readiness for both entries and exits: inspect fresh account, held positions, and complete open orders, then call `market_last_price` (or `market_last_prices` for all ordered assets) in that same run before submitting any order. Historical signal bars and a researcher's quote do not replace this check. Write the sequence into AI-owned execution prompts; never bypass the runtime's existing safety validation.

For entry/exit repairs, trace the state from confirmed fills to its consumer:
the fill must belong to the strategy's expected order and the held asset; an
order submission or another instrument's price is not fill evidence. Existing
position exits must remain reachable: entry filters must not bypass stops or
position management. Daily-only flags must reset at the next session. Handle
partial fills and restart reconciliation with the documented lifecycle methods;
compilation and one unrelated filled trade do not prove the requested exit works.

Apply these lifecycle checks to the behavior being repaired: do not add new exit features during an entry-only repair, or change an existing entry rule while repairing an exit. Preserve the original strategy's other behavior. A bounded repair of an attached strategy is an attached-edit turn: read its saved file first, unless current broker/fill/position evidence or a real file-access blocker must be resolved first. Do not resume an older Rules review or start a first-build plan just because one exists in context. Use only the current request's relevant evidence and focused documentation, save the bounded repair, and read it back. Then finish, or perform the validation the current task authorizes; an unrelated older plan does not expand the requested repair.

Treat every credential and environment variable as an exact dependency identity.
After reading an existing strategy, compare the literal names in the user's
request with the literal names used by the saved code. A similar prefix is not
evidence that two credentials serve the same system. In particular, a saved
broker connection cannot replace an API key used to authenticate an independent
HTTP data, database, notification, or model service.

If the user asks to remove exact variables that are absent from the saved code,
do not edit a similar-looking variable, weaken its required precondition, or
manufacture a revision. Explain that the named variables are already absent and
continue any separately requested validation on the unchanged current revision.
Only edit when the exact dependency or executable broker-authentication code is
actually present.

This exact-target audit is a write precondition, not a suggestion. When all
exact user-named targets are absent, do not call `patch_file`, `replace_file`,
`create_file`, or `delete_file`; do not make a no-op edit; and do not remove a
lookalike and later restore it. If an unchanged-revision backtest has already
started, leave that run alone. Never stop it or retroactively edit the strategy
to satisfy an edit premise that the saved-code evidence disproved.

Do not probe an optional `rules.json` with `get_file`. Read it only after a
successful `list_files` result or an earlier successful tool result proves that
the exact revision contains it. The `files` array returned by
`create_strategy` or `list_files` is that revision's complete file set: read
only paths it lists. A brand-new strategy has no `rules.json` until you create
one, so do not read it in the same batch as the starter files. A missing optional Rules file is not dependency
evidence, and a speculative failed file read must not derail an otherwise valid
edit, inspection, or backtest request.

Do not create or edit `rules.json` during a purely technical code repair that
preserves the user's trading rules. A requested durable behavior change follows
the Rules ledger contract below; mirror only that requested change, without
starting an unrelated historical Rules review. A new AI-owned build still needs
its canonical Rules file. Once the
requested executable file edit succeeds and its newest revision is read back,
stop adding files, renaming unrelated symbols, or broadening the repair. A
failed optional evidence tool does not authorize extra strategy cleanup when
the user supplied the exact fallback evidence needed for the requested fix.



The shared guide continues in the ordered resources below. Load the relevant continuation; these are complete source sections, not summaries.

- Part 2: `references/shared-guide-02.md`
- Part 3: `references/shared-guide-03.md`
- Part 4: `references/shared-guide-04.md`
- Part 5: `references/shared-guide-05.md`
