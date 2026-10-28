---
name: lumibot-api-reference
title: "LumiBot API Reference"
description: "Use for LumiBot strategy APIs, lifecycle hooks, orders, positions, entities, Asset construction, Bars/historical data, crypto/base/quote pairs, futures/forex/options entities, examples, notes/reminders, fast order management, slow basket scanners, batch bid/ask quotes, drift rebalancing, Perplexity helper, and general LumiBot method/property questions."
visibility: public
license: MIT
---
> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

For external clients, load guides with the BotSpot MCP `skills` tool (action=get, name=<skill>). Resource identifiers written as <skill>:references/<file> use name=<skill> and reference=references/<file>. Installed native clients can read the same local reference file. The following is shared authoring guidance; use the tools actually advertised by your client.

# LumiBot API Reference

For timed cancellation, broker-terminal reconciliation or late-fill questions,
first load `lumibot-api-reference:references/fast-order-management.md` with
`skills reference get(resource_key="lumibot-api-reference:references/fast-order-management.md")`.
When a complete timed entry/cancel/hedge pattern is requested, also load the
advertised `references/deadline-order-example.py` and give its complete code.
The guide establishes the framework contract; the example implements it. This
explicit guide-and-code pair is required even though the general rule below
prefers one smallest reference. An example alone does not replace that guide.

For a coherent refactor in a large file, group complete affected method-body
replacements in `patch_file`, using unique `def` context or verified line ranges
with `expectedOldText`. The scanner reference explains range ordering. A complete
`replace_file` is also valid. Include the reader AND every caller/signature
change. A helper-only revision does not optimize a scan. An ambiguous patch
saved nothing: change the edit mechanism, finish the save and read it back;
do not retry the same ambiguous assignment or stop the authorized repair.
Keep the batch reader's return type and every consumer consistent: `get_quotes`
returns a dictionary; the example wrapper's `.quotes` is a dictionary. Pass that
mapping to the pricing and pre-entry preparation helpers. A mapping does not
itself have a `.quotes` attribute. Trace both consumers in the final readback.



For a requested complete code pattern, use the advertised tested implementation
and retain its method bodies, callbacks, terminal reconciliation, exception
handling and bounded recovery. Completeness takes precedence over brevity when
omitting a helper can change order safety. Explain the supplied input hooks
separately; do not replace that implementation with a shorter newly invented
class. A narrow component question may show that component, and an authorized
saved-file repair preserves the existing entrypoint and trading policy. Replacing its broken lifecycle with the complete loaded helper in a strategy-owned file is permitted; retaining an unsafe abbreviated controller is not a narrower repair.
For a timed-order explanation, state both limits directly: `sleeptime` cannot
preempt a running `on_trading_iteration`, and broker cancellation-confirmation
latency cannot be guaranteed by strategy code.

Use this skill when a strategy needs LumiBot API semantics, lifecycle behavior,
orders, positions, entities, helpers, asset construction, historical data/Bars
semantics, market/data-provider behavior, or implementation examples that are
more specific than the core build workflow.

For authorized initial-budget compatibility repairs, follow the persistent
baseline guidance in `lumibot-strategy-building`. A current property definition does
not prove its backing value was available in the failing deployed lifecycle.

Use the conversation to distinguish a capability question from an accepted
implementation. When the user follows up on an already discussed scanner
optimization by asking you to perform it, finish the saved edit and readback in
this turn. Verifying the installed API is a prerequisite to that work, not a
substitute for it. Another explanation that batching is possible leaves the
accepted task undone. A standalone API question or explicit request for advice
without changes remains read-only.

For a new generic timed-entry/cancel/hedge pattern, load
`references/deadline-order-example.py` and include its complete tested lifecycle
implementation in the answer. Its exact advertised callable identity is
`skills reference get(resource_key="lumibot-api-reference:references/deadline-order-example.py")`.
Python examples are callable reference resources, not unavailable script files.
After the overview points to that implementation, load it before answering;
the overview's deadline arithmetic alone does not implement the requested pattern.
Do not claim a linked example is unavailable without attempting its advertised
resource key and receiving an actual access error. For a narrow hedge callback-versus-polling
component, load `references/hedge-operation-example.py`. That standalone
component is not the integration pattern for an existing shared hedge queue;
use the complete-method serialization in `order-operation-ownership.md` for
that queue, its preparation, continuation and completion owners instead.
Loading a resource does
not show the code to the user. Keep the actual reconciliation and completion
methods; asset/signal inputs can remain strategy-specific.

