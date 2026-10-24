HOW TO LOAD AND USE COMPONENTS

Below is an example of how you might load and use any of the components (for example, OptionsHelper) in a LumiBot strategy:

    1.	At the top of your strategy file, import the component:

from lumibot.components.options_helper import OptionsHelper

	2.	In your initialize method, instantiate the component:

def initialize(self):
    # Your other initialization code here...
    self.options_helper = OptionsHelper(self)
    self.vars.options_chains = None
    self.vars.options_chain_date = None


	3.	In another lifecycle method (for example, on_trading_iteration), you can then use it:

def on_trading_iteration(self):
    underlying_asset = Asset("SPY")
    today = self.get_datetime().date()
    if self.vars.options_chains is None or self.vars.options_chain_date != today:
        self.vars.options_chains = self.get_chains(underlying_asset)
        self.vars.options_chain_date = today
    chains = self.vars.options_chains
    target_date = self.get_datetime().date() + timedelta(days=21)
    expiry = self.options_helper.get_expiration_on_or_after_date(
        target_date, chains, "call", underlying_asset=underlying_asset
    )

This pattern applies similarly to the other components (eg. DriftRebalancerLogic): import, instantiate in initialize, then call their methods as needed.

IMPORTANT: GETTING VIX DATA
To get VIX data in a strategy, use the standard lumibot data methods:
    vix_asset = Asset("VIX", asset_type=Asset.AssetType.INDEX)
    vix_price = self.get_last_price(vix_asset)
Do NOT use VixHelper. Use self.get_last_price() with an INDEX asset type instead.

HERE ARE THE COMPONENTS IN LUMIBOT:

--------------------------------------------------------------
INDICATORS SUBSYSTEM (self.indicators) -- USE THIS FIRST
--------------------------------------------------------------

PREFER THIS OVER HAND-ROLLED INDICATORS. `self.indicators` is a built-in accessor on every Strategy (no import, no instantiation required) that provides cached, O(log N) indicator lookups backed by pandas-ta-classic. If the user's strategy (or a strategy you are refining) computes indicators by hand with `df["col"].rolling(...).mean()`, `.ewm(...)`, or a `compute_indicators()` helper, prefer rewriting it to use `self.indicators` when you can make it as a local mechanical change that preserves behavior. Caching avoids repeated calculations; equivalence is not automatic. Preserve the algorithm, smoothing, initialization, historical inputs and decision timing, and verify matching values before replacing an existing calculation. Do not expand a narrow user edit into an unrelated indicator migration.

When to use it:
- Any time the strategy needs an SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, VWAP, SUPERTREND, etc. (pandas-ta-classic ships ~130 indicators).
- Any time a user-defined computation over a historical DataFrame is needed (rolling medians, custom slope, z-scores, etc.) -- use `self.indicators.custom(...)`.

Built-in passthrough (snake_case of the pandas-ta name):
    sma_50 = self.indicators.sma(asset, length=50, timestep="day")
    rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")
    macd = self.indicators.macd(asset, fast=12, slow=26, signal=9, timestep="minute")
    bbands = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")

Single-column built-ins (SMA, EMA, RSI, ATR, etc.) return the current scalar value directly, usually a float/np.float64. Do NOT access `.sma_50`, `.rsi_14`, etc. on those values:
    sma_50 = self.indicators.sma(asset, length=50, timestep="day")  # float scalar
    rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")  # float scalar

Multi-column built-ins return an IndicatorRow -- an attribute-style read-only view over the pandas Series for the CURRENT bar. Read fields directly:
    macd_line, signal_line, hist = macd.MACD_12_26_9, macd.MACDs_12_26_9, macd.MACDh_12_26_9
    upper, mid, lower = bbands.BBU_20_2_0, bbands.BBM_20_2_0, bbands.BBL_20_2_0

Always guard for None/NaN -- early in the series the indicator will not have enough history:
    sma_50 = self.indicators.sma(asset, length=50, timestep="day")
    if sma_50 is None or pd.isna(sma_50):  # import pandas as pd when using pd.isna
        return

