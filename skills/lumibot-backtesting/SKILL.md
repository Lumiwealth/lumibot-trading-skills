---
name: lumibot-backtesting
title: Backtest and debug a LumiBot strategy
description: Use for strategy repair and unfinished first-cycle validation after failed, timed-out or zero-trade backtests, including a terminal wake or a request to explain what happened. Repair pending-entry state through its full lifecycle, not only initialization. For read-only investigation, engine diagnosis, historical-data coverage, or a request not to edit or rerun, use backtest-analysis instead.
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

--------------------------------------------------------------
BACKTEST RESCUE WORKFLOW
--------------------------------------------------------------

If list_backtests returns no owned runs, do not call get_agent_runtime_diagnostics
with a fabricated or all-zero backtestId. Inspect the saved code and the user's
reported failure; repair a demonstrated code defect without claiming run proof.
Only a returned real backtest identity can support run diagnostics.
## Saved-file evidence

Read a known entrypoint such as `main.py` directly. Before reading optional
Rules or helper files whose presence is unknown, use `list_files` on the exact
revision and read only the returned paths. In particular, `rules.json` is
optional; do not probe for it with `get_file`. If the listing shows no Rules
file, skip Rules review and continue diagnosing the runtime from the available
code and logs. Do not create a file merely to make inspection possible.

## Hook Evidence And Queryability

- Treat every backtest hook identifier as opaque. Do not call UUID-only backtest
  tools with a non-UUID hook identifier. If the terminal hook id is not a UUID,
  use its factual terminal evidence and the attached saved revision. Do not
  probe `get_backtest_logs`, `backtest_status`, or artifact tools with that id.

STOP before any plan or backtest reader and validate the hook identifier. A
non-UUID hook label is never a valid argument to `get_backtest_logs`,
`backtest_status`, `get_agent_runtime_diagnostics`, or an artifact reader. Do not call one of those tools to
discover or confirm the expected validation failure. Plan setup may happen,
but the first domain evidence call for an unqueryable hook must be `get_file`.

The terminal hook is already evidence. A strategy, AI strategy, revision, or
conversation id from the request context is never a backtest identifier. If its backtest identifier is absent,
non-UUID, or absent from a successful backtest inventory, do not call
`get_backtest_logs`, `backtest_status`, or another ID-based reader with it. Use
the hook's exact terminal error/status plus the attached saved file, then make
the authorized intent-preserving repair. A query failure caused only by an
unaddressable fixture/legacy identifier is preventable and is not required
diagnosis.
A `bt-...` label is not a UUID. If the hook supplies that kind of label and no
successful inventory returned an exact persisted match, go directly from plan
setup to `get_file`; never call an ID-based backtest reader first.

When the terminal hook already contains a concrete runtime error and the saved
strategy is attached, do not call `get_backtest_logs` merely to rediscover that
same error—even if the hook identifier happens to look like a UUID. Set up or
reconcile the visible plan, then read the attached saved file and repair the
specific error from the hook.

For catastrophic negative equity, extreme loss, or position explosion, a
duplicate-entry guard alone is not a complete risk repair. When the saved file
contains explicit sizing and concentration parameters such as
`risk_fraction=1.0` or `max_positions=100`, reduce the explicit sizing and
concentration parameters in the saved revision as well as preventing repeated
entries. Read back those reduced values before starting validation.

For a bounded rescue that changes more than one non-contiguous region of one
saved file, use one complete `replace_file` after the fresh `get_file` read.
Do not construct a multi-operation `patch_file` payload for that rescue. The
complete replacement avoids a partially shaped operation and still creates one
immutable revision that must be read back before validation.

Before every first-cycle `start_backtest`, establish the visible plan first. It
must contain the current action and a future validation row. After the start
returns, use `record_external_wait_in_plan` with the exact returned backtest ID,
revision ID, and `externalWaitId`; never create the plan after the run starts.

CRITICAL ACTION CONTRACT:
- Treat every backtest hook identifier as opaque. Do not call UUID-only backtest
  tools with a non-UUID hook identifier. If the terminal hook id is not a UUID,
  use its factual terminal evidence and the attached saved revision. Do not
  probe `get_backtest_logs`, `backtest_status`, or artifact tools with that id.
- After saving and reading back the implementation, finish implementation before starting its backtest: complete the satisfied earlier plan rows and activate the launch row in one serialized plan update. A successful file save or backtest start does not automatically complete those visible rows.
- Copy the exact latest returned revision ID into any plan linkage and backtest request. Never reconstruct or retype opaque IDs. Optional plan revisionId fields can be omitted when they are unnecessary; an invented or shortened identifier is never a substitute for the actual returned ID.
- A failed original run is terminal even while its retry is queued. Describe each run separately: original failed, retry waiting/running/completed as actually returned. Do not append a generic “first backtest is not finished” statement that contradicts the original terminal result.


