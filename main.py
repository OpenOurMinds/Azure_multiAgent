"""
Multi-Agent Automated Trading System.

Initializes the hierarchical multi-agent team (Orchestrator + Fundamental,
Technical, and Risk Management agents), uses AzureOpenAIResponsesClient for
high-fidelity reasoning, and outputs a structured Securities Trading Strategy.
"""
import asyncio
import os
import json

from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIResponsesClient

from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
)
from agents.orchestrator import OrchestratorAgent
from schemas import SecuritiesTradingStrategy

load_dotenv()


def create_responses_client() -> AzureOpenAIResponsesClient:
    """Build Azure OpenAI Responses client for the orchestrator and all agents."""
    return AzureOpenAIResponsesClient(
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        deployment_name=AZURE_OPENAI_DEPLOYMENT,
    )


def print_strategy(strategy: SecuritiesTradingStrategy) -> None:
    """Print the structured Securities Trading Strategy in a readable format."""
    print("\n" + "=" * 60)
    print("SECURITIES TRADING STRATEGY")
    print("=" * 60)
    print(f"Security:     {strategy.security or 'N/A'}")
    print(f"Direction:    {strategy.direction}")
    print(f"Confidence:   {strategy.confidence}")
    print("-" * 60)
    print("Technical summary:")
    print(strategy.technical_summary)
    print("-" * 60)
    print("Fundamental summary:")
    print(strategy.fundamental_summary)
    print("-" * 60)
    print("Risk assessment:")
    print(strategy.risk_assessment)
    print("-" * 60)
    print("Rationale:")
    print(strategy.rationale)
    if strategy.conditions:
        print("Conditions:", strategy.conditions)
    if strategy.warnings:
        print("Warnings:", strategy.warnings)
    print("=" * 60)


async def main():
    # Initialize the multi-agent team via the central Orchestrator
    client = create_responses_client()
    orchestrator = OrchestratorAgent(client=client)

    # Example user objective (can be replaced with CLI/API input)
    user_query = os.getenv(
        "TRADING_QUERY",
        "Give me a trading strategy for AAPL considering technicals, fundamentals, and risk.",
    )

    print("User objective:", user_query)
    print("Running orchestrator (classify -> delegate -> synthesize)...")

    strategy = await orchestrator.run_workflow(user_query)

    print_strategy(strategy)

    # Optional: output as JSON for downstream systems
    print("\nStructured output (JSON):")
    print(json.dumps(strategy.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
