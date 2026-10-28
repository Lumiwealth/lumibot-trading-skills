> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# Multi-Leg Option Structures in LumiBot

Part of the `options-strategies` skill. Every description is per one package.
Scale every leg by the same package quantity unless a ratio is stated. These
are mechanics, not recommendations.

## Leg topology

### Vertical spreads (one expiration)

| Structure | Legs | Builder |
|---|---|---|
| Bull call debit spread | buy lower-strike call, sell higher-strike call | `build_call_vertical_spread_orders(u, expiry, lower_strike, upper_strike, qty)` |
| Bear call credit spread | sell lower-strike call, buy higher-strike call | `build_call_orders(u, expiry, call_strike=short, quantity_to_trade=qty, wing_size=width)` |
| Bull put credit spread | sell higher-strike put, buy lower-strike put | `build_put_vertical_spread_orders(u, expiry, upper_strike, lower_strike, qty)` |
| Bear put debit spread | buy higher-strike put, sell lower-strike put | build manually (see below) |

A credit vertical opens for more than zero and less than its width. A debit
vertical costs more than zero and less than its width.

### Iron condor (one expiration, four ordered strikes)

1. Buy the lower put wing.
2. Sell the higher put.
3. Sell the lower call.
4. Buy the higher call wing.

Order: long put < short put < short call < long call. A standard iron condor
opens for a net credit smaller than either wing width. Max loss per package is
`max(put_width, call_width) - credit`, times the multiplier.

### Butterfly (one expiration)

Long call butterfly: buy one lower call, sell two middle calls, buy one upper
call, normally equal wing widths. A put butterfly uses puts. Keep the
1 : -2 : 1 ratio. Builder:
`build_butterfly_spread_orders(u, expiry, lower, middle, upper, qty, right)`.

### Straddle and strangle (one expiration)

- Long straddle: buy a call and a put at the same strike
  (`build_straddle_orders`).
- Long strangle: buy an out-of-the-money put and an out-of-the-money call
  (`build_strangle_orders`; the lower strike is the put, the upper is the call).
- Short straddle or strangle: sell those legs. The builders create long
  versions, so build short versions yourself. Short uncovered structures can
  have very large or unlimited loss. Only use them when the user's rules allow
  the exposure and the broker permits it.

### Calendar and diagonal (two expirations)

- Calendar: same strike and right, sell the nearer expiry, buy the farther
  (`build_calendar_spread_orders(u, strike, near_expiry, far_expiry, qty, right)`).
- Diagonal: as a calendar but with different strikes
  (`build_diagonal_spread_orders(u, near_expiry, far_expiry, near_strike, far_strike, qty, right)`).

Validate both expirations with `get_expiration_on_or_after_date` and evaluate
both quotes. Calendars are sensitive to the volatility term structure.

### Ratio spread (one expiration)

`build_ratio_spread_orders(u, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right)`
buys `buy_qty` at `buy_strike` and sells `sell_qty` at `sell_strike`. Whether
the long strike sits above or below the short strike changes the risk
completely. Confirm the direction with the user; never assume it.

## Building legs manually

```python
def _option(self, underlying, expiry, strike, right):
    return Asset(
        underlying.symbol,
        asset_type=Asset.AssetType.OPTION,
        expiration=expiry,
        strike=strike,
        right=right,
        underlying_asset=underlying,
    )

# Bear put debit spread: buy the higher put, sell the lower put
orders = [
    self.create_order(self._option(u, expiry, high_strike, "put"), qty, "buy"),
    self.create_order(self._option(u, expiry, low_strike, "put"), qty, "sell"),
]
self.options_helper.execute_orders(orders, limit_type="fastest")
```

Only use strikes that appear in `chains.strikes(expiry, "PUT")` (or "CALL").

## Complete iron condor entry

