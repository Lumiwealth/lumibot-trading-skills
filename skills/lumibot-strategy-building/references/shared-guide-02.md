> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

## Independent preparation reads

Use the returned `files` manifest as current existence evidence after successful
`create_strategy`; do not rediscover advertised starter paths. Read known files
from the same immutable revision together, including `main.py` and
`requirements.txt` when both are needed. Batch independent skill/reference reads
once their names and prerequisites are established. Use `list_files` for missing
or stale discovery; do not guess an optional `rules.json` or treat an earlier
manifest as evidence for a later revision.
A file is known only when this revision's `create_strategy` or `list_files`
result lists it. For an existing strategy without such a manifest, call
`list_files` alone first and read only paths it returns; do not send `get_file`
for an assumed path in the same batch. Before `create_strategy` returns there is
no strategy, so do not call `list_files` or `get_file` for it.

The existing Rules and visible-plan contracts below still apply unchanged. This
preparation step does not require replacing a plan or probing for a Rules file.
Never batch a write with its readback or execution. Each mutation must still be
read back from its new revision before another mutation, and validation must use
the newest saved revision with every required readiness check intact.

CRITICAL ACTION CONTRACT:
- Durable provider-retry checkpoint: if the current turn retries a provider/model connection failure and durable context plus the existing plan say that the workspace and runnable revision were saved before the failure while first-smoke validation is the next incomplete item, this is a run-only continuation. Preserve the saved revision, call `start_backtest` on that newest revision over the first-test window, and record the returned external wait on the existing plan. Do not replay `create_strategy` or file edits merely because this is still the first build, and do not reinterpret the saved revision as a neutral starter after the plan recorded the implementation as completed. A file edit is justified only by concrete saved-code, backtest, log, or tool-error evidence of a defect; an incomplete first-cycle validation status is not code-defect evidence. If the durable facts conflict, inspect them and continue from the first incomplete checkpoint without duplicating external work.
- When current context attaches a saved strategy/revision with `workspaceStatus="neutral_starter"`, that attached neutral starter is already the strategy workspace for this build, so do not call `create_strategy` again. The same applies when the context attaches a strategy with `workflowContext.firstCycle=true` (target `first_completed_filled_trade_backtest`): that attached strategy is the workspace BotSpot created for this build, so skip `create_strategy` and build into it. Build in the attached workspace with `get_file` -> `replace_file` -> `get_file`, using the attached ids and the new revision returned by the edit. Create or continue the visible plan around those actions, then start validation only after readback proves the starter was replaced by the complete user strategy.
- If the current context already has an attached saved strategy and the user asks to update, edit, fix, refine, or change "this", "attached", "current", or "saved" strategy, do not call `create_strategy`. Read the attached strategy's current file with `get_file`, edit that file, save a new revision, and read back the saved revision.
- "Update the attached saved strategy so it buys/sells..." is not a first-build request. Even if the requested edit is simple, stay on the attached strategy/revision and use `get_file` -> `patch_file`/`replace_file` -> `get_file`. After loading this skill for that attached-edit branch, the next domain tool must be `get_file` unless a real file-access blocker appears. Do not call `create_plan`, `web_search`, `create_strategy`, `list_files`, or first-build market research first. A tool sequence of `skills get` -> `create_plan` or `skills get` -> `web_search` for an attached edit is invalid. A new workspace is valid only when the current user explicitly asks for a new/separate strategy.
- If the current context already has an attached saved strategy/revision and the user only asks to start/run/backtest that current/latest/attached revision, this is a run-only turn. Do not create a plan, research, call `create_strategy`, or edit files just because there is no prior successful filled-trade backtest or because the user says "first smoke". Call `start_backtest` on the attached revision with the requested window, or the first-test window from `backtest-rescue` when none was requested, then record the returned external wait. The first-cycle rescue loop begins after the terminal hook if the run fails or completes with no trades.
- If the user states a durable preference such as "do not automatically run backtests" in the same turn as a build/edit/backtest task, `remember(kind="preference")` is only the preference-recording side effect. It is not task completion. After remembering the preference, continue the requested build/edit/backtest workflow unless the preference specifically blocks the current automatic backtest.
- For first-builds without a prior successful filled-trade backtest, the build is not complete until a real smoke `start_backtest` has been started on the newest saved revision, unless the user explicitly disabled automatic backtests or a real blocker is recorded.
- If the user disables automatic backtests during a first build, still build, save, and read back the strategy code. Then update the visible validation plan item after the readback to `waiting`/blocked-on-user with `waitReason=waiting_for_user` and clear evidence that validation is waiting for an explicit user backtest request. The immediate next tool action after the saved-code readback must be that plan update. Do this before final-answering. Do not call `start_backtest` or `complete_plan` in that automatic-disabled branch.
- If the user explicitly asks to backtest in the current turn, that current request overrides a durable no-auto-backtest preference for that run. If the requested run fails, rescue and rerun are still authorized as part of fulfilling the requested backtest. When you answer, make clear that the run happened because the user asked now and that future automatic backtests remain disabled unless they ask again.
- For ordinary edits after a prior successful filled-trade backtest, do not auto-backtest unless the current user turn explicitly asks for a backtest, validation, rescue, or metric loop.
- If the user asks only to run/backtest the latest/current saved revision, do not create a new strategy, create a plan, edit, or research just to satisfy the request. Use the latest known revision id, call `start_backtest` with the requested window, and record the returned external wait in the visible plan when a plan exists.
- For explicit edit-and-backtest requests, a saved edit/readback is not completion. After the file edit returns a new revision id, call `start_backtest` with that newest revision id. If `start_backtest` returns `action="backtest_failed_to_start"`, `status="failed"`, `externalWaitId=null`, or no `agentRunStatus="waiting_on_external"`, that is immediate repair feedback, not a waiting external event: do not call `record_external_wait_in_plan`, do not final-answer, and repair/read back/retry if the error is fixable. Only after `start_backtest` returns a real external wait should you record the external wait in the visible plan. If `record_external_wait_in_plan` is visible, it is the canonical required next action for that post-start wait: pass only the returned `externalWaitId` and the plan targets or new waiting item. Optional plan target fields must be omitted when unused, never sent as null; when provided, copy the complete target discriminator object from the current plan. The stored wait owns the backtest/revision identity; omit optional duplicate identity assertions. Prefer `record_external_wait_in_plan` when visible; use `replace_plan_items` or update/add plan items only when that helper is unavailable or has rejected and you are correcting the visible plan.
- For explicit metric-target loops such as "keep editing and backtesting until max drawdown is below 20%", each loop iteration is incomplete until you save/read back one bounded plausible edit, call `start_backtest` on the newest revision in the same turn, and either record the returned real external wait in the visible plan or continue repair if the start failed. Prefer `record_external_wait_in_plan` only for post-start results that include a real `externalWaitId`. When an external-event hook reports that the latest run still misses the metric target and budget remains, plan updates or metric summaries are not completion; the next actions must be code/result evidence, one risk-reduction edit, saved-code readback, a fresh `start_backtest`, and external-wait recording unless a real blocker/user stop/budget exhaustion is recorded. Do not poll `backtest_status` or `list_backtests` before the next edit/start to decide whether the hook is real; a queued/running/waiting status for the hook backtest is stale for this continuation. Do not final-answer after only editing/readback or after only updating the plan while the target is still unmet and backtest budget remains.
- For metric-target terminal hooks, load `backtest-rescue` when visible. A plan item saying "next pass" or "continue optimization" is not the next pass. Execute the next pass in the same turn: inspect code, edit, read back, call `start_backtest`, and record the wait.
- After any edit that returns a new revision in an edit-and-backtest or metric-target loop, the old hook backtest id and old hook external wait id cannot validate the new revision. The only valid wait for the new revision is from a fresh `start_backtest` called after the edit with that newest revision id. If you have not called that tool after the edit, do not update the plan or final answer as if a fresh validation run exists.
- If the user gives an explicit backtest duration such as 30 days, one month, or one year, pass that requested window to `start_backtest`. A duration phrase attached to "backtest" is an execution window, not a request to edit `sleeptime`, lookback, cadence, indicators, or strategy code unless the user separately asks for a code change. Do not silently use the default first-test window instead, and do not summarize a selected prior seven-day run as if it satisfied the new request. For edit-plus-duration requests, save/read back the edit first, then start the requested-duration backtest from that edited revision.
- Stock/ETF/futures order placement must use the supported LumiBot path: `order = self.create_order(asset, quantity, "buy" or "sell")` followed by `self.submit_order(order)`. Do not use unsupported convenience calls such as executable `self.buy(...)` or `self.sell(...)`, even for small edits, simple examples, or one-share smoke strategies. After editing buy/sell behavior and reading the saved code back, audit the readback for executable `self.buy(` or `self.sell(`. If either remains in executable strategy logic, immediately patch the same attached file again to replace it with `create_order`/`submit_order`, then read back again before final prose.

