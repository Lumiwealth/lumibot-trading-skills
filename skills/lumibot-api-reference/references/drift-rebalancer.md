> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-drift-rebalancer
description: Use when LumiBot strategy code needs DriftRebalancerLogic, allocation drift calculations, or portfolio rebalancing helpers.
---

--------------------------------------------------------------
DRIFTREBALANCERLOGIC COMPONENT
--------------------------------------------------------------

`DriftRebalancerLogic` is a high-level helper that **calculates weight drift for each asset in a portfolio and, when necessary, submits the orders required to bring the portfolio back to its target allocation.**
Internally it delegates to two sub-helpers—`DriftCalculationLogic` and `DriftOrderLogic`—but you can treat the top-level class as a single “rebalancer” object with two public methods:

* **`calculate()`** – returns a `pandas.DataFrame` that shows, for every asset, its current weight, target weight, and drift.
* **`rebalance()`** – examines that DataFrame and submits the appropriate market or limit orders.

## Submission is separate from execution completion

`rebalance()` returning `True` means the drift check selected work and the order
logic ran. It does not establish confirmed fills, final weights, or cash safety
for the strategy's actual fee and fill contract. A sleep is not a fill receipt.
Do not mark a scheduled allocation complete from this return value or put all
remaining execution behind the next weekly/monthly signal date.

For a normal Python-owned whole-unit cash portfolio, load
`lumibot-strategy-building:references/rebalance-state.md` and its complete
`rebalance-example.py` source-copy integration. Keep the original signal and
weights in the strategy file; the retained execution owner finishes accepted
work between signal dates. Other supported account, fractional and order
policies retain their own actual contracts. If using this component instead,
verify those specific contracts and reconcile positions, pending orders and
spendable cash until the target is actually satisfied. Never assume the helper
name supplies missing execution guarantees.

Constructor
----------------
```python
class DriftRebalancerLogic:
    def __init__(
        *,
        strategy: Strategy,
        drift_type: DriftType = DriftType.ABSOLUTE,
        drift_threshold: Decimal = Decimal("0.10"),
        order_type: Order.OrderType = Order.OrderType.LIMIT,
        acceptable_slippage: Decimal = Decimal("0.005"),
        fill_sleeptime: int = 15,
        shorting: bool = False,
        fractional_shares: bool = False,
        only_rebalance_drifted_assets: bool = False
    ) -> None
```

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| **strategy** | `Strategy` | — | Reference to the parent `Strategy`; used for prices, orders, and logging. |
| **drift_type** | `DriftType.ABSOLUTE` &#124; `DriftType.RELATIVE` | `ABSOLUTE` | *Absolute* drift uses raw % differences; *Relative* divides the difference by the target weight. |
| **drift_threshold** | `Decimal` | `0.10` | Rebalance is triggered when `abs(drift)` exceeds this level. |
| **order_type** | `Order.OrderType` | `LIMIT` | `MARKET` or `LIMIT` orders are supported. |
| **acceptable_slippage** | `Decimal` | `0.005` | Slippage cushion when computing limit prices (0.5 %). |
| **fill_sleeptime** | `int` | `15` | Compatibility delay after sell submission; it does not confirm sale fills. |
| **shorting** | `bool` | `False` | If `True`, the rebalancer may create/cover short positions. |
| **fractional_shares** | `bool` | `False` | If `True`, share quantities are rounded to 1e-9; otherwise whole shares. |
| **only_rebalance_drifted_assets** | `bool` | `False` | If `True`, only the assets whose drift exceeds the threshold are traded; otherwise every asset is adjusted. |

Key Methods
----------------
| Method | Returns | Description |
|--------|---------|-------------|
| **`calculate(portfolio_weights)`** | `pd.DataFrame` | Computes drift for each asset. `portfolio_weights` is a list of dicts: `{"base_asset": Asset, "weight": Decimal}`. |
| **`rebalance(drift_df)`** | `bool` | If drift_df omitted, raise error; otherwise, compares each drift to `drift_threshold`, submits orders, and returns `True` if trades were sent. |

The returned DataFrame columns
```
symbol         str   # Asset symbol (e.g. "AAPL")
base_asset     Asset # Asset object
is_quote_asset bool  # True for the quote/cash asset
current_quantity Decimal
current_value   Decimal
current_weight  Decimal (0-1)
target_weight   Decimal (0-1)
target_value    Decimal
drift           Decimal (+ buy, - sell, 0 no-action, ±1 full buy/sell/cover)
```

Usage
----------------
```python
from decimal import Decimal
from lumibot.entities import Asset, Order
from lumibot.components.drift_rebalancer_logic import DriftRebalancerLogic, DriftType

class MyRebalanceStrategy(Strategy):

    def initialize(self):
        # Instantiate the component
        self.drift_rebalancer = DriftRebalancerLogic(
            strategy=self,
            drift_type=DriftType.ABSOLUTE,
            drift_threshold=Decimal("0.05"),      # 5 %
            order_type=Order.OrderType.LIMIT,
            acceptable_slippage=Decimal("0.002"), # 20 bps
            fractional_shares=True
        )

        # Define your target allocation once or update it dynamically
        self.target_weights = [
            {"base_asset": Asset("AAPL"), "weight": Decimal("0.25")},
            {"base_asset": Asset("MSFT"), "weight": Decimal("0.25")},
            {"base_asset": Asset("GOOGL"), "weight": Decimal("0.25")},
            {"base_asset": Asset("AMZN"), "weight": Decimal("0.25")}
        ]

    def on_trading_iteration(self):
        # 1. Calculate drift
        drift_df = self.drift_rebalancer.calculate(self.target_weights)

        # 2. Rebalance if needed
        if self.drift_rebalancer.rebalance(drift_df):
            self.log_message("Rebalance orders requested; fills and final weights still require reconciliation.")
```

Drift Interpretation Rules
----------------
* **`drift > 0`** → need to **BUY** (positive gap vs. target).
* **`drift < 0`** → need to **SELL** (negative gap vs. target).
* **`drift == 1 / -1`** → special signals generated by the helper:
  * `1` = start/cover a full position when you currently hold none.
  * `-1` = exit or fully short an existing position.

Additional Considerations
----------------
* **Cash management:** `DriftOrderLogic` reads cash and attempts fee-aware sizing. Verify the configured commission schedule, quantities, price bounds and actual execution path; this is not a guarantee against overdrafts for every configuration. Do not count unconfirmed sale proceeds, and inspect actual minimum cash after execution.
* **Quote asset safety:** The quote/cash asset always receives a drift of `0`; the rebalancer never trades it directly.
* **Shorting workflows:** Set `shorting=True` to allow the component to create short positions or cover existing ones automatically.
* **Backtesting vs. live:** When `strategy.is_backtesting` is `False`, the helper waits `fill_sleeptime` seconds between sell-side and buy-side orders to improve fill reliability.

The component exposes allocation drift calculations and order submission. The strategy remains responsible for its accepted schedule, unfinished execution, truthful completion state and the actual account/fee contract.