Custom return contract: a function returning a Series yields a scalar value;
a function returning a DataFrame yields an IndicatorRow. Guard either result
for missing history before using its value or fields.

Custom indicators (replaces the legacy `compute_indicators()` helper pattern):
    def _median(df):
        return df["close"].rolling(200).median()
    median_val = self.indicators.custom("median_200", _median, asset, timestep="day")  # scalar

    # Multi-column custom indicator returning a DataFrame also works:
    def _ema_cross(df):
        fast = df["close"].ewm(span=50, adjust=False).mean()
        slow = df["close"].ewm(span=200, adjust=False).mean()
        return pd.DataFrame({"ema_fast": fast, "ema_slow": slow})
    row = self.indicators.custom("ema_cross_50_200", _ema_cross, asset, timestep="minute")
    if row is not None and row.ema_fast is not None and row.ema_slow is not None:
        ...

Key properties:
- Cache is keyed by (asset, timestep, params) and auto-invalidates via a `(len(df), df.index[-1])` fingerprint when new bars arrive -- no manual clearing needed.
- Lookup is O(log N) (searchsorted on the DataFrame index), not O(N).
- Call it inline inside `on_trading_iteration`; manual precomputation is not required. Sufficient historical warmup is still required. Check availability and None/NaN before using the result.
- Works in both backtesting and live trading.

BAR AVAILABILITY AND TIMING:
- Establish the provider/runtime bar timestamp convention and which bar was fully
  available at the decision time. An as-of timestamp alone is not proof that a
  bar was complete; use the actual data-source contract and recorded observations.
- Apply the requested completed-bar selection once. If history already ends at
  the latest completed bar, adding `.shift(1)` creates an extra delay. Do not add
  a shift merely to "avoid lookahead" or because execution happens next session.
- Preserve the calculation's original index. Align multi-timeframe inputs by
  availability time, then distinguish signal observation from order/fill time.
- Verify values against original observed bars at signal boundaries, including
  eligible signals with no fill. A strategy's own logged indicator can repeat
  the same calculation error and is not independent confirmation.

MIGRATION RULES (only for a requested or necessary behavior-preserving change):
1. If you see `df = self.get_historical_prices(asset, length=...).df` followed by `df["sma_x"] = df["close"].rolling(x).mean()` (or `.ewm(...)`, or any pandas window op producing an indicator column), consider replacing it with `sma_x = self.indicators.sma(asset, length=x, timestep=...)` (or the appropriate built-in scalar). Do not read an attribute from a single-column built-in return value.
2. If you see a `compute_indicators(self, asset)` helper, consider moving its body into a local/nested function passed into `self.indicators.custom("name", fn, asset, timestep=...)`.
3. Do this migration when you can make it as a safe, local mechanical change that preserves behavior. If user-provided logs or current context show that the API you would use is unavailable, do not use that API; explain the upgrade path instead.

--------------------------------------------------------------
CHARTED INDICATORS AND SIGNALS
--------------------------------------------------------------

Use this section when a user asks to add, inspect, explain, or fix strategy charts, indicator graphs, plotted signals, trade markers, backtest visualizations, missing indicators, missing markers, or anything involving `add_line`, `add_marker`, or `add_ohlc`.

Core rule: logging is not charting. `self.log_message(...)` explains decisions in logs, but it does not create indicator graph data. Anything the user expects to see on the backtest indicator chart must be emitted through:

- `self.add_ohlc(...)` for price candles or custom OHLC series.
- `self.add_line(...)` for continuous numeric series such as SMA, EMA, RSI, MACD, signal, histogram, Supertrend, trailing stops, hard stops, position size, support/resistance, and risk thresholds.
- `self.add_marker(...)` for sparse events such as buy/sell signals, fills, exits, stop hits, crossovers, regime changes, and rejected/skipped trade decisions that are important enough to inspect visually.

Before claiming a product bug, read the saved strategy code and check:

