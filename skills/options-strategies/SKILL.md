---
name: options-strategies
description: Load before writing, editing, debugging or backtesting any LumiBot strategy that trades options, including single calls or puts, covered calls, cash-secured puts, the wheel, vertical spreads, iron condors, butterflies, straddles, strangles, calendars, diagonals and ratio spreads, or when an options backtest makes no trades. Covers OptionsHelper, chains, expirations, strikes, greeks, liquidity checks, multi-leg orders, assignment and expiry handling, position management and options data on BotSpot.
license: MIT
metadata:
  title: "Options Strategies in LumiBot"
---
# Options Strategies in LumiBot

This skill teaches an AI agent how to write correct, tradeable options strategies
with LumiBot (https://github.com/Lumiwealth/lumibot, docs at
https://lumibot.lumiwealth.com) and how to backtest and deploy them on BotSpot
(https://botspot.trade).

It assumes you already know the basic LumiBot strategy lifecycle
(`initialize`, `on_trading_iteration`, `self.vars`, orders, positions). If not,
load the `lumibot-strategy-building` skill first. For general API semantics see
`lumibot-api-reference`; for speed see `fast-lumibot-strategies`; for
stock-only logic see `stock-etf-strategies`; for indicators and charts see
`lumibot-indicators`.

Nothing in this skill is investment advice. Structures, symbols, deltas and
expirations below are illustrations of mechanics, not recommendations.

Reference files (load with `skills` action=get, name=options-strategies,
reference=<path>):

- `references/multileg-structures.md`: exact leg topology for verticals, iron
  condors, butterflies, straddles, strangles, calendars, diagonals and ratio
  spreads, with a complete iron condor example and package closing code.
- `references/wheel-strategy.md`: the wheel (cash-secured puts, assignment,
  covered calls) as a complete worked pattern.
- `references/options-strategy-notes.md`: why an options backtest makes no
  trades, and how to repair it without changing the user's rules.
- `references/quote-snapshots-and-speed.md`: making scanners that read many
  option quotes fast and correct.

---

## 1. Options on BotSpot: data, backtests and deployment

**Backtest data.** Options backtests on BotSpot currently need the user's own
options data source. BotSpot's managed default data route does not provide
options history right now, so an options backtest on the default route is
refused before it starts. The two supported choices are:

- `alpaca`: the user's own connected Alpaca account (a free paper account
  works). Alpaca options history starts in February 2024, so backtest windows
  must begin on or after that.
- `polygon`: the user's own Polygon API key, saved as the environment variable
  `POLYGON_API_KEY`. The user saves the key themselves (for example with
  `saved_env_vars` action=create, or in BotSpot settings) and you pass the
  returned id in `envVarSetIds` on `start_backtest`.

When you call `start_backtest` from an outside MCP client, pass
`dataProvider` ("alpaca" or "polygon") on the call. Ask the user which source
they want if it is not obvious. If the user has neither, explain how to connect
an Alpaca account or save a Polygon key. Never describe a missing data source
as a problem with the strategy.

Option quote coverage differs by source. Some sources record trades but little
bid/ask history, so `evaluate_option_market` may fall back to the last trade
price in backtests (see section 6). That is normal; it is not a reason to
invent prices.

**Inspecting real chains.** `get_broker_option_chain` reads a live option chain
from the user's saved broker connection (read-only). Narrow it with
`expiration` or `expirationStart`/`expirationEnd`, `strikeMin`/`strikeMax`,
`right` and `limit`. Use it to sanity check that an underlying has the
expirations and strikes your code assumes. `get_broker_quotes` with
`assetType` option plus `expiration`, `strike` and `right` reads one contract.

**Explaining a structure.** `show_option_payoff` draws profit and loss at
expiration for legs the user describes (long or short, call or put, strike,
premium, contracts) with breakevens. It fetches no data and places no trade.
Use it to confirm with the user that the structure you are about to code is
the one they mean.

**Deployment.** A live or paper options bot needs a broker connection that
supports options (and multi-leg orders, if the strategy uses them). Starting a
deployment with `start_deployment` and every real-money action require the
user's own approval on botspot.trade. Never try to bypass that step.

---

## 2. Before writing code: pin down the structure

Options strategies fail most often because one detail was guessed. Before you
create or edit a strategy, make sure you know:

1. **Underlying.** Prefer liquid optionable underlyings (for example SPY, QQQ,
   IWM, GLD) or the exact symbols the user named. Index options (SPX, NDX,
   XSP and similar) are cash-settled; equity and ETF options deliver shares.
2. **Every leg.** Right (call or put), side (buy or sell), quantity ratio and
   strike relationship. A ratio spread is ambiguous until you know whether
   the long strike is above or below the short strike: "buy one and sell two
   options ten points apart" does not say. If the direction cannot be read
   from the user's own words, ask one precise question before writing code.
   Do not infer it from a convention or a market view.
3. **Expiration rule.** For example "first expiration at least 30 days out",
   "nearest weekly", "0 DTE". Calendars and diagonals need two rules.
4. **Strike rule.** ATM, a percentage out of the money, a fixed distance, or a
   target delta. Wing widths for spreads.
5. **Entry timing and frequency.** Time of day, signal, how many packages can
   be open at once.
6. **Exits.** Profit target, stop, days-to-expiration exit, delta exit, roll
   rule, or hold to expiry. What happens on assignment.
7. **Sizing.** Contracts per package, or a risk budget. Remember the contract
   multiplier (normally 100 shares per contract).

Show the user the structure in plain words (or with `show_option_payoff`)
before a large build. Preserve their rules exactly once agreed.

---

## 3. Always use OptionsHelper

Use `lumibot.components.options_helper.OptionsHelper` for contract discovery,
pricing checks and multi-leg orders. It validates that a contract actually has
tradeable data at the current simulated time, which hand-rolled chain parsing
does not. Do not pick contracts by hand from raw chain dictionaries and do not
invent helper method names.

```python
from datetime import timedelta
from lumibot.components.options_helper import OptionsHelper
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class MyOptionsStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
        self.options_helper = OptionsHelper(self)
        self.vars.chains = None
        self.vars.chains_date = None
```

### Method catalog (use only these names)

Discovery and analytics:

| Method | Returns | Notes |
|---|---|---|
| `find_next_valid_option(underlying_asset, rounded_underlying_price, expiry, put_or_call="call")` | `Asset` or None | Searches near the given strike for a contract with quote data, falling back to last trade price. Use it to turn a target strike into a real contract. |
| `get_expiration_on_or_after_date(dt, chains, call_or_put, underlying_asset=None)` | `date` or None | Always pass `underlying_asset` so the expiry is validated against real data. |
| `find_strike_for_delta(underlying_asset=..., underlying_price=..., target_delta=..., expiry=..., right=...)` | strike or None | Use keyword arguments. `underlying_price` is a required float. Puts use negative deltas. |
| `get_delta_for_strike(underlying_asset, underlying_price, strike, expiry, right)` | float or None | Delta of one strike. |
| `get_strike_deltas(underlying_asset, expiry, strikes, right, stop_greater_than=None, stop_less_than=None)` | dict strike to delta | Batch deltas with early stop. |
| `evaluate_option_market(option_asset, max_spread_pct=None)` | `OptionMarketEvaluation` | Bid, ask, last price, spread, buy and sell anchors, data quality flags. |
| `OptionsHelper.has_actionable_price(evaluation)` | bool | True when the buy price is finite, positive and not blocked by the spread filter. |
| `calculate_multileg_limit_price(orders, limit_type)` | float or None | `limit_type` is "best", "fastest" or "mid". |
| `get_order_details(order)` | dict | Readable summary of an order's contract. |
| `aggregate_portfolio_greeks(positions, underlying_asset)` | dict | Summed greeks across option positions on one underlying. |
| `check_spread_profit(initial_cost, orders, contract_multiplier=100)` | float or None | Current profit of a package versus its opening cost. |

Order builders (build `Order` objects, do not submit):

| Method | Legs |
|---|---|
| `build_call_vertical_spread_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity)` | buy call at lower, sell call at upper (bull call debit spread) |
| `build_put_vertical_spread_orders(underlying_asset, expiry, upper_strike, lower_strike, quantity)` | sell put at upper, buy put at lower (bull put credit spread) |
| `build_call_orders(underlying_asset, expiry, call_strike, quantity_to_trade, wing_size)` | sell call at strike, buy call at strike + wing (bear call credit spread), returned as a tuple |
| `build_put_orders(underlying_asset, expiry, put_strike, quantity_to_trade, wing_size)` | sell put at strike, buy put at strike minus wing, returned as a tuple |
| `build_calendar_spread_orders(underlying_asset, strike, near_expiry, far_expiry, quantity, right)` | sell near, buy far |
| `build_diagonal_spread_orders(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity, right)` | sell near, buy far, different strikes |
| `build_butterfly_spread_orders(underlying_asset, expiry, lower_strike, middle_strike, upper_strike, quantity, right)` | 1 : -2 : 1 |
| `build_straddle_orders(underlying_asset, expiry, strike, quantity)` | buy call and put at one strike |
| `build_strangle_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity)` | buy put at lower, buy call at upper |
| `build_ratio_spread_orders(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right)` | buy `buy_qty` at buy_strike, sell `sell_qty` at sell_strike |

Verify the sides a builder produces against the user's intent. For example the
straddle and strangle builders create long structures; a short straddle needs
the sides reversed (build your own orders with `self.create_order`, see
`references/multileg-structures.md`).

Execution (build and submit):

| Method | Notes |
|---|---|
| `execute_orders(orders, limit_type=None)` | Submits a list of orders as one multi-leg package. With `limit_type`, prices it first. |
| `execute_call_vertical_spread(...)`, `execute_put_vertical_spread(...)`, `execute_calendar_spread(...)`, `execute_butterfly_spread(...)`, `execute_straddle(...)`, `execute_strangle(...)`, `execute_diagonal_spread(...)`, `execute_ratio_spread(...)` | Same arguments as the matching builder plus `limit_type=None`. Return True when submitted. |

There is no helper named `get_chains_expirations_with_data` or anything like
it. To find a contract: `self.get_chains(...)`, then
`get_expiration_on_or_after_date(...)` with `underlying_asset`, then
`find_next_valid_option(...)` or `find_strike_for_delta(...)`.

The legacy `check_option_liquidity(...)` still exists; prefer
`evaluate_option_market(...)` in new code.

---

## 4. The canonical selection flow

```python
def on_trading_iteration(self):
    underlying = Asset("SPY", asset_type=Asset.AssetType.STOCK)
    today = self.get_datetime().date()

    # 1. Chains: fetch at most once per day and cache in self.vars.
    if self.vars.get("chains") is None or self.vars.get("chains_date") != today:
        self.vars.chains = self.get_chains(underlying)
        self.vars.chains_date = today
    chains = self.vars.chains
    if not chains:
        self.log_message("No option chains available today", color="yellow")
        return

    # 2. Underlying price.
    price = self.get_last_price(underlying)
    if price is None:
        self.log_message("No underlying price", color="yellow")
        return

    # 3. Expiration: validated against real data.
    target = today + timedelta(days=30)
    expiry = self.options_helper.get_expiration_on_or_after_date(
        target, chains, "put", underlying_asset=underlying
    )
    if expiry is None:
        self.log_message(f"No valid expiration on or after {target}", color="yellow")
        return

    # 4. Strike: by delta (puts use negative delta).
    strike = self.options_helper.find_strike_for_delta(
        underlying_asset=underlying,
        underlying_price=float(price),
        target_delta=-0.30,
        expiry=expiry,
        right="put",
    )
    if strike is None:
        self.log_message("No strike found for target delta", color="yellow")
        return

    # 5. Resolve a real contract and check its market.
    option = self.options_helper.find_next_valid_option(underlying, strike, expiry, "put")
    if option is None:
        return
    evaluation = self.options_helper.evaluate_option_market(option, max_spread_pct=0.25)
    self.log_message(f"{option}: {evaluation}", color="blue")
    if not OptionsHelper.has_actionable_price(evaluation):
        self.log_message(f"Skip {option}: {evaluation.data_quality_flags}", color="yellow")
        return

    # 6. Order with an explicit limit price.
    order = self.create_order(option, 1, "sell", limit_price=evaluation.sell_price)
    self.submit_order(order)
```

Every step can return None. Check each one, log why you stopped, and return.
Never substitute a made-up value.

---

## 5. Choosing expirations and strikes

**Chains.** `self.get_chains(asset)` returns a `Chains` object. Useful
methods: `chains.expirations("CALL")` or `("PUT")` (strings),
`chains.expirations_as_dates("CALL")`, `chains.strikes(expiration, "CALL")`.
Use only expirations and strikes that the chain returns. Never build a contract
from a rounded number that may not be listed (for example a $1 strike on an
underlying that lists $5 strikes).

**Expirations.** Translate the user's rule into a target date and call
`get_expiration_on_or_after_date`. For "nearest weekly" use today as the target.
For 0 DTE use today and then confirm the returned expiry equals today. For a
window ("between 30 and 45 days") check the returned date is inside the window
and skip if not, rather than silently widening the window.

**Strikes by moneyness.** For "5% out of the money" compute the target
(`price * 0.95` for puts, `price * 1.05` for calls), then let
`find_next_valid_option` pick the nearest real contract. For ATM, use the
current price.

**Strikes by delta.** Use `find_strike_for_delta` with keyword arguments.
Then confirm the chosen contract's delta with `get_delta_for_strike` or
`self.get_greeks(option, underlying_price=price)` if the rule is strict. A
strike near the money does not automatically match a delta target; measure it.

**Wings.** Choose short strikes first, then compute wings from the requested
widths (`long_put = short_put - put_width`, `long_call = short_call + call_width`)
and confirm each wing strike is listed in the chain for that expiry. If the
exact wing strike is not listed, take the nearest listed strike in the safe
direction (further out) and log it, or ask the user if width matters exactly.

**Greeks.** `self.get_greeks(option_asset, asset_price=None,
underlying_price=None, risk_free_rate=None, query_greeks=False)` returns a dict
with keys such as `delta`, `gamma`, `theta`, `vega` and `implied_volatility`.
Pass prices you already have to avoid extra requests. Greeks can be None when
data is missing; guard for it.

---

## 6. Liquidity and pricing

Call `evaluate_option_market(option, max_spread_pct=...)` for every leg before
submitting. The returned `OptionMarketEvaluation` contains `bid`, `ask`,
`last_price`, `spread_pct`, `spread_too_wide`, `missing_bid_ask`,
`missing_last_price`, `buy_price`, `sell_price`, `used_last_price_fallback`,
`max_spread_pct` and `data_quality_flags`.

Rules:

- Log the evaluation. Place the order only when
  `OptionsHelper.has_actionable_price(evaluation)` is True. Otherwise log the
  flags and skip.
- Use `evaluation.buy_price` as the limit for buys and `evaluation.sell_price`
  for sells.
- Pass `max_spread_pct` only when the user set a spread limit or the strategy
  genuinely needs one. A cheap protective wing often has a wide percentage
  spread on a few cents; a strict filter can block every package.
- In backtests with sources that lack bid/ask history, the helper may price
  from the last trade (`used_last_price_fallback` is True). That reflects real
  recorded trades and is acceptable for simulation. A contract with no recent
  trade is still unpriceable; skip it.
- For multi-leg packages use `calculate_multileg_limit_price(orders, limit_type)`
  or pass `limit_type` to `execute_orders`. "mid" estimates value and may not
  fill. "fastest" buys at asks and sells at bids and is the right choice when
  the user wants the trade to execute now. "best" is the most favorable limit.
  A positive package price is a debit, a negative one is a credit.
- `calculate_multileg_limit_price` needs a valid two-sided bid and ask on every
  leg. It does not use the last-trade fallback, so with a data source that has
  little bid/ask history it returns None and `execute_orders(...,
  limit_type=...)` refuses to submit (it logs "Failed to calculate limit
  price"). In that case, either submit the package without a limit
  (`limit_type=None`, a market package) only if the user accepts that, or keep
  the package unpriced and skip. Never fabricate a bid or ask.
- Sanity check package economics: a standard credit vertical opens for more
  than zero and less than its width; an iron condor's credit is smaller than
  either wing width. A price outside those bounds means a leg is wrong.

---

## 7. Multi-leg orders

Build every leg first, then submit the whole package once:

```python
orders = self.options_helper.build_put_vertical_spread_orders(
    underlying, expiry, upper_strike=short_strike, lower_strike=long_strike, quantity=1
)
ok = self.options_helper.execute_orders(orders, limit_type="fastest")
if not ok:
    self.log_message("Spread not submitted", color="red")
```

- **One decision, one package.** When one decision needs several structures
  (for example a put ratio spread plus a call ratio spread on the same day),
  concatenate the lists from the builders and call `execute_orders(...)` once
  with the combined list. Do not submit each structure separately.
- **Closing a package.** Read the actual current positions, build the opposite
  side for every held leg (long becomes sell, short becomes buy, quantity is
  `abs(position.quantity)`), and submit the complete closing list once. Do not
  close legs one at a time. See `references/multileg-structures.md` for code.
- **Broker support.** Atomic multi-leg submission depends on the broker. If
  the deployment broker cannot take a package, tell the user instead of
  silently legging in.
- **Never resubmit on uncertainty.** If a submission result is unclear, check
  open orders and positions before trying again. A pending package owns that
  position change.

Standard leg topology for every common structure is in
`references/multileg-structures.md`. Read it before writing any multi-leg
entry.

---

## 8. Position management

**Signed quantities are the truth.** Positive is long, negative is short, zero
is flat. Reconstruct option exposure from `self.get_positions()` each time you
need it; do not trust a remembered order.

```python
def _option_positions(self, underlying_symbol):
    out = []
    for pos in self.get_positions():
        a = pos.asset
        if a.asset_type == Asset.AssetType.OPTION and a.symbol == underlying_symbol:
            out.append(pos)
    return out
```

Group by expiration, right and strike to identify each package.

**Manage before opening.** If a package or a pending order for it exists,
decide whether to hold, close or roll it before opening another. A partially
filled structure is not flat.

**State in `self.vars`.** Store the opening credit or debit, entry date and the
package's leg identities in `self.vars` so exits can be evaluated after a
restart. Initialize every field in `initialize()` and read with
`self.vars.get(name, default)` because older saved state may lack new fields.

**Common exits.**

- Profit target or stop on a package: `check_spread_profit(initial_cost,
  orders)` with orders describing the held legs, or compute from current
  `evaluate_option_market` prices times the multiplier.
- Time exit: close when days to expiration (`(expiry - today).days`) falls
  below the user's threshold. Many strategies close before the final days to
  avoid assignment and gamma risk.
- Delta exit: `get_delta_for_strike` or `get_greeks` on the short leg.
- Roll: close the current package and open the next one, preferably as two
  checked steps (close, confirm flat, open) unless the broker supports a
  single roll order.

`aggregate_portfolio_greeks(positions, underlying_asset)` gives net delta,
gamma, theta and vega for a risk check.

`on_filled_order(self, position, order, price, quantity, multiplier)` runs when
an order fills. Use it to record fill prices for later profit calculations.

---

## 9. Assignment and expiry

**In LumiBot backtests** (recent versions), contracts still held at expiry are
settled automatically:

- Out of the money: the contract expires worthless.
- In the money, equity or ETF option: physical delivery at the strike. A long
  call buys shares, a short put is assigned and buys shares, a short call is
  assigned and sells (or shorts) shares, a long put sells shares. If a long
  in-the-money option cannot be exercised because the account cannot support
  it, its intrinsic value is settled in cash instead.
- In the money, index option (SPX-style): cash settlement of intrinsic value.

Early assignment of short options is off by default in backtests. A strategy
can enable a conservative model with the strategy parameters
`option_early_assignment_enabled` (True or False),
`option_early_assignment_max_dte_days` and
`option_early_assignment_max_extrinsic`.

**In live trading**, the broker decides assignment and exercise, and timing can
differ from the backtest. Write code that inspects positions every iteration
and handles whatever it finds:

- Shares appear after a short put is assigned: switch to the next phase (for
  example covered calls in a wheel).
- Shares disappear after a short call is assigned: return to the first phase.
- A short leg of a spread is assigned early: the remaining long leg and the
  new stock position must be managed, usually by closing both.

Make sure the account can absorb assignment. A cash-secured put needs
`strike * 100 * contracts` in cash. A short call without the shares is an
uncovered position; only use it if the user's rules allow it and the broker
permits it.

If the user prefers never to be assigned, close or roll positions before
expiry with a days-to-expiration exit.

---

## 10. Sizing

- Cost of a long option: `premium * multiplier * contracts`.
- Max loss of a defined-risk credit spread:
  `(width - credit) * multiplier * contracts`.
- Cash-secured put collateral: `strike * multiplier * contracts`.
- Covered call: one contract per 100 shares held.

Compute contracts from `self.get_cash()` or `self.get_portfolio_value()` and
the user's risk rule, round down to an integer, and skip the trade if the
result is zero. Do not create accidental leverage by ignoring collateral already
tied up in open packages.

---

## 11. Speed

Options strategies get slow when they read many contracts.

- Fetch chains at most once per day (or per expiry change), cache in
  `self.vars`.
- Do not call `get_greeks` or `evaluate_option_market` on every strike in the
  chain. Narrow first with `find_strike_for_delta` or moneyness, then evaluate
  a handful of candidates.
- When a scanner must price many contracts, read their quotes in one batch and
  pass each quote into `evaluate_option_market(..., quote=quote)` (supported
  on LumiBot 4.6.19 and later) so the helper does not fetch again. Load
  `references/quote-snapshots-and-speed.md` for the exact contract.
- Keep broker order reads (`self.get_orders()`) out of per-candidate loops.

For general speed patterns load the `fast-lumibot-strategies` skill.

---

## 12. Building and testing on BotSpot with MCP tools

A typical workflow:

1. `create_strategy` to make a workspace (or `list_strategies` and
   `get_strategy` for an existing one). `marketplace_strategies` and
   `clone_strategy` let the user start from a published strategy.
2. `get_file` for `main.py`, then `replace_file` (whole file) or `patch_file`
   (targeted edit) with the returned `editHandle`. For a large options rewrite,
   prefer `replace_file` with the complete file, then read it back with
   `get_file` and confirm imports, the strategy class and the full order path
   are present.
3. `start_backtest` with `revisionId`, `startDate`, `endDate` and
   `dataProvider` ("alpaca" or "polygon"). Keep the first window short (a few
   weeks to a few months) and after February 2024 if using Alpaca data. Follow
   the user's wishes about whether to run a backtest at all.
4. `backtest_status` to follow progress (it also shows recent orders with
   strike, expiration and option type).
5. When done: `get_backtest_logs` for errors, warnings and your
   `log_message` output; `get_backtest_artifact` then `query_csv` on the
   trades artifact to check fills, strikes and expirations;
   `show_backtest_dashboard` or `get_backtest_visuals` for charts.
6. `list_revisions` and `set_strategy_revision` to compare or return to an
   earlier version.
7. Deployment with `start_deployment` only when the user asks, and the user
   approves it on botspot.trade.

If the backtest makes no trades, load `references/options-strategy-notes.md`.

---

## 13. Integrity rules

- Never add fake fills, dummy legs, hardcoded "proof" trades or
  `if backtesting:` branches to make a backtest trade. A strategy must trade
  because its normal entry path works.
- Preserve the user's signals, thresholds, structure, sizing and exits. Fix
  technical defects (data availability, API misuse, state handling) freely,
  but propose any change to trading rules and get the user's approval before
  saving it.
- Do not swap a multi-leg structure for a simpler one without approval. If a
  directional multi-leg idea cannot find liquid legs, you may propose a
  one-contract call or put version that still uses `evaluate_option_market`,
  and let the user decide.
- Never use `pd.np`; import numpy as `np`.
- Results from a backtest are simulations. Do not present them as expected
  future returns.
