The following methods and properties are available in the Strategy class:

ORDER MANAGEMENT

create_order(self, asset: Union[str, Asset], quantity: Union[int,float,Decimal,str], side: str, limit_price: Optional[float] = None, stop_price: Optional[float] = None, stop_limit_price: Optional[float] = None, trail_price: Optional[float] = None, trail_percent: Optional[float] = None, time_in_force: str = "gtc", good_till_date: Optional[datetime.datetime] = None, take_profit_price: Optional[float] = None, stop_loss_price: Optional[float] = None, stop_loss_limit_price: Optional[float] = None, secondary_limit_price: Optional[float] = None, secondary_stop_price: Optional[float] = None, secondary_stop_limit_price: Optional[float] = None, secondary_trail_price: Optional[float] = None, secondary_trail_percent: Optional[float] = None, position_filled: Optional[float] = None, exchange: Optional[str] = None, quote: Optional[Asset] = None, pair: Optional[str] = None, order_type: Optional[Order.OrderType] = None, order_class: Optional[Order.OrderClass] = None, type: Optional[Order.OrderType] = None, custom_params: Optional[dict] = None, smart_limit: Optional[SmartLimitConfig] = None) -> Order  (NOTE: For bracket/OTO exits, prefer secondary_* fields; take_profit_price/stop_loss_price/stop_loss_limit_price are deprecated aliases. For options, prefer smart_limit=SmartLimitConfig(preset=SmartLimitPreset.NORMAL) over market orders.)
submit_order(self, order: Union[Order, List[Order]], **kwargs) -> Union[Order, List[Order], None]
submit_orders(self, orders: List[Order], **kwargs) -> List[Order] (deprecated; call submit_order with a list) 
cancel_order(self, order: Order) -> None - A cancel request is not terminal confirmation. Reconcile get_order(order.identifier), terminal status and actual fills/positions. Pending-cancel/cancelling may make is_active() false but still leaves unresolved fill exposure; retain the affected order blocker until reconciled. Do not put a broker refresh before an armed cancellation deadline.
cancel_orders(self, orders: List[Order]) -> None
cancel_open_orders(self) -> None
get_selling_order(self, position: Position) -> Optional[Order]
sell_all(self, cancel_open_orders: bool = True, is_multileg: bool = False) -> None
get_order(self, identifier: str) -> Optional[Order] - In live trading, refreshes broker order state before returning when supported; prefer this direct lookup for same-order checks after submit_order
get_orders(self, identifiers: Optional[Union[str,List[str]]] = None, statuses: Optional[Union[Order.OrderStatus,List[Order.OrderStatus],Tuple[Order.OrderStatus,...],Set[Order.OrderStatus]]] = None) -> List[Order] - In live trading, refreshes broker order state before returning when supported. Use statuses=Order.ACTIVE_STATUSES for active/open order checks. Status filters must use Order.OrderStatus enums, not strings. Broad broker order lists can lag briefly after submit; use get_order(order.identifier) for same-order checks.
get_asset_potential_total(self, asset: Union[str, Asset]) -> Union[float,Decimal]
close_position(self, asset: Union[str,Asset], fraction: float = 1.0) -> Optional[Order] - Closes that asset using its actual position quantity, including fractional holdings. A returned order is a submission, not proof of a flat position. Do not floor a full exit to an integer or substitute sell_all() for an asset-scoped exit.


## Cash-bounded stock entry and complete exits

Executable cash-bounded stock-entry and full-exit examples live in the
`lumibot-strategy-building` skill. Use it when implementing or repairing
cash-only execution. The API signatures above remain the method contract;
those examples are strategy code, not additional built-in Strategy methods.

ACCOUNT MANAGEMENT

