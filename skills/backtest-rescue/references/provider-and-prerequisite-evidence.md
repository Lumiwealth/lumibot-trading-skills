> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

## Provider and gateway failures

Read the causal exception and its preceding operation before interpreting the
last log line. Cleanup or extension-shutdown warnings after the traceback do
not replace the exception that stopped the run. A failure on the first model
request does not prove a completed decision, a valid no-trade result, Rules
compliance, or performance; partial statistics are not that evidence.

When a managed model request rejects settings, inspect the exact saved model
and reasoning configuration, current supported model settings, and available
runtime provenance. Preserve the user's choices. The rejection alone does not
prove that the provider lacks that setting. Do not retry identical code and
settings against an unchanged gateway, remove reasoning, switch models, request
a personal API key, or rewrite the strategy to hide the incompatibility. Retry
only after a concrete compatible correction or verified platform repair. When
the necessary repair is outside strategy tools, record a platform blocker and
state the concrete next check in the answer: compare the advertised settings
for the exact selected model with the gateway validator and native provider
request, correct the demonstrated mismatch, then verify that exact model and
settings through the same runtime before retrying the saved strategy. Do not
stop at "platform compatibility needs fixing"; identify what must be checked
without pretending that the check or repair has already happened. A platform blocker is not
`waiting_for_user` unless a real user decision is missing; do not ask the user
to relax their strategy mandate to resolve a platform failure. An unavailable
docs lookup is not evidence of incompatibility and does not prevent reporting
the concrete evidence already available.

## Blocked data-source prerequisites

A start result with action=data_source_required and status=not_started is a
blocked prerequisite, not a completed or failed execution. State plainly that
nothing ran and explain the requirement the user must supply. When returned
options require user-owned options data, say that explicitly. Carry each
returned alternative through to its actionable setup step: a broker connection
uses the named Broker Connections page, while a user API key must be their
own key saved as an environment variable with the returned provider key name.
Do not reduce these to provider names or omit where the user saves the key.
Use only the alternatives actually returned, ask which one to use, and do not
switch data sources or retry a refusal that says retryWillNotHelp.