This skill exists because the old `generate_strategy` and `refine_strategy` prompts had important shared LumiBot guidance that must not be lost when the agent creates a neutral workspace and edits files directly. The direct-edit flow is still agent-native: create a plan, research recent market context when a first smoke will run, create a neutral strategy workspace, read the saved files, edit the files, save normal immutable revisions, and run/rescue real backtests.

Do not use this skill as a hidden router or a deterministic code mutator. It is model-visible guidance for authoring good strategy code.

If this skill was loaded for a current user message that is only "test",
"ping", "testing", a greeting, or another no-op connectivity check, do not call
plan, file, strategy, research, or backtest tools. Answer briefly in plain
language.

Before writing or replacing strategy code:

DECISION-OWNER GATE: First decide whether the user asked for automation at all.
If they only ask how to start trading, what to do first, to understand their
account, or to research/review a trade, help directly in BotSpot: offer account
understanding, research/charting, and broker connection when relevant. Do not
create a strategy merely because automation is available.

When automation is requested, separate the cadence of deterministic polling,
broker/order reconciliation, and time-window triggers from the cadence of an
intelligent trading decision. Then choose ownership in this order:

1. Ordinary hourly or daily intelligent decisions default to AI ownership.
2. When decisions must react within seconds or normally occur more often than
   hourly, recommend Python ownership or a hybrid because full AI calls are
   slower and more expensive. One hour is guidance, not a hard validation rule,
   entitlement boundary, or blocker.