get_portfolio_value(self) -> Optional[float] - Forces a live broker refresh; returns None if the broker balance refresh fails instead of returning stale/zero data.
get_cash(self) -> Optional[float] - Forces a live broker refresh; returns None if the broker cash refresh fails instead of returning stale/zero data.
Do not use undocumented account helpers such as `get_portfolio()` in generated strategies. Use `get_portfolio_value()` and `get_cash()` and handle `None`.
adjust_cash(self, amount: float, reason: str = "manual_adjustment", allow_negative: Optional[bool] = None) -> float - Backtesting-only direct cash adjustment. Positive amounts add cash, negative amounts remove cash.
deposit_cash(self, amount: float, reason: str = "deposit") -> float - Backtesting-only external cash contribution. Use for funding events, not for strategy alpha.
withdraw_cash(self, amount: float, reason: str = "withdrawal", allow_negative: Optional[bool] = None) -> float - Backtesting-only external cash withdrawal or distribution.
configure_cash_financing(self, enabled: bool = True, account_mode: str = "margin", day_count_basis: int = 360, missing_rate_policy: str = "carry_forward") -> None - Backtesting-only financing configuration for cash balances, margin debit, and credit accrual rules.
set_cash_financing_rates(self, credit_rate_annual: Optional[float] = None, debit_rate_annual: Optional[float] = None) -> None - Backtesting-only annualized financing rates. Use None to keep the prior side unchanged.
get_position(self, asset: Union[str, Asset]) -> Optional[Position] - Returns a fresh broker-refreshed live Position (asset, quantity, avg_fill_price, orders; crypto hold/available) and auto-maps continuous futures to the active contract.
get_positions(self) -> List[Position] - Fresh broker-refreshed live list of Position objects; excludes the quote/cash asset unless include_cash_positions=True; unknown broker asset types are returned as Asset.AssetType.UNKNOWN.

DATA

get_last_price(self, asset: Union[str, Asset], quote: Optional[Asset] = None, exchange: Optional[str] = None) -> Optional[float] - Trade-based last price (last traded price / last bar close). Can be stale (especially for options) and may return None. Never treat this as bid/ask/mid; for option valuation/sizing/spread checks prefer get_quote(...).mid_price (or OptionsHelper.evaluate_option_market)
get_last_prices(self, assets: List[Union[str, Asset]], quote: Optional[Asset] = None, exchange: Optional[str] = None) -> Dict[Asset,float] - Returns an AssetsMapping so you can index by Asset or symbol string
get_historical_prices(self, asset: Union[Asset,str], length: int, timestep: str = "", quote: Optional[Asset] = None, include_after_hours: bool = True) -> "Bars" - Bars.df is timezone-aware datetime with open/high/low/close/volume (+return, dividends when present); returns None if the data source has no bars; prefer `bars.pandas_df` and pandas operations (do NOT use `return_polars`; deprecated)
get_historical_prices_for_assets(self, assets: List[Union[Asset,str]], length: int, timestep: str = “minute”, include_after_hours: bool = True) -> Dict[Asset,Bars] - Batch/threaded request; keys are sanitized assets or (base, quote) tuples; values are Bars or None per asset # Use get_historical_prices_for_assets when getting prices for a list of assets, it is much faster than get_historical_prices in a loop
get_quote(self, asset: Asset, quote: Optional[Asset] = None, exchange: Optional[str] = None) -> Optional[Quote] - Quote includes price, bid, ask, sizes, volume, timestamp (and mid_price); unavailable/error reads may return None. For options and thin markets, prefer quote.mid_price (with bid/ask validation) over get_last_price()
get_quotes(self, assets: List[Asset], quote: Optional[Asset] = None, exchange: Optional[str] = None) -> Dict[Asset, Optional[Quote]] - Available from LumiBot 4.6.19. Exact Asset keys preserve option identity. Schwab batches up to 50 symbols per HTTP request; other data sources may fall back to individual get_quote calls. Options honor the configured option data source. Native batch errors raise; absent quotes remain None without automatic per-contract retries. Preserve provider timestamps and the strategy's existing missing/stale-data policy. get_last_prices returns trade prices and cannot replace bid/ask formulas. See the `fast-lumibot-strategies` skill (reference `references/scanner-performance.md`) for bounded scanner use.
OptionsHelper.evaluate_option_market(option_asset: Asset, max_spread_pct: Optional[float] = None, *, quote: Optional[Quote] = None) -> OptionMarketEvaluation - This is a different return type from Quote. In 4.6.20 it has bid, ask, last_price, spread_pct, has_bid_ask, spread_too_wide, missing_bid_ask, missing_last_price, buy_price, sell_price, used_last_price_fallback, max_spread_pct and data_quality_flags. OptionMarketEvaluation does not have `mid_price`. Preserve an existing midpoint formula using its bid/ask fields or the exact supplied Quote.mid_price; buy_price and sell_price are execution anchors, not interchangeable midpoint values. An explicit quote must belong to this exact option. Do not pass a missing snapshot member as quote=None, which means no supplied quote and may fetch again. Check the public LumiBot source for the return type before relying on any other attribute.
Quote freshness evidence (verified LumiBot 4.6.20): inspect quote_time, bid_time and ask_time separately from request completion. In SchwabData, the general Quote.timestamp falls back to the local current time when those provider timestamps are absent; it therefore cannot by itself prove a recent market observation. Missing provider times remain unknown. Unchanged bid/ask values do not establish stale data, and a successful request does not establish a real-time entitlement. Match the exact asset, expiry, strike, right and observation times when comparing an option formula with another screen. Preserve the user's existing stale/missing-data policy; do not invent a new maximum age or loosen entry thresholds to force a trade. A hosted runtime or tool response may normalize option quote times, so inspect the actual returned fields rather than assuming this fallback reached the response you are reading.
Schwab error-boundary compatibility (verified 4.6.20): get_quote catches exceptions from get_quotes([asset]) and returns None. Direct get_quotes does not catch malformed-member ValueError/TypeError, request-level ConnectionError, or native HTTP transport errors. Numeric quote fields containing strings can raise TypeError during Quote construction; an HTTP read timeout can propagate as httpx.HTTPError. Bound recovery at the acquisition boundary, while allowing unrelated strategy errors to propagate. A ConnectionError alone does not establish provider-wide downtime. For example, a returned contract whose quote field is a list raises ValueError in _quote_from_response and aborts the bulk call, even if another contract has a valid quote. Replacing singleton reads with an unhandled bulk call therefore changes reachable behavior. Use the bounded quote-snapshot example to retain healthy members; do not convert a whole-provider outage into a successful empty scan or fall back to an unbounded serial loop.
get_yesterday_dividend(self, asset: Asset) -> Optional[float]

