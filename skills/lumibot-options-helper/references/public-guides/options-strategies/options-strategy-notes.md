> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Options Backtest Made No Trades: Diagnosis and Repair

Part of the `options-strategies` skill. Use this when an options backtest
finishes with zero or very few trades, or when contracts cannot be found.

## First: is it data, code or rules?

1. **Data.** Was the backtest run on an options data source? On BotSpot,
   options backtests need `dataProvider` "alpaca" (the user's connected Alpaca
   account, history from February 2024) or "polygon" (the user's own
   `POLYGON_API_KEY`). A window that starts before the source's history, or an
   underlying the source does not cover, produces empty chains.
2. **Code.** Invented helper names, missing `underlying_asset` on
   `get_expiration_on_or_after_date`, strikes not in the chain, a warmup gate
   that returns before any option is selected, assuming every chain field is
   present, or a crash in `on_trading_iteration`.
3. **Rules.** The user's own conditions did not occur in the window. That is
   not a defect.

## Evidence to gather (BotSpot MCP tools)

- `get_backtest_logs` with a `query` such as "option", "chain", "expiration",
  "strike", "spread", "Skip" or "Traceback" to find where the code stopped.
  Good strategies log a reason at every early return; add those logs if they
  are missing.
- `backtest_status` for the final stage and any recent orders.
- `get_backtest_artifact` for the trades artifact, then `query_csv` to list
  orders and fills (status, strike, expiration, option type).
- `get_broker_option_chain` (read-only, needs a saved broker connection) to
  confirm which expirations and strikes really exist for the underlying today.

## Common causes and repairs

| Symptom in logs | Likely cause | Repair |
|---|---|---|
| AttributeError on an OptionsHelper method | invented method name | use only the methods listed in the skill |
| No valid expiration | window too narrow, or `underlying_asset` missing | pass `underlying_asset`; confirm the window with the user |
| Option found but always skipped | spread filter too strict, missing bid/ask | log `data_quality_flags`; apply only the user's spread limit; let the last-trade fallback work in backtests |
| Every multi-leg package rejected | one leg (often a far wing) has no quote | try the next listed wing strike or the next expiry; keep the structure |
| "Failed to calculate limit price" | a leg has no two-sided bid/ask (common with last-trade-only data) | see the skill's pricing section; never invent quotes |
| Orders rejected | not enough cash or buying power | size from available cash; report it |
| Nothing logged at all | early return before selection (warmup, schedule, market hours) | log each gate; fix the gate if it is a code bug |
| Trades only at the start | state flag never reset after exit | reset state when positions show flat |

## Repair principles

- Fix technical defects freely: data availability, API usage, state handling,
  logging, contract lookup.
- Preserve the user's signals, thresholds, structure, sizing and exits. If a
  rule change seems necessary, explain why in plain words and offer specific
  choices (a longer window, one exact threshold change). Wait for the user's
  choice before saving it.
- Broaden contract search in normal ways: use the nearest valid expiry with
  data, continue to the next candidate after an untradeable combination, and
  log each rejected combination.
- If a directional multi-leg idea still cannot find liquid legs, you may
  propose a one-contract call or put version that still uses
  `evaluate_option_market`. Let the user decide.
- For a substantial rewrite, use `replace_file` with the complete `main.py`,
  then `get_file` to read it back and confirm the imports, the strategy class
  and the complete order path are present. If a `patch_file` call fails, no
  change was saved; read the file again with `get_file` for a fresh
  `editHandle`, then retry.
- Never add fake fills, dummy legs, hardcoded validation orders or
  `if backtesting:` branches. The strategy must trade through its normal path.
- Choose the first test window to fit the rules: a 30-day expiry cycle needs
  at least one or two months to show an entry and an exit.
- Only start a backtest when the user wants one.
