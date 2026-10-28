> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# LumiBot examples: charts, futures, fees and quotes

Charting with add_ohlc/add_line/add_marker, Heikin Ashi, crypto futures, explicit and continuous futures, backtest fee setup, quotes, smart limit orders, Greeks, live SMA and retroactive indicators.

These snippets show methods from inside a `Strategy` subclass (`self` is the strategy). Imports such as `Asset`, `Order`, `TradingFee`, `timedelta` and `pd` are assumed. Examples are illustrations of the API, not trading recommendations.

```python
# Example - Using add_marker/add_line/add_ohlc for debugging and visualization:
# -----------------------------------------------------------------------------
# This example demonstrates how to use add_marker, add_line, and add_ohlc to visualize
# important events in your strategy, such as buy/sell signals or indicator crossovers.
# IMPORTANT: Always pass the asset parameter when you have an Asset object - this enables
# proper multi-symbol charting where indicators overlay on their corresponding asset's price chart.

# Get the historical prices for SPY for the last 100 days
asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
bars = self.get_historical_prices(asset, 100, "day")

# Check if the data is available
if bars is not None:
    # To get the DataFrame of SPY data
    df = bars.df
    last_bar = df.iloc[-1]

    # Plot the asset price as OHLC candles. This is useful for debugging and visualization.
    # Notice how we pass the asset parameter - this associates the candles with the SPY chart
    self.add_ohlc(
        "SPY",
        open=last_bar["open"],
        high=last_bar["high"],
        low=last_bar["low"],
        close=last_bar["close"],
        detail_text="SPY Price",
        asset=asset,
    )

    # Compute the 50-day SMA via self.indicators (O(1) per call, compute-once).
    # PREFER this over df["close"].rolling(50).mean(): the indicator subsystem
    # memoizes the full-series compute and indexes at the current bar automatically.
    sma_50 = self.indicators.sma(asset, length=50, timestep="day")

    # Add a line point for the moving average (continuous single-value series)
    # IMPORTANT: We pass asset=asset so this indicator overlays on the SPY price chart
    self.add_line("SMA_50", sma_50, color="blue", width=2, detail_text="50-day SMA", asset=asset)

    # Check if the last price is above the moving average
    last_ohlc = df.iloc[-1]
    if last_ohlc["close"] > sma_50:
        # Add a marker for the buy signal. Note how we only use markers to show significant events, not every price point
        # Notice how we are using markers sparingly, we are only using them when certain events happen, not every iteration (otherwise we would have way too many markers and crash the chart)
        # IMPORTANT: We pass asset=asset so this marker appears on the SPY price chart
        self.add_marker("Buy Signal", last_ohlc["close"], color="green", symbol="arrow-up", size=10, detail_text="Buy Signal", asset=asset)
    else:
        # Add a marker for the sell signal. See how we are only using markers when certain events happen, not every iteration (otherwise we would have way too many markers)
        # NOTE: We only use markers to show significant events, not every price point, this is important to avoid cluttering the chart. Only use markers when certain events happen, for continuous data use add_line
        self.add_marker("Sell Signal", last_ohlc["close"], color="red", symbol="arrow-down", size=10, detail_text="Sell Signal", asset=asset)


# Example - Plotting Heikin Ashi candles with add_ohlc():
# -----------------------------------------------------------------------------
# This example shows how to compute a derived OHLC series (Heikin Ashi) and plot it.
# Use self.vars to persist previous HA values between iterations.

import math

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
bars = self.get_historical_prices(asset, 2, "day")
if bars is not None:
    df = bars.df
    prev = df.iloc[-2]
    cur = df.iloc[-1]

    ha_close = (cur["open"] + cur["high"] + cur["low"] + cur["close"]) / 4.0
    prev_ha_close = (prev["open"] + prev["high"] + prev["low"] + prev["close"]) / 4.0
    prev_ha_open = (prev["open"] + prev["close"]) / 2.0
    ha_open = (prev_ha_open + prev_ha_close) / 2.0
    ha_high = max(cur["high"], ha_open, ha_close)
    ha_low = min(cur["low"], ha_open, ha_close)

    if all(math.isfinite(float(x)) for x in [ha_open, ha_high, ha_low, ha_close]):
        self.add_ohlc(
            "Heikin Ashi",
            open=ha_open,
            high=ha_high,
            low=ha_low,
            close=ha_close,
            detail_text="Heikin Ashi candles",
            asset=asset,
        )


# Example - Trading Crypto Futures with Bitunix:
# -----------------------------------------------------------------------------
# This example shows how to trade crypto futures using the Bitunix exchange.

# Get the last price of BTC
asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)
last_price = self.get_last_price(asset)

# Trade BTC futures on Bitunix
if last_price is not None:
    futures_asset = Asset("BTCUSDT", asset_type=Asset.AssetType.CRYPTO_FUTURE)
    # Create a market order to buy 0.1 BTC futures
    order = self.create_order(futures_asset, 0.1, "buy", order_type="market")
    self.submit_order(order)
else:
    self.log_message("BTC price data unavailable. Skipping trade.", color="red")

    
# Example - Closing a position with Bitunix (you must use the self.close_position method because it is a crypto future):
# -----------------------------------------------------------------------------
# This example shows how to close a position in a crypto future using the Bitunix exchange, you cannot simply sell the asset because it is a future and will open another position.
# To "sell" a future you must close the position using the self.close_position method, using submit_order will simply open another position.

# Get positions
positions = self.get_positions()

# Check if the position is a crypto future
for position in positions:
    if position.asset.asset_type == Asset.AssetType.CRYPTO_FUTURE:
        # Close the position
        self.close_position(position.asset)
        self.log_message(f"Closed position for {position.asset.symbol}", color="green")
    else:
        self.log_message(f"Position for {position.asset.symbol} is not a crypto future", color="red")


# Example - Trading Explicit Futures Contracts (root symbol + expiration):
# -----------------------------------------------------------------------------
# CRITICAL: For Asset.AssetType.FUTURE, the symbol MUST be the ROOT (e.g., "CL", "ES", "MES").
# The specific contract is selected via expiration=... (do NOT embed month codes/year into Asset.symbol).
# Use the correct expiration date for the contract you want to trade.

import datetime

front_expiry = datetime.date(2026, 2, 1)
next_expiry = datetime.date(2026, 3, 1)

front_asset = Asset("CL", asset_type=Asset.AssetType.FUTURE, expiration=front_expiry)
next_asset = Asset("CL", asset_type=Asset.AssetType.FUTURE, expiration=next_expiry)


# Example - Futures Calendar Spread (2-leg spread across expirations):
# -----------------------------------------------------------------------------
# Long calendar spread example: buy the front contract, sell the next contract.

orders = [
    self.create_order(front_asset, 1, "buy"),
    self.create_order(next_asset, 1, "sell"),
]
self.submit_order(orders)


# Example - Trading Futures with DataBento:
# -----------------------------------------------------------------------------
# This example shows how to trade futures contracts using DataBento for backtesting

# Define a futures asset (continuous contract)
futures_asset = Asset("MES", asset_type=Asset.AssetType.CONT_FUTURE)  # Micro E-mini S&P 500

# Get historical data for futures (for charting; indicators come from self.indicators)
bars = self.get_historical_prices(futures_asset, 100, "minute")
if bars and not bars.df.empty:
    df = bars.df

    # Compute the 20-bar SMA via self.indicators (O(1) per call, compute-once).
    # PREFER this over df["close"].rolling(20).mean() every iteration.
    current_sma = self.indicators.sma(futures_asset, length=20, timestep="minute")
    current_price = df["close"].iloc[-1]

    # Plot price as OHLC candles (STRONGLY RECOMMENDED for price data)
    last_bar = df.iloc[-1]
    self.add_ohlc("MES", open=last_bar["open"], high=last_bar["high"],
                  low=last_bar["low"], close=last_bar["close"], asset=futures_asset)

    # Plot the SMA as a line (use add_line for derived indicators)
    self.add_line("SMA_20", current_sma, color="blue", asset=futures_asset)

    # Simple trading logic: buy if price above SMA, sell if below
    if current_price > current_sma:
        order = self.create_order(futures_asset, 5, "buy")  # 5 contracts
        self.submit_order(order)
        self.log_message(f"Bought 5 contracts of {futures_asset.symbol}", color="green")
    elif current_price < current_sma:
        order = self.create_order(futures_asset, 5, "sell")  # 5 contracts
        self.submit_order(order)
        self.log_message(f"Sold 5 contracts of {futures_asset.symbol}", color="red")


# Example - Futures Backtesting (default: IBKR):
# -----------------------------------------------------------------------------
# This example shows how to backtest a futures strategy using Interactive Brokers (REST)

from lumibot.backtesting import InteractiveBrokersRESTBacktesting

class FuturesStrategy(Strategy):
    def initialize(self):
        # Keep state in self.vars; never assign arbitrary attributes such as self.asset.
        self.vars.asset = Asset("ES", asset_type=Asset.AssetType.CONT_FUTURE)  # S&P 500 futures
        
    def on_trading_iteration(self):
        # Your futures trading logic here
        pass

# Backtest with futures-specific fees
if __name__ == "__main__":
    if IS_BACKTESTING:
        # Use per-contract fees for futures (typical: $0.85 per contract for standard, $0.50 for micros)
        trading_fee = TradingFee(per_contract_fee=0.85)

        results = FuturesStrategy.backtest(
            InteractiveBrokersRESTBacktesting,
            benchmark_asset=Asset("SPY", Asset.AssetType.STOCK),
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
        )


# Example - Options Backtesting with Per-Contract Fees:
# -----------------------------------------------------------------------------
# For options strategies, use per_contract_fee instead of flat_fee.
# per_contract_fee is multiplied by the number of contracts in each order.
# IBKR charges $0.65 per contract per leg.

# On BotSpot, the options data provider is chosen by start_backtest; locally,
# datasource_class=None lets the environment pick it. Bind a provider class such as
# PolygonDataBacktesting only when the user explicitly asks for one.

class OptionsStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
        # Options trading logic here
        pass

    def on_trading_iteration(self):
        # Your options trading logic here
        pass

# Backtest with per-contract options fees
if __name__ == "__main__":
    if IS_BACKTESTING:
        # Use per_contract_fee for options (IBKR standard: $0.65/contract/leg)
        # A 40-contract spread order will cost 40 x $0.65 = $26.00 per leg
        trading_fee = TradingFee(per_contract_fee=0.65)

        results = OptionsStrategy.backtest(
            None,  # datasource_class
            benchmark_asset=Asset("SPY", Asset.AssetType.STOCK),
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
            quote_asset=Asset("USD", Asset.AssetType.FOREX),
            budget=100000,
        )


# Example - Multiple Futures Contracts:
# -----------------------------------------------------------------------------
# This example shows how to trade multiple futures contracts in one strategy

def initialize(self):
    # Portfolio of futures contracts
    self.vars.futures_assets = [
        Asset("ES", asset_type=Asset.AssetType.CONT_FUTURE),   # S&P 500
        Asset("MES", asset_type=Asset.AssetType.CONT_FUTURE),  # Micro S&P 500
        Asset("NQ", asset_type=Asset.AssetType.CONT_FUTURE),   # NASDAQ 100
        Asset("CL", asset_type=Asset.AssetType.CONT_FUTURE),   # Crude Oil
    ]

def on_trading_iteration(self):
    for asset in self.vars.futures_assets:
        # Get data for each futures contract
        bars = self.get_historical_prices(asset, 50, "day")
        if bars and not bars.df.empty:
            # Your trading logic for each futures contract
            pass


# Example - Get quote with bid/ask spread:
# -----------------------------------------------------------------------------
# This example shows how to get detailed market data including bid/ask spreads
# using get_quote which returns a Quote object with bid, ask, and other market data.

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
quote = self.get_quote(asset)
if quote is not None:
    self.log_message(f"Bid: {quote.bid}, Ask: {quote.ask}, Mid: {quote.mid_price}")


# Example - Smart limit order for options (highly recommended):
# -----------------------------------------------------------------------------
# Smart limit orders walk the bid/ask spread from midpoint toward the best achievable price.
# Use preset to control speed: FAST (aggressive), NORMAL (balanced), PATIENT (conservative).
#
# Simplest usage:
# - set order_type=Order.OrderType.SMART_LIMIT (defaults to NORMAL)
# Tuned usage:
# - pass smart_limit=SmartLimitConfig(preset=..., final_price_pct=..., final_hold_seconds=...)

option_asset = Asset("SPY", asset_type=Asset.AssetType.OPTION, expiration=expiry, strike=400, right=Asset.OptionRight.CALL)
evaluation = self.options_helper.evaluate_option_market(option_asset, max_spread_pct=0.20)
if self.options_helper.has_actionable_price(evaluation):
    order = self.create_order(option_asset, 1, "buy", order_type=Order.OrderType.SMART_LIMIT)
    self.submit_order(order)
else:
    self.log_message(f"Skipping illiquid option: {evaluation.data_quality_flags}", color="yellow")


# Example - Getting Greeks for an option (handling None):
# -----------------------------------------------------------------------------
# This example shows how to properly get and use Greeks for options trading.
# CRITICAL: get_greeks() can return None when option price data is unavailable
# (e.g., illiquid options with no recent trades or quotes). Always check for None!
# IMPORTANT: Do NOT use "return" when Greeks is None - that would block your entire
# strategy. Instead, use a conditional guard to only execute Greeks-dependent logic
# when Greeks are available.

underlying_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
underlying_price = self.get_last_price(underlying_asset)

# Create the option asset
option_asset = Asset(
    "SPY",
    asset_type=Asset.AssetType.OPTION,
    expiration=expiry_date,
    strike=400,
    right=Asset.OptionRight.CALL
)

# Get Greeks - check if None before using, but DON'T return/exit if None
greeks = self.get_greeks(option_asset, underlying_price=underlying_price)

# Use a guard pattern - only execute Greeks-dependent logic if Greeks are available
if greeks is not None:
    delta = greeks.get("delta")
    gamma = greeks.get("gamma")
    theta = greeks.get("theta")
    vega = greeks.get("vega")
    iv = greeks.get("implied_volatility")

    self.log_message(f"Option Greeks - Delta: {delta:.3f}, Gamma: {gamma:.4f}, Theta: {theta:.3f}, Vega: {vega:.3f}, IV: {iv:.2%}")

    # Example use case: only buy if delta is in a target range
    if delta is not None and 0.3 <= delta <= 0.5:
        self.log_message("Delta is in target range, considering trade", color="green")
        # Place order here
    else:
        self.log_message(f"Delta {delta} outside target range [0.3, 0.5], skipping", color="yellow")
else:
    # Greeks unavailable - log it but let the strategy continue
    self.log_message(f"Greeks unavailable for {option_asset.symbol} - option may be illiquid", color="yellow")

# Strategy continues here - other logic can still execute even if Greeks were None


# Example - Up-to-date SMA with live last price:
# -----------------------------------------------------------------------------
# This example shows how to compute a simple moving average (SMA) using both
# historical price data and the latest available price so that it reflects
# the most current market conditions (live data, since get historical prices
# may be delayed).
asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
df = self.get_historical_prices(asset, 20, "minute").df
last = self.get_last_price(asset)
sma20 = (df["close"].iloc[-19:].sum() + last) / 20
self.log_message(f"SMA-20 (live): {sma20:.4f}")


# Example - Retroactive indicators using get_historical_prices():
# Draw lines and markers at past datetimes using df.index from historical data.
# Useful for support/resistance levels, trendlines, or marking historical events.

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
bars = self.get_historical_prices(asset, 30, "day")

if bars is not None and self.vars.get("support_level") is None:
    df = bars.df
    support_price = df["low"].min()  # Detect support level
    self.vars.support_level = support_price  # Lock the value!

    # Draw retroactively across all past bars
    for dt in df.index:
        self.add_line("Support", self.vars.support_level, color="orange", dt=dt, asset=asset)

    # Add a marker at the lowest point
    lowest_idx = df["low"].idxmin()
    self.add_marker("Support Found", df.loc[lowest_idx, "low"], color="blue",
                   symbol="diamond", dt=lowest_idx, asset=asset)

# Continue drawing the locked level going forward
if self.vars.get("support_level") is not None:
    self.add_line("Support", self.vars.support_level, color="orange", asset=asset)


# Example - Retroactive indicators by storing datetimes in self.vars:
# Track datetimes/prices as you iterate, then draw retroactively when pattern detected.
# Useful for pattern detection where you want to mark the bars that formed it.

asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)

# Initialize history storage
if not hasattr(self.vars, "history"):
    self.vars.history = []
    self.vars.pattern_marked = False

# Store current datetime and price each iteration
current_price = self.get_last_price(asset)
if current_price is not None:
    self.vars.history.append((self.get_datetime(), current_price))
    self.vars.history = self.vars.history[-100:]  # Limit memory

# When pattern detected, draw retroactive markers and lines
if len(self.vars.history) >= 5 and not self.vars.pattern_marked:
    if some_pattern_condition:
        self.vars.pattern_marked = True

        # Mark the last 5 bars that formed the pattern
        for dt, price in self.vars.history[-5:]:
            self.add_marker("Pattern", price, color="purple", symbol="circle",
                           dt=dt, asset=asset, detail_text="Part of pattern")

        # Draw a trendline between two points
        high_dt, high_price = max(self.vars.history[-5:], key=lambda x: x[1])
        self.add_line("Trendline", high_price, color="red", dt=high_dt, asset=asset)
        self.add_line("Trendline", current_price, color="red", asset=asset)
```
