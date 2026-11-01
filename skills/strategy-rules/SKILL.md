---
visibility: public
name: strategy-rules
public-name: strategy-rules
title: "Strategy Rules and Backtest Evidence"
description: Use when durable strategy intent is added, changed, removed, synchronized to Python, or reviewed against an exact backtest before repair or deployment.
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Strategy Rules

Choose the semantic change before rewriting `rules.json`:

| Requested change | Smallest ledger edit |
| --- | --- |
| Add a compatible requirement | Append one active Rule. Carry every existing Rule object, including its complete interpretation, forward unchanged. |
| Replace a requirement | Change only that requirement in the matching Rule; retain every other accepted requirement in its active interpretation and record the previous complete interpretation in history. |
| Remove a requirement | Disable/delete the removed Rule, preserving its provenance and history. |

An existing compound mandate is not permission to summarize, split or normalize
it during a bounded edit. Construct the complete valid JSON from the latest
`get_file` readback and use `replace_file` with that edit handle. Check the final
active interpretations against that original readback, not against a shortened
paraphrase in the proposed edit. Original quotes and history remain provenance;
they do not replace missing active requirements.
Do not splice JSON object fragments or unescaped prose with a patch; preserve
the existing structural validation and the complete valid ledger.


This skill owns the conversational Agent's Rules work. There is no separate
Rules auditor.

For a queryable terminal run with active Rules, complete and commit that run's
review BEFORE any Python repair or new backtest. This order applies to `pass`,
`fail` and `unknown`, including a compliant run with no fills. Keep the exact
old backtest/revision review separate from the later repaired revision's
validation review. Finish the visible review step with a successful
`commit_backtest_rules_review` call before activating or executing the edit
step; recording a passing review after saving the repair is out of order.

## Route here

Load this skill when the user states durable strategy behavior, asks to update
Python to match Rules, asks whether a backtest obeyed Rules, receives a terminal
backtest wake for a revision with active Rules, or asks to validate a revision
before deployment.

Manual edits made in the Rules tab are already saved by React and Node. Never
re-save them merely because they changed. A manual save must not start an Agent
run. When the Rules tab invokes the explicit Python synchronization action,
then this Agent owns the code change, backtest, review, and repair loop.

## Plain-English ledger

In the revision model, saving `rules.json` creates a new immutable revision just
like saving Python. After a Rules-file write succeeds, every readback, plan
update, validation, and `start_backtest` must use the revision id returned by that Rules-file write. Never reuse the earlier Python-write revision merely
because `main.py` content did not change in the Rules save.

`rules.json` is durable user intent. Keep one independently editable Rule per
requirement with a short title, active/disabled/deleted status, the user's quote,
a faithful interpretation, provenance, and edit history. Preserve exact symbols,
numbers, scope, exceptions, and cadence. Never put code identifiers, verdicts,
fill counts, audit objects, or evidence into `rules.json`.

Preserve the difference between an allocation target and a hard risk ceiling.
"Hold/invest X%" normally defines a target at the stated decision cadence;
"at most", "never exceed", and an explicit exposure limit define a ceiling.
Disclose a material interpretation without silently converting one into the
other. Keep the signal observation, sizing valuation, fill, and later portfolio
mark distinct; a completed-close signal does not identify the next fill price.

A request to "remember", "save", or "make lasting" a rule for this strategy
means persist that strategy-scoped intent in `rules.json`. Do not call general memory tools
such as `remember(kind="preference")`, `remember(kind="strategy_outcome")`, or
`remember(kind="fact")` for strategy Rules unless the user separately asks to save a
personal preference or cross-strategy historical fact.

Every newly created ledger must include the top-level schema `version` before
the first `create_file` call. Do not use a failed create as schema discovery.
Every Rule object requires a non-empty string `id` field, `status`, and
`interpretation`. The persisted ledger uses
`title`, `raw_quote`, `source`, and `edit_history` for readable intent and
provenance. Use those existing field names when authoring a Rule. Preserve an
existing valid ledger's optional fields and shape; a bounded edit does not
authorize rebuilding it. Keep the original `raw_quote` as provenance and append
the new request and previous interpretation to `edit_history` when intent changes.
Do not substitute `ruleId` for `id`; `ruleId` belongs to review/audit result
payloads, not the persisted `rules.json` Rule schema.
When the user removes or relaxes a durable constraint, do not rewrite that same
Rule as an active inverse. Mark the old Rule `disabled` or `deleted`, append an
edit-history entry that records the user's change and its provenance, and add a
new active Rule only when the remaining intent actually establishes one. This
preserves history without leaving the removed restriction active.

