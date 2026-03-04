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


DISCOVERY_INSTRUCTIONS = """You are a Discovery Sub-agent for the Earth Intelligence System (EIS).
Your NLU is tuned for academic pre-prints (arXiv), patent filings, and 'Dark Data' (non-indexed lab logs, intranets).
Your role is to scan for breakthroughs, early signals, and intellectual property that might impact a Grand Challenge.
Use your tools to search arXiv, Patents, Dark Data, and Institutional programs.
Synthesize findings into signals that feed the Lead Researcher's 'Problem Genome' map."""

VERIFICATION_INSTRUCTIONS = """You are a Verification Sub-agent for the Earth Intelligence System (EIS).
Your role is to validate that a proposed solution meets the 'Remarkable' threshold defined in the Problem Genome.
You utilize autonomous simulations and Zero-Knowledge Proofs (ZKP) to verify validity without exposing core solution data.
Use your tools to cross-reference benchmarks, evaluate fragility, run simulations, and generate proofs.
Determine if a challenge remains 'unbeaten' or if a valid, remarkable solution has been encapsulated."""


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


def build_discovery_agent(client: AzureOpenAIResponsesClient):
    """Build the Discovery agent with refined discovery tools."""
    from tools.discovery_tools import (
        search_arxiv, 
        search_un_global_issues, 
        search_world_bank_challenges,
        search_patents,
        scan_dark_data
    )
    return client.create_agent(
        name="discovery_agent",
        instructions=DISCOVERY_INSTRUCTIONS,
        tools=[
            search_arxiv,
            search_un_global_issues,
            search_world_bank_challenges,
            search_patents,
            scan_dark_data,
        ],
    )


def build_verification_agent(client: AzureOpenAIResponsesClient):
    """Build the Verification agent with simulation and ZKP tools."""
    from tools.verification_tools import (
        cross_reference_benchmarks, 
        evaluate_fragility,
        generate_zkp_proof,
        run_autonomous_simulation
    )
    return client.create_agent(
        name="verification_agent",
        instructions=VERIFICATION_INSTRUCTIONS,
        tools=[
            cross_reference_benchmarks,
            evaluate_fragility,
            generate_zkp_proof,
            run_autonomous_simulation,
        ],
    )