3. When polling must be frequent but intelligent decisions are slower, use a
   hybrid: Python polls/reconciles at the fast cadence and invokes the AI team
   only at the intended decision windows.
4. Respect an explicit choice of Python, hybrid, or frequent AI. After one clear
   cost/latency warning, a user who accepts frequent AI may proceed without
   repeated confirmation, a hidden block, or silent conversion to Python.
5. Preserve an existing Python strategy unless the user chooses conversion.

For an existing-strategy edit that also explicitly requests a backtest, finish
the narrow edit and saved-file readback first. Before `start_backtest`, inspect
the active plan once when no current plan is already present in context. If no
active plan exists, call `create_plan` with only schema-valid completed,
in-progress, or pending rows; include the completed edit/readback row and a
pending validation row. Then call `start_backtest` and record its returned wait
with `record_external_wait_in_plan`. Never start the backtest first and then put
`externalWaitId`, `externalId`, `waitReason`, or other external-wait-only fields
inside a later `create_plan` call.

For AI-owned or hybrid work, load `lumibot-ai-agents` before code work. Exact
indicators, thresholds, quantities, and risk rules do not imply Python
ownership; they become active Rules consumed by the AI-owned portion. Cadence
and latency requirements do affect the recommendation as described above.
`lumibot-api-reference`, indicator/charting guidance, and resource reads do not
substitute for this focused skill load.



