> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Cheap observations, deliberate AI decisions

An AI-owned strategy has one trading/risk owner and one or more useful research
roles. Choose the team for the work: a small options strategy may need one
researcher, while macro allocation or research debate can need several. This
does not require rerunning every role whenever the Python lifecycle wakes up.

Python may observe conditions, retain evidence and order identities, and deliver
attention. The trader interprets the evidence and owns contract selection,
quantity, risk, pricing, entry, recovery, exit and re-entry. Generic numerical
tools can calculate Greeks, payoff, package prices and cash; the trader evaluates
those results. A recommendation parsed into Python sizing and order submission
does not establish agent-owned trading. Explicitly chosen Python execution is
still a supported different architecture.

## Four different clocks

Describe entry opportunities, expiration horizon, intended holding duration and
management review frequency separately. A weekly setup review does not mean
buying weekly or holding seven days. A minute observation interval does not mean
minute inference. Healthy longer-held positions should not trigger a new entry
discussion every day unless the mandate calls for that.

## Saved attention is actual structured state

Where the installed runtime provides `self.agents.attention`, the trader uses
`attention_watch` to save an exact underlying-price boundary, signed basket-value
boundary, position-quantity condition, time or order-status condition. `attention_list` inspects its own
conditions; `attention_remove` removes its obsolete ones after reconciliation.
The tool returns the saved record. A prose promise or memory note does not
install a monitor. Check runtime availability before authoring against it.

Each condition has a stable watch identity, a position/setup operation identity,
its reason, a comparison and threshold/time, and exact related order identifiers.
The AI chooses those values. Prefer a few meaningful changes, rather than an
automatic ten-minute reminder. Add a separate threshold if further worsening
requires another decision after the first warning was already considered.

The lifecycle polls read-only observations on the existing clock. It groups
simultaneous conditions into one packet and runs no model on quiet observations.
An unchanged breach fires once, not once per minute. An identical registration
does not reset that episode. A cleared condition can fire again on a new breach.
Missing data is a visible, deduplicated data warning, never a false all-clear.

A basket observation uses the AI's exact legs, signed quantities and contract
multipliers. Its sum of last-price marks is a cheap attention signal, not a
claim of executable bid/ask or a fresh package quote. The trader obtains actual
available execution evidence again before submitting. Quantity-change conditions
can detect residual exposure; choose them for meaningful management rather than
requesting an inference merely to announce every expected fill.

Use the monitor's single-flight decision context so two callbacks cannot launch
duplicate team cycles. A successful cycle acknowledges only its original packet;
new warnings arriving during that cycle remain pending. Exceptions retain the
packet for recovery. Persisted conditions and pending events use ordinary
strategy state. Restarts replay attention, never a broker order.

The monitor's `dispatch(callback)` runs that callback synchronously in a backtest
and in one owned worker during live operation. Poll normally from the lifecycle;
quiet calls start no worker or model. Join the owned worker from termination
hooks. The callback must raise on an incomplete agent run so its packet remains
pending. A worker error is surfaced to the lifecycle, not silently acknowledged
or retried every minute. This does not supply automatic order recovery or a
provider outage policy: those remain visible and must be handled deliberately.

### Lifecycle shape when this API is installed

Create the research roles and sole trader normally, with their actual strategy
policies and Rules. Tell the trader that a time watch called `research_review`
requests another research cycle; other watches deliver management evidence with
the dated prior answer. These names are one explicit application contract, not
required names for every strategy. Bootstrap one initial review at an eligible
time, then let the AI choose subsequent reviews and risk conditions. For example,
the following lifecycle methods use the existing roles named `researcher` and
`trader`; they contain no contract, quantity, price or order decision:

```python
def on_trading_iteration(self):
    self.agents.attention.poll()
    self.agents.attention.dispatch(self._review_attention)

def _review_attention(self, packet):
    if any(event["watch_id"] in {"initial_review", "research_review"} for event in packet):
        research = self.agents["researcher"].run(
            task_prompt="Review the setup using current strategy time and dated evidence.",
            context={"attention": packet, "prior_research": self.vars.get("research")})
        self._require_completed(research)
        self.vars.set("research", {"at": self.get_datetime().isoformat(), "answer": research.summary})
    decision = self.agents["trader"].run(
        task_prompt="Manage the attention evidence and save your next conditions or review.",
        context={"attention": packet, "dated_research": self.vars.get("research")})
    self._require_completed(decision)

@staticmethod
def _require_completed(result):
    if not (result.payload or {}).get("execution_outcome", {}).get("decision_completed"):
        raise RuntimeError("Incomplete decision; preserve attention for recovery")

def on_strategy_end(self):
    self.agents.attention.join()

def on_abrupt_closing(self):
    self.agents.attention.join()
```

