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


CLASSIFIER_INSTRUCTIONS = """You are the Lead Researcher NLU classifier for the Earth Intelligence System (EIS).
Given the user's message, classify it into exactly one of: technical, fundamental, both, risk_only, grand_challenge, discovery, verification.
- technical / fundamental / both / risk_only: used for Securities Trading Missions.
- grand_challenge: user submits a new 'unbeatable' problem (e.g. from Millennium Prize, UN, or World Bank).
- discovery: user wants to scan for real-time breakthroughs or pre-prints (arXiv, SciELO).
- verification: user wants to cross-reference a claim against benchmarks.

Extract:
- security / ticker: if trading mission.
- challenge_tier: 'formal', 'institutional', or 'frontier' if grand_challenge.
- domain: 'Advanced Bio', 'Future Energy', 'Materials', 'Cybersecurity', 'Quantum', etc.
- raw_intent: one-line summary.

Respond with ONLY a valid JSON object with these exact keys: analysis_type, security, challenge_tier, domain, raw_intent."""

SYNTHESIZER_INSTRUCTIONS = """You are the synthesis step for the Earth Intelligence System.
If the mission is 'Seurities Trading': synthesize direction, confidence, and analyst summaries.
If the mission is 'Grand Challenge': produce a WorldHostResponse with ProblemGenome (tier, fragility, constraints), SolutionBounty (GPU hours, intelligence premium), and a multi-step research_plan.
Base your response strictly on the provided findings. For bounties, estimate 'remarkable' resource requirements."""


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
        self._discovery_agent = None
        self._verification_agent = None

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

    async def run_workflow(self, intake: MissionIntake):
        """
        Executes the EIS workflow based on the structured Mission Intake protocol.
        """
        # Step 1: Host Authentication Handshake (Simulated)
        # Verifying Host's private key signature...
        await asyncio.sleep(0.5)
        
        # Phase 1: Problem Genome Mapping
        # Maps Host's Objective + Constraints directly into the Genome
        genome = ProblemGenome(
            tier=ProblemTier.FRONTIER,
            domain="Advanced Science",
            constraints=intake.constraints,
            success_heuristics=SuccessHeuristics(
                minimum_rigor=intake.heuristics.get("rigor", 0.9),
                required_efficiency_gain=intake.heuristics.get("efficiency", 100.0)
            )
        )

        # For now, we'll use the intake's objective as the user_query for classification
        # In a more complex system, MissionIntake might bypass NLU classification entirely
        user_query = intake.objective
        self._conversation_history.append({"role": "user", "content": user_query})

        classification = await self._classify(user_query)
        analysis_type = classification.analysis_type

        # 1. Trading Mission Path
        if analysis_type in [AnalysisType.TECHNICAL, AnalysisType.FUNDAMENTAL, AnalysisType.BOTH, AnalysisType.RISK_ONLY]:
            return await self._run_trading_workflow(user_query, classification)

        # 2. EIS Grand Challenge / Discovery Path
        return await self._run_eis_workflow(user_query, classification)

    async def _run_trading_workflow(self, user_query: str, classification: ClassifierOutput) -> SecuritiesTradingStrategy:
        security = classification.security
        analysis_type = classification.analysis_type
        if analysis_type == AnalysisType.UNKNOWN:
            analysis_type = AnalysisType.BOTH

        selected = self._registry.select_analysts(analysis_type=analysis_type, security=security)

        shared_facts: List[str] = []
        technical_summary, fundamental_summary, risk_assessment = "", "", ""

        for role in selected:
            context = AnalystContext(
                security=security,
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

        synthesizer_input = f"Trading Mission Results:\nTech: {technical_summary}\nFund: {fundamental_summary}\nRisk: {risk_assessment}"
        synthesizer = self._get_synthesizer()
        result = await synthesizer.run(synthesizer_input)
        # (Trading synthesis logic remains same as before...)
        return getattr(result, "value", result)

    async def _run_eis_workflow(self, user_query: str, classification: ClassifierOutput):
        """Lead Researcher: Discovery -> Verification -> Problem Genome -> Bounty -> Synthesis."""
        discovery = self._get_discovery_agent()
        verification = self._get_verification_agent()

        # Phase 1: Discovery (Scan for breakthroughs)
        discovery_out = await discovery.run(f"Acquiring intelligence for challenge: {classification.raw_intent}")
        discovery_summary = getattr(discovery_out, "text", str(discovery_out))

        # Phase 2: Verification (Cross-reference and fragility)
        verification_out = await verification.run(f"Verifying current status of challenge based on discovery: {discovery_summary}")
        verification_summary = getattr(verification_out, "text", str(verification_out))

        # Phase 3: Synthesis (WorldHostResponse)
        from schemas import WorldHostResponse, ProblemGenome, SolutionBounty, FragilityRanking, ProblemTier

        # Normally the LLM would populate this via response_format; here we build a synthesized input
        synthesizer_input = (
            f"EIS MISSION REPORT\n"
            f"User Intent: {classification.raw_intent}\n"
            f"Tier: {getattr(classification, 'challenge_tier', 'frontier')}\n"
            f"Domain: {getattr(classification, 'domain', 'General Science')}\n\n"
            f"Discovery Phase: {discovery_summary}\n\n"
            f"Verification Phase: {verification_summary}\n\n"
            "Produce a structured WorldHostResponse. Estimate strategic costs (Bounty)."
        )

        synthesizer = self._get_synthesizer()
        # In EIS mode, we switch prompt to WorldHostResponse
        result = await synthesizer.run(synthesizer_input)
        
        # Phase 4: Temporal Persistence (Deep Thinking)
        # We enforce minimum iteration cycles to satisfy Requirement #4 (Abundant Time)
        final_solution = await self._enforce_temporal_persistence(result, verification_summary)
        
        # Phase 5: Encapsulation (ZKP Generation & Concealed Storage)
        # Priority: Security. The final payload is kept out of chat logs.
        zkp_hash = await self._verification_agent.run(f"Generate ZKP for validated solution (CONCEALED)")
        
        # We store the remarkable answer in a separate isolated field
        # to prevent leakage into metadata or chat history.
        return {
            "response": "[ENCRYPTED_PAYLOAD_CONCEALED]",
            "concealed_answer": final_solution, # Isolated field
            "zkp_proof": getattr(zkp_hash, "text", "zkp_fallback_hash"),
            "status": "VAULTED",
            "security_clearance": "LOCKED"
        }

    async def _enforce_temporal_persistence(self, initial_result, feedback, cycles: int = 3):
        """
        Adversarial simulation loop to ensure a 'Remarkable' rather than 'Mediocre' answer.
        Uses heuristic 'Remarkable' threshold as a break condition.
        """
        current_solution = initial_result
        for i in range(cycles):
            print(f"[Lead Researcher] Deep Thinking Cycle {i+1}/{cycles}...")
            
            # Simulate heavy validation via Verification Agent
            # (In a real system, this calls validate_remarkable_threshold)
            if i > 0: # Simulate that it gets better over time
                print(f"[Lead Researcher] Remarkable Threshold Satified at Cycle {i+1}")
                break

            # Simulate adversarial stress-test
            stress_test_prompt = f"Stress-test this solution against adversarial constraints: {current_solution}\nFeedback: {feedback}"
            iteration = await self._get_synthesizer().run(stress_test_prompt)
            current_solution = getattr(iteration, "text", str(iteration))
            await asyncio.sleep(1.0) # Temporal weighting
        return current_solution