When a queryable terminal backtest has active Rules, inspect its trades, indicator
rows and logs, then call `commit_backtest_rules_review` for that exact run and
revision BEFORE editing code or starting another backtest. Record compliant
Rules too: zero trades or an execution latch does not waive this review.
The review documents the observed run; it does not change the Rules.
A successful review is immutable for that exact run/revision. Retain its
returned receipt, then proceed to the repair or validation step; do not commit
the same review again with rewritten summaries or additional equivalent evidence.
A new backtest result receives its own review; a revised summary of the old run
is not a new backtest.

Copy a domain tool's returned `externalWaitId` verbatim into the plan tool.
It is an opaque token: never reconstruct, retype from memory, or substitute a
backtest/revision ID. Keep the whole returned token unchanged. A plan-link
copy error does not authorize a duplicate queued backtest; correct the token
from the existing successful start response.

### Complete entry-state repairs

A pending-entry flag represents unresolved owned orders, not whether this strategy
has ever submitted an order. A repair is incomplete if it only changes the initial
flag value, or removes the flag without replacing duplicate-order protection.
For recurring flat-position entries, reconcile current owned active orders before
evaluating the entry, and keep the existing position check. For example:

```python
# At each iteration, before the existing entry checks:
owned_active_entries = [
    order for order in self.get_orders()
    if order.asset.symbol == self.symbol and order.is_active()
]
self.entry_submitted = bool(owned_active_entries)
# Keep the existing signal, position, sizing and submission logic below.
```

A failed state read is unknown, not an empty list. Preserve any explicit one-time
or per-session allowance separately; derive the real session key when needed.
For multi-leg strategies, retain their exact-order ownership and reconciliation.
Before saving, trace both states through the complete edited file: (1) an active
owned order prevents a duplicate; (2) after terminal resolution and when flat,
a later qualifying entry is reachable even if the signal has stayed true.
Initialization-only edits fail the second trace; deleting all pending-order
protection fails the first. Neither is a complete repair.
Before recording a no-trade Rules review, read the actual trades, indicators
and logs for that exact backtest. When metadata lists `indicators.csv` or
`indicators.parquet`, retrieve that artifact and inspect its observations with
`query_csv` (or the matching artifact reader), as well as the trade artifact.
A filename in metadata and an empty trade query do not establish which signals
fired. Complete these reads before `commit_backtest_rules_review`, even when a
stuck execution flag is already visible in the source.

### Continue the active rescue workflow

Before starting validation, finish each earlier implementation/review plan row
whose criteria are satisfied by the saved revision and readback. A later
start-validation row cannot be completed while an earlier implementation row
remains in progress. After start returns, bind the exact external wait to the
current start/validation rows. If a plan mutation is rejected, correct that plan
state using its actual rows before yielding; do not start a duplicate backtest.


- A provider-failed model turn is not a failed backtest. When durable retry context says the prior turn failed at the provider, a runnable strategy revision was already saved, the plan marks workspace/code work complete, and the first smoke has not started, continue from that checkpoint. Preserve the saved revision and resume the next incomplete validation step: start the first backtest over the first-test window on the newest saved revision, then record its returned external wait on the existing plan. Do not call `create_strategy`, `patch_file`, or `replace_file` in this checkpoint-continuation path unless a concrete failed backtest, log, saved-code readback, or tool result proves that a code change is needed. Merely rereading valid saved code or noticing that first-cycle validation is still incomplete is not evidence that the code should be rewritten.
- Before calling `record_external_wait_in_plan`, a visible plan must already exist. If the user asks to start a backtest and keep a plan accurate but no plan exists, call `create_plan` before `start_backtest`, then use the returned external wait to update that plan. Never call `record_external_wait_in_plan` first and create the plan only after the helper rejects the wait.
- When diagnosis reveals a repair before the next pending validation, reuse
  that earliest pending item's id: change its label/criteria to repair and start
  validation, then mark it `in_progress`. Preserve the completed diagnosis and
  its evidence. Add a later pending terminal-result review row before starting
  the backtest. Do not append an `in_progress` repair after an earlier pending
  validation row, or parent it under a completed diagnosis. Reuse the existing
  next step rather than skipping it or adding a duplicate repair subtree.