INDICATORS (self.indicators)

self.indicators is the PREFERRED, high-performance way to compute indicators. It caches results per-(asset, timestep, params) and uses O(log N) timestamp lookup instead of recomputing every iteration. Prefer to rewrite hand-rolled `df[...].rolling(...).mean()`, `.ewm(...).mean()`, `np.where(...)` loops, or maintained `compute_indicators()` helpers to use it when you can make the change mechanically without changing behavior. If current logs or context show that an API is unavailable, do not use that API; explain the upgrade path instead.

Built-in passthrough (pandas-ta-classic, ~130 indicators available: SMA, EMA, RSI, MACD, ATR, BBANDS, ADX, STOCH, VWAP, SUPERTREND, etc.):
  sma_50 = self.indicators.sma(asset, length=50, timestep="day")
  rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")
  macd = self.indicators.macd(asset, fast=12, slow=26, signal=9, timestep="minute")
  bbands = self.indicators.bbands(asset, length=20, std=2.0, timestep="day")

Single-column built-ins (SMA, EMA, RSI, ATR, etc.) return the current scalar value directly, usually a float/np.float64. Do NOT access `.sma_50`, `.rsi_14`, etc. on those values:
  sma_50 = self.indicators.sma(asset, length=50, timestep="day")  # float scalar
  rsi_14 = self.indicators.rsi(asset, length=14, timestep="minute")  # float scalar

Multi-column built-ins return an IndicatorRow (attribute-style read-only view over a pandas Series for the current bar). Access fields directly:
  macd_line, signal_line, hist = macd.MACD_12_26_9, macd.MACDs_12_26_9, macd.MACDh_12_26_9
  upper, mid, lower = bbands.BBU_20_2_0, bbands.BBM_20_2_0, bbands.BBL_20_2_0

Note: None/NaN is possible early in the series before the indicator has enough history. Guard scalar built-ins with `if sma_50 is None or pd.isna(sma_50): return` (import pandas as pd when using pd.isna). Guard multi-column rows by checking the row and the specific attributes.

Custom return contract: a function returning a Series yields a scalar value;
a function returning a DataFrame yields an IndicatorRow. Guard either result
for missing history before using its value or fields.

Custom indicators (replaces legacy compute_indicators() pattern):
  def _median_200(df):
      return df["close"].rolling(200).median()
  median_val = self.indicators.custom("median_200", _median_200, asset, timestep="day")  # scalar

  # Multi-column custom indicator returning a DataFrame also works:
  def _compute(df):
      ema_fast = df["close"].ewm(span=50, adjust=False).mean()
      ema_slow = df["close"].ewm(span=200, adjust=False).mean()
      return pd.DataFrame({"ema_fast": ema_fast, "ema_slow": ema_slow})
  row = self.indicators.custom("ema_cross", _compute, asset, timestep="minute")
  if row.ema_fast > row.ema_slow: ...

