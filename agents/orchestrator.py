"""Central Orchestrator: NLU classifier, delegation, shared context, and strategy synthesis."""
import asyncio
from typing import List, Optional

from agent_framework.azure import AzureOpenAIResponsesClient

from schemas import (
    AnalysisType,
    ClassifierOutput,
    AnalystContext,
    SecuritiesTradingStrategy,
)
from agents.registry import AgentRegistry, get_registry, TECHNICAL_ANALYST, FUNDAMENTAL_ANALYST, RISK_ANALYST


CLASSIFIER_INSTRUCTIONS = """You are an NLU classifier for a securities trading system.
Given the user's message, classify it into exactly one of: technical, fundamental, both, risk_only, unknown.
- technical: user asks about price, charts, volume, trends, moving averages, technical indicators.
- fundamental: user asks about earnings, financials, balance sheet, macro, valuation, growth.
- both: user asks for full analysis or a trading strategy combining technical and fundamental.
- risk_only: user asks only about risk, volatility, limits, drawdown.
- unknown: cannot determine or general question.
Extract: security (ticker/symbol if mentioned, e.g. AAPL), sector (if mentioned), time_horizon (short_term/medium_term/long_term if mentioned), and raw_intent (one-line summary).
Respond with ONLY a valid JSON object with these exact keys: analysis_type, security, sector, time_horizon, raw_intent. Use null for missing optional fields."""

SYNTHESIZER_INSTRUCTIONS = """You are the synthesis step of a multi-agent trading system.
You receive findings from the Technical Analyst, Fundamental Analyst, and Risk Management Agent.
Produce a single structured Securities Trading Strategy: direction (BUY/SELL/HOLD), confidence (LOW/MEDIUM/HIGH), technical_summary, fundamental_summary, risk_assessment, rationale, conditions, and warnings.
Be concise and base the strategy strictly on the provided findings. Do not invent data."""


