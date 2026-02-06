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
    UNKNOWN = "unknown"


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
