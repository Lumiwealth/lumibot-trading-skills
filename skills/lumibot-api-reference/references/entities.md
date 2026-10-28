> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-entities
description: Use when inspecting or editing LumiBot strategy code that creates assets, orders, positions, options, futures, or other entities.
---

Entities are classes that represent the main components of a trading strategy. They are used to define the assets, orders, and positions that the strategy will interact with. The following are the main entities that can be used in a strategy:

class Asset:
    class OptionRight:
        CALL = "CALL"
        PUT = "PUT"

    class AssetType:
        STOCK = "stock"
        OPTION = "option"
        FUTURE = "future"
        CONT_FUTURE = "cont_future"
        FOREX = "forex"
        CRYPTO = "crypto"
        CRYPTO_FUTURE = "crypto_future"
        INDEX = "index"
        MULTILEG = "multileg"

    def __init__(
        self,
        symbol: str,
        asset_type: str = AssetType.STOCK,
        expiration: date = None,
        strike: float = 0.0,
        right: str = None,
        multiplier: int = 1,
        leverage: int = 1,
        precision: str = None,
        underlying_asset: "Asset" = None,
        auto_expiry: str = None,
    ):
        pass
        
class Chains(dict):
    '''
    Dict-like container from get_chains(). Use as dict or convenience methods.

    Structure: {"Multiplier": 100, "Exchange": "SMART",
                "Chains": {"CALL": {"2024-01-15": [100.0, 105.0, ...]}}}

    Methods:
    - chains.calls() -> {"2024-01-15": [strikes], ...}
    - chains.puts() -> {"2024-01-15": [strikes], ...}
    - chains.expirations("CALL") -> ["2024-01-15", ...]
    - chains.strikes(date_or_str, "CALL") -> [100.0, 105.0, ...]
    '''
    pass

class Bars:
    '''
    Historical price data from get_historical_prices().

    Properties:
    - df: pandas DataFrame (datetime index, open/high/low/close/volume columns)

    Usage:
    bars = self.get_historical_prices("AAPL", 100, "minute")
    if bars:
        df = bars.df
        last_close = df['close'].iloc[-1]
    '''
    pass

class Order:
    Transaction = namedtuple("Transaction", ["quantity", "price"])

    class OrderClass:
        SIMPLE = "simple"
        BRACKET = "bracket"
        OCO = "oco"
        OTO = "oto"
        MULTILEG = "multileg"

    class OrderType:
        MARKET = "market"
        LIMIT = "limit"
        STOP = "stop"
        STOP_LIMIT = "stop_limit"
        TRAIL = "trailing_stop"
        SMART_LIMIT = "smart_limit"

    class OrderSide:
        BUY = "buy"
        SELL = "sell"
        BUY_TO_COVER = "buy_to_cover"
        SELL_SHORT = "sell_short"
        BUY_TO_OPEN = "buy_to_open"
        BUY_TO_CLOSE = "buy_to_close"
        SELL_TO_OPEN = "sell_to_open"
        SELL_TO_CLOSE = "sell_to_close"

    class OrderStatus:
        UNPROCESSED = "unprocessed"
        SUBMITTED = "submitted"
        OPEN = "open"
        NEW = "new"
        CANCELLING = "cancelling"
        CANCELED = "canceled"
        FILLED = "fill"
        PARTIALLY_FILLED = "partial_fill"
        CASH_SETTLED = "cash_settled"
        ASSIGNED = "assigned"
        EXERCISED = "exercised"
        ERROR = "error"
        EXPIRED = "expired"

    ACTIVE_STATUSES = (UNPROCESSED, SUBMITTED, OPEN, NEW, PARTIALLY_FILLED)

    def __init__(
        self,
        strategy,
        asset: Union[str, Asset] = None,
        quantity: float = None,
        side: OrderSide = None,
        limit_price: float = None,
        stop_price: float = None,
        stop_limit_price: float = None,
        trail_price: float = None,
        trail_percent: float = None,
        take_profit_price: float = None,
        stop_loss_price: float = None,
        stop_loss_limit_price: float = None,
        trail_price: float = None,
        trail_percent: float = None,
        smart_limit: "SmartLimitConfig" = None,
        time_in_force: str = "day",
        good_till_date: datetime.datetime = None,
        exchange: str = None,
        position_filled: bool = False,
        quote: Asset = None,
        pair: str = None,
        date_created: datetime.datetime = None,
        type: OrderType = None,
        order_type: OrderType = None,
        order_class: OrderClass = None,
        trade_cost: float = None,
        custom_params: dict = None,
        identifier: str = None,
        avg_fill_price: float = None,
        error_message: str = None,
        child_orders: list = [],
        tag: str = "",
        status: OrderStatus = "unprocessed"):
        pass

    def is_active(self) -> bool: ...
    def is_canceled(self) -> bool: ...  # True for canceled/cancelling/error/expired terminal states.
    def is_filled(self) -> bool: ...