For an existing-file callback, polling or duplicate-hedge repair, also load
lumibot-strategy-building's `references/order-operation-ownership.md`. Trace every
caller into the shared fill initializer and protect its lookup/create/publication
and active-operation pointer with the same state owner before hedge submission.
Preserve the existing strategy's entry, quantity, replacement and next-cycle
policy; a lock on only one callback or the final submission is incomplete.

For a slow scanner or performance edit, choose from the actual saved causal path before selecting an implementation. An existing timed entry/cancel/hedge operation uses the complete lifecycle guide and implementation above, even when the request only says trading is slow. A scan-only optimization is incomplete while that operation still loses cancel/fill ownership or can duplicate a hedge. Preserve its prices and trading policy; do not make an optional pricing choice a prerequisite to the mechanical repair.

For a demonstrated acquisition-only bottleneck, load
`references/scanner-performance.md` and its complete bounded quote-reader example.
Treat that acquisition repair as one coherent refactor: batch the repeated option reads
AND remove unnecessary candidate-level account reads. A whole-scan cached order
list is not safe: retain each original symbol guard and fresh viable-decision
checks. When those are the measured bottlenecks, keep the original one-stock
quote read per symbol unchanged; do not add an unmeasured basket-wide stock
prefetch to the same repair. Inject acquired option quotes into existing pricing helpers;
do not bypass their bid/ask, fallback or eligibility branches with raw snapshot
access. Direct `get_quotes` can raise where singleton `get_quote` returned None,
so retain failure isolation for every newly batched asset type. Finish and audit
both demonstrated acquisition hot paths before answering. This focused resource is preferable to the long
deadline/hedging reference for acquisition-only work; the user's word "speed" never overrides a demonstrated timed-order lifecycle defect. Do not introduce quote batching, chain-cache policy or extra reference inspection into a lifecycle repair when those are not its demonstrated cause.

`options-strategies` is self-contained and has no supplementary resources.
The editing instructions in `lumibot-strategy-building` are in its loaded body;
its optional asset/pattern references are separate, exactly named resources.
Not every loaded skill requires a separate resource. Never invent a placeholder
path as a mandatory editing prerequisite. If an unadvertised lookup fails, use
the guidance already loaded and an actual advertised path only when needed;
that lookup failure does not prevent editing the saved file.

Choose the existing architecture before loading a replacement controller. An
existing coherent operation/queue owner with a duplicate hedge or partial-fill
replacement defect uses the lumibot-strategy-building operation-ownership and
quantity-accounting references. Repair its connected methods in place; do not
add an unused controller or port the whole business strategy unnecessarily.
When the combined scan/cancel/hedge owner is missing or incoherent, load
`lumibot-api-reference:references/fast-order-example.md`, then its complete raw
`lumibot-api-reference:references/fast-order-controller.py` source. Copy that
controller into a strategy-owned helper and connect the original business
subclass, price and runner; a disconnected helper does not complete the repair.

Mandatory resource-loading contract: this SKILL.md is routing guidance, not
enough by itself for a code edit or precise runtime/API claim. After loading
this skill for a semantic answer or saved-code edit, load exactly one smallest
relevant reference file with `skills reference get`, then return to the user's
evidence or file work. Load a second reference only when the first one does not
contain a different, specific API fact required by the request. Do not treat
the reference catalog below as a checklist. `references/notes-reminders.md` is
not a default first-build reference; use it only when shared guardrails are the
actual unresolved subject. Use direct LumiBot source tools as stronger evidence
when the exact framework behavior is still uncertain.

For a broker rejection or an owned-position exit, trace the relevant provider
adapter's intent encoding, submission and response/error handling. A Strategy
method that merely delegates does not establish those behaviors. Compare the
deployed framework version with the source reference before drawing a causal
conclusion. If they differ, inspect the matching public release source when
available; otherwise state which behavior is observed, which belongs only to the
reference version and what remains unresolved. Never turn broker error wording
alone into an account-permission diagnosis or claim that current source proves
an older deployment's exception path.

When source inspection is requested, documentation is not a substitute for
reading the implementation. An empty literal search does not complete a requested source inspection:
retry with a shorter identifier or distinctive word, then read the relevant
returned source path. Report a source-access blocker only when the tool actually
returns one; distinguish an unsuccessful query from unavailable source.

Load the smallest relevant reference file with `skills reference get`:

Every reference below belongs to this skill. Use its complete advertised
`resource_key="lumibot-api-reference:references/<file>"`; the current tool does
not take separate `skill_name` and `file_path` arguments. Never attach one of these reference paths to `lumibot-strategy-building` or another
skill, including when those skills were loaded in the same turn.

