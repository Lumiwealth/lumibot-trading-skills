# LumiBot Trading Skills

Free trading strategy skills for Claude Code, Codex and Cursor, built on [LumiBot](https://github.com/Lumiwealth/lumibot).

The guides and `catalog.json` are generated from the same maintained skill source
used by BotSpot's authoring agent. They are published together after privacy and
parity checks; there is no separately edited public version. Installed native
skills keep the version you installed until you update the package. Compatible BotSpot MCP server versions read the published catalog and
refresh its content automatically; older servers retain their bundled version
until their normal update.

A guide is published when its canonical source is marked `visibility: public`.
Private owners and their nested guides are excluded. Publication preserves the
complete source files byte for byte, including frontmatter and references; it
does not rewrite instructions for an external audience. The source's
`public-name` is an MCP discovery alias, so existing MCP names can stay stable
while installed folders use the canonical source name.

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
| `strategy-building-core` (MCP: `lumibot-strategy-building`) | Start here. Writing, fixing and backtesting any LumiBot strategy, plus the checks that catch bad backtests. |
| `backtest-rescue` (MCP: `lumibot-backtesting`) | Diagnose failed or no-trade backtests from logs, fills and artifacts; use local LumiBot or BotSpot MCP. |
| `lumibot-api-reference` | Exact LumiBot method names, lifecycle methods and working code examples. |
| `stock-etf-strategies` | Stocks and ETFs: moving averages, breakouts, mean reversion, rotation and rebalancing. |
| `lumibot-options-helper` (MCP: `options-strategies`) | Options: covered calls, the wheel, spreads, iron condors, straddles and more. |
| `lumibot-indicators-and-charting` (MCP: `lumibot-indicators`) | Indicators like SMA, RSI, MACD and Bollinger Bands, and putting them on the backtest chart. |
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

Connecting exposes the `skills` tool. The agent lists the catalogue, reads the
relevant guide with `skills(action="get", name="...")`, then loads its references
when needed. MCP does not install native skills or put every guide into every
model turn automatically. A native installation provides the same files through
your client's skill loader. Neither connection guarantees that a client will
read the right guide; the client must actually load it and use its instructions.

Running a bot with your own broker always needs your approval on botspot.trade first. Nothing trades without you saying yes.

## Good to know

- These skills teach an AI how to write code. They are not investment advice.
- A backtest shows what would have happened in the past. It does not promise anything about the future.
- Trading can lose money. Test with a paper account before you use real money.

## Check the layout

```bash
python3 tests/test_skills_layout.py
python3 -m unittest discover -s tests
```

## License

MIT. See [LICENSE](LICENSE).
