> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# AI-Only Runtime Order Contract

Use this reference to understand what current LumiBot supplies to every
trading-enabled AI-only agent. Do not copy these generic mechanics into each
saved agent prompt. Python must not become the order manager for an AI-only
build.

LumiBot exposes `stock-trading` and `options-trading` through ADK
`SkillToolset`. Its base runtime prompt requires the agent to load the matching
skill before it researches, opens, changes, closes, or manages an asset. This
happens at agent runtime, so BotSpot does not need to classify the asset in
advance. A broad mandate can choose an option and then load the options skill.

## Before Every Buy or Sell

The matching runtime skill requires fresh evidence before
`orders_submit_order`, including:

1. `account_portfolio`
2. `account_positions`
3. `market_last_price` for the exact ordered symbol or underlying
4. For options multi-leg work: retrieve chain/quote evidence for every leg
5. Confirm the intended order does not create duplicate exposure against
   current positions and open orders

The exact evidence depends on the asset and order structure. LumiBot's built-in
tool descriptions and runtime skill are the source of truth, not a copied
sequence in the saved strategy prompt.

## After Every Submit

The runtime skill requires a self-check before claiming success:

1. Capture the submitted order id / identifier from the submit result.
2. Re-read that exact order with the built-in order lookup / open-order tools.
3. Treat submit acknowledgement as incomplete until status evidence shows
   submitted, open, partially filled, filled, canceled, rejected, or error.
4. If status is still unknown or lagging, wait briefly with a bounded retry
   inside the same cycle rather than inventing a fill.
5. After a fill or partial fill, re-read `account_positions` and confirm the
   resulting contracts or shares match the intended trade.
6. For multi-leg orders, confirm every intended leg appears in positions or
   that the multi-leg order is still open/working as a unit. Do not assume an
   iron condor or credit spread is on because one leg filled.
7. If rejected, canceled, or errored, log the broker reason from tool output,
   do not retry blindly in a tight loop, and leave the account flat or in the
   last verified state.

## Open-Order and Duplicate Guards

The runtime skill requires:

- Check active/open orders for the same symbol or option package before a new
  entry.
- Do not place a second iron condor / credit spread / ORB entry while an
  equivalent position or working entry already exists, unless the user
  explicitly allows pyramiding.
- Pending-cancel / cancelling remains active for duplicate blocking until the
  exact order reaches a broker-terminal canceled, rejected/error, expired, or
  filled state. A cancel acknowledgement is not terminal evidence. Refresh only
  the exact order with a bounded retry; missing or rate-limited evidence keeps
  the blocker in place rather than permitting a duplicate entry.

## Saved Prompt Boundary

The saved system prompt should contain user-specific strategy policy such as:

- the instrument universe and permitted structures
- entry and exit conditions
- DTE, delta, wing, credit, stop, target, and roll policy
- risk and exposure limits
- cadence and any user-specific restrictions

Include the trading agent's own responsibility to obtain fresh account,
position, open-order, exact-contract and executable-price facts before acting,
respect the requested atomic defined-risk package, and verify both the returned
broker result and the resulting positions before claiming execution. This
responsibility belongs explicitly in the trading agent's saved instructions;
"verify the outcome" alone omits the resulting-position check. A researcher summary or a separate Rules file does not assign that
responsibility to the trader. Refer to the matching runtime trading skill for
the implementation. Do not duplicate generic chain retrieval, order-tool call
order, signed-close mapping, pending-order reconciliation or the full submission
and verification workflow. Those mechanics evolve in LumiBot and remain owned
by its runtime skills and real-model gate.

## What Python Must Not Do in AI-Only Mode

- Poll `get_order` / `get_orders` and then place repair orders in Python
- Parse `result.summary` into `create_order` / `submit_order`
- Maintain a Python state machine that owns fills while the agent only comments
- Reimplement the runtime skill workflow in Python or the saved prompt

Python may still set cadence and call `self.agents["trader"].run(...)`.
