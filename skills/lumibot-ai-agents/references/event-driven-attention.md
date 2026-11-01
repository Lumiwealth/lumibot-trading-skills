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

After declining an opportunity, schedule the next eligible opportunity or a
meaningful change in evidence. A new watch name or an already-due timer does not
make the same unresolved uncertainty a new event. Request immediate research
when it can resolve a new decision-relevant gap; otherwise reuse the dated work
and explain what evidence or time will justify another cycle. Keep urgent new
risk responsive rather than imposing an arbitrary daily model-call cap.

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

Every material management rule declared in the role policy needs an observation
that can actually notice it while the team sleeps. Map each promised price,
position-value, time or order outcome to a saved condition or an explicitly
chosen sufficiently frequent review. A stock-price boundary alone cannot detect
an options-value profit or loss threshold: use the signed basket observation
when the policy depends on that value. Check units, signed quantities and the
comparison direction with the actual position. Do not invent profit targets or
loss thresholds for a policy that deliberately uses other conditions. The
monitor reports facts; the trader decides what action those facts warrant.

Use the monitor's single-flight decision context so two callbacks cannot launch
duplicate team cycles. A successful cycle acknowledges only its original packet;
new warnings arriving during that cycle remain pending. Exceptions retain the
packet for recovery. Persisted conditions and pending events use ordinary
strategy state. Restarts replay attention, never a broker order.

### Lifecycle shape when this API is installed

Create the research roles and sole trader normally, with their actual strategy
policies and Rules. The shared `dispatch_team` coordinator handles role routing,
dated answer storage and required-decision completion. Each AI-saved condition
chooses a `review_scope`: `setup` for an eligible new setup, `research` when new
research is needed, or `management` when relevant dated evidence is sufficient.
Setup/research scopes run the declared researchers, then the decision agent;
management runs only the decision agent using the unchanged dated answers.
Arbitrary watch names have no routing meaning. Multiple simultaneous conditions
produce one team cycle, not one run per condition.

Choose one top-level dispatcher. Call `dispatch_team` directly from the
lifecycle as shown below: it already acquires single-flight ownership and
acknowledges the completed packet. Wrapping it in `dispatch(callback)` or a
`decision()` context prevents the inner team from running. The outer callback
could then acknowledge a packet for which no agent ran. The shared coordinator
is the complete dispatch entry point, not the body of another dispatch callback.

For the existing roles named `researcher` and `trader`:

```python
def on_trading_iteration(self):
    self.agents.attention.poll()
    self.agents.attention.dispatch_team(
        decision_agent="trader", research_agents=["researcher"],
        context={"symbol": self.parameters["symbol"]})

def on_strategy_end(self):
    self.agents.attention.join()

def on_abrupt_closing(self):
    self.agents.attention.join()
```

Use all relevant research role names for a larger team. `context` is passed
unchanged as `team_context`; `dated_research` maps each role to its actual last
answer and reception time. The component chooses no trading action and never
interprets an answer as a signal, quantity or order. It supplies the same scope
contract to the decision agent on every run, so the strategy does not need to
copy a watch-name protocol into several prompts and Python branches.

Register one initial eligible setup after creating the roles, and retain the
successful registration across restarts. For example, inside initialization or
an appropriate eligible lifecycle callback:

```python
if not self.vars.get("attention_started", False):
    self.agents.attention.watch(
        owner="lifecycle", watch_id="initial-review", operation_id="initial-setup",
        metric="time", comparison="gte", value=self.get_datetime().isoformat(),
        reason="First eligible setup opportunity", review_scope="setup")
    self.vars.set("attention_started", True)
```

Set an observation `sleeptime` appropriate to the mandate. Omitting the initial
registration leaves the team dormant. Direct Python `watch` takes flat fields,
an explicit owner and `value`; it does not accept a `condition` dictionary. The
model's `attention_watch` supplies its role owner and accepts `value_json`.
Registration is not completed research, a completed decision or an order.

The trader chooses subsequent conditions with their appropriate scopes. After
a declined setup or confirmed closure, it can save the next eligible `setup`
review. During a healthy holding, use meaningful `management` conditions rather
than a daily entry discussion. If a decision needs new research, defer that
evidence-dependent action and register a `research` review. The current run
completes; the subsequent coordinated cycle supplies fresh answers. Keep this
separate from an urgent protective decision that can use still-sufficient known
evidence. A scheduled review is never proof that the future work already ran.

`dispatch_team` uses the existing single-flight dispatcher. A required research
or decision run that returns incomplete raises and leaves its packet pending.
Only completed research answers are stored as usable. Restarts retain those
answers, watches and undelivered warnings without repeating the initial review.
Preserve existing `self.vars` flags and state during initialization.

For different coordination, a custom lifecycle may instead call
`dispatch(callback)` with a callback that invokes the actual agent handles and
checks their completion. Do not call another dispatcher from that callback.
It runs synchronously in a backtest and in one owned worker during live
operation. Poll normally, join at termination, and raise on incomplete required
runs so attention remains pending. Worker failures surface to the lifecycle;
the component does not silently retry them or supply an order-recovery policy.
For custom clock windows, persist the attempted window before calling either
role and store completion separately. An incomplete answer must stay visible;
it must not turn every remaining minute of the same window into another team
run. Use an explicit bounded recovery policy or a distinct scheduled/new-evidence
review, preserving observations for held exposure and working orders. An attempt
marker is not permission to acknowledge undelivered attention or claim success.
Verify the custom callback's actual request/routing contract,
answer handoff and incomplete-result handling; do not assume a watch name has
built-in meaning. Keep one monitor state owner and do not reproduce its
persistence, deduplication or single-flight algorithms in strategy code.

At saved-code readback, trace initial review, a declined entry, a later eligible
setup, management while holding, partial or failed orders and confirmed closure.
Verify quiet polls and triggered scopes with the installed API. Confirm hosted
runtime compatibility separately; this excerpt proves no Manager run.

## Research and management

A new setup needs the relevant fresh research and trader. For an existing
position, give the trader the dated prior research, alert facts, account,
positions and exact orders. The trader decides whether that research still
applies and requests a refresh when needed. Keep synchronous agent invocations
in the lifecycle coordinator, outside an active ADK agent's event loop. A nested
`AgentHandle.run()` inside a synchronous tool currently fails with an event-loop
error; a static architecture description does not prove that wiring works.
An AI-selected research review scope asks the coordinator to refresh the
configured research roles and pass their actual answers unchanged to the
decision agent. Management scopes can use their dated saved answers.
This routing uses the AI's explicit scheduling contract, not parsed market prose
or Python judgment about a trade. Do not substitute invented cached research or discard a research
result and pass a placeholder instead.

The trader's policy should name the evidence it needs and the management
choices it owns. Its recovery policy must preserve returned working-order
identities with the operation and reconcile partial, failed or cancel-pending
orders and residual positions before another submission; rely on the runtime
for observation and single-flight coordination.
For an order-status watch, `value_json` lists the states that should trigger a
decision, not merely the states being tracked. A watch matching only `new` and
`partially_filled` does not wake when that order is canceled. Choose the relevant
fill, cancellation, failure and partial-fill outcomes, using the exact returned
parent and child identities needed to observe the operation. A normal successful
transition need not run fresh research when the saved management policy suffices.
Separate an established holding's review frequency from entry-order recovery:
an unfilled canceled order may need an earlier bounded setup/repricing review,
while a healthy monthly holding should remain quiet. Preserve the requested
opportunity limit; neither a canceled order nor a new minute permits repeated
unbounded entry attempts or replacement of a still-working order.
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