```python
from datetime import timedelta
from lumibot.components.options_helper import OptionsHelper
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class IronCondorExample(Strategy):
    parameters = {
        "symbol": "SPY",
        "days_to_expiry": 30,
        "short_delta": 0.20,
        "wing_width": 5,
        "contracts": 1,
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.options_helper = OptionsHelper(self)
        self.vars.chains = None
        self.vars.chains_date = None
        self.vars.open_package = None  # dict describing the held legs

    def _strike_listed(self, chains, expiry, strike, right):
        listed = chains.strikes(expiry, right.upper())
        return any(abs(float(s) - float(strike)) < 1e-6 for s in listed)

    def on_trading_iteration(self):
        p = self.parameters
        u = Asset(p["symbol"], asset_type=Asset.AssetType.STOCK)
        today = self.get_datetime().date()

        if self.vars.get("open_package"):
            return  # manage the open package instead (see closing below)

        if self.vars.get("chains") is None or self.vars.get("chains_date") != today:
            self.vars.chains = self.get_chains(u)
            self.vars.chains_date = today
        chains = self.vars.chains
        price = self.get_last_price(u)
        if not chains or price is None:
            return

        expiry = self.options_helper.get_expiration_on_or_after_date(
            today + timedelta(days=p["days_to_expiry"]), chains, "call", underlying_asset=u
        )
        if expiry is None:
            return

        short_put = self.options_helper.find_strike_for_delta(
            underlying_asset=u, underlying_price=float(price),
            target_delta=-p["short_delta"], expiry=expiry, right="put",
        )
        short_call = self.options_helper.find_strike_for_delta(
            underlying_asset=u, underlying_price=float(price),
            target_delta=p["short_delta"], expiry=expiry, right="call",
        )
        if short_put is None or short_call is None or short_put >= short_call:
            self.log_message("No valid short strikes", color="yellow")
            return

        long_put = short_put - p["wing_width"]
        long_call = short_call + p["wing_width"]
        if not (self._strike_listed(chains, expiry, long_put, "put")
                and self._strike_listed(chains, expiry, long_call, "call")):
            self.log_message("Wing strikes not listed", color="yellow")
            return

        put_legs = self.options_helper.build_put_vertical_spread_orders(
            u, expiry, upper_strike=short_put, lower_strike=long_put, quantity=p["contracts"]
        )
        call_legs = list(self.options_helper.build_call_orders(
            u, expiry, call_strike=short_call, quantity_to_trade=p["contracts"],
            wing_size=p["wing_width"],
        ))
        orders = put_legs + call_legs
        if any(o is None for o in orders):
            return

        for order in orders:
            ev = self.options_helper.evaluate_option_market(order.asset)
            if not OptionsHelper.has_actionable_price(ev):
                self.log_message(f"Skip: {order.asset} {ev.data_quality_flags}", color="yellow")
                return

        net = self.options_helper.calculate_multileg_limit_price(orders, "fastest")
        if net is None:
            return
        self.log_message(f"Package price {net}", color="blue")
        if not (0 < -net < p["wing_width"]):  # credit must be between 0 and the width
            self.log_message("Package price outside expected bounds", color="red")
            return

        if self.options_helper.execute_orders(orders, limit_type="fastest"):
            self.vars.open_package = {
                "expiry": expiry.isoformat(),
                "package_price": net,
                "strikes": [long_put, short_put, short_call, long_call],
            }
```

`calculate_multileg_limit_price` returns a signed sum: buys add, sells
subtract, so a credit package is negative. A sensible sanity check for this
iron condor is `0 < -net < wing_width`; skip the trade if it fails, because a
price outside those bounds usually means a leg is wrong.

## Closing a package from current positions

```python
def _close_package(self, underlying_symbol, expiry):
    closing = []
    for pos in self.get_positions():
        a = pos.asset
        if (a.asset_type == Asset.AssetType.OPTION
                and a.symbol == underlying_symbol
                and a.expiration == expiry
                and pos.quantity != 0):
            side = "sell" if pos.quantity > 0 else "buy"
            closing.append(self.create_order(a, abs(pos.quantity), side))
    if not closing:
        self.vars.open_package = None
        return
    if self.options_helper.execute_orders(closing, limit_type="fastest"):
        self.log_message(f"Closing {len(closing)} legs", color="blue")
```

Rules for closing:

- Derive sides and quantities from current signed positions, never from the
  original entry order.
- Submit all legs together. Do not close only the short legs and leave the
  longs (or the reverse) unless the user wants that.
- Clear `self.vars.open_package` only after positions show flat (check on a
  later iteration or in `on_filled_order`).
- If a close is still pending, do not send another one.
- `self.sell_all(is_multileg=True)` closes every position; use it only when the
  user wants everything closed.