Set an observation `sleeptime` appropriate to the requirement, and actually
register the initial eligible time watch from initialization or an appropriate
lifecycle callback. Omitting that bootstrap leaves the example dormant.
The Python method and the model tool have distinct signatures. The model's
`attention_watch` tool supplies its role owner automatically. Direct Python
registration requires that owner plus the flat metric/comparison/value fields;
it does not accept a `condition` dictionary. For example, at the first eligible
review callback, after creating the roles:

```python
self.agents.attention.watch(
    owner="lifecycle", watch_id="initial_review", operation_id="initial_setup",
    metric="time", comparison="gte", value=self.get_datetime().isoformat(),
    reason="First eligible setup review")
```

Persist that successful registration so a restart restores it rather than
creating repeated initial decisions. Registration is not a completed AI decision.
`initialize()` runs again after a restart. Preserve existing `self.vars` research,
watch-registration flags and pending operation identity with defaults; assigning
`None` or `False` over them at every initialization repeats setup and loses context.
Use `self.vars.get(key, default)` when establishing persistent defaults.

The trader must use the returned attention tools to register subsequent watches;
an instruction to "watch risk" without a saved condition leaves it unmonitored.
Pass the coordinator's refresh contract to the trader, not just to Python. For
the example above, its effective prompt must explain that a time watch named
`research_review` runs research before the next trading decision. After a
declined setup or confirmed closure, the trader schedules the next eligible
opportunity through that route. While holding, it chooses needed management
events without creating a daily entry discussion. A coordinator branch that no
agent knows how to request is a dormant branch, not a working refresh policy.

At saved-code readback, trace the whole decision loop: initial review, a declined
entry, a later eligible setup, management while holding, partial or failed orders,
and confirmed closure. Check that each state can reach the appropriate next
decision and that its actual role prompt or tool contract explains how. This is
a semantic review, not a requirement for these example names or a Python state
machine. Keep runtime-owned deduplication and grouping in the runtime; do not
copy those algorithms into the strategy or demand the same wording in every
prompt.
Verify quiet polls, the initial cycle, a triggered management cycle and its next
attention plan with the installed API. Confirm hosted runtime compatibility
separately; do not claim this excerpt proves a Manager run.

## Research and management

A new setup needs the relevant fresh research and trader. For an existing
position, give the trader the dated prior research, alert facts, account,
positions and exact orders. The trader decides whether that research still
applies and requests a refresh when needed. Keep synchronous agent invocations
in the lifecycle coordinator, outside an active ADK agent's event loop. A nested
`AgentHandle.run()` inside a synchronous tool currently fails with an event-loop
error; a static architecture description does not prove that wiring works.
An AI-selected watch identity can explicitly request a research review: the
coordinator invokes the researcher and passes its answer unchanged to the
trader. Other position-management events can use the dated saved answer.
This routing uses the AI's explicit scheduling contract, not parsed market prose
or Python judgment about a trade. Do not substitute invented cached research or discard a research
result and pass a placeholder instead.

The trader's policy should name the evidence it needs and the management
choices it owns. Its recovery policy must preserve returned working-order
identities with the operation and reconcile partial, failed or cancel-pending
orders and residual positions before another submission; rely on the runtime
for observation and single-flight coordination.
 It should check exact held contracts and current quotes before
an order, reconcile the related pending order and residual position, then decide
whether to hold, cancel/replace, exit or roll under the active Rules. A known
risk-reducing exit need not rerun a broad candidate search or all researchers.

A working exit means a specific broker order for this operation is still active.
It is not a flat position. A partial fill leaves residual exposure. Before another
close, the trader checks that order's terminal state and current residual
quantities. An unrelated order cannot suppress monitoring for this position.
After confirmed closure and no remaining obligation, remove the obsolete watches.
A new position receives a fresh operation identity and fresh attention policy.

## Verify behavior and inference separately

Use native state/race tests for quiet observations, one sustained-warning event,
simultaneous warnings, new worsening, unrelated orders, partial fills, cancellation,
restart and closure. Use real-model cases to establish actual tool use and
meaningful decisions. Configuration, a memory note and a completed job label
are not runtime proof.

Keep wall time and simulation time distinct. Historical decisions cannot see
data from a later simulated minute while a model is still reasoning. Verify that
live observation and broker reconciliation remain responsive during model work;
do not infer that from a single-threaded historical backtest.

Report decision cycles, role runs, actual inference responses and tool
continuations separately. One research-plus-trader cycle needs at least two
initial invocations, often more responses for tool use. Record tokens, cache,
retries, provider/tier, latency and actual billing. An API-equivalent estimate
is not an observed ChatGPT credit debit. A short favorable backtest is neither
proof of profitability nor qualification of historical bid/ask execution.
