# LumiBot examples: data, orders, positions and state

Historical prices, quotes, last prices, VIX, option and crypto and forex orders, cash accounting, chains, delta strikes, positions, `self.vars`, `self.indicators` and `set_market`.

These snippets show methods from inside a `Strategy` subclass (`self` is the strategy). Imports such as `Asset`, `Order`, `TradingFee`, `timedelta` and `pd` are assumed. Examples are illustrations of the API, not trading recommendations.

```python
# Example - Get historical prices for a single asset:
# This example demonstrates how to retrieve historical price data for a stock asset.
# IMPORTANT: When you get historical prices, plot them with add_ohlc() for candlestick visualization.

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
bars = self.get_historical_prices(asset, 2, "day")
if bars is not None:
    df = bars.df  # DatetimeIndex (tz-aware) with open/high/low/close/volume/return columns
    last_ohlc = df.iloc[-1]  # Most recent bar
    self.log_message(f"Last price of SPY: {last_ohlc['close']}, open: {last_ohlc['open']}")

    # Plot the price candle - this gives users candlestick charts instead of just numbers
    self.add_ohlc("SPY", open=last_ohlc["open"], high=last_ohlc["high"],
                  low=last_ohlc["low"], close=last_ohlc["close"], asset=asset)


# Example - VIX is an INDEX (not a stock) + guard against None/NaN:
# This example demonstrates how to fetch VIX safely before using it in a filter.

import math

vix_asset = Asset("VIX", asset_type=Asset.AssetType.INDEX)  # Never use "^VIX"
vix_val = self.get_last_price(vix_asset)
if vix_val is None or not math.isfinite(float(vix_val)):
    self.log_message("VIX unavailable (None/NaN); skipping VIX filter this iteration.", color="yellow")
else:
    self.log_message(f"VIX gate check: value {float(vix_val):.2f} vs threshold 20.0", color="blue")


# Example - Logging what triggered a decision:
rsi = self.get_indicator("RSI", symbol="SPY", period=14)
self.log_message(f"RSI gate check: value {rsi:.2f} vs sell > 70")
if rsi > 70:
    self.log_message("RSI gate passed, preparing to sell SPY", color="yellow")
    # submit_order(...) here
else:
    self.log_message("RSI gate failed, holding position")


# Example - Get historical prices for an option:
# This example shows how to retrieve historical data for an options contract.

asset = Asset(
    "AAPL",
    asset_type=Asset.AssetType.OPTION,
    expiration=datetime.datetime(2020, 1, 1),
    strike=100,
    right=Asset.OptionRight.CALL)
bars = self.get_historical_prices(asset, 30, "minute")

if bars is not None:
    df = bars.df  # DatetimeIndex (tz-aware) with OHLCV data
    last_ohlc = df.iloc[-1]
    self.log_message(f"Last price of AAPL option: {last_ohlc['close']}, open: {last_ohlc['open']}")


# Example - Create an order for an option with a trailing stop:
# This example demonstrates how to create a buy order for an option contract with a trailing stop.

from lumibot.entities import Asset, Order
import datetime

asset = Asset(
    "SPY",
    asset_type=Asset.AssetType.OPTION,
    expiration=datetime.date(2019, 1, 1),
    strike=100.00,
    right=Asset.OptionRight.CALL,
)
order = self.create_order(
    asset,
    1,
    "buy",
    order_type=Order.OrderType.TRAIL,
    trail_percent=0.05,
)
self.submit_order(order)


# Example - Create an order for a cryptocurrency:
# This example shows how to place a market order to buy a cryptocurrency.

from lumibot.entities import Asset

base = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)
quote = Asset("USD", asset_type=Asset.AssetType.FOREX)
order = self.create_order(base, 0.05, "buy", quote=quote)
self.submit_order(order)


# Example - Create an order for a FOREX pair:
# This example demonstrates how to create a limit order for a forex pair.

from lumibot.entities import Asset

asset = Asset(
   symbol="CHF",
   asset_type=Asset.AssetType.FOREX)
# NOTE: `Asset` does NOT accept a `currency=` kwarg. Forex pairs are represented by a base
# asset plus a quote asset passed via `quote=...` when placing orders.
quote = Asset("EUR", asset_type=Asset.AssetType.FOREX)
order = self.create_order(asset, 100, "buy", quote=quote, limit_price=100.00)
self.submit_order(order)


# Example - Create an order for selling an option:
# This example shows how to create and submit an order to sell an option contract.

from lumibot.entities import Asset, Order, SmartLimitConfig, SmartLimitPreset
import datetime

asset = Asset(
   "SPY",
   asset_type=Asset.AssetType.OPTION,
   expiration=datetime.date(2025, 12, 31),  # Example expiration date
   strike=100.00,
   right=Asset.OptionRight.CALL)
# Option orders: prefer SMART_LIMIT to reduce slippage (defaults to NORMAL preset if no config is provided)
order = self.create_order(asset, 1, Order.OrderSide.SELL_TO_OPEN, order_type=Order.OrderType.SMART_LIMIT)
self.submit_order(order)


# Example - Get historical prices returns None if no data is available:
# This example demonstrates proper error handling when requesting historical data.

missing_asset = Asset("XYZ", asset_type=Asset.AssetType.STOCK)
bars = self.get_historical_prices(missing_asset, 30, "minute")
if bars is None:
    self.log_message(f"No data available for {missing_asset.symbol}")
else:
    df = bars.df

    
# Example - Get historical prices for multiple assets returns None:
# This example shows how to retrieve historical prices for multiple assets at once.

assets = [
    Asset("AAPL", asset_type=Asset.AssetType.STOCK),
    Asset("MSFT", asset_type=Asset.AssetType.STOCK),
    Asset("GOOGL", asset_type=Asset.AssetType.STOCK),
]
historical_prices = self.get_historical_prices_for_assets(assets, 30, "minute")
for asset_obj, bars in historical_prices.items():
    if bars is None:
        self.log_message(f"No data available for {asset_obj}")
        continue
    df = bars.df
    last_bar = df.iloc[-1]


# Example - Comparing get_last_price vs historical bars:
# In live trading get_last_price returns the broker's latest tick; historical bars lag.

spy_stock = Asset("SPY", asset_type=Asset.AssetType.STOCK)
latest_price = self.get_last_price(spy_stock)
minute_bar = self.get_historical_prices(spy_stock, 1, "minute")


# Example - Working with Quote objects:

quote = self.get_quote(spy_stock)
if quote.ask is not None and quote.bid is not None:
    mid = quote.mid_price
    self.log_message(f"SPY bid {quote.bid}, ask {quote.ask}, mid {mid}")


# Example - Using self.vars for persistent state:

self.vars.signal_counts = self.vars.get("signal_counts", {})
self.vars.signal_counts.setdefault("SPY", 0)
self.vars.signal_counts["SPY"] += 1


# Example - Cash accounting for contributions, distributions, and financing:
# Use the explicit cash-accounting methods instead of faking cashflows as returns.

def initialize(self):
    self.configure_cash_financing(
        enabled=True,
        account_mode="margin",
        day_count_basis=360,
        missing_rate_policy="carry_forward",
    )
    self.set_cash_financing_rates(
        credit_rate_annual=0.02,
        debit_rate_annual=0.08,
    )


def on_trading_iteration(self):
    if self.first_iteration:
        self.deposit_cash(5000, reason="initial_contribution")

    if self.vars.get("take_distribution", False):
        self.withdraw_cash(1000, reason="quarterly_distribution")

    if self.vars.get("apply_admin_fee", False):
        self.adjust_cash(-25, reason="admin_fee")

        
# Example - Get chains for an asset:
# This example demonstrates how to retrieve options chains for a stock.

chains_asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)
chains = self.get_chains(chains_asset)

# Dict-style access (backwards compatible):
calls_dict = chains["Chains"]["CALL"]
puts_dict = chains["Chains"]["PUT"]

# Convenience methods (cleaner):
calls = chains.calls()  # All CALL options
puts = chains.puts()  # All PUT options
expirations = chains.expirations("CALL")  # List of expiration dates

# Get strikes for a specific date (can pass date object or string):
expiry_date = datetime.date(2024, 1, 15)
strikes = chains.strikes(expiry_date, "CALL")  # Pass date object directly

# Note: self.get_chains() is very slow, so cache results when possible.

# Example - Selecting a delta-based strike with OptionsHelper (keyword args only):
# This snippet shows the canonical pattern for strike selection by delta.

import datetime

underlying_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
chains = self.get_chains(underlying_asset)
if chains is None:
    self.log_message("No option chains available for SPY", color="yellow")
    return

target_dt = self.get_datetime() + datetime.timedelta(days=7)
expiry = self.options_helper.get_expiration_on_or_after_date(target_dt, chains, "call", underlying_asset=underlying_asset)
if expiry is None:
    self.log_message("No valid expiration found on/after target date", color="yellow")
    return

underlying_price = self.get_last_price(underlying_asset)
if underlying_price is None:
    self.log_message("Underlying price unavailable; cannot select strikes", color="yellow")
    return

call_strike = self.options_helper.find_strike_for_delta(
    underlying_asset=underlying_asset,
    underlying_price=float(underlying_price),
    target_delta=0.25,
    expiry=expiry,
    right="call",
)


# Example - Chains for an asset with a specific expiration date
# This example shows how to read/filter chains for diagnostics/validation (not for brute-force delta searches).

underlying_asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)

chains_result = self.get_chains(underlying_asset)
if not chains_result:
    self.log_message("Could not retrieve options chains for NVDA")
    return

chains = chains_result.get('Chains')
call_chains = chains.get('CALL')
expiry = expiration_date.strftime('%Y-%m-%d')
call_chain_for_expiry = call_chains.get(expiry)  # Returns a list of strike prices
if call_chain_for_expiry is None or len(call_chain_for_expiry) == 0:
    self.log_message(f"No options found for expiration date {expiration_date}")
    return

# Get the strike closest to the current price
current_price = self.get_last_price(underlying_asset)
atm_strike = min(call_chain_for_expiry, key=lambda x: abs(x - current_price))

put_chains = chains.get('PUT')
put_chain_for_expiry = put_chains.get(expiry)  # Returns a list of strike prices
if put_chain_for_expiry is None or len(put_chain_for_expiry) == 0:
    self.log_message(f"No put options found for expiration date {expiration_date}")


# Example - Getting details about a position:
# This example demonstrates how to retrieve information about a specific position.

position = self.get_position(Asset("AAPL", asset_type=Asset.AssetType.STOCK))

if position is not None:
    self.log_message(f"Position for AAPL: {position.quantity} shares")

quantity = position.quantity


# Example - Getting the last price of an asset:
# This example shows how to get the current price of an option position.

asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)
current_datetime = self.get_datetime()
current_date = current_datetime.date()

positions = self.get_positions()
for position in positions:
    asset = position.asset
    if asset.asset_type == Asset.AssetType.OPTION and asset.underlying_asset.symbol == self.symbol:
        expiration_date = asset.expiration
        days_to_expiration = (expiration_date - current_date).days

        if expiration_date < current_date:
            self.log_message(f"Option {asset} has expired")
            continue

        # For options, prefer quote-derived mark pricing (bid/ask/mid). Last trade can be stale.
        quote = self.get_quote(asset)
        if quote is not None and quote.bid is not None and quote.ask is not None:
            self.log_message(f"{asset} bid {quote.bid}, ask {quote.ask}, mid {quote.mid_price}")
        else:
            last_trade = self.get_last_price(asset)
            self.log_message(f"{asset} last trade {last_trade} (quote unavailable)")
        break
        
# Example - Selling a position:
# This example demonstrates how to liquidate an existing stock position.

position = self.get_position(Asset("AAPL", asset_type=Asset.AssetType.STOCK))
if position is not None:
    asset = position.asset
    quantity = position.quantity
    order = self.create_order(asset, quantity, Order.OrderSide.SELL)
    self.submit_order(order)

# Example - Using variables in the strategy:
# This example shows how to use persistent variables in your strategy.

# Use self.vars for variables that need to persist between trading iterations
# NOTE: self.vars prevents overwriting any built-in attributes of the Strategy class
def initialize(self):
    self.vars.my_variable = 10

def on_trading_iteration(self):
    self.log_message(f"My variable is {self.vars.my_variable}")
    self.vars.my_variable += 1

# Example - Another example of using variables in the strategy:
# This example demonstrates how to safely check if a persistent variable exists.

def on_trading_iteration(self):
    # Check if the variable exists before using it
    if not hasattr(self.vars, "filled_count"):
        self.vars.filled_count = 0

    self.log_message(f"The number of filled orders is {self.vars.filled_count}")

def on_filled_order(self, position, order, price, quantity, multiplier):
    if not hasattr(self.vars, "filled_count"):
        self.vars.filled_count = 0

    self.vars.filled_count += 1

    
# Example - Preferred way to compute technical indicators (self.indicators):
# self.indicators is the PRIMARY way to get technical indicator values in LumiBot.
# It computes any indicator ONCE over the full bar series and returns the value at
# the current bar in O(1). This replaces the slower pattern of calling
# get_historical_prices + df["close"].rolling(...).mean() every iteration.
#
# Passthrough to pandas-ta-classic (~130 indicators): single-column returns a float:
#     sma200 = self.indicators.sma(asset, length=200, timestep="day")
#     rsi14  = self.indicators.rsi(asset, length=14, timestep="day")
#     ema50  = self.indicators.ema(asset, length=50, timestep="day")
#     atr14  = self.indicators.atr(asset, length=14, timestep="day")
#
# Multi-column indicators return an IndicatorRow (attribute access, dots normalized to underscores):
#     bb   = self.indicators.bbands(asset, length=20, std=2, timestep="day")
#     macd = self.indicators.macd(asset, fast=12, slow=26, signal=9, timestep="day")
#     lower_band = bb.BBL_20_2_0
#     upper_band = bb.BBU_20_2_0
#
# Custom / user-defined indicators (function receives the full-history DataFrame,
# returns a Series (scalar lookup) or DataFrame (IndicatorRow lookup) as of strategy time):
#     def median_200(df):
#         return df.assign(median_200=df["close"].rolling(200).median())
#
#     row = self.indicators.custom("median_200", median_200, asset, timestep="day")
#     if row is None:
#         return  # not enough bars yet
#     median_val = row["median_200"]
#
# When porting an existing strategy, replace every `df["col"] = df["close"].rolling(...)...`
# pattern inside on_trading_iteration with a `self.indicators.<name>` / `self.indicators.custom`
# call; do not hand-roll rolling windows per iteration.

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
sma50 = self.indicators.sma(asset, length=50, timestep="day")  # float at the current bar
rsi14 = self.indicators.rsi(asset, length=14, timestep="day")
if sma50 is None or rsi14 is None:
    return  # data source has no bars for this asset/timestep yet

    
# Example - Ignoring USD as a position: 
# This example demonstrates how to filter out USD cash positions when processing your portfolio.

positions = self.get_positions()

for position in positions:
    if position.asset.symbol == "USD" and positon.asset.asset_type == Asset.AssetType.FOREX:
        continue
    # Do something with the position

# Example - Set Market Example:
# This example shows how to configure your strategy to operate outside normal market hours.

# Set the market to 24/7 for crypto trading or pre/post market strategies
def initialize(self):
    self.set_market("24/7")
    self.sleeptime = "15S"  # Run every 15 seconds

def on_trading_iteration(self):
    dt = self.get_datetime()

    if dt.weekday() < 5:  # Check if it's a weekday
        self.log_message(f"Current datetime: {dt}")
    else:
        self.log_message("It's the weekend!")
```
