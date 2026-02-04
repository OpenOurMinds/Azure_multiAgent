"""
Single-agent example with financial tools (reference for Technical Analyst structure).

For the full multi-agent system (Orchestrator + Fundamental, Technical, Risk agents),
use main.py. This file demonstrates the tool pattern used by agents/specialists.py
with real-world financial APIs (Yahoo Finance via yfinance).
"""
import os
import asyncio
from typing import Annotated
from pydantic import Field

from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient

# Import financial tools from the shared tools package
from tools.technical_tools import get_price_history, get_volume_analysis, get_price_summary
from tools.fundamental_tools import get_earnings_summary

load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Single agent with technical + fundamental tools (mirrors multi-agent specialists)
agent = AzureOpenAIChatClient(
    endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
).create_agent(
    name="TradingAssistant",
    instructions="You are a helpful trading assistant. Use the provided tools to fetch price, volume, and earnings data. Summarize findings concisely.",
    tools=[
        get_price_history,
        get_volume_analysis,
        get_price_summary,
        get_earnings_summary,
    ],
)


async def main():
    result = await agent.run("What is the recent price and volume for AAPL?")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