The cache auto-invalidates when new bars arrive (data-tag fingerprint of `(len(df), df.index[-1])`), so you never need to manually clear it. Call self.indicators.<fn>(...) directly inside on_trading_iteration; no warmup, no manual caching.

When porting a legacy strategy: (a) DELETE any `df = self.get_historical_prices(...).df` followed by `df["sma_x"] = df["close"].rolling(x).mean()` and replace with `sma_x = self.indicators.sma(asset, length=x, timestep="day")`; (b) never read an attribute from a single-column built-in return value; (c) DELETE any `compute_indicators()` helper and move its body into a local/nested function passed into `self.indicators.custom(...)`.

CHART FUNCTIONS

add_marker(self, name: str, value: Optional[float] = None, color: Optional[str] = None, symbol: str = "circle", size: Optional[int] = None, detail_text: Optional[str] = None, dt: Optional[datetime.datetime] = None, asset: Optional[Asset] = None) -> Optional[dict]
  - CORRECT usage: self.add_marker("Buy Signal", price, color="green", symbol="arrow-up", detail_text="Bullish crossover", asset=spy_asset)
  - First param is 'name' (the marker label), second is 'value' (the y-axis position)
  - Use 'detail_text' for hover text (NOT 'text' - that parameter does NOT exist!)
  - Pass only finite numeric values (skip markers if data is missing)
  - IMPORTANT: Pass the asset parameter when you have an Asset object - enables proper multi-symbol charting
  - accepted symbols: arrow-up, arrow-down, and star (do not use any other symbols or it will not work!)
  - accepted colors: red, green, blue, yellow, purple, orange, pink, black, white, gray, and brown
add_ohlc(self, name: str, open: float, high: float, low: float, close: float, color: Optional[str] = None, detail_text: Optional[str] = None, dt: Optional[datetime.datetime] = None, asset: Optional[Asset] = None) -> Optional[dict]
  - CORRECT usage: self.add_ohlc("SPY", open=o, high=h, low=l, close=c, detail_text="SPY Price", asset=spy_asset)
  - Use for OHLC bars (price candles) from get_historical_prices(); preferred over add_line() for price
  - First param is 'name' (the series label), then open/high/low/close (numeric)
  - Use 'detail_text' for hover text (NOT 'text' - that parameter does NOT exist!)
  - Only plot when all OHLC values are real finite numbers
  - Color defaults to green/red (bullish/bearish); pass color only if you want to override
  - IMPORTANT: Pass the asset parameter when you have an Asset object - enables proper multi-symbol charting
add_line(self, name: str, value: float, color: Optional[str] = None, style: str = 'solid', width: int = None, detail_text: str = None, dt: Optional[datetime.datetime] = None, asset: Optional[Asset] = None) -> Optional[dict]
  - CORRECT usage: self.add_line("MA_20", ma_value, color="blue", detail_text="20-day MA", asset=spy_asset)
  - First param is 'name' (the line label), second is 'value' (the numeric value to plot)
  - Use 'detail_text' for hover text (NOT 'text' - that parameter does NOT exist!)
  - Only plot when value is a real number; use documented colors (or hex) and styles solid/dotted/dashed
  - IMPORTANT: Pass the asset parameter when you have an Asset object - this enables proper multi-symbol charting
get_markers_df(self) -> pd.DataFrame
get_lines_df(self) -> pd.DataFrame
get_ohlc_df(self) -> pd.DataFrame

PLOT_NAME USAGE RULES

- When `asset` is provided, do NOT set `plot_name` for normal price/indicator overlays; let Lumibot group by asset automatically.
- Use `plot_name` only when intentionally creating a separate indicator pane (RSI/MACD/Stochastic/Volume/etc.).
- Do NOT create per-symbol `plot_name` values unless the user explicitly asks for dedicated panels.
- Keep distinct `plot_name` count small by default (max 4) unless the user explicitly asks for more panes.

PARAMETERS

get_parameters(self) -> Dict[str,Any]
set_parameters(self, params: dict) -> Dict[str,Any]

OPTIONS

