> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-indicators
description: Use when LumiBot strategy code needs indicators, pandas-ta-classic helpers, or migration away from hand-rolled rolling calculations.
---

--------------------------------------------------------------
INDICATORS SUBSYSTEM (self.indicators) -- USE THIS FIRST
--------------------------------------------------------------

PREFER THIS OVER HAND-ROLLED INDICATORS. `self.indicators` is a built-in accessor on every Strategy (no import, no instantiation required) that provides cached, O(log N) indicator lookups backed by pandas-ta-classic. If the user's strategy (or a strategy you are refining) computes indicators by hand with `df["col"].rolling(...).mean()`, `.ewm(...)`, or a `compute_indicators()` helper, prefer rewriting it to use `self.indicators` when you can make it as a local mechanical change that preserves behavior. Caching avoids repeated calculations; equivalence is not automatic. Preserve the algorithm, smoothing, initialization, historical inputs and decision timing, and verify matching values before replacing an existing calculation. Do not expand a narrow user edit into an unrelated indicator migration.

Answer contract: for indicator-computation explanations, including code-example questions,
and when advising a user to migrate from hand-rolled rolling indicator columns
to `self.indicators`, explicitly say `self.indicators`
provides cached lookups. Also explicitly say single-column built-ins such as
SMA/EMA/RSI return the current scalar value, while multi-column built-ins return a current-bar row. A custom function
returning a Series produces a scalar; a DataFrame produces an IndicatorRow. Do not leave these facts only in
your private reasoning or in code examples.

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

IndicatorRow fields are case-sensitive. Column names keep pandas-ta-classic's
original case; attribute access only replaces dots and hyphens with underscores.
For these parameters, `macd["MACDs_12_26_9"]` and `bbands["BBU_20_2.0"]`
are equivalent bracket accesses. Inspect `row.as_dict()` when parameters change
instead of guessing field names. Guard both multi-column rows for None before
reading fields and check the selected values for NaN before making decisions.

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
3. Do this migration when you can make it as a safe, local mechanical change that preserves behavior. If user-provided logs or current context show that the API you would use is unavailable, do not use that API; explain the upgrade path instead. Record the change in the `changes` field as "Performance upgrade: migrated to self.indicators".
