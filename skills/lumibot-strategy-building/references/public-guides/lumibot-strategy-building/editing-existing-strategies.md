> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Editing an existing BotSpot strategy

Use with the `lumibot-strategy-building` skill whenever you change saved
strategy code: bug fixes, parameter changes, behavior edits, repairs after a
failed backtest, or copying rules between strategies.

## The basic loop

1. Read: `get_file` on the current revision (or the revision the user named).
   Keep the returned `editHandle` with that read.
2. Inspect: find every place the value or state you are changing is used.
3. Write once: one `patch_file` call with all non-overlapping operations for
   the request, or one `replace_file` with the complete corrected file.
4. Read back: `get_file` on the new revision returned by the write. Verify every
   requested change and the behavior that must stay the same.
5. Stop, or run the validation the user asked for. Do not start a backtest
   merely because an edit was saved.

Diagnosis is not completion. When the user asked for a fix and you found the
concrete change, make it, save it and read it back in the same turn. Only stop
at an explanation if a real blocker prevents editing or the user asked only for
an inspection.

## Text anchors

- Copy `oldText` byte for byte from the latest readback, including blank lines
  and indentation. Never rebuild it from memory, a summary or the desired new
  text.
- An anchor must match exactly one place. Strategy code often repeats the same
  assignment in `initialize` and in a reset or exit method; include the
  enclosing function context so you change the intended one.
- Use `replaceAll=true` only when every occurrence is part of the requested
  change.
- If a patch fails as ambiguous or missing, re-read the file. The desired
  behavior may already exist from an earlier write; if so, keep that revision.
  Otherwise retry with a unique larger anchor, a guarded line range with the
  exact expected old text, or a complete `replace_file`. A rejected patch saved
  nothing. Do not resend the same ambiguous anchor and do not report a failed
  patch as saved.
- For adding initialization state, the unique `def initialize(self):` line is a
  better anchor than a block of assignments that also appears elsewhere.
- If a first build was done with `patch_file` and the readback is partial,
  missing imports, missing the class, or still contains starter code or a
  duplicate `__main__` block, replace the whole file.

## Change only what was asked

- Inspect every consumer of the parameter or state you change. A stop distance
  may also feed sizing or an entry condition.
- Preserve behavior, not the old expression. Example: if sizing was
  `cash / price * stop_distance / normalizer` and the user changes only the
  stop distance, keep the old ratio as an independent sizing multiplier so
  quantities do not change. Changing the expression to keep sizing stable is
  correct here, not an unauthorized sizing change. If the user explicitly asks
  to change sizing, change it.
- An exit repair must not change entry rules, and an entry repair must not add
  exit features. Keep unrelated behavior intact.
- When a saved `rules.json` describes the behavior you changed, update the
  matching rule in the same piece of work so code and Rules agree. A purely
  technical repair that keeps the trading rules unchanged does not need a Rules
  edit. Do not create a Rules file for a small parameter change on a strategy
  that has none.
- Once the requested change is saved and read back, stop. Do not rename
  unrelated symbols, add files or broaden the repair.

## Exact targets and credentials

- Treat each credential and environment variable name as an exact identity. A
  similar prefix is not the same system. A saved broker connection does not
  replace an API key that authenticates a separate data, database,
  notification or AI service.
- If the user asks to remove variables that are not in the saved code, do not
  edit a look-alike, weaken its check or make a no-op revision. Say the named
  variables are already absent and continue any other requested work on the
  unchanged revision.

## Working on the right strategy

- If the user names a different strategy ("the one called X", "apply this to X
  too", "do not change Y"), resolve it with `list_strategies`, then
  `list_revisions` for that strategy, and pass its ids to the file tools. Never
  reuse the open strategy's revision id for a different strategy.
- Edit only the named target unless the user asks to edit both.

## Copying rules from one strategy to another

"Use the same rules as X" means executable parity, not a guessed theme.

1. Read both the source and the target code before editing.
2. Diff executable assignments, thresholds, cadence, branches and helper calls.
3. Patch the differing behavior lines into the target file. Do not replace the
   target wholesale with the source file.
4. Keep the target's identity: its symbol, name, account and labels, unless the
   user asks to change them. Do not merge in unrelated features the source
   does not have.
5. After the readback, check the target identity line literally. If a source
   symbol leaked into the target (for example the target should trade one
   ticker and now names the source's ticker), patch it back and read again.

## Replacing stale values and sources

- When the user gives a concrete replacement value (cost basis, entry price,
  threshold, cadence, symbol), replace the stale literal in the saved code.
- When the user says to stop using a value or source, remove every executable
  fallback to it. Example: "stop using the broker position average as the sell
  trigger basis" means the trigger logic must not read
  `position.avg_fill_price` at all, not even as a last resort.
- For fill-price repairs, prefer the newest confirmed fill of an order this
  strategy placed. If the user supplied a specific fill, store that exact value
  in strategy state (`self.vars`) as the starting known fill, keep updating it
  from later confirmed fills, and hold or skip when no strategy-owned fill is
  known.
- When a live bot is involved, check broker evidence (`get_broker_orders`,
  `get_broker_positions`, deployment order and position telemetry) before
  changing fill logic, when those tools are available for that deployment.

## When a file write fails

An invalid or stale edit handle, a validation error or any file-tool error
means no revision was created. Re-read with `get_file`, use the fresh handle,
and retry. After a complex patch fails, a complete `replace_file` is often the
clearest route. A denied write, missing permission or concurrent change is a
different situation; report it accurately.

## Backtest after an edit

- If the user asked for an edit and a backtest, save and read back first, then
  `start_backtest` on the new revision. A backtest of the old revision does not
  validate the edit.
- If the user gave a window ("30 days", "one year"), pass it to
  `start_backtest`. That is not a request to change cadence or lookbacks.
- If `start_backtest` returns a failure instead of a backtest id, nothing is
  running. Fix the cause and retry.