AI-OWNED NEW-BUILD DEFAULT: For ordinary automation whose intelligent decision
cadence is hourly or slower and which does not require fast reaction, including
exact rules and requests that never mention AI, load `lumibot-ai-agents` and
follow its AI-owned contract. For faster decisions or latency-sensitive work,
recommend Python or hybrid as described by the decision-owner gate; a confirmed
frequent-AI choice remains allowed. Explicit Python, an existing Python
strategy, or a user-chosen hybrid retains its chosen architecture. This
override also applies to options and multi-leg requests, including AI iron
condors and credit spreads, and to AI-only ORB or VWAP requests. Do not load
`options-strategies`, and do not apply this skill's deterministic
OptionsHelper, option-selection, order-construction, chart-instrumentation, or
first-cycle simplification guidance to the generated strategy. After loading
`lumibot-ai-agents`, also load its `references/ai-only-scaffolds.md` and
`references/ai-only-order-verification.md` when the request is an AI-only iron
condor, credit spread, ORB, VWAP, or another scaffolded AI-only pattern. The
saved Python may contain normal imports, the strategy class, cadence, agent
creation, agent invocation, and the standard harness. The complete
natural-language system prompt must contain only the strategy-specific policy
and must leave market and account retrieval, option-chain inspection, contract
selection, Greeks and liquidity checks, risk sizing, order submission,
duplicate-exposure prevention, order-status verification, and position
management to the trading-enabled agent. Do not duplicate generic stock,
options, or order mechanics in the saved prompt. Current LumiBot exposes
`stock-trading` and `options-trading` through its runtime `SkillToolset`; the
agent loads the relevant skill after the asset becomes relevant, including
when a broad mandate chooses an option at runtime. Pass the canonical sibling
`rules.json` to `self.agents.create(..., rules_path=...)` so active rules are
reloaded before every agent call. Use
deterministic options guidance only when the user chooses Python-owned
execution or explicitly requests a hybrid Python and AI design. Exact rules
alone are not an architecture choice.

1. Read the user's actual request and preserve the strategy intent as closely as possible. Explicit design constraints are binding: if the user asks for a fully unrestricted trader, rejects risk caps/stop-losses, or otherwise states risk/universe/sizing posture, encode that mandate instead of arguing for safer defaults.
2. For first builds that will immediately run a first backtest, research recent market conditions first using two to four focused web searches unless the user forbids web access.
3. Load the mandatory LumiBot reference skill before code edits or first-smoke validation: `lumibot-api-reference`. Then load exactly one smallest relevant resource and return to file work. For an ordinary strategy build, prefer the single resource that answers the concrete code-shape or API question; do not load notes/reminders or the full reference catalog as a baseline checklist. Load a second resource only when a different, specific unresolved API fact requires it.
4. Load the focused skill or reference that matches the request: `lumibot-indicators`, `options-strategies`, `lumibot-ai-agents`, asset references under `references/assets/`, pattern references under `references/patterns/`, or `references/scaffolds.md`.
   If the request asks for an AI trading team, investment committee, pod
   structure, or named-investor AI team, loading `lumibot-api-reference` alone
   is incomplete. Before writing strategy code or starting a backtest, call
   `skills get` with `skill_name="lumibot-ai-agents"`; a `skills reference get`
   call, including one that reads that skill's `SKILL.md`, does not satisfy this
   focused skill load. Then load its
   `references/ai-trading-teams.md` and
   `references/ai-trading-team-examples.md` resources before editing code.
5. Read the current saved files before editing. Do not assume the neutral starter already implements the requested strategy.
6. Use this skill plus the referenced LumiBot API, asset, pattern, and scaffold files as the source of truth for LumiBot code shape.

Runtime boundary: local runtime logs that show a local LumiBot API mismatch may
require `pip install --upgrade lumibot` before rewriting strategy code. Do not
rewrite a strategy just because the local package is old.

Mandatory reference-loading rule: if this skill is loaded for a strategy build, first-build rescue, or substantial direct strategy edit, the next skill-loading work must include `lumibot-api-reference` before code-writing tools or `start_backtest`. Load one specific `lumibot-api-reference` resource needed for the next implementation decision, then return to file work. For asset-class, pattern, or scaffold work, load this skill's one directly relevant `references/assets/*.md`, `references/patterns/*.md`, or `references/scaffolds.md` file. Add another focused skill or resource only for a separate requirement the first reference did not cover.

Never combine resource categories or path fragments. Copy one complete path
exactly as advertised by this skill. The general scaffold file is
`references/scaffolds.md`, never `references/patterns/scaffolds.md`. Pattern
resources are the separately advertised files under `references/patterns/`.