- Plan mutations are serialized. Call `get_active_plan` when the current plan
  and item ids are not already present in structured context, then make one
  mutation and wait for its result before constructing another. Never send
  `update_plan_item`, `update_plan_items`, `replace_plan_items`, or
  `create_plan` together in one assistant action. After `start_backtest`, use
  `record_external_wait_in_plan` as the single normal mutation; do not try the
  generic plan mutations first.
- Every `create_plan.items[]` object must include a non-empty `label`, a
  non-empty `completionCriteria`, and a valid `status`. Check the complete array
  before the call. Do not use a failed `create_plan` call to discover required
  fields.
- For a short placeholder file or a repair that replaces most of the file,
  call `replace_file` directly with the complete content and latest edit handle.
  Never estimate an `endLine` beyond the exact returned file or use
  `patch_file` as line-count discovery. Reserve `patch_file` for a genuinely
  localized edit whose complete line range is visible in the latest readback.
- If the retry context and plan disagree about whether the revision was saved or validation already started, inspect the current plan/revision/backtest facts and continue from the first factually incomplete step. Never replay completed workspace creation or file edits just because the model request is being retried, and never start a duplicate validation backtest.

Use this skill when a newly created or edited strategy has a failed backtest, a timed-out backtest, or a completed backtest with zero filled trades. The goal is not to explain failure and stop. The goal is to use the backtest evidence, create a normal strategy revision when a fix is justified, and rerun until the user has a working result or you can clearly prove that the request is unsupported or needs one concise clarification.

Completed launch rows record that a run was started; they do not promise that
its later result succeeded. Keep those rows completed. On a failed observation,
resolve the existing result-review row with its actual evidence and outcome,
then add linked repair/revalidation work. Never rename a completed launch into
a diagnosis row or reset it to in_progress. Omitting outcome in a patch retains
the saved outcome; it does not clear it. Ordinary handoffs complete the current
row, wait for the successful result, then start the next existing row.

## Unqualified long runs on a saved expensive AI model

A strategy's managed provider calls consume real BotSpot AI credits. They are
separate from how the current chat or an evaluation actor is funded. Explain
that credit consumption alongside the rough cost estimate, not as merely
model-equivalent usage. Compute any token estimate from explicit assumptions:
`calls * (input_tokens_per_call * input_rate_per_million +
output_tokens_per_call * output_rate_per_million) / 1_000_000`. Calculate each
input/output term before multiplying by the call count; do not mix tokens per
call with tokens for the whole run. Count every configured agent invocation and
state that tool output, reasoning tokens, retries and actual cadence can change
the total. Use the catalog's rates and distinguish provider cost from any
separately documented BotSpot credit conversion.

If the user has not yet chosen the saved expensive model/cost for a long test,
present two complete choices before asking:
- Keep the preferred model for the entire requested window.
- First test the requested longer window on the catalog's cheaper bot model,
  THEN test a shorter window on the original preferred model.
Name both models and both phases in the second choice. A binary “preferred or
cheap for this test?” loses the second phase. A missing runner or other code
problem does not replace this cost comparison; explain that separately.

A model name in saved code is configuration, not a human cost choice. A generic
"run this strategy for a year" request has not selected that expensive model's
cost. The exception applies when the human explicitly selected that model for
this validation (in the current request or a prior confirmed choice). Then
proceed without asking again or silently switching models. Resolve this before
following the run-only instruction to start before normal prose.

Core rule: keep the rescue inside the normal conversation. The user should see your tool calls, status updates, diagnosis, revision creation, and reruns as ordinary assistant work. Do not describe this as a hidden job or a separate system.

Read-only boundary: the words "failed", "broken", or "not working" do not by
themselves authorize rescue. If the user asks to investigate or explain an
existing run, diagnose the backtest engine or historical-data path, or says not
to change the strategy or start another backtest, load `backtest-analysis`
instead. Do not load this skill merely because an existing run has incomplete
data or skipped iterations.

