# LumiBot Trading Skills

Free trading strategy skills for Claude Code, Codex and Cursor, built on [LumiBot](https://github.com/Lumiwealth/lumibot).

Ask your AI to build a trading bot, and these skills teach it how to do it right. It learns how to write a LumiBot strategy, backtest it, read the results, and avoid the mistakes that make backtests lie. They cover stocks, ETFs, options, crypto, futures and AI agents that trade.

LumiBot is the open-source Python trading library from Lumiwealth. Docs: https://lumibot.lumiwealth.com

## Install in one command

**Claude Code**

```
/plugin marketplace add Lumiwealth/lumibot-trading-skills
/plugin install lumibot-trading-skills@lumiwealth
```

Or from your shell:

```bash
claude plugin marketplace add Lumiwealth/lumibot-trading-skills
claude plugin install lumibot-trading-skills@lumiwealth
```

**Codex, Cursor, Claude Code and 70+ other agents** (with the [skills](https://skills.sh) CLI, Node 22 or newer):

```bash
npx skills add Lumiwealth/lumibot-trading-skills
```

Add `-g` to install for every project, or `-a codex` / `-a cursor` / `-a claude-code` to pick one agent.

**Codex by hand.** Codex reads personal skills from `~/.agents/skills`:

```bash
git clone https://github.com/Lumiwealth/lumibot-trading-skills.git
mkdir -p ~/.agents/skills
cp -R lumibot-trading-skills/skills/* ~/.agents/skills/
```

Restart Codex if the skills do not show up right away.

## The skills

| Skill | What it helps with |
|---|---|
| `lumibot-strategy-building` | Start here. Writing, fixing and backtesting any LumiBot strategy, plus the checks that catch bad backtests. |
| `lumibot-backtesting` | Diagnose failed or no-trade backtests from logs, fills and artifacts; use local LumiBot or BotSpot MCP. |
| `lumibot-api-reference` | Exact LumiBot method names, lifecycle methods and working code examples. |
| `stock-etf-strategies` | Stocks and ETFs: moving averages, breakouts, mean reversion, rotation and rebalancing. |
| `options-strategies` | Options: covered calls, the wheel, spreads, iron condors, straddles and more. |
| `lumibot-indicators` | Indicators like SMA, RSI, MACD and Bollinger Bands, and putting them on the backtest chart. |
| `lumibot-ai-agents` | Strategies where AI agents do the research and one AI agent places the trades. |
| `fast-lumibot-strategies` | Making slow strategies and big scanners fast, and handling orders quickly and safely. |
| `using-botspot-mcp` | Using the free BotSpot MCP to build, backtest and run strategies in the cloud. |

Each skill folder has a `SKILL.md` and a `references/` folder with deeper notes. Your AI opens the reference files only when it needs them. Some skills mention a `skills` tool for loading references. That is how the BotSpot MCP serves them. Here, the files are already on your computer in `references/`.

## Quick start

1. **Install** the skills with one of the commands above.
2. **Ask** your AI: "Build me a moving average strategy for SPY and backtest it."
3. **Run it** with LumiBot: `pip install lumibot`, then run the strategy file your AI wrote. The [LumiBot docs](https://lumibot.lumiwealth.com) show how to backtest and how to connect a broker.

## Connect to hosted backtests

Do not want to set up Python and data? Connect the BotSpot MCP. It is free to connect, and it creates a free BotSpot account for you. Your AI can then use strategy-building skills, research data and hosted backtest tools. Hosted compute and heavier usage depend on your plan.

Claude Code:

```bash
claude mcp add --transport http botspot https://mcp.botspot.trade/mcp
```

Other apps that support MCP can use the same address: `https://mcp.botspot.trade/mcp`. Learn more at [botspot.trade](https://botspot.trade).

Running a bot with your own broker always needs your approval on botspot.trade first. Nothing trades without you saying yes.

## Good to know

- These skills teach an AI how to write code. They are not investment advice.
- A backtest shows what would have happened in the past. It does not promise anything about the future.
- Trading can lose money. Test with a paper account before you use real money.

## Check the layout

```bash
python3 tests/test_skills_layout.py
```

## License

MIT. See [LICENSE](LICENSE).