1. Does it compute the indicator only in local variables/logs, or does it call `add_line` for every visible series the user expects?
2. Do marker calls happen on every real trade/event path, including exits, stop-outs, reversals, and early-return branches?
3. Are the plotted values finite numbers? `None`, NaN, and infinity are skipped by LumiBot.
4. Is `asset=...` passed when an Asset object exists so the overlay lands on the asset chart?
5. Is `dt=...` aligned to the historical bar timestamp when plotting old bars, not accidentally using the current wall-clock timestamp for every point?

Function signatures:

```python
self.add_ohlc(
    name,
    open,
    high,
    low,
    close,
    color=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)

self.add_line(
    name,
    value,
    color=None,
    style="solid",
    width=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)

self.add_marker(
    name,
    value=None,
    color="blue",
    symbol="circle",
    size=None,
    detail_text=None,
    dt=None,
    plot_name="default_plot",
    asset=None,
)
```

Use `detail_text`, not `text`. The `text=` parameter does not exist and will crash.

Panel and scale guidance:

- Keep price-scale overlays on the default asset plot: OHLC candles, SMA/EMA, Bollinger bands, Supertrend, stops, trailing stops, entries/exits.
- Use a separate `plot_name` for non-price-scale series that would distort the price chart: RSI, MACD, MACD histogram, Stochastic, ADX, VIX-like filters.
- Keep pane count small. A common layout is the main price plot plus one `RSI` pane and one `MACD` pane.
- Multi-line indicators need one `add_line` call per series. A MACD panel normally has MACD line, signal line, and histogram. RSI often includes RSI, 70, 50, and 30 reference lines if those levels matter to decisions.

Safe plotting helper pattern:

```python
def _plot_line(self, name, value, *, asset, dt, color=None, plot_name="default_plot", detail_text=None, style="solid"):
    if value is None or pd.isna(value):
        return
    self.add_line(
        name,
        float(value),
        color=color,
        style=style,
        detail_text=detail_text,
        dt=dt,
        plot_name=plot_name,
        asset=asset,
    )
```

Example: chart MACD and RSI that the strategy already computes:

```python
dt = latest_bar.name if hasattr(latest_bar, "name") else self.get_datetime()
close_price = float(latest_bar["close"])

self.add_ohlc(
    "BTC",
    open=float(latest_bar["open"]),
    high=float(latest_bar["high"]),
    low=float(latest_bar["low"]),
    close=close_price,
    dt=dt,
    asset=asset,
)

self.add_line("Entry EMA", entry_ema, color="blue", width=2, dt=dt, asset=asset)
self.add_line("Exit EMA", exit_ema, color="orange", width=2, dt=dt, asset=asset)

self.add_line("MACD", macd_line, color="blue", dt=dt, plot_name="MACD", asset=asset)
self.add_line("MACD Signal", macd_signal, color="orange", dt=dt, plot_name="MACD", asset=asset)
self.add_line(
    "MACD Histogram",
    macd_hist,
    color="green" if macd_hist >= 0 else "red",
    dt=dt,
    plot_name="MACD",
    asset=asset,
)

self.add_line("RSI", rsi_value, color="purple", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 70", 70.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)
self.add_line("RSI 30", 30.0, color="gray", style="dashed", dt=dt, plot_name="RSI", asset=asset)
```

Marker rules:

- Never add a marker on every iteration for a continuous value. That makes charts unusable. Use `add_line` instead.
- Add markers only when an event happens. Examples: entry signal, submitted buy, filled buy, exit signal, submitted sell, stop triggered, crossover confirmed.
- If users complain that trades are missing from the chart, first check whether every trade path has a marker. A strategy can be missing marker emissions independently of any display problem.

Backtest artifact debugging:

- `indicators.csv` and `indicators.parquet` come from the accumulated `add_line`, `add_marker`, and `add_ohlc` calls.
- On BotSpot, read these backtest outputs with `get_backtest_artifact` (and `query_csv` for CSV tables) to confirm the strategy emitted the rows you expect before changing strategy logic.
- If `indicators.csv` or `indicators.parquet` has the expected rows but the chart does not show them, that is a display problem, not a strategy bug; report it with `send_feedback`.