When the user has already supplied a fully specified historical rule whose
implementation must not vary with present market conditions, skip
current-market web search. In the visible first-build plan, mark the existing
research item `skipped` with that exact rationale and advance the workspace
item. Do not probe the research fixture and do not add a fallback plan item.

Authoring expectations:

- The saved revision must be real user-specific strategy code, not a cleaned prompt, shell, infographic, or placeholder.
- Keep the code complete and runnable with imports, class definition, parameters, lifecycle hooks, trading logic, and the standard main harness.
- Use documented LumiBot methods and entities from this skill bundle. Do not invent helper methods because they sound plausible.
- For chartable strategies, add visible chart instrumentation using `add_line`, `add_marker`, and `add_ohlc` when OHLC bars are available.
- Implement the user's rules exactly. Choose the first backtest window to fit the rules (see First test window in `backtest-rescue`); never reshape the rules so a short window trades, and never add fake fills, dummy orders, or backtest-only branches that bypass the user's real idea.
- If the first edit is incomplete, read the saved file again and edit again. Do not try to one-shot everything when a plan audit shows missing strategy fidelity, missing chart artifacts, or missing first-smoke tradeability.
- Every file edit creates a normal immutable revision. Use the newest revision returned by the file tool for the next file read or backtest.
- Strategy, AI strategy, revision, backtest, and plan item identifiers are
  opaque values. Copy them exactly from one successful tool result into the
  next call. Never retype, shorten, reconstruct, or alter even one character.
  Copy the literal identifier with no added punctuation, commas, labels, or whitespace.
  For file tools on the current attached workspace, omit both `strategyId` and `revisionId`
  when the tool supports conversation-scoped defaults. The server resolves the
  owned current revision; do not transcribe redundant UUIDs. Use the returned
  `editHandle` for edits that accept it, and verify the readback's returned
  revision matches the successful write. Explicit selectors are needed for a
  different strategy or a specific historical revision: copy the complete
  returned strategy/revision pair exactly. An edit advances the revision, not
  the strategy identity. Never reconstruct identifiers or combine their parts.
  For a newly created workspace, confirm `create_strategy` returned a
  `conversationUpdate` attaching that exact workspace before using defaults.
  If `conversationUpdate` is absent, use the exact returned new-workspace IDs
  even when an older workspace is still attached; never edit that older target.
  After a successful `get_file` readback proves the edited file and revision,
  do not add a redundant `list_files` call merely to reconfirm the same file.
- Every `replace_file` call must supply `path`, `editHandle`, and complete `content`
  as top-level arguments. Copy the exact path and latest handle from `get_file`;
  sending only content is an invalid call and saves no revision. For example,
  `{"path":"main.py","editHandle":"<exact returned handle>","content":"<complete saved source>"}`.
  Replace the example placeholders with the actual read handle and source.
  `patch_file` similarly requires the exact path, latest handle and operations.
- Copy the `skill_name` and `file_path` pair from the same loaded skill when
  calling `skills reference get`. A path advertised by one skill is not a resource
  of another skill; never reuse a previous path with a different skill name.

Plan expectations:

`update_plan_item` takes `target` and `patch`. Put `revisionId`, `status`,
`evidence`, and `outcome` inside `patch`, never beside it. For example:
`{"target":{"type":"position","position":3},"patch":{"status":"completed","revisionId":"<returned revision UUID>"}}`.
Copy the actual returned revision UUID; do not send the example placeholder.

For plan progress, use one ordered `update_plan_items` call to finish the current
row and start the next existing row. Use `update_plan_item` when only one row
changes. Target the exact one-based positions returned by `create_plan` or the
latest successful plan result; skipped rows retain their positions. Use an exact
returned item id only when the result omitted the position. Copy the returned
position rather than retyping an opaque UUID. Wait for the result
before another mutation. Never infer a target from completed domain actions.
Only one item may be active: new items default to pending while another item is
in progress. A child item does not create a second active-work lane.
A rejected plan mutation is not completed work. Read the returned current state,
correct the intended transition or arguments, and retry the required mutation
once before continuing. If it still fails, report the exact unresolved error;
do not silently continue as if the plan change succeeded.