class SmartLimitPreset:
    FAST = "fast"
    NORMAL = "normal"
    PATIENT = "patient"

class SmartLimitConfig:
    def __init__(
        self,
        preset: str = SmartLimitPreset.NORMAL,
        final_price_pct: float = 1.0,
        slippage: float = None,  # BACKTESTING ONLY (fill simulation)
        step_seconds: int = None,
        final_hold_seconds: int = None,
    ):
        pass
        
class Quote:
    def __init__(
        self,
        asset: Asset,
        price: float = None,
        bid: float = None,
        ask: float = None,
        volume: float = None,
        timestamp: datetime.datetime = None,
        bid_size: float = None,
        ask_size: float = None,
        change: float = None,
        percent_change: float = None,
        quote_time: datetime.datetime = None,
        bid_time: datetime.datetime = None,
        ask_time: datetime.datetime = None,
        raw_data: dict = None):
        pass

    # Mid price helper
    @property
    def mid_price(self):
        pass
        

HOW TO USE ENTITIES
Entities are classes that represent different types of assets, orders, positions, and other objects in the LumiBot framework. Here are some examples of how to use them:

1.	Asset:

# Create an asset object
asset = Asset("AAPL", asset_type=Asset.AssetType.STOCK)

# Create an option asset object
option_asset = Asset(
    "AAPL", 
    asset_type=Asset.AssetType.OPTION, 
    expiration=datetime.date(2022, 1, 1),
    strike=100.00, 
    right=Asset.OptionRight.CALL
    )

# Create a cryptocurrency asset object
crypto_asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)

# Create a spot crypto pair by separating the base and quote assets.
# Do NOT create Asset("BTC-USD", asset_type=Asset.AssetType.CRYPTO) or
# Asset("BTC/USD", asset_type=Asset.AssetType.CRYPTO) as the base asset.
# For BotSpot routed backtests / IBKR-style BTC/USD, USD is commonly a FOREX
# quote asset. Some crypto venues use crypto quote assets such as USDT; preserve
# the requested quote symbol and asset type instead of silently substituting USD.
base_asset = Asset("BTC", asset_type=Asset.AssetType.CRYPTO)
quote_asset = Asset("USD", asset_type=Asset.AssetType.FOREX)
bars = self.get_historical_prices(base_asset, 50, "hour", quote=quote_asset)
last_price = self.get_last_price(base_asset, quote=quote_asset)
order = self.create_order(base_asset, 0.001, "buy", quote=quote_asset)

When repairing broken `BTC-USD` or `BTC/USD` strategy code, update the executable
asset object, not just comments or `self.symbol`. A valid repair removes
`Asset(self.symbol, asset_type=Asset.AssetType.CRYPTO)` when `self.symbol` is a
pair string, creates separate base/quote assets, and passes `quote=quote_asset`
to historical price, last price, quote, and order calls that need the pair.

# Create a forex asset object
# NOTE: `Asset` does NOT accept an `exchange=` kwarg. If you need to route a request to a
# specific exchange/venue, pass `exchange=` to methods like `get_historical_prices(...)`,
# `get_quote(...)`, or `create_order(...)` (where supported).
#
# Forex assets are base/quote pairs managed via the `quote=` argument when placing orders.
base_asset = Asset("EUR", asset_type=Asset.AssetType.FOREX)
quote_asset = Asset("USD", asset_type=Asset.AssetType.FOREX)
# Example: order = self.create_order(base_asset, 100, "buy", quote=quote_asset)

Possible values for AssetType and OptionRight:

Possible values for Asset.OptionRight:
- CALL
- PUT

Possible values for Asset.AssetType:
- STOCK
- OPTION
- FUTURE
- FOREX
- CRYPTO
- INDEX
- MULTILEG
- CRYPTO_FUTURE

# For BitUnix and some other brokers, you can also use:
assset.leverage = 10.0  # Set leverage for the asset. this will be used for futures trading.

2.	Order:

# Create an order object
order = self.create_order(
    asset, 
    quantity, 
    Order.OrderSide.BUY, 
    limit_price=100.00
    )

# Submit the order
self.submit_order(order)

Possible values for Order.OrderSide:
- BUY
- SELL
- BUY_TO_COVER
- SELL_SHORT
- BUY_TO_OPEN
- BUY_TO_CLOSE
- SELL_TO_OPEN
- SELL_TO_CLOSE

Possible values for Order.OrderType:
- MARKET
- LIMIT
- STOP
- STOP_LIMIT
- TRAIL
- SMART_LIMIT

Possible values for Order.OrderClass:
- SIMPLE
- BRACKET
- OCO
- OTO
- MULTILEG

Use OrderType for how the parent order executes (market/limit/stop/stop_limit/trailing stop/smart_limit). Use OrderClass when you need linked child orders (bracket/oco/oto/multileg).

SMART_LIMIT notes:
- Recommended for options in live trading: walks from midpoint toward the bid/ask edge over time, cancel/replace as needed, to reduce slippage.
- SmartLimitConfig.slippage is BACKTESTING ONLY (fill simulation) and does not affect live orders.
- If OrderType is SMART_LIMIT and smart_limit is omitted, LumiBot uses a default SmartLimitConfig(preset=NORMAL, final_price_pct=1.0, final_hold_seconds=120).

Possible values for Order.OrderStatus:
- UNPROCESSED
- SUBMITTED
- OPEN
- NEW
- CANCELLING
- CANCELED
- FILLED
- PARTIALLY_FILLED
- CASH_SETTLED
- ASSIGNED
- EXERCISED
- ERROR
- EXPIRED
- UNKNOWN

Use Order.ACTIVE_STATUSES for currently active/open order filters.
Use order.is_canceled() for cancel confirmation instead of exact status checks.

3.	Position:
# Properties:
# - asset: Asset object
# - quantity: float

# Get the position for an asset
position = self.get_position(asset)

# Check if the position is available
if position is not None:
    self.log_message(f"Position for {asset}: {position.quantity} shares")

# Get a list of all positions
positions = self.get_positions()

# Loop through the positions
for position in positions:
    if position.asset.symbol == "USD" and position.asset.asset_type == Asset.AssetType.FOREX:
        continue
        
    self.log_message(f"Position for {position.asset}: {position.quantity} shares")

4.	TradingFee:

# For OPTIONS strategies: use per_contract_fee (charged per contract, multiplied by order quantity)
# IBKR standard is $0.65/contract/leg. A 40-contract spread = $26.00 per leg.
trading_fee = TradingFee(per_contract_fee=0.65)

# For FUTURES strategies: also use per_contract_fee (charged per contract)
# IBKR standard is ~$0.85/contract for standard futures, ~$0.50 for micros
trading_fee = TradingFee(per_contract_fee=0.85)

# For STOCK strategies: use percent_fee (percentage of order value)
trading_fee = TradingFee(percent_fee=0.001)  # 0.1% of order value

# flat_fee is a fixed amount per ORDER (regardless of quantity), useful for platform fees
trading_fee = TradingFee(flat_fee=5.00)  # $5 per order

# You can combine fee types if needed:
trading_fee = TradingFee(flat_fee=1.00, per_contract_fee=0.65)  # $1 base + $0.65/contract

5.	Quote:

# Get a quote and access bid/ask/mid
q = self.get_quote(asset)
if q is not None:
    self.log_message(f"Bid: {q.bid}, Ask: {q.ask}, Mid: {q.mid_price}")

# Live quotes can carry bid_time, ask_time, and quote_time. Backtest quotes never
# do, with every data provider; stock backtest quotes rebuilt from bars usually
# have bid/ask equal to the bar close or missing. Run quote-age checks, and any
# check that requires those timestamps, only when not self.is_backtesting.