- For fast cancel, cancel dispatch versus broker-terminal timestamps,
  cancel-after-seconds requirements, `CANCELLING`, second-level order flow, immediate hedge legs,
  hedge leg after entry fill, pair/spread legs, minimal order state machines,
  `on_filled_order` plus direct polling fallback, duplicate hedge prevention,
  `self.get_order(order.identifier)`, `processed_entry_order_ids`,
  `hedge_order_id`, or `Order.OrderStatus.ERROR`, load
  `references/fast-order-management.md` first, even if lifecycle methods are
  also relevant.
- `references/lifecycle-methods.md`: lifecycle callback methods, cumulative or
  incremental partial-fill quantity semantics, duplicate/out-of-order fill
  accounting, restart/reconnect reconciliation, cancels, sleeps,
  hedge-after-fill behavior, and live/backtest differences. Load it first when
  the question centers on `on_partially_filled_order`, processed fill quantity,
  cumulative high-water marks, restart snapshots, or persisted hedge progress.
- `references/methods-properties.md`: common Strategy methods and properties,
  historical prices, prices, orders, positions, helpers, and data access calls.
- `references/entities.md`: Asset, Order, Position, Bars, crypto/forex/options/
  futures entities, base/quote pair semantics, and related object shapes.
- `references/strategy-structure.md`: class/file shape and initialization.
- `references/examples.md`: reusable examples and implementation patterns.
- `references/notes-reminders.md`: shared guardrails and reminders.
- `references/fast-order-management.md`: cancel-after-N-seconds, direct order
  reads, hedge/pair legs, broker-native order classes, volatile quote handling,
  and manual-cancel recovery.
- `references/scanner-performance.md`: full-basket quote and order-read optimization, preservation checks and bounded quote consumption.
- `references/quote-snapshot-example.py`: executable public-API data-read example with bounded requests, missing-member retention and failed-member isolation. Adapt it into the strategy; it is not an installed LumiBot module.
- `references/drift-rebalancer.md`: drift rebalancing helper guidance.
- `references/perplexity-helper.md`: Perplexity helper guidance.
- `references/components-overview.md`: aggregate component overview when a broad
  map is more useful than a narrow reference.

There is no `references/options.md` file. For OptionsHelper construction and
execution methods, load the focused `options-strategies` skill. It returns
its complete guidance and has no supplementary reference files. If a general
component map is needed, the exact call is
`skills reference get(skill_name="lumibot-api-reference",
file_path="references/components-overview.md")`. Do not attach that path to
options-strategies. A missing resource is a correctable name/path lookup:
use the advertised owner and path and continue the authorized work.

Routing examples:

- Crypto pair, base/quote, BTC-USD/BTC/USD, futures symbol, forex pair,
  options asset, or `Asset(...)` construction: load `references/entities.md`.
  Do not patch crypto or other pair construction until that reference/source
  evidence tells you the exact base/quote shape. A variable rename or
  descriptive `self.symbol = "BTC-USD"` cleanup is not enough when the runtime
  asset object still treats the pair string as one base asset. For BTC-USD style
  code, the executable repair should separate the base and quote, e.g.
  `base_asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)`,
  `quote_asset = Asset("USD", asset_type=Asset.AssetType.FOREX)` or the
  source-verified venue quote type, then pass `quote=quote_asset` to price/order
  calls that need the pair context.
- Bars object, historical prices, `get_historical_prices`, `get_last_price`,
  order/position/cost-basis methods, or data provider behavior: load
  `references/methods-properties.md`; load `references/entities.md` too when
  object shape matters.
- `initialize`, `on_trading_iteration`, `sleeptime`, `set_market`, lifecycle
  callback semantics, partial-fill quantities, duplicate/out-of-order fills,
  restart/reconnect snapshots, persisted hedge progress, cancellations, and
  live-vs-backtest differences: load `references/lifecycle-methods.md`.
- Fast cancel, immediate hedge/pair legs, volatile quote handling, duplicate hedge
  prevention, `on_filled_order` plus polling fallback, or
  cancel-after-N-seconds: load `references/fast-order-management.md`. In other
  words, load `references/fast-order-management.md` first for fast order
  state-machine terms before answering or editing.
- Slow multi-asset scanners, repeated option quote calls, repeated account reads, or a requested quote snapshot: load `references/scanner-performance.md` first. It contains the two-level complete scan example. Use `references/methods-properties.md` only for a remaining exact API fact. Preserve eligibility and the original phase and scope of each order guard.
- Unknown broad component question: load `references/components-overview.md`
  first, then the narrower reference it points to.

For first-build or edit work, use this alongside `lumibot-strategy-building`; do
not replace the core workflow with API lookup alone. For indicator calculation
or chart emission, use `lumibot-indicators`.
