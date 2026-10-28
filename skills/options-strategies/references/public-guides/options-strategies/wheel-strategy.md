> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# The Wheel: a Worked Pattern

Part of the `options-strategies` skill. The wheel is a two-phase cycle:

1. **Put phase.** Sell a cash-secured put. If it expires out of the money,
   keep the premium and sell another. If it is assigned, you now own 100 shares
   per contract.
2. **Call phase.** While holding the shares, sell a covered call. If it
   expires out of the money, sell another. If it is assigned, the shares are
   sold and you go back to the put phase.

This describes mechanics. It is not a recommendation to trade it.

## Design rules

- The wheel's state comes from positions, not memory. Each iteration count the
  shares of the underlying and any open short options. Shares at or above
  `100 * contracts` means call phase; otherwise put phase.
- Never open a new short option while one is still open or an order for one is
  pending.
- Cash-secured means at least `strike * 100 * contracts` in cash is available
  for the put. Check `self.get_cash()` before selling.
- Covered means you hold at least `100 * contracts` shares. Never sell more
  calls than the shares cover.
- Use liquid optionable underlyings (for example SPY, QQQ, IWM) or the user's
  named symbol. If the account is too small for one contract on that symbol,
  say so and let the user pick a cheaper underlying.
- Assignment is handled by the broker live and by LumiBot's expiry settlement
  in backtests (in-the-money equity options deliver shares at the strike). The
  code only needs to notice that the share position changed.

## Example

```python
from datetime import timedelta
from lumibot.components.options_helper import OptionsHelper
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class WheelExample(Strategy):
    parameters = {
        "symbol": "SPY",
        "put_delta": -0.30,
        "call_delta": 0.30,
        "days_to_expiry": 30,
        "contracts": 1,
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.options_helper = OptionsHelper(self)
        self.vars.chains = None
        self.vars.chains_date = None

    def _short_options(self, symbol):
        return [
            p for p in self.get_positions()
            if p.asset.asset_type == Asset.AssetType.OPTION
            and p.asset.symbol == symbol and p.quantity < 0
        ]

    def _pending_option_orders(self, symbol):
        return [
            o for o in self.get_orders()
            if o.asset.asset_type == Asset.AssetType.OPTION
            and o.asset.symbol == symbol and o.is_active()
        ]

    def on_trading_iteration(self):
        p = self.parameters
        u = Asset(p["symbol"], asset_type=Asset.AssetType.STOCK)
        today = self.get_datetime().date()

        if self._short_options(p["symbol"]) or self._pending_option_orders(p["symbol"]):
            return  # one short option at a time

        stock = self.get_position(u)
        shares = float(stock.quantity) if stock else 0.0
        contracts = p["contracts"]
        call_phase = shares >= 100 * contracts
        right = "call" if call_phase else "put"
        target_delta = p["call_delta"] if call_phase else p["put_delta"]

        if self.vars.get("chains") is None or self.vars.get("chains_date") != today:
            self.vars.chains = self.get_chains(u)
            self.vars.chains_date = today
        chains = self.vars.chains
        price = self.get_last_price(u)
        if not chains or price is None:
            return

        expiry = self.options_helper.get_expiration_on_or_after_date(
            today + timedelta(days=p["days_to_expiry"]), chains, right, underlying_asset=u
        )
        if expiry is None:
            return
        strike = self.options_helper.find_strike_for_delta(
            underlying_asset=u, underlying_price=float(price),
            target_delta=target_delta, expiry=expiry, right=right,
        )
        if strike is None:
            return
        option = self.options_helper.find_next_valid_option(u, strike, expiry, right)
        if option is None:
            return

        if not call_phase:
            collateral = float(option.strike) * 100 * contracts
            if self.get_cash() < collateral:
                self.log_message(
                    f"Not enough cash to secure the put: need {collateral:.2f}", color="yellow"
                )
                return

        ev = self.options_helper.evaluate_option_market(option)
        if not OptionsHelper.has_actionable_price(ev):
            self.log_message(f"Skip {option}: {ev.data_quality_flags}", color="yellow")
            return

        order = self.create_order(option, contracts, "sell", limit_price=ev.sell_price)
        self.submit_order(order)
        self.log_message(f"Sold {right} {option} at {ev.sell_price}", color="green")
```

## Common wheel problems

- **Strict filters find nothing.** A narrow delta band plus a strict IV or
  expiration window may never match in the tested period. Log every rejection
  reason. If the user's own rule never fires, explain it and ask before
  loosening anything, one filter at a time.
- **Not enough buying power.** Every put is rejected because collateral
  exceeds cash. Report it plainly.
- **Waiting for assignment before trading.** The first backtest does not need
  an assignment to prove the code works; a filled put sale is enough. Use a
  window long enough (for example two or three months) to see at least one
  full expiry.
- **Calls without shares.** Call-phase logic that assumes shares the account
  does not hold creates uncovered calls. Always check the share count.
- **Rolling.** If the user wants to roll before expiry, buy back the open short
  option first, confirm it is flat, then open the next one.