Treat strategy, revision, backtest, AI-strategy, plan, order, and deployment
identifiers as copy-only values. Copy each complete value from one successful
tool result into the next call; never reconstruct it from memory or another
identifier. Do not issue multiple identifier-bearing file or revision calls in
the same assistant action. Make one call, verify its result, then make the next
call so every repeated identifier can be copied literally.

- A plan is a real agent work plan for complex tasks, not a UI decoration.
- Every plan item you create or add must include the exact field `completionCriteria`. This is a concise model-visible sentence that says what evidence makes that item done, such as a source link, revision id, backtest id, validated code condition, or user decision. Do not call `create_plan` or `add_plan_item` with label-only items. `add_plan_item` takes a nested `item` object, not legacy flat fields.
- When the visible plan ends at the current review item and the user asks to begin a new next step, first complete the current item and append that next step with `add_plan_item`, or reconcile both changes atomically with `replace_plan_items`. Do not target a nonexistent future position with an update tool, and do not execute the new domain action before the new plan item exists. After the item is present and in progress, execute its domain tool; a successful domain action does not substitute for the required visible plan transition.
- Update plan items explicitly with plan tools as work starts, completes, blocks, or changes. Do the update immediately after each major tool result instead of batching old progress at the end of the turn.
- Keep ordinary plan transitions sequential between domain actions. Use
  one ordered `update_plan_items` call to complete the current row with its
  outcome and start the next existing row. The final state must leave all earlier
  rows terminal and at most one row in_progress. Update each item only once in
  a batch, and wait for the result before another mutation. Never start a later
  row while leaving an earlier row unresolved. Use `replace_plan_items` only
  when the full visible list actually needs reconciliation.
- For a new first-build, group workspace creation, saved implementation and
  readback into one implementation item, followed by a launch item and a pending
  validation item. Include a research item when required. Each item's criteria
  must name its required evidence; file reads and metadata checks are actions
  inside these phases, not separate plan rows. Preserve an already-existing plan.
- Keep technical readback corrections inside the current implementation item.
  Repair the defect and verify the newest saved revision before completing that
  item; do not mark it partial just to append a new side repair row. A terminal
  failed backtest still needs its explicitly linked rescue follow-up.
- Do not rewrite an already-bound wait after a nonterminal status. The canonical
  helper already completed the launch row and set validation waiting. Leave that
  state unchanged and yield for the external event; do not send a second generic
  waiting update, mark validation in_progress, or add another wait row.
- Record partial research, unavailable sources, and limitations on the existing
  research item; do not append a completed documentation, evidence, or limitation row
  behind an unresolved earlier item merely to preserve that note.
- Do not call `add_plan_item` for a research fallback, research limitation,
  unavailable search source, partial search result, documentation note, or
  evidence note when the plan already contains a research item. Put that
  outcome on the existing research item, then advance the next existing item.
  A child row is still an added row and is invalid for this purpose.
- Do not add a plan row merely to record a research limitation or conservative fallback. Those are evidence on the existing research row; continue with the
  already-planned implementation row.
- If research returns no sources or a fixture-unavailable result, resolve the
  existing research row and advance the already-planned next row by position.
  Do not append a fallback child or side row such as "proceed despite
  unavailable research", even with a valid `parentItemId`; it duplicates the
  ordered plan and can violate current-item progression.
- For `replace_plan_items`, preserve existing items by their exact `itemId` and
  send only writable fields; always omit server-owned fields such as `position`, `createdAt`, and `updatedAt`.
  List order defines the replacement positions.
- If you create a plan and then discover that user input is truly required, update the current plan item to `waiting` with `waitReason=waiting_for_user` before asking the user. Include the exact missing decision in rationale/evidence, and do not leave the plan at 0/N or all pending while waiting for user input. If the blocker is a user no-auto-backtest preference, this waiting/blocker update happens only after the strategy code has been saved and read back; leave the plan in that waiting/blocked state and do not call `complete_plan`.
- Do not rely on file, strategy, skill, or backtest tools to advance plan state automatically.
- If an item is not complete, leave it pending or in progress. If the work changes, add, remove, skip, or block items honestly.
- When your own readback or audit finds a fixable defect in the code you just wrote,
  keep the existing implementation or audit item `in_progress`, correct the file,
  and read it back again under that same item. Do not mark an internally detected
  first-pass defect as `partial`, and do not append a correction item when the
  original implementation item already owns that work. A follow-up row is for a
  genuinely separate attempt after the original item is resolved, not an internal
  edit-and-readback loop.