get_chain(self, chains: dict, exchange: str = "SMART") -> dict
get_chains(self, asset: Asset) -> Chains
get_greeks(self, asset: Asset, asset_price: Optional[float] = None, underlying_price: Optional[float] = None, risk_free_rate: Optional[float] = None, query_greeks: bool = False) -> Optional[Dict[str,float]] - IMPORTANT: Returns None if option price data is unavailable (e.g., no trades or quotes). Always check if the result is None before accessing Greeks values. Returns dict with keys: delta, gamma, theta, vega, implied_volatility
get_strikes(self, asset: Asset, chains: Optional[dict] = None) -> List[float]
get_expiration(self, chains: dict) -> List[datetime.date]
get_multiplier(self, chains: dict, exchange: str = "SMART") -> str
options_expiry_to_datetime_date(self, expiry) -> datetime.date
get_option_expiration_after_date(self, dt: datetime.date) -> datetime.date

DATETIME

get_datetime(self, adjust_for_delay: bool = False) -> datetime.datetime
get_timestamp(self) -> int
get_round_minute(self, timeshift: int = 0) -> int
get_last_minute(self) -> int
get_round_day(self, timeshift: int = 0) -> int
get_last_day(self) -> int
get_datetime_range(self, length: int, timestep: str = “minute”, timeshift: Optional[int] = None) -> List[datetime.datetime]
localize_datetime(self, dt: datetime.datetime) -> datetime.datetime
to_default_timezone(self, dt: datetime.datetime) -> datetime.datetime

MISC

log_message(self, message: str, color: Optional[str] = “white”, broadcast: bool = False) -> Optional[str] # Possible colors: white, red, green, blue, or yellow (default is white). Broadcast will send the message to the logs and the console, only use for important messages.
sleep(self, sleeptime: float, process_pending_orders: bool = True) -> None # a safe sleep method, do not ever use regular time.sleep because it will cause a lot of issues in backtesting. only use self.sleep()
set_market(self, market: str) -> None # Use this method to set the market hours for the bot in the initilize lifecycle method. market can be “ASX”, “BMF”, “CFE”, “NYSE”, “stock”, “NASDAQ”, “BATS”, “CME_Equity”, “CBOT_Equity”, “CME_Agriculture”, “CBOT_Agriculture”, “COMEX_Agriculture”, “NYMEX_Agriculture”, “CME_Rate”, “CBOT_Rate”, “CME_InterestRate”, “CBOT_InterestRate”, “CME_Bond”, “CBOT_Bond”, “EUREX”, “HKEX”, “ICE”, “ICEUS”, “NYFE”, “JPX”, “LSE”, “OSE”, “SIX”, “SSE”, “TSX”, “TSXV”, “BSE”, “TASE”, “TradingCalendar”, “ASEX”, “BVMF”, “CMES”, “IEPA”, “XAMS”, “XASX”, “XBKK”, “XBOG”, “XBOM”, “XBRU”, “XBUD”, “XBUE”, “XCBF”, “XCSE”, “XDUB”, “XFRA”, “XETR”, “XHEL”, “XHKG”, “XICE”, “XIDX”, “XIST”, “XJSE”, “XKAR”, “XKLS”, “XKRX”, “XLIM”, “XLIS”, “XLON”, “XMAD”, “XMEX”, “XMIL”, “XMOS”, “XNYS”, “XNZE”, “XOSL”, “XPAR”, “XPHS”, “XPRA”, “XSES”, “XSGO”, “XSHG”, “XSTO”, “XSWX”, “XTAE”, “XTAI”, “XTKS”, “XTSE”, “XWAR”, “XWBO”, “us_futures”, “24/7”, “24/5”
update_parameters(self, params: dict) -> None
await_market_to_close(self, timedelta: Optional[int] = None) -> None
await_market_to_open(self, timedelta: Optional[int] = None) -> None
wait_for_order_registration(self, order: Order) -> Optional[Order]
wait_for_order_execution(self, order: Order) -> Optional[Order]
wait_for_orders_registration(self, orders: List[Order]) -> List[Order]
wait_for_orders_execution(self, orders: List[Order]) -> List[Order]

STRATEGY ATTRIBUTES

cash -> float
portfolio_value -> float
first_iteration -> bool
is_backtesting -> bool
quote_asset -> Asset
name -> str
initial_budget -> float
minutes_before_closing -> int
minutes_before_opening -> int
sleeptime -> Union[int,str] # this can use S (seconds), M (minutes), D (days). eg. "1M" for 1 minute or "10S" for 10 seconds
last_on_trading_iteration_datetime -> Optional[datetime.datetime]
vars -> persistent namespace (attribute-style access; survives restarts)
