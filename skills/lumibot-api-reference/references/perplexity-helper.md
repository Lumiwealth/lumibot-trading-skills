> PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

---
name: lumibot-perplexity-helper
description: Use when LumiBot strategy code needs PerplexityHelper, live financial news queries, or structured external search data.
---

--------------------------------------------------------------
PERPLEXITYHELPER COMPONENT
--------------------------------------------------------------

A helper for querying Perplexity’s API via an OpenAI-compatible client.
It supports two types of queries:
	•	Financial news queries: Returns structured financial news data—ideal for getting current news such as earnings reports, analyst recommendations, and other market-moving events.
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
    self.perplexity_helper = PerplexityHelper(api_key="your_api_key_here")

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
