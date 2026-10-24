# AI Trading Team Examples

These are reference shapes, not rigid templates and not investment advice.
Keep the user's own strategy intent first, then adapt the closest shape. Every
shape follows the core rules: research agents with `allow_trading=False`, one
trading agent that owns orders and risk, answers passed through `context`.

## Public LumiBot examples to study

LumiBot's open-source `lumibot/example_strategies/` folder includes AI team
examples. Copy their structure, not their exact prompts:

- `ai_trading_team_ray_dalio_idea_meritocracy.py`: a macro regime team. Growth,
  inflation and debt/liquidity researchers plus a disagreement critic, all
  non-trading, then one `trader` that rebalances a diversified ETF basket with
  plain-language rules (for example "hold at least three positions when risk is
  on", a short-term Treasury ETF as ballast). Daily cadence; Python only creates
  and runs the agents.
- `ai_trading_team_citadel_sector_pods.py`: a sector pod team. Five sector
  researchers and a non-trading risk critic, then one `portfolio_manager` that
  trades a portfolio across three or more sector ETFs and must not go all-in on
  one sector.

The file names describe an investing style the examples are loosely inspired
by. They do not reflect the holdings of, or an endorsement by, any person or
firm. Some example files pin an older model id and carry long data-usage
paragraphs written before LumiBot's runtime trading skills existed. For new
builds, omit `model` or use a current one, and keep only the strategy's own
rules in prompts. Examples that use a single agent plus a Python stop check are
not reference shapes for AI-only builds.

## Bull/bear leveraged ETF team

- Universe: leveraged long and inverse ETFs on broad indexes or sectors.
- Roles: bull thesis, bear thesis, volatility and risk critic, final portfolio
  manager.
- Fits a user who wants aggressive directional decisions and accepts leverage
  risk.
- The trader's prompt states the maximum leveraged exposure and that it must
  not repeat an entry already held or working.

## Bull/bear large-cap stock team

- Universe: liquid large-cap stocks.
- Roles: bullish analyst, bearish analyst, earnings and news analyst, final
  trader.
- Fits stock selection rather than ETF allocation.
- Start with a compact watchlist in the prompt; widen it after a first
  successful backtest.

## Macro regime allocation team

- Universe: diversified ETFs across equities, bonds, inflation hedges,
  commodities, short-term Treasuries and international equity.
- Roles: growth regime, inflation regime, debt and liquidity, disagreement
  critic, final allocator.
- The built-in FRED tools and `alpaca_news` give the researchers macro and news
  evidence.
- The allocator explains which upstream advice it accepted and rejected.

## Quality and value team

- Universe: high-quality stocks or quality/value ETFs.
- Roles: business-quality analyst, valuation analyst, moat and risk critic,
  final concentrated buyer.
- Fits low-turnover, fundamentals-style selection.
- The built-in SEC filing and financial statement tools (`get_filings`,
  `get_income_statement`, `get_balance_sheet`, `get_cash_flow`) let researchers
  read real fundamentals. Do not claim the team uses financial statements if
  those tools return nothing for the chosen symbols.

## Concentrated conviction team

- Universe: a small set of liquid, high-conviction stocks.
- Roles: thesis analyst, downside and risk analyst, catalyst analyst, final
  concentrated portfolio manager.
- Fits a user who wants fewer positions and stronger opinions.
- The trader's prompt states the maximum number of positions and the
  concentration cap the user chose.

## Public disclosure research team (synthetic example)

A user may want an AI that reads dated public disclosures (for example insider
transaction filings) and decides whether to act on them.

- Roles: a filing researcher with `allow_network=True` that finds and reads the
  relevant public documents itself, a timing and risk critic, final trader.
- A short hint in the researcher prompt about where to look is fine ("SEC
  EDGAR filings are a good starting point"). The agent browses, downloads and
  reads. No Python that downloads, parses or filters filings.
- Tell the researcher to use only documents dated on or before the simulated
  date, and to report the filing date and the transaction date separately,
  because disclosures arrive after the underlying transaction.
- In backtests, tell the user that web content fetched during a run can be
  newer than the simulated date, so results are an approximation.

## Sector pods team

- Universe: sector ETFs or liquid sector stocks.
- Roles: sector specialist pods, market regime critic, risk critic, final
  allocator.
- Fits a user who asks for a multi-pod or sector-specialist structure.
- Do not force every hedge-fund-style request into this exact shape. Use the
  broader pod and critic idea for other team patterns.