--------------------------------------------------------------
OPTIONSHELPER COMPONENT
--------------------------------------------------------------

**CRITICAL: You MUST use OptionsHelper for ALL options strategies. Do NOT attempt to manually select options from chains.**
OptionsHelper validates that options have tradeable data during backtesting and handles the complexities of option selection.

OptionsHelper is a utility component for constructing and managing various options strategies.

Constructor: OptionsHelper(strategy: Strategy)

Use only the documented method names below. Do not invent OptionsHelper
methods for chain/expiration lookup. In particular,
`get_chains_expirations_with_data` does not exist and generated code that calls
it will crash. To find a usable expiration, call `self.get_chains(...)`, then
`get_expiration_on_or_after_date(...)` with `underlying_asset`, and then
`find_next_valid_option(...)` for the strike/contract.

Basic Utility Functions:
1. find_next_valid_option(underlying_asset, rounded_underlying_price, expiry, put_or_call="call") -> Optional[Asset]
   - **ALWAYS USE THIS** - Finds a valid option, checking quote data first then last_price (last trade; can be stale) as fallback
2. get_strike_deltas(underlying_asset, expiry, strikes, right, stop_greater_than=None, stop_less_than=None) -> Dict[float, Optional[float]]
3. get_delta_for_strike(underlying_asset, underlying_price, strike, expiry, right) -> Optional[float]
4. find_strike_for_delta(underlying_asset, underlying_price, target_delta, expiry, right) -> Optional[float]
   - Use keyword arguments. `underlying_price` is required and must be a float (do not pass `expiry` as arg #2).
5. calculate_multileg_limit_price(orders, limit_type) -> Optional[float]
6. evaluate_option_market(option_asset, max_spread_pct=None) -> OptionMarketEvaluation
   - Returns a dataclass with: bid, ask, last_price, spread_pct, spread_too_wide, missing_bid_ask, missing_last_price, buy_price, sell_price, used_last_price_fallback, max_spread_pct, data_quality_flags. Always log the evaluation and only place orders if OptionsHelper.has_actionable_price(evaluation) returns True; otherwise log the flags and skip.
   - Legacy helper check_option_liquidity(...) still exists but generated code should migrate to evaluate_option_market.
7. has_actionable_price(evaluation) -> bool
   - Convenience helper to confirm evaluation.buy_price is finite, positive, and not blocked by spread filters.
8. get_order_details(order) -> Dict[str, Optional[Union[str, float, date]]]
9. get_expiration_on_or_after_date(dt, chains, call_or_put, underlying_asset=None) -> Optional[date]
   - **ALWAYS PROVIDE underlying_asset** - Gets expiration on/after date, validating option has tradeable data when underlying_asset provided

Order Building Functions (build orders but do not submit them):
10. build_call_orders(underlying_asset, expiry, call_strike, quantity_to_trade, wing_size) -> Tuple[Optional[Order], Optional[Order]]
11. build_put_orders(underlying_asset, expiry, put_strike, quantity_to_trade, wing_size) -> Tuple[Optional[Order], Optional[Order]]
12. build_call_vertical_spread_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity) -> List[Order]
13. build_put_vertical_spread_orders(underlying_asset, expiry, upper_strike, lower_strike, quantity) -> List[Order]
14. build_calendar_spread_orders(underlying_asset, strike, near_expiry, far_expiry, quantity, right) -> List[Order]
15. build_butterfly_spread_orders(underlying_asset, expiry, lower_strike, middle_strike, upper_strike, quantity, right) -> List[Order]
16. build_straddle_orders(underlying_asset, expiry, strike, quantity) -> List[Order]
17. build_strangle_orders(underlying_asset, expiry, lower_strike, upper_strike, quantity) -> List[Order]
18. build_diagonal_spread_orders(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity, right) -> List[Order]
19. build_ratio_spread_orders(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right) -> List[Order]