Server wake/resume rule: BotSpot Node may wake you after a terminal backtest observation with `externalKind="backtest"`, `externalId=<backtestId>`, revision id, terminal status, trade count, current plan, and wait/run state. That wake is evidence only. Node owns durable waiting/retry state, but only your plan tools mutate the visible plan. React is only a display layer and may be closed or stale. On a wake, inspect the current active plan, avoid duplicate waiting rows for the same external event, and use `update_plan_item`, `update_plan_items`, `add_plan_item`, `replace_plan_items`, or `complete_plan` for every visible plan change. Use `update_plan_item` with a required `target` object and a `patch` object; target by id when available, otherwise use `target: { type: "position", position: N }`. `add_plan_item` takes a nested `item` object. Plan id and plan item id are different: omit top-level `planId` in the current conversation unless the wake or `get_active_plan` gave you the actual plan id, and never pass a plan item id as `planId`. If a plan tool says `Active plan not found`, `Plan item not found`, says the id is a plan item id, says `cannot have outcome.status` while the item is still waiting, or otherwise rejects your id/shape, call `get_active_plan` when needed, retry with the correct current `target`/`patch` or nested `item` shape, and keep working. After `get_active_plan` in that recovery path, target the current waiting/active validation item by the id or position in the snapshot and retry the plan mutation before any diagnostic summary. A failed plan-tool call is correction feedback, not a rescue blocker. A wake for terminal `completed_no_trades` on a first-cycle validation backtest is an action turn, not a report-only turn. `outcome.status="unsuccessful"` is plan-item audit evidence, not the external backtest status and not permission to stop. For a no-trade first-cycle result, complete the terminal validation attempt with `outcome.status="unsuccessful"` and source backtest evidence using `update_plan_item`, then before any final assistant answer add or continue explicit rescue items after it with `add_plan_item`, setting `parentItemId` to the unsuccessful validation item id when available, or use `replace_plan_items` to reconcile the whole visible list once. If `add_plan_item` rejects the rescue item because it lacks `parentItemId` or `dependsOnItemIds`, retry the same plan mutation with that explicit reference and then execute the rescue item; do not summarize the rejection as a blocker. If `update_plan_item` returns a warning that the plan has an unsuccessful item with no explicit follow-up, your next model action must be `add_plan_item`, `replace_plan_items`, or a blocker/cancel plan tool, not assistant prose. If a plan tool result says a rescue item is now `in_progress`, your next assistant event must be a tool call for that item, such as `get_code`, `get_file`, a file-edit tool, a docs/artifact tool needed for the edit, or a plan tool marking a real blocker; do not emit status prose first. A successful `add_plan_item` that creates an `in_progress` rescue row is the start of execution, not an allowed stopping point. Set the current rescue item `in_progress`, inspect the saved code and available backtest evidence, create a normal corrected revision when the cause is fixable, call `start_backtest` over the same first-test window (or the correct longer window when the earlier run was too short), and mark that new validation item `waiting_for_external_event`. If a terminal wake says `backtestStatus`/`status` is `completed` and `tradeCountStatus="counted"` with `tradeCount` greater than zero, that satisfies first-cycle filled-trade validation ONLY when the fills also match the user's stated trading intent and are not catastrophic. Treat absurd frequency versus stated daily/position intent, destroyed equity / extreme return collapse, or an `outcomeQuality` failure marker as failed outcome quality: continue repair and start a verification backtest instead of declaring victory. A merely modest negative return does not by itself invalidate an otherwise intent-matching first-cycle smoke. Explicit user performance thresholds such as CAGR, total return, Sharpe, or max drawdown still force continued metric-target repair. Filled trades are necessary, not sufficient. If the current plan still shows a stale `in_progress` rescue/edit item, reconcile it with the delivered successful backtest evidence: mark the relevant rescue/validation item completed with `outcome.status="satisfied"`, then call `complete_plan` before assistant prose. Do not edit files or start another backtest after a completed filled-trade wake solely because the old current plan item is still in progress. Do not use `update_plan_items` to update the same plan item twice in one call. Do not call `complete_plan` while the latest validation attempt has `outcome.status="unsuccessful"` or `outcome.status="partial"` and no later completed follow-up item references it. Never treat `outcome.status="unsuccessful"` as the final rescue state for fixable first-cycle work; it is audit evidence for one failed attempt, and the next action is rescue work unless a real blocker, user stop, or attempt budget applies. A final assistant answer after only reporting the no-trade metrics, after only marking `outcome.status="unsuccessful"`, or after only creating an `in_progress` rescue item is forbidden for active first-cycle rescue.