When the user changes strategy behavior in chat, read `rules.json` plus the
relevant executable files. For a replacement or removal, update the closest semantic Rule and its history. For a broad legacy mandate, append a separate active Rule for an additive condition when there is no conflict; do not replace the entire mandate with a shorter summary. Preserve every unrelated accepted requirement, including the starting balance and validation window. Update executable behavior when the strategy is Python-based, save the necessary files into the final coherent revision, and read both files back. Do not create contradictory active Rules.
Do not backfill Rules from old code when no current user statement establishes
durable intent.

An instrument, indicator period, exposure, or schedule change is lasting
strategy behavior even when its executable edit is one line. Reconcile the
matching active Rule's interpretation with that requested change, preserving
unrelated requirements, Rule ids, original quotes, and history. "Leave everything
else the same" preserves those unrelated requirements; the changed requirement
must agree across the code and existing Rules. Finish the authorized file saves
sequentially, read back the final shared revision, and validate that revision.
The code-file readback alone does not complete this behavior change. A technical
repair that preserves trading intent still leaves the Rules meaning unchanged.

For a small structured JSON ledger, use `replace_file` with the complete valid
JSON derived from the latest successful readback. Change only the requested
intent and its corresponding history; preserve unrelated fields, Rule ids and
existing history. Check the complete object, including commas between sibling
fields, before writing. This is a structured document edit, not a sequence of
line removals. Do not perform a later cosmetic cleanup after the requested
change has been saved and verified; every extra write creates another revision
and another opportunity to damage valid intent.

### Additive ledger example

For a compatible addition, keep the existing object complete instead of
paraphrasing its interpretation. This neutral before/after illustrates shape;
use the actual accepted requirements and current request, not this wording.

Before:

~~~json
{"version": 1, "rules": [{"id": "mandate", "status": "active", "raw_quote": "Use the agreed universe and allocation. Exit on trend reversal. Validate with the agreed capital and dates.", "interpretation": "Use the agreed universe and allocation. Exit on trend reversal. Validate with the agreed capital and dates.", "source": {"kind": "user_chat"}}]}
~~~

After the user also requests a profit-target exit:

~~~json
{"version": 1, "rules": [{"id": "mandate", "status": "active", "raw_quote": "Use the agreed universe and allocation. Exit on trend reversal. Validate with the agreed capital and dates.", "interpretation": "Use the agreed universe and allocation. Exit on trend reversal. Validate with the agreed capital and dates.", "source": {"kind": "user_chat"}}, {"id": "additional_exit", "status": "active", "raw_quote": "Also exit at the profit target.", "interpretation": "Also exit at the profit target.", "source": {"kind": "user_chat"}}]}
~~~

A quote or edit-history copy does not preserve a requirement omitted from the
active interpretation. If a corrective save is rejected, compare its proposed
change with the actual final files. Refresh the handle and finish any missing
requested or preserved requirement before reporting completion; an earlier
successful save does not make a rejected correction unnecessary.

### Workflow boundaries

One-turn instructions such as no backtest or no deployment are workflow
boundaries for this request. Respect them without making them durable trading
Rules. Persist only behavior the user intends the strategy to retain.

Do not probe for a possibly missing `rules.json` with `get_file`. When the
current successful tool results have not already proved that `rules.json`
exists, call `list_files` once for the exact revision. Read the file only when
that returned inventory contains it. Otherwise create it with `create_file`.
A `list_files` result must arrive before it can justify a `get_file` call.
Never batch that existence check with `get_file`; parallel calls cannot use
inventory that has not returned yet.
A missing Rules ledger is a normal first-save state, not a reason to incur a
failed file-tool call.

Use each discovery tool's actual identifier schema. `list_files` accepts
`strategyId` and `revisionId`, not `aiStrategyId`. For the attached current
revision, prefer `list_files(revisionId=<exact revision id>)` or omit both ids
when active-context defaults are valid. Never send `aiStrategyId` to
`list_files`. `get_file` accepts `strategyId`, `revisionId`, and `path`, not
`aiStrategyId`. For an attached current revision, prefer the exact `path` plus
`revisionId`, or use active-context defaults when they are valid. Never send
`aiStrategyId` to `get_file`. For the current attached strategy, call
`list_backtests` with `scope="strategy"` and without either strategy identifier.
Node resolves the exact strategy from the scoped MCP token. Do not manually
copy `strategyId` or `aiStrategyId` from request context into this call. Copy
opaque identifiers only from a successful tool result when a later tool truly
requires them.

