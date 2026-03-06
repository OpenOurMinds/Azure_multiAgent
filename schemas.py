"""Shared schemas for the multi-agent trading system: classification, context, and strategy output."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    """NLU classification: which analysis path(s) the user query requires."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    BOTH = "both"
    RISK_ONLY = "risk_only"
    DISCOVERY = "discovery"  # EIS: Scan for breakthroughs
    VERIFICATION = "verification" # EIS: Cross-reference benchmarks
    GRAND_CHALLENGE = "grand_challenge" # EIS: Full World Host intake
    UNKNOWN = "unknown"


class MissionIntake(BaseModel):
    objective: str
    constraints: List[str]
    heuristics: Dict[str, float]

class ProblemTier(str, Enum):
    """The three primary tiers of challenges in the Earth Intelligence System."""
    FORMAL = "formal"          # Millennium Prize, etc.
    INSTITUTIONAL = "institutional" # UN, World Bank, etc.
    FRONTIER = "frontier"      # arXiv, SciELO pre-prints


class ClassifierOutput(BaseModel):
    """Output of the Orchestrator's NLU classifier."""
    analysis_type: AnalysisType = Field(description="Required analysis type(s)")
    security: Optional[str] = Field(default=None, description="Ticker or symbol if mentioned")
    sector: Optional[str] = Field(default=None, description="Market sector if mentioned")
    time_horizon: Optional[str] = Field(default=None, description="e.g. short_term, medium_term, long_term")
    raw_intent: str = Field(description="One-line summary of user intent")


class AnalystContext(BaseModel):
    """Context passed from Orchestrator to domain agents to avoid redundant tool calls."""
    security: Optional[str] = None
    sector: Optional[str] = None
    time_horizon: Optional[str] = None
    shared_facts: list[str] = Field(default_factory=list, description="Facts already gathered to reuse")
    orchestrator_instruction: str = Field(description="Specific task for this analyst")


class SecuritiesTradingStrategy(BaseModel):
    """Structured output synthesizing all agents' findings."""
    security: Optional[str] = Field(default=None, description="Primary security or basket")
    direction: str = Field(description="BUY / SELL / HOLD")
    confidence: str = Field(description="LOW / MEDIUM / HIGH")
    technical_summary: str = Field(description="Technical analyst findings")
    fundamental_summary: str = Field(description="Fundamental analyst findings")
    risk_assessment: str = Field(description="Risk management assessment")
    rationale: str = Field(description="Combined rationale for the strategy")
    conditions: list[str] = Field(default_factory=list, description="Conditions under which strategy holds")
    warnings: list[str] = Field(default_factory=list, description="Risk warnings and caveats")


# --- Earth Intelligence System (EIS) Schemas ---

class FragilityRanking(BaseModel):
    """How likely a challenge is to be solved soon vs resistant."""
    score: int = Field(ge=1, le=100, description="1=Centuries resistant, 100=Solved soon")
    rationale: str = Field(description="Why this fragility score was assigned")


class SuccessHeuristics(BaseModel):
    """Metrics that define a 'Remarkable' solve for a specific tier."""
    minimum_rigor: int = Field(ge=1, le=10)
    required_efficiency_gain: Optional[float] = None
    novelty_threshold: float = Field(default=0.8)
    adversarial_resistance: float = Field(default=0.9)


class ProblemGenome(BaseModel):
    """The machine-readable definition of a grand challenge."""
    challenge_id: str
    title: str
    tier: ProblemTier
    fragility: FragilityRanking
    constraints: list[str]
    success_metrics: list[str]
    heuristics: SuccessHeuristics
    domain: str = Field(description="e.g. Advanced Bio, Future Energy, Quantum")
    raw_source: str = Field(description="e.g. Clay Math, UN Global Issues")


class SolutionBounty(BaseModel):
    """The strategic cost evaluation for a 'remarkable answer'."""
    compute_weight_gpu_hours: float
    intelligence_premium_usd: float
    total_quote_usd: float
    proof_of_solution_hash: Optional[str] = Field(default=None, description="Zero-knowledge proof identifier")


class WorldHostResponse(BaseModel):
    """The finalized response from the Lead Researcher to the World Host."""
    genome: ProblemGenome
    bounty: SolutionBounty
    is_unbeatable: bool = Field(description="Whether current intelligence can solve it immediately")
    research_plan: list[str]
    status: str = Field(default="Active / Decoupled / Vaulted")