Order Execution Functions (build orders and then submit them):
20. execute_orders(orders, limit_type=None) -> bool
21. execute_call_vertical_spread(underlying_asset, expiry, lower_strike, upper_strike, quantity, limit_type=None) -> bool
22. execute_put_vertical_spread(underlying_asset, expiry, upper_strike, lower_strike, quantity, limit_type=None) -> bool
23. execute_calendar_spread(underlying_asset, strike, near_expiry, far_expiry, quantity, right, limit_type=None) -> bool
24. execute_butterfly_spread(underlying_asset, expiry, lower_strike, middle_strike, upper_strike, quantity, right, limit_type=None) -> bool
25. execute_straddle(underlying_asset, expiry, strike, quantity, limit_type=None) -> bool
26. execute_strangle(underlying_asset, expiry, lower_strike, upper_strike, quantity, limit_type=None) -> bool
27. execute_diagonal_spread(underlying_asset, near_expiry, far_expiry, near_strike, far_strike, quantity, right, limit_type=None) -> bool
28. execute_ratio_spread(underlying_asset, expiry, buy_strike, sell_strike, buy_qty, sell_qty, right, limit_type=None) -> bool

Advanced / Risk Management Functions:
29. aggregate_portfolio_greeks(positions, underlying_asset) -> Dict[str, float]
30. check_spread_profit(initial_cost, orders, contract_multiplier=100) -> Optional[float]

USAGE

1. Import the component:
    from lumibot.components.options_helper import OptionsHelper

2. In your strategy's initialize() method, instantiate the helper:
    def initialize(self):
        self.options_helper = OptionsHelper(self)
        self.vars.options_chains = None
        self.vars.options_chain_date = None

3. In a lifecycle method (e.g., on_trading_iteration), call its functions:
    def on_trading_iteration(self):
        underlying_asset = Asset("SPY")
        today = self.get_datetime().date()
        if self.vars.options_chains is None or self.vars.options_chain_date != today:
            self.vars.options_chains = self.get_chains(underlying_asset)
            self.vars.options_chain_date = today
        chains = self.vars.options_chains

        # CRITICAL: ALWAYS use get_expiration_on_or_after_date with underlying_asset to find valid expiry with data
        target_date = self.get_datetime().date() + timedelta(days=21)
        expiry = self.options_helper.get_expiration_on_or_after_date(
            target_date, chains, "call", underlying_asset=underlying_asset  # REQUIRED to validate data exists
        )

        if expiry:
            # ALWAYS use find_next_valid_option to ensure the option has tradeable data
            strike = 400  # or calculate based on underlying price
            option = self.options_helper.find_next_valid_option(
                underlying_asset, strike, expiry, "call"  # Validates quote/price data exists
            )
            if option:
                self.log_message(f"Found valid option: {option}", color="green")

--------------------------------------------------------------            
QUIVERHELPER COMPONENT
--------------------------------------------------------------

A helper class for interacting with QuiverQuant's bulk Congress trading data.  
It handles fetching, caching, and processing congressional trading data for specified Bioguide IDs.

Constructor: QuiverHelper(strategy: Strategy)

Key Methods:
1. __init__(strategy: Strategy) -> None - Initializes the QuiverHelper component
2. load_bulk_congress_trading_data() -> None - Loads existing Congress trading data from CSV file
3. fetch_congress_trading_data(bioguide_id, page=1, page_size=50, max_retries=5) -> list - Fetches trading data from QuiverQuant API
4. get_trading_data_for_bioguide(bioguide_id, as_of_date) -> list - Gets cached or fresh trading data for a bioguide
5. calculate_portfolio(transactions, as_of_date) -> dict - Calculates portfolio holdings from transactions

HOW TO LOAD AND USE THE QUIVERHELPER COMPONENT IN YOUR STRATEGY
--------------------------------------------------------------

1. At the top of your strategy file, import the component:

from lumibot.components.quiver_helper import QuiverHelper

2.	In your initialize() method, instantiate the component:

def initialize(self):
    # Your other initialization code here…
    self.quiver_helper = QuiverHelper(self)

