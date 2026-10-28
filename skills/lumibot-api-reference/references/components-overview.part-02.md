> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

- ``@agent_tool`` is the PRIMARY pattern for adding external data sources only when the user names a real provider/API, uploads reference code, or explicitly asks for a custom integration. Do not invent generic news APIs, placeholder URLs, or new API-key requirements.
- Always write Google-style docstrings with an ``Args`` section for ``@agent_tool`` functions. The source code and docstring are auto-included in the tool description.
- Built-in tools are ALWAYS included automatically, even when you pass custom ``tools`` or ``mcp_servers``.
- System prompts should be 2-3 sentences describing the strategy intent only. LumiBot handles position sizing, DuckDB usage, and backtesting safety internally.
- For any trading-enabled AI agent, make the system prompt/tool-use instructions explicit: immediately before every buy or sell order, call ``account_portfolio``, ``account_positions``, and ``market_last_price`` for the exact ordered symbol in the same agent run, then call ``orders_submit_order``. LumiBot intentionally rejects blind orders with ``ORDER_READINESS_REQUIRED`` if those readiness calls are missing.
- Create the agent once in ``initialize()``. Do not recreate it every iteration.
- Keep ``on_trading_iteration`` thin. Usually it should only call ``self.agents["name"].run(...)``. Only store/log ``result.summary`` if the user explicitly asks for chat-visible summaries.
- Do not add indicators, watchlists, fallback rules, manual order orchestration, markers, lines, or extra logging around an AI-agent strategy unless the user explicitly asks for them.
- For agent-owned trading, the final trading-enabled agent can inspect broker state and submit orders itself through LumiBot tools, so the strategy does not need to parse the agent summary and call ``get_cash()``, ``get_last_price()``, ``create_order()``, or ``submit_order()`` afterward. If the user wants hard deterministic execution boundaries, set all agents to ``allow_trading=False``, have them return validated structured recommendations, and let Python own sizing/order submission.
- AI agents require exactly one model-provider API key matching the ``default_model`` (GEMINI_API_KEY for Gemini, OPENAI_API_KEY for ``openai/...``, XAI_API_KEY for ``xai/...``, ANTHROPIC_API_KEY for ``anthropic/...``).