Avoid preventable discovery failures on terminal wakes. `list_backtests` has no
single-backtest `id` argument: call it with the strategy id and match the exact
returned backtest id, or use `backtest_status` for an exact id. Treat
hook identifiers as opaque. Do not call UUID-only backtest tools with a non-UUID hook identifier. If a hook uses a synthetic or legacy non-UUID identifier and `list_backtests` returns no exact persisted row, use the factual terminal hook evidence and the saved revision instead of probing `get_backtest_logs`, `backtest_status`, or artifact tools with an incompatible id. Treat
optional files according to the saved-file evidence workflow above. When the active
plan snapshot already contains one or more completed unsuccessful or partial
attempts plus later unresolved rows, prefer one `replace_plan_items` call that
preserves existing ids, resolves the current row, and adds the fully linked
follow-up. Do not probe `add_plan_item` with one parent id at a time when the
snapshot already shows the complete dependency set and progression order.
Never set the current item to waiting and then append another waiting item.
When a new user decision becomes necessary, resolve the current item as partial
and append the linked waiting follow-up in one `replace_plan_items` call.
After `get_active_plan` returns the authoritative snapshot. Do not manually copy
a plan item id into `update_plan_item` or `update_plan_items` for a multi-row
transition. Use one `replace_plan_items` call with the exact ids from that
snapshot, preserving every visible row and changing only the intended states.
Do not call `add_plan_item`, `update_plan_item`, or `update_plan_items` first in
this user-decision transition. Once inspection establishes that approval is
required, the first plan mutation after that inspection must be exactly one
`replace_plan_items` call. Do not call `add_plan_item` at all for that
transition, including as a probe with one unresolved parent and then another.
The replacement must preserve every visible item id, resolve the current item
as partial, and add one waiting follow-up whose `dependsOnItemIds` contains
every unsuccessful or partial attempt id already shown by the active-plan
snapshot.
If the snapshot already has a later unresolved item, do not append a new item
behind it. Instead, reuse the earliest existing unresolved item as the waiting
approval item, preserve its id, update its label and completion criteria to the
exact user decision, and leave any later items pending. Never place a waiting
approval row after an earlier pending validation row.


## Provider and data-source prerequisite failures

For a provider/gateway error or a `data_source_required` start result, load
`references/provider-and-prerequisite-evidence.md` before deciding the cause
or next action. Preserve the causal evidence, selected model/settings and
returned setup alternatives; a blocked prerequisite is not a completed run.

Duplicate-delivery override: a notice that the same terminal hook or external
event was already delivered and must not be duplicated is not a new rescue
authorization or a new terminal outcome. Treat an explicit "duplicate",
"already delivered", "do not rerun", or "do not duplicate the rescue" message
as a user stop for replaying that event. Do not inspect code, edit files, create
a replacement rescue plan, or call `start_backtest` from that duplicate notice.
You may read the current plan or exact backtest list only when needed to confirm
that no new run was created, then answer briefly that no duplicate action was
taken. This duplicate-delivery override takes precedence over the mandatory
repair-mode rules below.

Rules review rule: a terminal wake contains factual backtest state only. When the exact revision has active `rules.json` Rules, load `strategy-rules`, independently inspect the exact revision and per-Rule backtest evidence, and commit the completed evidence matrix with `commit_backtest_rules_review`. That tool stores the conclusion only. It does not analyze Rules. There is no separate auditor and no precomputed wake verdict. If the review fails, repair Python without weakening the Rule and call `start_backtest` again inside the same five-attempt budget. If it passes, do not make cosmetic repair rewrites. A missing file, empty ledger, or no active Rules means there is no Rules review to run. Rules compliance and first-build filled-trade readiness remain separate outcomes.

Raw completed rule: do not treat the raw manager word `completed` as first-cycle success by itself. Success requires terminal completion plus at least one real filled trade, or a stricter user-specified performance target if one exists. Raw `completed` with `tradeCount=0`, `resultClassification="no_trades"`, `firstCycleOutcome="no_trades"`, or UI/API status `completed_no_trades` is first-cycle repair mode until a filled-trade success, real blocker, user stop, or attempt budget applies.

Timeout override: a `terminated_timeout`, `timed_out` / timed-out run, `failureCategory=timeout`, or `tradeCountStatus=not_applicable_timeout` is NEVER "completed with no trades", even if the wake includes `tradeCount=0` or a no-trade classification. Narrate a timeout / platform-infrastructure failure. Prefer hosted runtime logs/logs first, subject to the hook queryability rules above. Do not enter the no-trade rule-loosening or zero-trade rescue sequence unless the run truly completed: `completed_no_trades`, or raw `completed` with `tradeCountStatus="counted"` and `tradeCount=0`, with no timeout evidence. Timeout evidence takes precedence over zero counts and no-trade labels. Preserve strategy rules and code unless logs establish a concrete, intent-preserving technical repair; a timeout alone does not justify a strategy edit. This override takes precedence over the rescue edit/rerun sequence below.



The shared guide continues in the ordered resources below. Load the relevant continuation; these are complete source sections, not summaries.

- Part 2: `references/shared-guide-02.md`
- Part 3: `references/shared-guide-03.md`
