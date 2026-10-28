> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

## Save the complete causal edit

Prepare the complete changed methods before saving. An initialization field,
lock wrapper or comment is scaffolding, not a quantity repair. When the repair
changes initialization, submission and reconciliation together, assemble the
complete current file and use `replace_file` with its fresh edit handle. Retain
every unrelated method and trading rule. This avoids repeated text blocks in
initialization and session-reset methods accidentally matching each other.
For a smaller patch, anchor on the complete enclosing method, including its
unique `def` line; a repeated field assignment is not a method anchor.

If an atomic patch reports ambiguity, none of its operations were saved. Choose
the intended returned match and use its `retryOperation` unchanged at the failed
operation index, retaining the rest of the batch. Earlier replacements can shift
later match indexes; use the latest error's matches for that later operation.
If no bounded retry is available, read the current file and save its complete
corrected replacement.
Do not retry the same ambiguous text and do not end with "not saved" while this
authorized recovery is available. Inspect every changed executable body and
every helper it calls after the successful save, including terminal branches.

A ledger with no submission path registering its attempts is dead scaffolding.
Before the first save, prepare the full causal change together: initialize the
operation, register/bind every submitted attempt, observe fills, size each
replacement from the ledger, and complete/resume from that same ledger. Use one
`patch_file` call with operations for those complete methods, or replace the
complete current file. Do not spend multiple writes adding disconnected fields
and helpers while leaving the old full-target submitter active. If an edit
introduces a syntax error, correcting syntax is only recovery of that edit;
continue the requested behavioral repair and read back its connected paths.

Initialization and session-reset code often repeat the same state assignments.
For adding initialization state, a unique `def initialize(self):` declaration
is a better insertion anchor than a block of assignments repeated in another
method. Copy that exact declaration/indentation from the current readback and
preserve the rest of its body. For replacing logic, anchor the whole actual
method from its unique declaration through the next method boundary. Do not
guess line numbers or try successively larger fragments of the same repeated
assignments. If that remains impractical, use `replace_file` with the COMPLETE
corrected current file and current editHandle, preserving all unrelated bytes.
An ambiguous or mismatched text anchor is a recoverable edit mistake, not an
authorization or infrastructure blocker. Finish the authorized save and final
readback; a truthful diagnosis or model-upgrade suggestion does not finish it.

Adding ledger fields does not require replacing `initialize`. Insert the new
assignments into the existing method; retain its helper constructors, data
providers, subscriptions, parameters and original setup statements. For example,
after reading the actual signature and indentation, use `patch_file` with the
current `editHandle` and an insertion operation shaped like:

~~~json
{
  "path": "main.py",
  "editHandle": "<exact current get_file editHandle>",
  "operations": [{
    "type": "insert_after",
    "anchor": "    def initialize(self):\n",
    "text": "        self._hedge_state_lock = threading.RLock()\n        self.vars.hedge_operations = RetainedOperations()\n"
  }]
}
~~~

Use the actual method signature, state names and safe insertion boundary from
the readback; keep any method docstring first. This inserts fields without
reconstructing or dropping the existing body. Before execution, compare the
original and saved initialization statements explicitly: every unchanged setup
statement must still be present, especially constructors later methods use.
