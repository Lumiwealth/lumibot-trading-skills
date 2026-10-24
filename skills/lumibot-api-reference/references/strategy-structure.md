Below is the standard single-file LumiBot strategy shape. Adapt it:

```python
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset, TradingFee, Order
import pandas as pd
from datetime import datetime

from lumibot.credentials import IS_BACKTESTING

"""
Strategy Description
--------------------
This strategy is an example demonstrating how to buy certain stocks 
on the first iteration. It's purely an example for LumiBot usage.
"""

class StockExampleAlgo(Strategy):
    parameters = {
        # "symbols": ["AAPL", "MSFT"]
    }

    def initialize(self):
        # This is called once at the start
        self.sleeptime = "1D" # Can be "1D", "1M", "1S" for days, minutes, seconds. Eg. "15S" for 15 seconds

    def on_trading_iteration(self):
        # This runs on each trading iteration
        symbols = self.parameters.get("symbols")
        if self.first_iteration:
            cash = self.get_cash()
            portion = (cash * 0.98) / len(symbols)
            for symbol in symbols:
                price = self.get_last_price(symbol)
                shares = int(portion // price)
                order = self.create_order(symbol, shares, Order.OrderSide.BUY)
                self.submit_order(order)

if __name__ == "__main__":
    if IS_BACKTESTING:
        ####
        # Backtesting
        ####
        trading_fee = TradingFee(percent_fee=0.001)

        # Must use the correct signature:
        result = StockExampleAlgo.backtest(
            datasource_class=None,
            benchmark_asset=Asset("SPY", Asset.AssetType.STOCK), # Use SPY as the benchmark asset unless otherwise specified, most people only care about relative performance to SPY
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
            quote_asset=Asset("USD", Asset.AssetType.FOREX), # Quote asset for the strategy. Most users don't want to change this, keep it as USD unless otherwise specified.
        )
    else:
        ####
        # Live Trading
        ####

        # This is all you need for live trading, the broker is chosen automatically based on env variables so you don't need to worry about which broker to use
        trader = Trader()
        strategy = StockExampleAlgo(
            quote_asset=Asset("USD", Asset.AssetType.FOREX), # Quote asset for the strategy. Most users don't want to change this, keep it as USD unless otherwise specified.
        )
        trader.add_strategy(strategy)
        strategies = trader.run_all()
```

Notes:

- Keep the whole strategy in one file with one `parameters = {}` dictionary at the top of the class. Do not set parameters again in the `__main__` block.
- `datasource_class=None` lets the environment choose the backtesting data provider. On BotSpot, the backtest run window and data provider are set by `start_backtest`, so do not hardcode backtest dates in the script.
- The broker for live trading is chosen from environment variables. Strategy code should never contain broker keys or broker-specific API calls.