This skill is complete in `SKILL.md` and has no subordinate resources. Never
call `load_skill_resource` for `strategy-rules`, and never invent a resource
such as `references/rules-ledger.md`.

## Exact post-backtest review

When a repair needs basic order, position, price, or historical-bars API facts,
load `lumibot-api-reference` and use its advertised smallest reference. For
ordinary order submission that is `references/methods-properties.md`; do not load an invented `references/orders.md`.

For every terminal backtest with active Rules:

1. Read the exact backtest revision's `rules.json` and `main.py`. Retain their
   returned SHA-256 content digests. Use each file tool's actual schema. For
   `get_file`, pass `path` with the exact `revisionId` and omit strategy identity
   when active context resolves the attached strategy. If strategy identity is
   required, pass `strategyId`, never `aiStrategyId`.
2. Load `backtest-analysis` when that skill is available in this client;
   otherwise load the public `lumibot-backtesting` guide through the client's
   advertised skill tool. The evidence procedure below remains the same.
   Resolve the exact backtest id without substituting another run.
3. Build a private evidence plan before querying. For every active Rule, write
   down its exact behavioral meaning, relevant decision timestamps or trading
   opportunities, evidence that could prove compliance, evidence that could
   prove a contradiction, and other active Rules that may legitimately block
   or modify the expected action. Do not expose this private matrix as filler
   prose, but do use it to ensure every Rule is independently covered.
4. Discover the exact run's manifest once with
   `list_backtests(scope="strategy", includeArtifacts=true)` and omit
   `strategyId`, `aiStrategyId`, and `id` for the current attached strategy.
   Node resolves the token's exact strategy claim. Select the returned row whose
   id exactly equals the supplied backtest id. Never manually retype, shorten,
   or reconstruct an identifier. `list_backtests` does not accept
   a backtest `id` filter. For exact status without manifest discovery, use
   `backtest_status(backtestId=<backtestId>)`. Never guess standard artifact
   labels or treat a successful preview of `stats.csv`, `trades.csv`, or
   `indicators.csv` as proof that the Rule-specific artifacts are absent.
   Retrieve every relevant manifest label with `get_backtest_artifact` before
   querying it. The first `query_csv` call for an artifact must contain only the
   bounded sample query, such as `SELECT * FROM data LIMIT 5`. Wait for that
   tool result before composing any column-specific SQL. Do not batch schema
   discovery and column-specific queries in the same tool call. JSON-derived
   trade artifacts may expose exact nested names such as
   `"asset.asset_type"`, not a flattened `asset_type`; use the literal returned
   column name or omit an unnecessary column. Keep column sets separate for each artifact,
   including artifacts from the same backtest. Do not copy `identifier` from trade events into trades
   unless the trades artifact itself exposes that column. Carry a returned event/order key only
   when it exists in that exact schema; otherwise retain the timestamp, symbol,
   side, quantity and price as evidence without inventing an order identity.
   In SQL, use the exact quoted
   identifier `"asset.asset_type"` or omit the column. An unquoted
   `asset.asset_type` is parsed as a table reference and a flattened
   `asset_type` does not exist. Never guess a convenience column name.
   Use this minimal filled-trade query shape only when its columns exist in
   that artifact:
   `SELECT time, symbol, side, status, price, filled_quantity FROM data WHERE lower(coalesce(status, '')) IN ('fill', 'filled') OR coalesce(try_cast(filled_quantity AS DOUBLE), 0) <> 0 ORDER BY time LIMIT 100`.
   The `try_cast` is required because an empty CSV can infer
   `filled_quantity` as text even when populated runs infer it as numeric.
   Do not add `asset.asset_type` to that query. It is unnecessary for fill
   linkage and is easy to misquote.
   Each `query_csv` call binds only its selected `artifactType` to `data`.
   Table aliases and CTEs still read that one artifact; they do not expose other
   artifacts from the run. Batch compatible bounded queries against the same
   artifact. To compare signals with positions or fills in a different artifact,
   query each artifact separately, then reconcile the returned rows using their
   actual timestamps and instrument identities. Do not join indicator columns
   with account columns inside a query whose `data` table contains only one of
   those schemas. If the separate evidence cannot establish the alignment,
   report the specific missing evidence instead of inventing a joined table.
   When a CSV cell contains structured JSON such as a positions list, inspect
   its returned shape and use the SQL engine's JSON functions. Do not extract
   nested quantities with an invented escaped regular expression. Keep absent,
   malformed, and empty values distinct; use nullable conversions when needed
   and report unusable evidence instead of converting it into a zero position.
   Preserve units when comparing quantities, values, and percentages. A share
   count divided by account dollars is not portfolio exposure. Establish the
   relevant asset, contemporaneous valuation price, contract multiplier when
   applicable, and account-value denominator. A cash-based account exposure
   calculation alone cannot isolate one instrument in a multi-asset account.
   Reuse the returned rows across Rules while keeping a separate
   verdict and evidence set for each Rule. Do not repeatedly download or query
   the same complete artifact once per Rule. Every available artifact used for
   a verdict must be queried. A preview is not row-level evidence.
