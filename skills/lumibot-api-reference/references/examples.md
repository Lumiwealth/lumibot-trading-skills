> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-examples
description: Use when a concrete LumiBot code pattern or example is needed before generating, refining, debugging, or directly editing strategy code.
---

# Example - Minimal built-in-tools AI agent:
# This example shows the smallest useful pattern for creating and running a LumiBot AI agent
# with only built-in tools. Built-in tools are included by default -- no explicit listing needed.

def initialize(self):
    self.agents.create(
        name="research",
        default_model="<default model id from CURRENT AI MODELS>",
        system_prompt="Use LumiBot tools and return a short summary.",
    )

def on_trading_iteration(self):
    self.agents["research"].run(
        context={"symbol": "SPY", "current_datetime": self.get_datetime().isoformat()}
    )


# Example - Strict minimal AI-owned trading team:
# Every AI-owned trading strategy keeps research separate from the sole terminal
# risk/trader. Do not collapse this to one trading-enabled agent.

def initialize(self):
    # Default to daily cadence for backtest speed/cost unless the user explicitly asks for intraday.
    self.sleeptime = "1D"
    self.agents.create(
        name="researcher",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt="Research opportunities and return a bounded evidence packet. Never trade.",
    )
    self.agents.create(
        name="risk_trader",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=True,
        system_prompt="Revalidate evidence and account risk, then trade or hold.",
    )

def on_trading_iteration(self):
    research = self.agents["researcher"].run()
    self.agents["risk_trader"].run(context={"research": research.summary})


# Example - Simple leveraged ETF AI trading team:
# Use this shape when the user asks for an AI trading team that should actively
# pick among a defined universe. The universe includes bullish and inverse
# leveraged ETFs, so the team can express risk-on or risk-off views without
# short selling. Keep on_trading_iteration thin: agents debate, then the trader
# agent handles orders.

parameters = {
    "universe": ["TQQQ", "SQQQ", "UPRO", "SPXU", "UDOW", "SDOW", "TNA", "TZA", "TECL", "TECS", "SOXL", "SOXS", "WEBL", "WEBS", "FAS", "FAZ", "LABU", "LABD", "ERX", "ERY", "GUSH", "DRIP", "DRN", "DRV", "TMF", "TMV", "NUGT", "DUST"],
}

def initialize(self):
    self.sleeptime = "1D"
    self.agents.create(
        name="researcher",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt="Rank the ETFs by upside. Be direct.",
    )
    self.agents.create(
        name="bull",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt="Argue for the strongest money-making trade.",
    )
    self.agents.create(
        name="bear",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt="Point out the biggest risk, briefly.",
    )
    self.agents.create(
        name="trader",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=True,
        system_prompt="Buy one ETF from the universe aggressively. Use nearly all cash.",
    )

def on_trading_iteration(self):
    context = {
        "date": self.get_datetime().date().isoformat(),
        "universe": self.parameters["universe"],
    }
    research = self.agents["researcher"].run(
        task_prompt="Pick the strongest ETF.",
        context=context,
    )
    bull = self.agents["bull"].run(
        task_prompt="Make the bull case.",
        context={**context, "research": research.summary},
    )
    bear = self.agents["bear"].run(
        task_prompt="Make the bear case.",
        context={**context, "research": research.summary, "bull": bull.summary},
    )
    self.agents["trader"].run(
        task_prompt="Sell anything that is not the pick, then buy the best ETF with nearly all available cash.",
        context={**context, "research": research.summary, "bull": bull.summary, "bear": bear.summary},
    )


# Example - Multi-agent investment committee:
# Use this shape when the user asks for a committee, debate, bull/bear agents,
# or multiple agents working together. The research agents can inspect account
# state and data, but only the portfolio manager can mutate orders.

def initialize(self):
    self.sleeptime = "1D"
    self.agents.create(
        name="evidence_researcher",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt=(
            "Gather market data, indicators, news, SEC fundamentals, SEC filings, "
            "and FRED macro context. Return a compact evidence pack with sources, "
            "top candidates, risks, and missing data."
        ),
    )
    self.agents.create(
        name="bull_case",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt=(
            "Build the strongest long-only case from the evidence pack. "
            "Focus on upside, catalysts, fundamentals, technical setup, and invalidation points."
        ),
    )
    self.agents.create(
        name="bear_case",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=False,
        system_prompt=(
            "Attack the long case. Find red flags, downside risks, filing concerns, "
            "valuation risk, weak technicals, and reasons to avoid or reduce size."
        ),
    )
    self.agents.create(
        name="portfolio_manager",
        default_model="<default model id from CURRENT AI MODELS>",
        allow_trading=True,
        system_prompt=(
            "Review the evidence, bull case, and bear case. Check cash, positions, "
            "open orders, prices, and risk limits. Place orders only when justified."
        ),
    )