3.	In another lifecycle method (for example, on_trading_iteration), use its functions:

import datetime

def on_trading_iteration(self):
    # Define the Bioguide ID (e.g., for a specific congressperson)
    bioguide_id = "X000000"  # Placeholder: replace with the Bioguide ID you want to follow
    as_of_date = datetime.date.today()  # Only include transactions on or before today

    # Retrieve trading data for the given Bioguide ID
    trading_data = self.quiver_helper.get_trading_data_for_bioguide(bioguide_id, as_of_date)
    self.log_message(f"Retrieved {len(trading_data)} transactions for {bioguide_id}.")

    # Calculate the current portfolio based on the transactions
    portfolio = self.quiver_helper.calculate_portfolio(trading_data, as_of_date)
    self.log_message(f"Current portfolio for {bioguide_id}: {portfolio}")

ADDITIONAL CONSIDERATIONS
-------------------------
	•	API Key Setup:
Ensure you have a .env file with your QuiverQuant API key stored as:

QUIVER_API_KEY=<your QuiverQuant key>

The API key is loaded at runtime using dotenv.load_dotenv().

	•	Data Caching:
The component caches downloaded data in a CSV file (bulk_congress_trading_data.csv).
Cached data is reused for 24 hours to reduce API calls and improve strategy performance.
	•	Error Handling:
Robust error handling with retry logic (including exponential backoff) is implemented in fetch_congress_trading_data
to manage rate limits and transient server errors gracefully.

--------------------------------------------------------------
PERPLEXITYHELPER COMPONENT
--------------------------------------------------------------

A helper for querying Perplexity’s API via an OpenAI-compatible client.
It supports two types of queries:
	•	Financial news queries: Returns structured financial news data, ideal for getting current news such as earnings reports, analyst recommendations, and other market-moving events.
	•	General queries: Returns structured responses based on a provided (or default) JSON schema, which is useful for finding symbols that match specific criteria, identifying volatile stocks, or retrieving other trading-related insights.

This component is especially valuable because it can perform live searches to gather real-time information, ensuring your strategy has access to the latest data when making decisions.

Constructor
----------------
class PerplexityHelper:
    def __init__(self, api_key: str) -> None

Key Methods
------------
	1.	execute_financial_news_query(self, user_query: str) -> dict
	•	Description:
Executes a financial news query by constructing a prompt that adheres to a strict JSON schema, sending the query to the Perplexity API, cleaning the response, and returning structured financial news data.
	•	Expected Data Structure:
        {
            "query": "<string, echo the user's query>",
            "analysis_summary": "<string, a concise summary of the news findings>",
            "items": [
                {
                "symbol": "<string, e.g. 'AAPL' or 'TSLA'>",
                "asset_type": "<string, e.g. 'stock', 'crypto', 'index'>",
                "headline": "<string, a brief headline summarizing the news>",
                "confidence": <integer, 0-10>,
                "sentiment_score": <integer, -10 to 10>,
                "popularity_metric": <integer, non-negative count>,
                "volume_of_messages": <integer, optional>,
                "magnitude": <integer, 0-10>,
                "type_of_news": "<string, optional, e.g. 'earnings', 'ipo', 'macro'>",
                "price_targets": {
                    "low": <float, optional>,
                    "high": <float, optional>,
                    "average": <float, optional>
                },
                "additional_info": {
                    "sector": "<string, optional>",
                    "recent_events": "<string, optional>",
                    "notable_executive_actions": "<string, optional>",
                    "macro_support": "<string, optional>",
                    "related_tickers": ["<string, list of similar tickers>"],
                    "external_links": ["<string, URL>"]
                }
                }
            ]
        }

    2.	execute_general_query(self, user_query: str, custom_schema=None, model: str = "sonar") -> dict
	•	Description:
