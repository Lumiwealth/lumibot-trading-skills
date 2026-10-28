> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

# AI Trading Team Examples

These examples are reference shapes, not rigid templates. Preserve the user's
requested strategy intent first, then adapt the closest pattern.

## Canonical running examples

Two LumiBot examples are running and follow the team conventions. Copy their
shape, not their exact prompts. Both live in LumiBot's
`lumibot/example_strategies/` folder.

- `ai_trading_team_ray_dalio_idea_meritocracy.py`: growth, inflation and
  debt/liquidity researchers plus a `thoughtful_disagreement` critic, all
  without trading, then one `trader` that rebalances a diversified ETF basket
  with plain-language rules ("hold at least three positions when risk is on",
  SHV as ballast). Daily cadence; Python only creates and runs the agents.
- `ai_trading_team_citadel_sector_pods.py`: five sector pods and a non-trading
  `risk_manager` critic, then one `portfolio_manager` that trades a 3+ sector
  ETF portfolio and must not go all-in on one sector.

Both files still name an older model; new builds use the model marked
(default) in CURRENT AI MODELS. Their long readiness and data-usage paragraphs predate
LumiBot's runtime trading skills; new prompts keep only the strategy's own
rules. `ai_iron_condor.py` (one agent plus a Python stop check) and the disclosure-following bots are not reference shapes yet.

## Bull/Bear Leveraged ETF AI Trading Team

- Universe: leveraged long and inverse ETFs around broad indexes or sectors.
- Useful roles: bull thesis agent, bear thesis agent, volatility/risk critic,
  final portfolio manager.
- Good fit when the user wants aggressive directional AI decisions and accepts
  leverage risk.
- For AI-only builds, require max leverage exposure and repeat-order prevention
  in the final trading agent's prompt.

## Bull/Bear Large-Cap Stocks AI Trading Team

- Universe: liquid mega-cap or large-cap stocks.
- Useful roles: bullish analyst, bearish analyst, earnings/news analyst, final
  trader.
- Good fit when the user wants stock selection rather than ETF allocation.
- Use a compact watchlist for first smoke tests; broad universes can be added
  after the first successful backtest.

## Ray Dalio Idea Meritocracy AI Trading Team

- Universe: diversified ETFs such as equities, bonds, inflation hedges,
  commodities, cash-like Treasury ETFs, and international equity proxies.
- Useful roles: growth regime agent, inflation regime agent,
  debt/liquidity agent, disagreement/risk agent, final allocator.
- Good fit for macro allocation. Add real news or macro tools when requested
  and when matching keys are available.
- The final trading agent should explain which upstream advice it accepted and
  rejected so `agent_detail` can support later analysis.

## Warren Buffett Value AI Trading Team

- Universe: high-quality stocks or quality/value ETFs.
- Useful roles: business-quality analyst, valuation analyst, moat/risk critic,
  final concentrated buyer.
- Good fit for low-turnover, fundamental-style selection.
- Avoid pretending to use financial statements unless the code includes a real
  data source or uploaded dataset.

## Bill Ackman Concentrated AI Trading Team

- Universe: a small set of liquid, high-conviction stocks.
- Useful roles: activist thesis analyst, downside/risk analyst, catalyst
  analyst, final concentrated portfolio manager.
- Good fit when the user wants fewer positions and stronger opinions.
- For AI-only builds, the final trading agent's prompt should enforce max
  position count and concentration caps when the user states them.

## Citadel Sector Pods AI Trading Team

- Universe: sector ETFs or sector-specific liquid stocks.
- Useful roles: sector specialist pods, macro/market-regime critic, risk
  manager, final allocator.
- Good fit when the user asks for a multi-pod or sector-specialist structure.
- Do not force every Citadel-style request into this exact structure. If the
  user asks for a different hedge-fund team pattern, use the broader pod and
  risk-manager idea without pigeonholing it.
