# AI-Only Runtime Order Contract

Use this reference to understand what current LumiBot already supplies to every
trading-enabled agent, and to audit a strategy that duplicates those mechanics.
Do not copy these generic mechanics into each saved agent prompt. Python must
not become the order manager in an AI-only strategy.

LumiBot gives every agent built-in runtime skills, including `stock-trading`
and `options-trading`. Its base runtime prompt tells the agent to load the
matching skill before it researches, opens, changes, closes or manages an
asset. This happens while the agent runs, so the strategy author does not need
to classify the asset in advance. A broad mandate can choose an option and then
load the options skill itself.

## Before every buy or sell

The matching runtime skill requires fresh evidence before
`orders_submit_order` (or `orders_submit_multileg`), including:

1. `account_portfolio`
2. `account_positions`
3. `market_last_price` for the exact ordered symbol or underlying
4. For multi-leg options: chain and quote evidence for every leg
5. A check that the order does not duplicate exposure already held or already
   working in open orders (`orders_open_orders`)

The exact evidence depends on the asset and order structure. LumiBot's built-in
tool descriptions and runtime skills are the source of truth, not a copied
sequence in the saved strategy prompt.

## After every submit

The runtime skill requires a self-check before the agent claims success:

1. Capture the order id from the submit result.
2. Re-read that exact order (`orders_get_status`, `orders_open_orders`,
   `orders_wait_for_terminal`).
3. Treat a submit acknowledgement as incomplete until status shows submitted,
   open, partially filled, filled, canceled, rejected or error.
4. If status is unknown or lagging, wait with a bounded retry inside the same
   cycle rather than assuming a fill.
5. After a fill or partial fill, re-read `account_positions` and confirm the
   shares or contracts match the intended trade.
6. For multi-leg orders, confirm every leg appears in positions, or that the
   package order is still working as a unit. One filled leg does not mean an
   iron condor or spread is on.
7. If rejected, canceled or errored, report the broker's reason from the tool
   output, do not retry blindly in a tight loop, and leave the account flat or
   in the last verified state.

## Open-order and duplicate guards

- Check open orders for the same symbol or option package before a new entry.
- Do not place a second iron condor, credit spread or breakout entry while an
  equivalent position or working entry exists, unless the user explicitly
  allows adding to positions.
- A pending cancel still blocks duplicates until the exact order reaches a
  terminal state (canceled, rejected, error, expired or filled). A cancel
  acknowledgement is not terminal. Missing or rate-limited status keeps the
  block in place.

## What belongs in the saved prompt

User-specific strategy policy only:

- instrument universe and permitted structures
- entry and exit conditions
- DTE, delta, wing, credit, stop, target and roll policy
- risk and exposure limits
- cadence-related rules and user-specific restrictions

Do not add generic chain retrieval, tool-call order, signed close sides,
pending-order reconciliation, atomic submission or verification prose. Those
details live in LumiBot and improve over time.

## What Python must not do in AI-only mode

- Poll `get_order` or `get_orders` and place repair orders in Python
- Parse `result.summary` into `create_order` or `submit_order`
- Keep a Python state machine that owns fills while the agent only comments
- Reimplement the runtime skill workflow in Python or in the saved prompt

Python sets the cadence, creates the agents and calls
`self.agents["trader"].run(...)` after the research agents.
