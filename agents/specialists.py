"""Domain-specialized agents: Fundamental, Technical, and Risk Management."""
from agent_framework.azure import AzureOpenAIResponsesClient

from tools.fundamental_tools import (
    get_earnings_summary,
    get_income_statement_summary,
    get_balance_sheet_summary,
    get_macro_indicators,
)
from tools.technical_tools import (
    get_price_history,
    get_volume_analysis,
    get_moving_averages,
    get_price_summary,
)
from tools.risk_tools import (
    evaluate_volatility,
    evaluate_position_limit_compliance,
    evaluate_downside_risk,
)
from agents.registry import TECHNICAL_ANALYST, FUNDAMENTAL_ANALYST, RISK_ANALYST


FUNDAMENTAL_INSTRUCTIONS = """You are a Fundamental Analyst Agent for securities trading.
Your role is to analyze market fundamentals: earnings reports, income statements, balance sheets, and macroeconomic indicators.
Use your tools to fetch data (earnings, income statement, balance sheet, macro indicators) and provide a concise, factual summary.
Focus on valuation-relevant metrics and growth. Do not make price targets or trading recommendations; only report fundamental findings.
If the user or context provides a ticker or sector, use it in your tool calls. Reuse any shared facts provided in the context to avoid redundant tool calls."""

TECHNICAL_INSTRUCTIONS = """You are a Technical Analyst Agent for securities trading.
Your role is to analyze price movements, chart patterns, volume, and moving averages.
Use your tools to fetch price history, volume, moving averages, and price summaries. Provide a concise technical assessment.
Do not make fundamental or risk conclusions; only report technical findings. Use the security/sector from context when provided.
Reuse any shared facts provided in the context to avoid redundant tool calls."""

RISK_INSTRUCTIONS = """You are a Risk Management Agent for securities trading.
Your role is to evaluate downside risk, volatility, and compliance with trading limits before a strategy is finalized.
Use your tools to evaluate volatility, position limit compliance, and downside risk. Provide a clear risk assessment.
Do not recommend entries or targets; only state whether risk is acceptable and any limit breaches or caveats.
Use the security from context when provided."""


def build_fundamental_analyst(client: AzureOpenAIResponsesClient):
    """Build the Fundamental Analyst agent with fundamental tools."""
    return client.create_agent(
        name=FUNDAMENTAL_ANALYST,
        instructions=FUNDAMENTAL_INSTRUCTIONS,
        tools=[
            get_earnings_summary,
            get_income_statement_summary,
            get_balance_sheet_summary,
            get_macro_indicators,
        ],
    )


def build_technical_analyst(client: AzureOpenAIResponsesClient):
    """Build the Technical Analyst agent with technical tools."""
    return client.create_agent(
        name=TECHNICAL_ANALYST,
        instructions=TECHNICAL_INSTRUCTIONS,
        tools=[
            get_price_history,
            get_volume_analysis,
            get_moving_averages,
            get_price_summary,
        ],
    )


def build_risk_analyst(client: AzureOpenAIResponsesClient):
    """Build the Risk Management agent with risk tools."""
    return client.create_agent(
        name=RISK_ANALYST,
        instructions=RISK_INSTRUCTIONS,
        tools=[
            evaluate_volatility,
            evaluate_position_limit_compliance,
            evaluate_downside_risk,
        ],
    )