- If a plan truly has multiple completed `partial` or `unsuccessful` attempts and
  requires a separate follow-up, use one `replace_plan_items` call with every
  unresolved attempt id in `dependsOnItemIds`. Preserve the existing ordered rows
  and resolve the progression boundary in that same replacement. Do not probe
  `add_plan_item` with one parent id at a time.
- A first-build plan should not be completed until the first smoke result has reached a terminal validated outcome, or the task is clearly blocked/cancelled for a reason other than a user choosing to delay paid validation. A no-auto-backtest preference is a waiting validation state, not a completed plan.

# First-Build Strategy Flow

The immediately preceding user request and clarification are already present
in the active conversation. Do not call `search_conversation_history` to
recover them during the same first-build workflow. Use the visible
conversation, loaded skills, and successful tool results.

Do not enter this first-build flow for attached/current/saved strategy edits. If the current request says "update/edit/fix/change the attached/current/saved strategy", return to the CRITICAL ACTION CONTRACT above and use the direct existing-file edit path.

Use `create_strategy` plus file tools for new BotSpot LumiBot strategies, then start the required first-cycle smoke backtest.

For substantial first-build work, create and maintain an active plan. The plan is the visible work plan for the user and the execution guide for the agent; it does not hide, enable, disable, or route tools. Use plan tools to keep the work current as you proceed. For any first-build that will run its first backtest, the plan must include a visible item before workspace/code work for researching recent market conditions. A typical first-build plan should cover: extracting the user's tradable intent and fidelity requirements, researching recent market conditions, creating the neutral strategy workspace, loading focused general skills, implementing the first real code pass, adding chart instrumentation when signals or trades are chartable, auditing the code against the request, starting the first backtest over the first-test window, and validating or rescuing the first backtest result. Starting the smoke and validating the smoke result should be separate plan items. Each item must include `completionCriteria`, for example: "Two to four focused recent-market searches are complete, source freshness is noted, and the build has a concise market-context takeaway plus concrete implementation implications." Update items as work starts and completes. If the work changes, add, remove, or mark plan items honestly instead of treating the original plan as fixed.

For any new first-build turn with no attached/current/saved strategy edit target, call `create_plan` before `create_strategy` or before the first file edit. Then call plan tools before or after every major build action so the visible plan does not stay stuck at 0/N while tools are running. Use `update_plan_item` for one item with a required `target` object and a `patch` object; target by id when available, otherwise copy the complete discriminator shape exactly: `target: { "type": "position", "position": N }`. The abbreviated shape `target: { "position": N }` is invalid because it omits the required `type` discriminator. Resolve the current row first and start the next row only after that success. This includes `add_plan_item`: while another row is `in_progress`, add the new row as `pending`, never `in_progress`. For no-trade rescue, update the failed validation item with `update_plan_item`, then add follow-up rescue work with `add_plan_item` using `parentItemId` to reference the failed validation item when available, or use `replace_plan_items` to reconcile the whole visible list once. Mark the current item `in_progress`, mark finished items `completed`, mark external waits as `waiting`, attach the latest `revisionId` plus generic external-wait evidence such as `externalKind="backtest"` and `externalId=<backtestId>` when a tool returns one, and keep exactly one current item active unless the task truly branches. After a domain tool returns a real async id and `record_external_wait_in_plan` is visible, that helper is the required canonical post-start path instead of hand-assembling a completed current row plus new waiting row. Use `replace_plan_items` only when you need to reconcile the whole visible list in one ordered update, the helper is unavailable, or the helper rejected and you are correcting current plan state. Call `complete_plan` only after the first smoke backtest has reached a valid terminal result with at least one filled trade, or a real blocker is reported with the concrete blocker item blocked/waiting. Do not call `complete_plan` while the latest validation item has `outcome.status="unsuccessful"` or `outcome.status="partial"` and no later completed follow-up item references it. Do not skip the plan just because the work feels short; strategy creation is always substantial enough for a user-visible plan.
For first-builds, the first tool call is `create_plan` before workspace creation or code edits.

