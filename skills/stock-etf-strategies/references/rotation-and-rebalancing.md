# Rotation and Rebalancing

Part of the `stock-etf-strategies` skill. Covers fixed-weight portfolios,
momentum rotation (hold the top N of a universe) and periodic rebalancing.
Illustrations only, not recommendations.

## Rules to confirm

- Universe and target weights (fixed, equal weight, ranked).
- Ranking metric for rotation (for example trailing return over N days).
- Rebalance schedule (monthly, weekly, on signal) and any tolerance band.
- What to hold when nothing qualifies (cash, a defensive ETF).

## Example: monthly rebalance to target weights

```python
from lumibot.entities import Asset
from lumibot.strategies import Strategy


class TargetWeights(Strategy):
    parameters = {
        "weights": {"SPY": 0.6, "TLT": 0.3, "GLD": 0.1},
        "tolerance": 0.02,  # skip trades smaller than 2% of portfolio value
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.vars.last_rebalance_month = None

    def on_trading_iteration(self):
        dt = self.get_datetime()
        month_key = f"{dt.year}-{dt.month:02d}"
        if self.vars.get("last_rebalance_month") == month_key:
            return

        weights = self.parameters["weights"]
        assets = {s: Asset(s, asset_type=Asset.AssetType.STOCK) for s in weights}
        prices = self.get_last_prices(list(assets.values()))
        if any(prices.get(a) in (None, 0) for a in assets.values()):
            self.log_message("Missing prices, skipping rebalance", color="yellow")
            return

        total = self.get_portfolio_value()
        tolerance_value = total * self.parameters["tolerance"]

        sells, buys = [], []
        for symbol, asset in assets.items():
            price = float(prices[asset])
            position = self.get_position(asset)
            held = float(position.quantity) if position else 0.0
            target_qty = int((total * weights[symbol]) // price)
            delta = target_qty - held
            if abs(delta) * price < tolerance_value:
                continue
            if delta < 0:
                sells.append(self.create_order(asset, abs(delta), "sell"))
            elif delta > 0:
                buys.append((asset, delta, price))

        for order in sells:
            self.submit_order(order)

        # Buy only with cash on hand now; sales free cash after they fill.
        budget = self.get_cash() * 0.99
        for asset, qty, price in buys:
            affordable = int(min(qty, budget // price))
            if affordable > 0:
                self.submit_order(self.create_order(asset, affordable, "buy"))
                budget -= affordable * price

        self.vars.last_rebalance_month = month_key
```

In a backtest, sells and buys submitted in the same iteration usually both
fill, but sizing the buys from cash before the sells fill keeps behavior safe
live. If the user wants the buys to use the sale proceeds the same day, run
the buy step on the next iteration after sales fill (track a "pending buys"
flag in `self.vars`).

## Example: momentum rotation (top N)

```python
def _rank(self, assets, lookback):
    history = self.get_historical_prices_for_assets(assets, length=lookback + 1, timestep="day")
    scores = {}
    for asset in assets:
        bars = history.get(asset) if history else None
        if bars is None or bars.df is None or len(bars.df) < lookback + 1:
            continue
        closes = bars.df["close"]
        scores[asset] = float(closes.iloc[-1] / closes.iloc[-(lookback + 1)] - 1)
    return sorted(scores, key=scores.get, reverse=True)
```

Then:

1. Pick the top N from the ranking (skip assets with missing data rather than
   ranking them as zero).
2. Sell holdings that are no longer in the top N.
3. Buy the new top N at equal weight, sized from available cash with a
   running budget as above.
4. Record the rotation date in `self.vars`.

## Pitfalls

- **Double rebalancing after a restart.** Store the last rebalance key in
  `self.vars` and check it first.
- **Overspending.** Sum the cost of every buy against one cash budget.
- **Missing prices.** Skip the rebalance (and log it) rather than selling
  everything because one price is missing.
- **Survivorship bias.** A universe of today's leaders flatters the backtest.
- **Turnover.** Frequent rebalances with tiny deltas add costs. A tolerance
  band helps, but only use one if the user wants it.
- **Fractional shares.** If the user wants exact weights with small
  accounts, fractional quantities help, but confirm the deployment broker
  supports them (see the main skill).