Executes a general query using either a default or a custom JSON schema. This method is ideal for retrieving general market insights, symbol lists, or other trading-related data.
	•	Expected Data Structure (Default Schema which can be customized by providing a custom_schema):
        {
            "query": "<string, echo the user's query>",
            "response_summary": "<string, brief answer (1-3 sentences)>",
            "detailed_response": "<string, optional extended details>",
            "symbols": ["<string, list of relevant symbols>"]
        }

HOW TO LOAD AND USE THE PERPLEXITYHELPER COMPONENT IN YOUR STRATEGY
--------------------------------------------------------------

	1.	Import the component:

from lumibot.components.perplexity_helper import PerplexityHelper

	2.	Instantiate the helper in your strategy’s initialize() method:

def initialize(self):
    # Needs `import os`. Read the key from the environment; never hardcode it or use a placeholder default.
    self.perplexity_helper = PerplexityHelper(api_key=os.getenv("PERPLEXITY_API_KEY"))

    3.	Call its functions in a lifecycle method (e.g., on_trading_iteration):
def on_trading_iteration(self):
    # Example for a financial news query
    news_query = "What are the latest earnings reports for major tech companies?"
    news_data = self.perplexity_helper.execute_financial_news_query(news_query)
    self.log_message(f"News Query Result: {news_data}")

    # Example for a general query with the default schema
    general_query = "Which stocks are showing high volatility today?"
    general_data = self.perplexity_helper.execute_general_query(general_query)
    self.log_message(f"General Query Result: {general_data}")

Additional Considerations
-------------------------
	•	API Key Setup:
Ensure you have a valid Perplexity API key. It can be provided directly when instantiating the helper or set as the environment variable PERPLEXITY_API_KEY.
	•	Real-Time Information:
The PerplexityHelper is highly effective at retrieving current, real-time data. Whether you need up-to-the-minute earnings reports, analyst insights, or symbol-specific data, this component leverages Perplexity’s search capabilities to keep your strategy informed with the latest market developments.

--------------------------------------------------------------
DRIFTREBALANCERLOGIC COMPONENT
--------------------------------------------------------------

`DriftRebalancerLogic` calculates weight drift per asset and submits the orders
needed to return the portfolio to its target allocation. The constructor,
parameters, drift rules and a complete example are in
`references/drift-rebalancer.md` of this skill.

--------------------------------------------------------------
AI AGENTS COMPONENT
--------------------------------------------------------------

Use this component when the user wants an AI model to make or inform trading
decisions (non-deterministic, AI-powered trading). For the full design guide
(agent teams, prompts, tools, news, cost-aware backtesting), load the
`lumibot-ai-agents` skill. This section is the API summary.

Use AI agents when the user asks for AI, agents, an LLM, or adaptive reasoning
over news, economic data or market conditions. Do not use them when the strategy
is fully expressible as deterministic rules and indicators.

Model and keys: `default_model` picks the model. When running LumiBot yourself,
supply exactly one model-provider API key that matches it:

- OpenAI: ``default_model="openai/<model>"`` needs ``OPENAI_API_KEY``
- Gemini: ``default_model="<gemini model id>"`` (bare id, no provider prefix) needs ``GEMINI_API_KEY``
- xAI Grok: ``default_model="xai/<model>"`` needs ``XAI_API_KEY``
- Anthropic Claude: ``default_model="anthropic/<model>"`` needs ``ANTHROPIC_API_KEY``

Prefer a current model the user chooses. Non-Gemini ids are routed through
LiteLLM (which ships with LumiBot). The backtest replay cache keys on the model
id, so switching models produces fresh runs rather than stale replays.

Core imports
------------

```python
from lumibot.components.agents import BuiltinTools, MCPServer, agent_tool
```

Create and run
--------------

Create each agent once in ``initialize()`` with a short system prompt (2-3
sentences). Built-in tools (positions, portfolio, prices, orders, DuckDB, docs
search) are always included automatically, even when you pass custom ``tools``
or ``mcp_servers``.