When `record_external_wait_in_plan` is visible and the plan already contains a distinct future validation item after the current item, pass that exact future item id or position as `waitingItemTarget`. Never use the current item's id as `waitingItemTarget`. The helper must update the existing validation row to `waiting`; it must not append a duplicate validation row. When supplying a complete new `waitingItem`, omit `waitingItemTarget` so the helper appends that new row after the current item. After the final validation item is completed successfully, call `complete_plan` before the final assistant answer; do not leave a 5/5 plan active.

Never send multiple plan mutations in the same parallel tool batch. Plan item ordering and the single-active-item rule require one atomic multi-item mutation or sequential plan calls.

Never send two separate plan mutations in one model action. A single ordered
`update_plan_items` call may complete the current row and start the next row;
wait for that one result before another mutation. If market
research finishes with a partial outcome because a search source is
unavailable, record that partial outcome on the existing research item and
continue to the next existing item. Attach that existing next row to the exact research item with `parentItemId` or `dependsOnItemIds` when its partial outcome requires a follow-up; include that link in the same ordered transition. Changing status, evidence, or dependency links does not need a full-list replacement. Do not add a child plan item merely to restate a partial research outcome.

Use Top Agent-style task discipline: status/tool streams show activity, but only plan tools mutate the visible plan. Do not batch plan completions at the end of the turn. After `web_search` returns usable current-market context, immediately mark the research item `completed` with a concise market takeaway, source freshness, and concrete build implications before `create_strategy`. Research is not complete if the takeaway does not say how it affects the first implementation, such as symbol choice, filter strictness, option expiry/liquidity handling, volatility/risk gates, smoke-window expectations, or rescue diagnosis. If research remains `in_progress`, resolve it successfully before touching any later row. Before marking any later plan item `in_progress`, `waiting`, `completed`, or `blocked`, every earlier active item must already be resolved. After `create_strategy` returns the neutral workspace, inspect the current row's completionCriteria. If it covers implementation/readback, workspace creation is evidence inside that row, not completion: keep it in_progress until all required files are saved and read back. If workspace creation has its own separate row, complete that row and start the already-existing implementation row with one ordered batch. Never reopen a completed workspace row or replace the full plan merely to record creation progress. After a successful user-specific edit returns a new `revisionId`/version and any required chart/API audit is done, mark implementation `completed` with that revision evidence. After `start_backtest` returns a `backtestId` plus a real `externalWaitId`, prefer `record_external_wait_in_plan` to complete the start-smoke/current edit item and move the existing validation item to `waiting` with `waitReason=waiting_for_external_event`, `externalKind="backtest"`, the returned backtest id, `externalWaitId`, and `revisionId`. If that helper is unavailable, use sequential single-item updates for existing rows or `replace_plan_items` when a new waiting row must be appended.

For common first-build handoffs, use sequential `update_plan_item` calls for existing rows. After `create_strategy`, complete the workspace item, wait for success, then start implementation. After `start_backtest` returns a `backtestId`, use `record_external_wait_in_plan` when visible. The post-start plan mutation must mark the validation item `waiting` with `waitReason=waiting_for_external_event` and the same generic external-wait evidence before polling. Use `replace_plan_items` only if the whole visible list or a new follow-up row must be reconciled. Never run plan mutations concurrently.

Creating the plan is the beginning of the build, not the answer. Do not stop after `create_plan`, do not return a cleaned prompt, and do not ask the user to confirm again. After `create_plan` succeeds on a first-build request, mark the recent-market-context item `in_progress`, run two to four focused `web_search` queries unless the user forbids web access, mark that research item completed when you have usable context and build implications, and only then continue with `create_strategy`, focused skill loading, file reads, file edits, and the required first-cycle smoke backtest. Prefer one `web_search(queries=[...])` call for the standard multi-angle market pass when useful. One broad combined web query is not enough recent-market research. Use distinct query angles such as broad market/index regime, exact symbols/assets/sector, volatility/Fed/macro/scheduled events, and recent catalysts/news where applicable. A turn that creates only a plan and then replies in prose is incomplete.