5. Match evidence to the Rule's meaning:

   - Indicator and price conditions require point-in-time indicator values,
     position state, eligibility, blocking-Rule state, intended action, and the
     resulting order or fill. A trade row alone cannot prove an SMA, delta, or
     signal Rule. Independently verify the calculation and its input-bar timing
     from the original observed market data at representative signal boundaries.
     A logged value can repeat the strategy's own lag, smoothing or indexing bug;
     agreement between that value and its orders does not prove the requested
     indicator was implemented correctly. If the original bars or initialization
     are unavailable, record the precise evidence gap instead of asserting PASS.
   - Entry Rules must distinguish flat from already holding. "Buy while above"
     does not require duplicate purchases on every above-threshold bar unless
     the saved Rule explicitly says so.
   - Exit Rules require position-before and position-after evidence, not merely
     an eventual sell somewhere in the run.
   - Cadence Rules require grouping by the actual trading session and checking
     that the allowance rearms in the next session.
   - Risk Rules require point-in-time account value and maximum-loss or exposure
     evidence for each new position.
   - Allocation targets require the intended quantity, decision-time price and
     account value, existing/pending position, rounding, actual fills and costs.
     A later marked weight after a price gap is not alone proof of wrong sizing.
     Explain any difference from those actual observations; do not invent a
     numerical tolerance or excuse an unexplained deviation. An explicit hard
     ceiling still requires evidence that its limit was respected.
   - Option-selection Rules require the exact contracts, strikes, expirations,
     and point-in-time Greeks used at selection.
   - Multi-leg Rules require shared package identity for every entry and exit
     leg plus final position evidence proving no orphan leg remained.

6. Decide pass or fail only from affirmative evidence. Zero trades are not an
   automatic failure and are not an automatic pass. For example, a no-entry
   result can obey an entry condition when indicators and decision logs prove
   the condition never became true.
   An affirmative action Rule cannot pass from implementation code alone. If a
   Rule says to enter, exit, reset, size, or construct an order when a stated
   opportunity occurs, first prove whether that opportunity occurred and then
   prove the required runtime action. When the opportunity occurred and the
   action did not, the Rule fails unless point-in-time evidence proves that a
   different active Rule legitimately blocked it. Code evidence may explain the
   defect, but it cannot turn an unexecuted required action into a pass.
   Likewise, absence of orphan legs when no package was submitted is not
   evidence that an atomic package Rule passed. With no submitted package, use
   `unknown` when package identity or lifecycle telemetry is absent, or `fail`
   when the Rule required a package at an observed eligible opportunity.
   Never use "no contradictory evidence," an unexecuted branch, or the mere
   absence of a bad event as affirmative proof of a required behavior.
   A restriction Rule is different: it forbids something rather than requiring
   an action (trade only these symbols, never exceed a size, never trade
   outside a window). It passes when the complete order and trade artifacts
   show no violating event, including a run with zero filled trades. Cite the
   bounded query that returned zero violating rows, and check submitted or
   canceled orders too, not only fills. Use `unknown` only when those
   artifacts are missing or truncated.
7. If evidence is missing, continue gathering it. Do not call the review done
   with a vague "could not verify" result. Identify the exact missing artifact
   or field as a product defect if the runtime failed to preserve evidence. The
   review result is `unknown`, the product state is validation blocked, and the
   missing-telemetry contract must say exactly what observation was required.
   The only Rule verdict values are `pass`, `fail`, and `unknown`. A conditional
   Rule whose predicate did not apply, or whose action was legitimately blocked
   by another active Rule, is `pass` when point-in-time evidence proves that
   fact. Never invent `not_applicable`, `blocked`, or another verdict value.
