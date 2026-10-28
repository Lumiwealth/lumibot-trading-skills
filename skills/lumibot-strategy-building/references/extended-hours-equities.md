> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# US equity extended-hours strategies

Use with the `lumibot-strategy-building` skill whenever a US stock or ETF
strategy trades or prepares before the regular open, after the regular close,
pre-market, post-market or overnight.

## Separate four concerns

Keep these apart in the saved code:

1. Framework wake calendar: when LumiBot runs iterations.
2. The broker's supported session windows for the symbol.
3. Current quote availability.
4. Order eligibility at this moment.

`set_market("24/7")`, `set_market("24/5")`, descriptive flags or disabled sleeps
keep the loop awake. None of them proves the broker can quote or execute the
symbol at that time.

## Preparing after hours, trading in regular hours

For a strategy that must prepare data after the close but submit orders only in
regular hours:

- `self.set_market("24/7")` is a reasonable wake setting so scheduled
  iterations run after hours. It is not the default for ordinary equity
  strategies and is not permission to trade at all hours.
- With a continuous market setting, `self.broker.is_market_open()` is not an
  order-safety check. Compute the real session from a timezone-aware US
  exchange calendar and require it before every submit, cancel, modify, close or
  cleanup. Data fetching, scoring and saving the plan can run outside it.
- Persist the plan and its idempotency state in `self.vars` so a later
  iteration loads the same plan and reconciles broker positions and orders
  before acting. If a planned execution is missed (holiday, unexpected closure,
  failed run, incomplete ladder), keep the plan pending and let the next valid
  regular-session iteration continue it. Never silently rebuild and reorder the
  plan to hide missing state.
- Use a maintained exchange calendar package (declared in `requirements.txt`)
  for trading days, observed holidays across year boundaries and early closes.
  A hand-written holiday list is not equivalent.

## Decision clock versus execution session

- An exact HH:MM decision means that local minute, once per eligible day. Do
  not turn it into "any time after HH:MM" unless the user asked for catch-up.
- Guard every reachable order path with the actual timezone-aware session.
  Keep an explicit entry-time restriction on entries without silently applying
  it to protective exits, which have their own rules.
- Convert `self.get_datetime()` with `ZoneInfo("America/New_York")` before
  comparing times. Do not compare a raw datetime's clock fields and label them
  Eastern.

## Broker sessions

Use an explicit timezone-aware session guard per broker. Published defaults to
start from (always confirm against the broker's current documentation):

- Schwab equities: pre-market 07:00 to 09:25 ET, regular 09:30 to 16:00 ET,
  after-hours 16:05 to 20:00 ET. Keep the 09:25 to 09:30 and 16:00 to 16:05
  gaps; one continuous 07:00 to 20:00 window is not equivalent. Do not assume
  API execution before 07:00 ET just because the broker advertises round-the-
  clock trading in its own app.
- Alpaca, Tradier and IBKR publish their own windows; check them rather than
  hardcoding unverified times.

## Pricing outside regular hours

- Call `self.get_quote(asset)` for the current decision price before requesting
  history. Require a usable bid and ask, check the broker's quote time is fresh
  for the strategy's cadence, and reject a spread wider than the strategy's
  explicit threshold. `get_last_price()` is a fallback and may be stale. A
  one-minute bar close is not a live executable price.
- Use the broker's own `bid_time`, `ask_time` or `quote_time` to judge
  freshness. A locally generated fallback timestamp is not proof.
- These checks are live-only. Backtest quotes are rebuilt from bars and never
  carry broker timestamps, so skip them when `self.is_backtesting` and price
  from the bar, or every backtest bar is rejected.
- Use `get_historical_prices()` for lookback context (for example the prior 15
  completed minute highs). Request a window wide enough to survive minutes with
  no trades. An empty minute-bar response does not prove the quote endpoint has
  no data; log "quote available, signal context incomplete" in that case.

```python
from datetime import timezone
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")


def _fresh_equity_quote(self, asset, max_age_seconds=30):
    """Return a quote fresh enough to trade on, or None.

    Args:
        asset: The stock or ETF Asset.
        max_age_seconds: Largest allowed age of the broker quote in live trading.

    Returns:
        The Quote, or None when it is missing, crossed, or stale.
    """
    quote = self.get_quote(asset)  # Before historical-bar requests.
    if quote is None:
        return None
    if self.is_backtesting:
        # Backtest quotes are rebuilt from bars and never carry broker times.
        # Freshness and spread checks are live-only; price from the bar.
        return quote if quote.price is not None else None
    if quote.bid is None or quote.ask is None:
        return None
    bid, ask = float(quote.bid), float(quote.ask)
    if bid <= 0 or ask <= 0 or ask < bid:
        return None
    broker_times = [t for t in (quote.bid_time, quote.ask_time, quote.quote_time) if t is not None]
    if not broker_times:
        return None  # Live quote without broker time cannot prove freshness.
    broker_time = max(broker_times)
    if broker_time.tzinfo is None:
        broker_time = broker_time.replace(tzinfo=timezone.utc)
    now_utc = self.get_datetime().astimezone(timezone.utc)
    if abs((now_utc - broker_time.astimezone(timezone.utc)).total_seconds()) > max_age_seconds:
        return None
    return quote


def _now_et(self):
    """Return the current strategy time in New York."""
    return self.get_datetime().astimezone(NEW_YORK)
```

Define these as methods of the strategy class. In live trading the
missing-timestamp branch fails closed; do not write "if times exist, check age"
and then accept a quote with no times.

## Orders outside regular hours

- Use `create_order(...)` plus `submit_order(...)` with an explicit
  `limit_price` for entries and exits. Never a market order for an
  extended-hours stock trade.
- A limit price alone does not select the extended session on every broker:
  - Schwab: LumiBot maps simple stock limit orders to Schwab's extended
    "seamless" session; market orders map to the normal session.
  - Alpaca: set the order's broker custom parameter `extended_hours=True` and
    use `day` or `gtc` time in force.
  - Tradier: use `time_in_force="pre"` or `"post"` for the intended session;
    `day` does not select extended hours.
  - IBKR: Outside-RTH and overnight routing need extra broker attributes. Do
    not promise IBKR extended execution unless the LumiBot adapter you run is
    known to send them.
- Do not generate bracket, OCO, OTO, trailing-stop or stop children for an
  extended-hours stock trade unless that broker's exact API path is known to
  support every child outside regular hours. Instead, monitor take-profit and
  stop levels in strategy code and submit a bounded marketable limit exit from
  a freshly validated quote. Do not swap in a second unchecked quote inside the
  exit helper.

## Order state

- Before any entry, reconcile the tracked order with `self.get_order(order_id)`
  and check same-asset active orders. A submitted, open, new or partially filled
  entry for the same asset blocks another entry.
- A successful submit is acknowledgement, not a fill. Set entry basis, targets,
  stops, counters and held flags only from confirmed fills. Clear tracked state
  only after a confirmed terminal error, rejection, cancellation or expiration,
  with a bounded cooldown before retrying. Apply the same rule to exits.

## What a backtest can and cannot prove

A historical backtest can validate syntax, control flow, order types,
duplicate-entry protection and basic signal behavior at any time of day. It
cannot prove that the broker returns fresh quotes or accepts orders in a live
extended-hours session. Say that plainly to the user.
