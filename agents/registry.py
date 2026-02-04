"""Agent Registry: dynamic selection of analysts by security, sector, and analysis type."""
from typing import List, Optional

from schemas import AnalysisType


# Analyst role names used by the orchestrator
TECHNICAL_ANALYST = "technical_analyst"
FUNDAMENTAL_ANALYST = "fundamental_analyst"
RISK_ANALYST = "risk_analyst"


class AgentRegistry:
    """
    Registry to select which domain agents should be invoked for a given
    classification (NLU output). Supports sector- and security-based overrides.
    """

    def __init__(self) -> None:
        self._sector_to_analysts: dict[str, List[str]] = {
            "technology": [TECHNICAL_ANALYST, FUNDAMENTAL_ANALYST],
            "financials": [FUNDAMENTAL_ANALYST, TECHNICAL_ANALYST],
            "healthcare": [FUNDAMENTAL_ANALYST, TECHNICAL_ANALYST],
            "energy": [FUNDAMENTAL_ANALYST, TECHNICAL_ANALYST],
            "default": [TECHNICAL_ANALYST, FUNDAMENTAL_ANALYST],
        }
        self._agents: dict[str, object] = {}

    def register(self, role: str, agent: object) -> None:
        """Register an agent by role name."""
        self._agents[role] = agent

    def get_agent(self, role: str) -> Optional[object]:
        """Get registered agent by role."""
        return self._agents.get(role)

    def select_analysts(
        self,
        analysis_type: AnalysisType,
        security: Optional[str] = None,
        sector: Optional[str] = None,
    ) -> List[str]:
        """
        Return ordered list of analyst roles to invoke based on classification.
        Risk analyst is always included when we have a security (before finalizing strategy).
        """
        base: List[str] = []
        if analysis_type == AnalysisType.TECHNICAL:
            base = [TECHNICAL_ANALYST]
        elif analysis_type == AnalysisType.FUNDAMENTAL:
            base = [FUNDAMENTAL_ANALYST]
        elif analysis_type in (AnalysisType.BOTH, AnalysisType.UNKNOWN):
            sector_key = (sector or "default").lower().strip() if sector else "default"
            base = self._sector_to_analysts.get(sector_key, self._sector_to_analysts["default"]).copy()
        elif analysis_type == AnalysisType.RISK_ONLY:
            base = [RISK_ANALYST]

        # Always add risk before strategy synthesis when we have a security
        if security and RISK_ANALYST not in base:
            base.append(RISK_ANALYST)
        return base


_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Singleton access to the agent registry."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