```python
def initialize(self):
    self.sleeptime = "1D"
    self.agents.create(
        name="researcher",
        default_model="<model id>",
        allow_trading=False,
        system_prompt="Research opportunities and return a bounded evidence packet. Never trade.",
    )
    self.agents.create(
        name="trader",
        default_model="<model id>",
        allow_trading=True,
        system_prompt="Revalidate the evidence and account risk, then trade or hold.",
    )

def on_trading_iteration(self):
    research = self.agents["researcher"].run(
        context={"current_datetime": self.get_datetime().isoformat()}
    )
    self.agents["trader"].run(context={"research": research.summary})
```

``AgentRunResult`` fields: ``summary``, ``text``, ``cache_hit`` (replayed from
the backtest cache), ``warning_messages``, ``tool_calls``, ``tool_results`` and
``payload`` (trace metadata, including ``trace_path`` when available).

News
----

For market news, prefer the built-in Alpaca/Benzinga tool over a custom news
API:

```python
tools=[BuiltinTools.news.alpaca_news()]
```

It uses the active Alpaca broker credentials when the broker is Alpaca;
otherwise set ``ALPACA_NEWS_API_KEY`` / ``ALPACA_NEWS_API_SECRET``. It searches
by symbol and date window, not keyword. Scan first with
``include_content=False`` (``limit`` 10 to 20 for one symbol, 30 to 50 for broad
scans), then re-read important stories with ``include_content=True`` and
``exclude_contentless=True``. Follow ``next_page_token`` with ``page_token``
when needed. In backtests the tool clamps future ``end`` timestamps to the
simulated datetime and reports ``lookahead_clamped``. For sparse single-stock
news, query ETF proxies such as ``SPY,QQQ,DIA,IWM`` or sector ETFs.

Custom tools with ``@agent_tool``
-------------------------------

Add ``@agent_tool`` only when the user names a real provider/API, supplies
reference code, or explicitly asks for a custom integration. Never invent
placeholder APIs, fake URLs or new API-key requirements. The decorator
registers the method as a tool, builds its schema from type hints and the
docstring, and includes the function source in the tool description, so always
write a Google-style docstring with an ``Args`` section.

```python
import os
import requests
from lumibot.components.agents import agent_tool

@agent_tool(
    name="get_economic_indicator",
    description="Fetch a US economic indicator (e.g. REAL_GDP, FEDERAL_FUNDS_RATE, CPI).",
)
def get_economic_indicator(self, indicator: str) -> dict:
    '''Fetch a US economic indicator value.

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
        name="research",
        default_model="<model id>",
        system_prompt="Use economic data to decide between a growth ETF and a short-term Treasury ETF.",
        tools=[self.get_economic_indicator],
    )
```

MCP servers (optional, advanced)
--------------------------------

```python
MCPServer(
    name="my-data-source",
    url="https://my-mcp-server.example.com/mcp",
    exposed_tools=["tool_a", "tool_b"],
    timeout_seconds=120,
)
```

Pass them via ``mcp_servers=[...]`` in ``self.agents.create(...)``. Keep any API
key in an environment variable, not in strategy source.

Key rules
---------

- Create agents once in ``initialize()``; never recreate them every iteration.
- Keep ``on_trading_iteration`` thin: usually just the agent ``run(...)`` calls.
- Keep exactly one trading-enabled agent (``allow_trading=True``); research
  agents use ``allow_trading=False`` and hand off through their summaries.
- A trading-enabled agent must call ``account_portfolio``, ``account_positions``
  and ``market_last_price`` for the exact symbol in the same run immediately
  before ``orders_submit_order``. LumiBot rejects blind orders with
  ``ORDER_READINESS_REQUIRED``. Say this explicitly in the trader's prompt.
- If the user wants hard deterministic execution boundaries, set every agent to
  ``allow_trading=False``, have them return structured recommendations, and let
  Python own sizing and order submission.
- AI-agent backtests call a model on every simulated iteration, so they are slow
  and can cost model usage. Keep the first backtest short (about a week of daily
  iterations) and the universe small. Do not add a deterministic
  ``self.is_backtesting`` trade that bypasses the agent path to force a result.
- Run the agent decision path before date, session or filter gates that can
  return early, or the agent never executes.