def on_trading_iteration(self):
    context = {"current_datetime": self.get_datetime().isoformat()}
    evidence = self.agents["evidence_researcher"].run(context=context)
    bull = self.agents["bull_case"].run(context={**context, "evidence": evidence.summary})
    bear = self.agents["bear_case"].run(context={**context, "evidence": evidence.summary, "bull_case": bull.summary})
    self.agents["portfolio_manager"].run(
        context={
            **context,
            "evidence": evidence.summary,
            "bull_case": bull.summary,
            "bear_case": bear.summary,
        }
    )


# Example - AI agent with built-in Alpaca/Benzinga news:
# Use this when the user asks for news access and they can provide Alpaca credentials.
# This avoids fake NewsAPI wrappers. The tool searches by symbols and date windows,
# not keywords. The agent should scan headlines/summaries first, then fetch full
# article content only when it needs to read deeper.

from lumibot.components.agents import BuiltinTools

def initialize(self):
    # Built-in tools (positions, portfolio, last_price, load_history_table,
    # duckdb.query, docs.search, orders) are ALWAYS included automatically.
    # The Alpaca news tool is added alongside them.
    self.agents.create(
        name="news_research",
        default_model="<default model id from CURRENT AI MODELS>",
        system_prompt=(
            "Use Alpaca news and market tools to make trading decisions. "
            "For news, first scan with include_content=False and limit 30 for broad market context. "
            "If an article matters, call alpaca_news again with include_content=True and exclude_contentless=True. "
            "If next_page_token is returned and the first page is not enough, call again with page_token. "
            "Use article timestamps and avoid look-ahead bias."
        ),
        tools=[BuiltinTools.news.alpaca_news()],
    )

def on_trading_iteration(self):
    result = self.agents["news_research"].run(
        context={
            "current_datetime": self.get_datetime().isoformat(),
            "news_search_guidance": (
                "Use SPY,QQQ,DIA,IWM for broad market news, or sector ETFs "
                "such as XLK,SMH, XLF,KRE, XLE,USO, XLV,XBI when single-stock news is sparse."
            ),
        }
    )
    trace_path = (result.payload or {}).get("trace_path")
    if trace_path:
        self.log_message(f"Trace: {trace_path}", color="blue")


# Example - AI agent with @agent_tool wrapping a REST API:
# @agent_tool wraps any REST API as an agent tool. This is the most reliable approach
# for explicit custom data sources. Do not invent generic APIs for strict minimal
# AI-agent requests. Always include Google-style docstrings with Args sections.
# The source code is auto-included in the tool description sent to the agent.

import os
import requests

from lumibot.components.agents import agent_tool

@agent_tool(
    name="get_economic_indicator",
    description="Fetch a US economic indicator (e.g. REAL_GDP, CPI, FEDERAL_FUNDS_RATE).",
)
def get_economic_indicator(self, indicator: str) -> dict:
    '''Fetch a US economic indicator value from a data provider.

    Args:
        indicator: The indicator function name (e.g. REAL_GDP, CPI, FEDERAL_FUNDS_RATE).

    Returns:
        A dict with the indicator data from the API.
    '''
    resp = requests.get("https://www.alphavantage.co/query", params={
        "function": indicator, "apikey": os.environ.get("ALPHAVANTAGE_API_KEY")
    }, timeout=15)
    return resp.json()

def initialize(self):
    self.agents.create(
        name="liquidity_research",
        default_model="<default model id from CURRENT AI MODELS>",
        system_prompt=(
            "Use money supply and liquidity data to decide between "
            "TQQQ and SHV. Focus on whether M2 liquidity is expanding."
        ),
        tools=[self.get_economic_indicator],
    )

def on_trading_iteration(self):
    self.agents["liquidity_research"].run()


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
# Passthrough to pandas-ta-classic (~130 indicators) — single-column returns a float:
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

# Example - Using add_marker/add_line/add_ohlc for debugging and visualization:
# -----------------------------------------------------------------------------
# This example demonstrates how to use add_marker, add_line, and add_ohlc to visualize
# important events in your strategy, such as buy/sell signals or indicator crossovers.

Continuation: `references/examples.part-02.md`