class OrchestratorAgent:
    """
    Central Orchestrator: manages workflow, classifies user intent (NLU),
    delegates to domain agents with shared context, and synthesizes a
    structured Securities Trading Strategy.
    """

    def __init__(
        self,
        client: AzureOpenAIResponsesClient,
        registry: Optional[AgentRegistry] = None,
    ) -> None:
        self._client = client
        self._registry = registry or get_registry()
        self._conversation_history: List[dict] = []
        # Lazy-built agents
        self._classifier_agent = None
        self._synthesizer_agent = None
        self._technical_agent = None
        self._fundamental_agent = None
        self._risk_agent = None

    def _get_classifier(self):
        if self._classifier_agent is None:
            try:
                self._classifier_agent = self._client.create_agent(
                    name="Classifier",
                    instructions=CLASSIFIER_INSTRUCTIONS,
                    response_format=ClassifierOutput,
                )
            except TypeError:
                self._classifier_agent = self._client.create_agent(
                    name="Classifier",
                    instructions=CLASSIFIER_INSTRUCTIONS,
                )
        return self._classifier_agent

    def _get_synthesizer(self):
        if self._synthesizer_agent is None:
            try:
                self._synthesizer_agent = self._client.create_agent(
                    name="Synthesizer",
                    instructions=SYNTHESIZER_INSTRUCTIONS,
                    response_format=SecuritiesTradingStrategy,
                )
            except TypeError:
                self._synthesizer_agent = self._client.create_agent(
                    name="Synthesizer",
                    instructions=SYNTHESIZER_INSTRUCTIONS,
                )
        return self._synthesizer_agent

    def _get_technical_agent(self):
        if self._technical_agent is None:
            from agents.specialists import build_technical_analyst
            self._technical_agent = build_technical_analyst(self._client)
            self._registry.register(TECHNICAL_ANALYST, self._technical_agent)
        return self._technical_agent

    def _get_fundamental_agent(self):
        if self._fundamental_agent is None:
            from agents.specialists import build_fundamental_analyst
            self._fundamental_agent = build_fundamental_analyst(self._client)
            self._registry.register(FUNDAMENTAL_ANALYST, self._fundamental_agent)
        return self._fundamental_agent

    def _get_risk_agent(self):
        if self._risk_agent is None:
            from agents.specialists import build_risk_analyst
            self._risk_agent = build_risk_analyst(self._client)
            self._registry.register(RISK_ANALYST, self._risk_agent)
        return self._risk_agent

    async def _classify(self, user_query: str) -> ClassifierOutput:
        """Run NLU classifier on user query."""
        classifier = self._get_classifier()
        result = await classifier.run(user_query)
        if hasattr(result, "value") and result.value is not None:
            return result.value
        text = getattr(result, "text", str(result)) or ""
        text = text.strip()
        # Extract JSON block if wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        try:
            return ClassifierOutput.model_validate_json(text)
        except Exception:
            return ClassifierOutput(
                analysis_type=AnalysisType.UNKNOWN,
                raw_intent=text[:200] if text else user_query[:200],
            )

    def _build_context_message(self, context: AnalystContext) -> str:
        parts = [context.orchestrator_instruction]
        if context.security:
            parts.append(f"Security/ticker: {context.security}")
        if context.sector:
            parts.append(f"Sector: {context.sector}")
        if context.time_horizon:
            parts.append(f"Time horizon: {context.time_horizon}")
        if context.shared_facts:
            parts.append("Shared facts (reuse, do not re-fetch): " + "; ".join(context.shared_facts))
        return "\n".join(parts)

    async def _run_analyst(self, role: str, context: AnalystContext) -> str:
        """Run one domain analyst with context and return its text summary."""
        agent = self._registry.get_agent(role)
        if agent is None:
            if role == TECHNICAL_ANALYST:
                agent = self._get_technical_agent()
            elif role == FUNDAMENTAL_ANALYST:
                agent = self._get_fundamental_agent()
            elif role == RISK_ANALYST:
                agent = self._get_risk_agent()
            else:
                return f"Unknown analyst: {role}"
        msg = self._build_context_message(context)
        result = await agent.run(msg)
        return getattr(result, "text", str(result))

    async def run_workflow(self, user_query: str) -> SecuritiesTradingStrategy:
        """
        Classify query -> delegate to analysts with context -> synthesize strategy.
        """
        self._conversation_history.append({"role": "user", "content": user_query})

        classification = await self._classify(user_query)
        security = classification.security
        sector = classification.sector
        time_horizon = classification.time_horizon
        analysis_type = classification.analysis_type

        if analysis_type == AnalysisType.UNKNOWN:
            analysis_type = AnalysisType.BOTH

        selected = self._registry.select_analysts(
            analysis_type=analysis_type,
            security=security,
            sector=sector,
        )

        shared_facts: List[str] = []
        technical_summary = ""
        fundamental_summary = ""
        risk_assessment = ""

        for role in selected:
            context = AnalystContext(
                security=security,
                sector=sector,
                time_horizon=time_horizon,
                shared_facts=shared_facts,
                orchestrator_instruction=f"User objective: {classification.raw_intent}. Provide your analysis concisely.",
            )
            out = await self._run_analyst(role, context)
            if role == TECHNICAL_ANALYST:
                technical_summary = out
                shared_facts.append("Technical: " + out[:300])
            elif role == FUNDAMENTAL_ANALYST:
                fundamental_summary = out
                shared_facts.append("Fundamental: " + out[:300])
            elif role == RISK_ANALYST:
                risk_assessment = out

        if not technical_summary:
            technical_summary = "No technical analysis requested or available."
        if not fundamental_summary:
            fundamental_summary = "No fundamental analysis requested or available."
        if not risk_assessment:
            risk_assessment = "No risk assessment requested or available."

        synthesizer_input = (
            f"User query: {user_query}\n\n"
            f"Technical Analyst findings:\n{technical_summary}\n\n"
            f"Fundamental Analyst findings:\n{fundamental_summary}\n\n"
            f"Risk Management findings:\n{risk_assessment}\n\n"
            "Produce the structured Securities Trading Strategy (direction, confidence, summaries, rationale, conditions, warnings)."
        )

        synthesizer = self._get_synthesizer()
        result = await synthesizer.run(synthesizer_input)
        if hasattr(result, "value") and result.value is not None:
            strategy = result.value
        else:
            text = getattr(result, "text", str(result))
            try:
                strategy = SecuritiesTradingStrategy.model_validate_json(text)
            except Exception:
                strategy = SecuritiesTradingStrategy(
                    security=security,
                    direction="HOLD",
                    confidence="LOW",
                    technical_summary=technical_summary[:500],
                    fundamental_summary=fundamental_summary[:500],
                    risk_assessment=risk_assessment[:500],
                    rationale=text[:500] if text else "Synthesis failed.",
                    conditions=[],
                    warnings=["Structured parsing failed; review raw output."],
                )
        strategy.security = strategy.security or security
        self._conversation_history.append({"role": "assistant", "content": strategy.model_dump_json()})
        return strategy
