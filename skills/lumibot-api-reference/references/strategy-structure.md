> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-strategy-structure
description: Use when reviewing or editing overall LumiBot strategy file shape, imports, class structure, main block, and runnable script organization.
---

The initial-purchase example below intentionally acts only on its first
iteration. Use that lifetime only for an explicitly initial/one-time policy.
For recurrent entry Rules, evaluate each eligible session/signal and retain only
the owned unresolved-order/position duplicate blocker. Do not copy the example's
`self.first_iteration` guard or add a lifetime `entry_submitted` flag that prevents
all future legitimate entries. Account-budget anchors are different: persist the
first verified value before unrelated missing-price/history returns, then keep
that baseline rather than resetting it when a new entry is allowed.

Below is an example snippet you can adapt:

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
            parameters=params, # Only needed if you load a config
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

We want your code to replicate or adapt that structure. Use a single code block, no triple backticks, with inline comments.