8. Call `commit_backtest_rules_review` once with the exact backtest id,
   revision id, overall result, one verdict per active Rule, and typed evidence
   references. Normally omit `rulesDigest` and `codeDigest` from the commit call.
   Node derives and stores both exact digests from the immutable revision. The
   optional digest inputs are integrity assertions only, not fields to copy by
   hand. This tool only commits the analysis. It does not inspect or judge
   anything.
   For `pass` and `fail`, omit `missingTelemetry` when no observation is
   missing. For `unknown`, supply the required typed object for that Rule.
   Do not send null for an optional non-nullable field; omit absent values.

Typed evidence references must match the tool schema:

The only evidence source values are `artifact`, `log`, `metric`, and `code`.
Never invent `runtime`, `trade`, `indicator`, or another source value.

- `artifact`: real manifest label, the exact bounded SELECT, returned row count,
  and concrete detail;
- `log`: exact query, time range, matched-line count, and concrete detail;
- `metric`: real artifact label, metric name, observed value, and detail;
- `code`: `main.py` or `rules.json`, exact reviewed digest, line range, and
  detail.

Use exactly one of these shapes per evidence item, with no extra keys:

```json
{"source":"artifact","label":"indicators.csv","query":"SELECT ... FROM data","rowCount":3,"detail":"..."}
{"source":"log","query":"entry|exit","matchedLines":2,"startTime":"...","endTime":"...","detail":"..."}
{"source":"metric","label":"stats.csv","metric":"max_drawdown","observedValue":0.08,"detail":"..."}
{"source":"code","path":"rules.json","lines":"6-10","detail":"..."}
```

For artifact and metric evidence the key is `label`, matching
`get_backtest_artifact`. For log evidence, never add `label`. Code evidence
names only the path and lines; Node attaches the already-validated digest for
that exact file. Validate every evidence object against these four shapes before
the single commit call. Do not use a failed commit call as schema discovery.

Immediately before committing, compare the set of active Rule ids from
`rules.json` with the proposed verdict ids. There must be exactly one verdict
for every active Rule, with no duplicate or missing id. The `rules` array
length must equal the number of active Rule ids. Never append the complete
verdict array twice, even when reusing shared evidence across Rules.

Build the complete `rules` array before the tool call. Every array element must be a complete JSON object
containing `ruleId`, `verdict`, `summary`, and its complete `evidence` array.
Never compress, splice, or repair an object while serializing the tool arguments.
Before committing, verify that every evidence object has an explicit valid
`source` of `artifact`, `log`, `metric`, or `code`. Never substitute a label or
path into the `source` field.
Use at most three concise evidence references per Rule in the immutable commit.
Reuse the strongest shared queries and identify exact rows or timestamps in
their details instead of copying every observation into tool arguments. Never
emit a partial Rule object or a trailing fragment.
Do not make a partial commit call, do not move a
Rule id into an invented key, and do not call the tool until the complete plain
JSON payload has been checked against the active Rule ids and tool schema.

For each `unknown` Rule verdict, send its own `missingTelemetry.artifactOrField`
and `missingTelemetry.reason` inside that Rule object. Check every unknown Rule;
one Rule cannot borrow another Rule missingTelemetry. Never invent an artifact name or use prose such as
"trades look correct" as a reference.

The stored review is immutable evidence for that exact file pair. If the tool
rejects stale digests, reread the newest exact revision and never attach an old
review to changed Rules or code.

After a successful commit for a backtest, never call
`commit_backtest_rules_review` again for that same backtest. Retain the
successful tool result as the committed fact and move to repair or final
reporting. A second call with revised wording is an invalid attempt to replace
immutable evidence.

A Rules verdict covers the listed Rules, not every execution obligation. During
an active authorized build/edit validation, independently observed execution
defects still require repair even when every listed Rule says `pass`. In
particular, unrequested borrowing caused by spending a cash budget at an earlier
quote, missing required position protection, or duplicate completed exits are
implementation failures; a favorable return or truthful caveat does not finish
the build. Keep the committed review immutable, load `backtest-rescue`, repair
the causal owner, read back the saved revision and verify it within the existing
attempt allowance. Do not add or weaken customer Rules to change that verdict.
For an analysis-only request, explicit save-only instruction, user stop or
exhausted attempt allowance, report the evidence and respect that boundary.
Missing evidence alone and ordinary investment losses are not automatic edits.

