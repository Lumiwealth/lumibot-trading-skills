> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# LumiBot examples: options strategies and research helpers

Strike selection for a target expiry, crypto prices, OptionsHelper multi-leg executions (calendar, straddle, strangle, diagonal, ratio), market evaluation, order details, spread profit, and PerplexityHelper queries.

These snippets show methods from inside a `Strategy` subclass (`self` is the strategy). Imports such as `Asset`, `Order`, `TradingFee`, `timedelta` and `pd` are assumed. Examples are illustrations of the API, not trading recommendations.

```python
# Example - Getting strike prices for a stock option:
# -----------------------------------------------------------------------------
# This example demonstrates how to find valid option strikes for a target expiration date,
# handling cases where the desired expiration might not be available.

# Retrieve the current price of PLTR stock.
pltr_asset = Asset("PLTR", asset_type=Asset.AssetType.STOCK)
current_price = self.get_last_price(pltr_asset)
if current_price is None:
    self.log_message(f"{pltr_asset.symbol} price data unavailable. Skipping trade.", color="red")
    return

# Use self.get_datetime() instead of datetime.now() to avoid using datetime.now()
target_expiration_dt = self.get_datetime() + timedelta(days=30)
target_expiration_date = target_expiration_dt.date()
target_expiration_str = target_expiration_date.strftime("%Y-%m-%d")

# Retrieve option chain for PLTR to determine valid strikes.
chains_res = self.get_chains(pltr_asset)
if not chains_res:
    self.log_message(f"Option chains data for {pltr_asset.symbol} unavailable. Skipping trade.", color="red")
    return
call_chains = chains_res.get("Chains", {}).get("CALL")
if not call_chains:
    self.log_message(f"Call option chains data for {pltr_asset.symbol} unavailable. Skipping trade.", color="red")
    return

# Check if the target expiration exists; if not, select the closest available expiration.
if target_expiration_str in call_chains:
    expiration_str = target_expiration_str
    expiration_date = target_expiration_date
else:
    # Convert available expiration strings to date objects for comparison.
    available_expirations = []
    for exp_str in call_chains.keys():
        try:
            exp_date = self.get_datetime().__class__.strptime(exp_str, "%Y-%m-%d").date()  # using class method for conversion
            available_expirations.append(exp_date)
        except Exception as e:
            self.log_message(f"Error parsing expiration date: {exp_str}, error: {e}", color="red")
    if not available_expirations:
        self.log_message("No valid expiration dates found in option chains.", color="red")
        return
    # Choose the available expiration date that is closest to the target expiration date.
    expiration_date = min(available_expirations, key=lambda x: abs((x - target_expiration_date).days))
    expiration_str = expiration_date.strftime("%Y-%m-%d")
    self.log_message(f"Target expiration {target_expiration_str} not available. Using closest available expiration: {expiration_str}", color="yellow")

strikes = call_chains.get(expiration_str)
if not strikes or len(strikes) == 0:
    self.log_message(f"No strikes available for expiration {expiration_str}. Skipping trade.", color="red")
    return

# Example - Getting historical prices for crypto assets:
# This example shows how to retrieve historical price data for cryptocurrency assets.

asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)
bars = self.get_historical_prices(asset, 30, "minute")

if bars is not None:
    df = bars.df
    last_bar = df.iloc[-1]

    # Plot the BTC price candle for visualization
    self.add_ohlc("BTC", open=last_bar["open"], high=last_bar["high"],
                  low=last_bar["low"], close=last_bar["close"], asset=asset)

# Example - Getting the last price of a cryptocurrency asset:
# This example demonstrates how to get the current market price of a cryptocurrency.

asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)
last_price = self.get_last_price(asset)
if last_price is not None:
    self.log_message(f"Last price of BTC in USD: {last_price}")

# Example - Executing a Calendar Spread
# This example demonstrates how to create and execute a calendar spread options strategy.

underlying_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
strike = 400

dt = self.get_datetime()
near_expiry = dt + timedelta(days=7)
far_expiry = dt + timedelta(days=30)

chains = self.get_chains(underlying_asset)
if chains is None:
    self.log_message(f"Failed to retrieve options chains for {underlying_asset}.", color="red")
else:
    near_expiry = self.options_helper.get_expiration_on_or_after_date(near_expiry, chains, "call")
    far_expiry = self.options_helper.get_expiration_on_or_after_date(far_expiry, chains, "call")

    if self.options_helper.execute_calendar_spread(underlying_asset, strike, near_expiry, far_expiry, quantity=1, right="call", limit_type="mid"):
        self.log_message("Calendar spread executed successfully.", color="green")
    else:
        self.log_message("Calendar spread execution failed.", color="red")


# Example - Executing a Straddle
# This example shows how to implement a straddle options strategy.

underlying_asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)
chains = self.get_chains(underlying_asset)

dt = self.get_datetime()
expiry = dt + timedelta(days=10)

expiry = self.options_helper.get_expiration_on_or_after_date(expiry, chains, "call")

strike = 150
if self.options_helper.execute_straddle(underlying_asset, expiry, strike, quantity=1, limit_type="mid"):
    self.log_message("Straddle executed successfully.", color="green")
else:
    self.log_message("Straddle execution failed.", color="red")


# Example - Executing a Strangle
# This example demonstrates a strangle options strategy.

underlying_asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)
dt = self.get_datetime()
chains = self.get_chains(underlying_asset)
expiry = dt + timedelta(days=10)
expiry = self.options_helper.get_expiration_on_or_after_date(expiry, chains, "call")
lower_strike = 145
upper_strike = 155
if self.options_helper.execute_strangle(underlying_asset, expiry, lower_strike, upper_strike, quantity=1, limit_type="mid"):
    self.log_message("Strangle executed successfully.", color="green")
else:
    self.log_message("Strangle execution failed.", color="red")


# Example - Executing a Diagonal Spread
# -----------------------------------------------------------------------------
# This example shows how to implement a diagonal spread, combining different strikes
# and expiration dates to potentially profit from time decay and price movement.

underlying_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
dt = self.get_datetime()
chains = self.get_chains(underlying_asset)

near_expiry = dt + timedelta(days=7)
far_expiry = dt + timedelta(days=30)

# Find the nearest expiration dates for the options
near_expiry = self.options_helper.get_expiration_on_or_after_date(near_expiry, chains, "call")
far_expiry = self.options_helper.get_expiration_on_or_after_date(far_expiry, chains, "call")

near_strike = 410
far_strike = 405
if self.options_helper.execute_diagonal_spread(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity=1, right="call", limit_type="mid"):
    self.log_message("Diagonal spread executed successfully.", color="green")
else:
    self.log_message("Diagonal spread execution failed.", color="red")


# Example - Executing a Ratio Spread
# -----------------------------------------------------------------------------
# This example demonstrates a ratio spread strategy, where you buy and sell options
# at different strikes in unequal quantities to create a specific risk profile.

underlying_asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)
dt = self.get_datetime()
chains = self.get_chains(underlying_asset)
expiry = dt + timedelta(days=10)
expiry = self.options_helper.get_expiration_on_or_after_date(expiry, chains, "call")
buy_strike = 148
sell_strike = 152
buy_qty = 1
sell_qty = 2
if self.options_helper.execute_ratio_spread(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right="call", limit_type="mid"):
    self.log_message("Ratio spread executed successfully.", color="green")
else:
    self.log_message("Ratio spread execution failed.", color="red")


# Example - Evaluating Option Market Data
# -----------------------------------------------------------------------------
# Use evaluate_option_market to inspect quotes, spreads, and fallback prices before placing orders.

option_asset = Asset("SPY", asset_type=Asset.AssetType.OPTION,
                     expiration=self.get_next_expiration_date(date.today(), 5),
                     strike=400, right="call", underlying_asset=Asset("SPY"))
evaluation = self.options_helper.evaluate_option_market(option_asset, max_spread_pct=0.15)
self.log_message(f"Option evaluation: {evaluation}", color="blue")
if evaluation.spread_too_wide:
    self.log_message("Spread exceeds max threshold; skipping entry.", color="red")
elif evaluation.buy_price is not None:
    tp_price = evaluation.buy_price * 1.5
    sl_price = evaluation.buy_price * 0.6
    order = self.create_order(
        option_asset,
        1,
        Order.OrderSide.BUY,
        order_type=Order.OrderType.LIMIT,
        limit_price=evaluation.buy_price,
        order_class=Order.OrderClass.BRACKET,
        secondary_limit_price=tp_price,
        secondary_stop_price=sl_price,
    )
    self.submit_order(order)
else:
    self.log_message("No executable price available for this option right now.", color="yellow")


# Example - Getting Order Details
# -----------------------------------------------------------------------------
# This example demonstrates how to retrieve detailed information about an order,
# which can be useful for logging, analysis, or decision-making in your strategy.

order = self.strategy.create_order(
    Asset("AAPL", asset_type=Asset.AssetType.OPTION,
          expiration=self.get_next_expiration_date(date.today(), 10),
          strike=150, right="call", underlying_asset=Asset("AAPL")),
    1, "buy",
    order_type=Order.OrderType.SMART_LIMIT,
)
details = self.options_helper.get_order_details(order)
self.log_message(f"Order Details: {details}", color="blue")


# Example - Checking Spread Profit
# -----------------------------------------------------------------------------
# This example shows how to calculate the potential profit percentage of an options
# spread strategy based on current market prices compared to initial cost.

# Assume an initial cost of $500 to establish the spread
initial_cost = 500
orders = self.options_helper.build_straddle_orders(
    Asset("AAPL", asset_type=Asset.AssetType.STOCK),
    self.get_next_expiration_date(date.today(), 10),
    strike=150, quantity=1
)
profit_pct = self.options_helper.check_spread_profit(initial_cost, orders)
if profit_pct is not None:
    self.log_message(f"Spread profit percentage: {profit_pct:.2f}%", color="blue")
else:
    self.log_message("Unable to calculate spread profit percentage.", color="red")

# Example - Using PerplexityHelper for a Financial News Query to Place a Stock Order
# -----------------------------------------------------------------------------
# This example demonstrates how to use AI-powered news analysis to make trading decisions,
# by identifying stocks with positive sentiment in recent earnings reports.

# This example queries for the latest earnings reports for major tech companies.
# It then checks if any news item has a strong bullish sentiment (sentiment_score ≥ 5)
# and high popularity (popularity_metric > 100). If found, it places a buy order for that stock.

news_query = "What are the latest earnings reports for major tech companies?"
news_data = self.perplexity_helper.execute_financial_news_query(news_query)

# Iterate through each news item returned by Perplexity
for item in news_data.get("items", []):
    sentiment = item.get("sentiment_score", 0)
    popularity = item.get("popularity_metric", 0)
    if sentiment >= 5 and popularity > 100:
        symbol = item.get("symbol")
        # Create an Asset for the symbol
        asset = Asset(symbol, asset_type=Asset.AssetType.STOCK)
        # Create and submit a buy order for 100 shares
        order = self.create_order(asset, 100, "buy")
        self.submit_order(order)
        self.log_message(f"Placed a buy order for {symbol} based on positive earnings news.", color="green")
        break
        
# Example - Using PerplexityHelper for a General Query on Volatile Stocks to Place a Trade
# -----------------------------------------------------------------------------
# This example shows how to use AI-powered market analysis to identify volatile stocks
# and implement a trading strategy based on price thresholds.

# This example sends a general query to identify stocks with unusual volatility.
# It then checks if any returned symbol is trading below a $50 threshold.
# If a symbol meets the criteria, it places a buy order for that stock.

general_query = "List stocks that are showing unusually high volatility."
general_data = self.perplexity_helper.execute_general_query(general_query)

# Verify if the response contains symbols and iterate over them
if "symbols" in general_data and len(general_data["symbols"]) > 0:
    for symbol in general_data["symbols"]:
        asset = Asset(symbol, asset_type=Asset.AssetType.STOCK)
        current_price = self.get_last_price(asset)
        # Check if the current price is below $50
        if current_price and current_price < 50:
            order = self.create_order(asset, 200, "buy")
            self.submit_order(order)
            self.log_message(f"Placed a buy order for {symbol} as it is volatile and priced below $50.", color="green")
            break
else:
    self.log_message("No volatile symbols found in Perplexity response.", color="red")

# Example - Using PerplexityHelper with a Custom Schema to Trade Stocks with Strong Earnings Growth
# -----------------------------------------------------------------------------
# This example demonstrates how to use a custom schema with AI-powered analysis
# to identify stocks with strong fundamentals and analyst support for potential investments.

# This example uses a custom JSON schema to query for stocks with high earnings growth and strong analyst ratings.
# It then checks if any stock has earnings_growth > 50 and an analyst_rating ≥ 4.5.
# If the current price of the stock is below its average price target, it places a buy order.

custom_schema = {
    "query": "<string, echo the user's query>",
    "stocks": [
        {
            "symbol": "<string, ticker symbol>",
            "earnings_growth": "<float, earnings growth percentage>",
            "analyst_rating": "<float, average analyst rating from 1 to 5>",
            "price_target": "<float, consensus price target in USD>"
        }
    ],
    "summary": "<string, overall summary of findings>"
}

general_query = "List stocks with high earnings growth and strong analyst ratings."
import os  # Added to avoid hard-coded model literal in example
perplexity_model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
custom_data = self.perplexity_helper.execute_general_query(general_query, custom_schema, model=perplexity_model)

# Iterate through the stocks returned in the custom query
for stock in custom_data.get("stocks", []):
    earnings_growth = stock.get("earnings_growth", 0)
    analyst_rating = stock.get("analyst_rating", 0)
    if earnings_growth > 50 and analyst_rating >= 4.5:
        symbol = stock.get("symbol")
        asset = Asset(symbol, asset_type=Asset.AssetType.STOCK)
        current_price = self.get_last_price(asset)
        avg_target = stock.get("price_target")
        # Place a buy order if the current price is below the average target price
        if current_price and avg_target and current_price < avg_target:
            order = self.create_order(asset, 150, "buy")
            self.submit_order(order)
            self.log_message(f"Placed a buy order for {symbol} based on strong earnings growth and analyst rating.", color="green")
            break
```