A persisted failing review is not an allowed stopping point during an active
terminal validation wake. The wake continues the existing validation workflow;
it is not a read-only review request. Before any final assistant prose, load
`backtest-rescue`, create or continue the visible rescue plan, repair the
Python that caused the proven violation without weakening `rules.json`, read
back the new revision, call `start_backtest` on that revision, and record the
returned external wait. Stop after the review only when the user explicitly
stopped the workflow, a real unsupported capability or entitlement blocks the
repair, or the existing attempt budget is exhausted. Reporting the failed
review and offering to repair later is a failed wake turn.

Before saving that repair, trace the Rule through the existing state owner,
not just its numeric setting: eligibility, publication, actual execution,
terminal-without-execution, and the next session or restart. State what is
reserved, what has actually happened, and when each is released or counted.
A submission counter is not an execution limit. Even for a small constant edit,
load `strategy-building-core`, then its applicable complete resource before
replacing order-state logic: `references/entry-fill-allowance.py` for filled-entry
limits, `references/protective-position-example.py` for position protection and
retained exits, or `references/rebalance-example.py` for accepted allocations.
Read only the resource needed by this repair. Connect it to the saved strategy's
real callers and callbacks; preserve an equivalent working owner. Check those transitions
again in the final readback before starting verification. A constant-only fix
is sufficient only when the preserved state transitions already enforce the
requested behavior. Missing live interleaving evidence limits the validation
claim; it does not justify leaving a known implementation defect unfixed.

For the specific transition from a committed failing Rules review into repair,
do not use `update_plan_items` to complete the reviewed item and activate the
repair item. Use one `replace_plan_items` call that preserves the existing item
ids and full visible list, records the failed review outcome, and makes exactly
one repair item current. This avoids the locked-current-item batch boundary.
Always commit the failing review before any Python file mutation. The failure
evidence must remain tied to the unmodified failing revision. Only after that
immutable commit succeeds may repair create a new Python revision and start a
new backtest.

Choose the file mutation from the actual change size before calling it. A
whole-file or substantial rewrite of a short placeholder strategy must use
`replace_file` with the latest `get_file` edit handle. Use `patch_file` only
when every referenced line is inside the returned file and the edit is truly
localized. If the returned file has fewer than 40 lines and the repair replaces
most of its class body or adds a substantially longer implementation, use
`replace_file` instead of `patch_file`. Never use a failed oversized
`replace_range` as line-count discovery.
If an authorized file edit fails because its edit handle is stale or invalid,
reread the file for a fresh edit handle and retry once with the same intended
semantic change. Do not abandon the requested Rules update or switch to an
unrelated tool after a recoverable stale-handle error.

## Compliance and filled-trade readiness are separate

Rules compliance answers whether behavior matched active Rules. First-build
validation answers whether a terminal smoke run produced at least one real
filled trade. Report and repair them separately. A compliant zero-trade run can
still fail first-build readiness. A filled-trade run can still fail Rules.

When a Rule fails and repair is authorized, load `backtest-rescue`, fix Python
without weakening the Rule, create a new revision, run the next validation
backtest within the existing attempt budget, and review the new exact revision
again. Do not edit Rules to manufacture a pass.

After every successful file mutation, use its returned new `revisionId` for the
next read or mutation. Read the new revision before a second edit and never
reuse the preceding revision or edit handle. A later `rules.json` save is the
newest whole-strategy revision, even when `main.py` was saved immediately
before it. Start the backtest from that Rules write's returned revision. For a
multi-row plan transition after these writes, refresh the active plan and use
one `replace_plan_items` call instead of `update_plan_items`.

## Strategy modes

For Python strategies, manual Rule saves mark code out of sync but do not alter
Python. Only the explicit synchronization action or a direct chat instruction
authorizes the Agent to update code. After synchronization, run and review a
backtest before declaring the revision aligned.

For AI-powered strategies, the trading agents consume the exact Rules ledger at
runtime. There is no Python synchronization action. Rules still require an
evidence-backed post-backtest review and a pre-deployment review tied to the
exact digests.

Historical revisions are evidence, not implicit branch points. Never edit a
historical revision in place. Use the product's explicit per-Rule copy action or
an explicit restore/copy operation to create a new latest revision.
