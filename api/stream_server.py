"""
SSE backend for the Command Center dashboard.
Streams ThoughtEvent-shaped events during orchestrator workflow for real-time Reasoning Trace.
Run: uvicorn api.stream_server:app --reload --port 8000
Set NEXT_PUBLIC_API_URL=http://localhost:8000 in dashboard .env.
"""
import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Lazy imports to avoid loading agent_framework if not used
_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from dotenv import load_dotenv
        load_dotenv()
        from agent_framework.azure import AzureOpenAIResponsesClient
        from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
        from agents.orchestrator import OrchestratorAgent
        client = AzureOpenAIResponsesClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            deployment_name=AZURE_OPENAI_DEPLOYMENT,
        )
        _orchestrator = OrchestratorAgent(client=client)
    return _orchestrator


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def run_workflow_with_stream(query: str):
    """Yield SSE events while running the orchestrator workflow."""
    from schemas import AnalystContext
    from agents.registry import TECHNICAL_ANALYST, FUNDAMENTAL_ANALYST, RISK_ANALYST
    from agents.orchestrator import OrchestratorAgent

    orch = get_orchestrator()
    classification = await orch._classify(query)
    yield sse_event({
        "type": "classification",
        "payload": {
            "analysis_type": classification.analysis_type.value,
            "security": classification.security,
            "sector": classification.sector,
            "time_horizon": classification.time_horizon,
            "raw_intent": classification.raw_intent,
        },
    })

    security = classification.security
    sector = classification.sector
    time_horizon = classification.time_horizon
    from schemas import AnalysisType
    analysis_type = classification.analysis_type
    if analysis_type == AnalysisType.UNKNOWN:
        analysis_type = AnalysisType.BOTH
    selected = orch._registry.select_analysts(analysis_type=analysis_type, security=security, sector=sector)

    shared_facts = []
    technical_summary = ""
    fundamental_summary = ""
    risk_assessment = ""

    for role in selected:
        yield sse_event({
            "type": "analyst_start",
            "agent": role,
            "instruction": f"User objective: {classification.raw_intent}. Provide your analysis concisely.",
        })
        # Simulate tool calls (framework may not expose granular tool events; we emit placeholders)
        if role == TECHNICAL_ANALYST and security:
            yield sse_event({"type": "tool_call", "agent": role, "tool": "get_price_history", "args": {"symbol": security, "period": "1mo"}})
            yield sse_event({"type": "tool_call", "agent": role, "tool": "get_volume_analysis", "args": {"symbol": security}})
        elif role == FUNDAMENTAL_ANALYST and security:
            yield sse_event({"type": "tool_call", "agent": role, "tool": "get_earnings_summary", "args": {"symbol": security}})
        elif role == RISK_ANALYST and security:
            yield sse_event({"type": "tool_call", "agent": role, "tool": "evaluate_volatility", "args": {"symbol": security}})

        context = AnalystContext(
            security=security,
            sector=sector,
            time_horizon=time_horizon,
            shared_facts=shared_facts,
            orchestrator_instruction=f"User objective: {classification.raw_intent}. Provide your analysis concisely.",
        )
        out = await orch._run_analyst(role, context)
        yield sse_event({"type": "analyst_end", "agent": role, "summary": out[:300]})
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

    # Simple risk score heuristic (0-100) from risk_assessment text
    risk_score = 35
    if "EXCEEDS" in risk_assessment or "high" in risk_assessment.lower():
        risk_score = 70
    elif "WITHIN" in risk_assessment:
        risk_score = 25
    yield sse_event({"type": "risk_score", "score": risk_score, "label": "Moderate" if risk_score < 60 else "High"})

    synthesizer_input = (
        f"User query: {query}\n\n"
        f"Technical Analyst findings:\n{technical_summary}\n\n"
        f"Fundamental Analyst findings:\n{fundamental_summary}\n\n"
        f"Risk Management findings:\n{risk_assessment}\n\n"
        "Produce the structured Securities Trading Strategy (direction, confidence, summaries, rationale, conditions, warnings)."
    )
    synthesizer = orch._get_synthesizer()
    result = await synthesizer.run(synthesizer_input)
    from schemas import SecuritiesTradingStrategy
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
                warnings=["Structured parsing failed."],
            )
    strategy.security = strategy.security or security
    yield sse_event({"type": "strategy", "payload": strategy.model_dump()})


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # shutdown


app = FastAPI(title="Trading Command Center API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """System health for observability: API latency, agent registry status."""
    import time
    start = time.perf_counter()
    registry_healthy = False
    agents = []
    try:
        orch = get_orchestrator()
        registry_healthy = orch._registry is not None
        agents = [
            {"id": "orchestrator", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "classifier", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "technical_analyst", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "fundamental_analyst", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "risk_analyst", "status": "idle", "lastActivityAt": None, "latencyMs": None},
        ]
    except Exception:
        pass
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return {"registry_healthy": registry_healthy, "agents": agents, "api_latency_ms": elapsed_ms}


@app.get("/stream")
async def stream(query: str = ""):
    """SSE stream of ThoughtEvents for the Reasoning Trace."""
    if not query:
        return StreamingResponse(
            iter([sse_event({"type": "strategy", "payload": None})]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    return StreamingResponse(
        run_workflow_with_stream(query),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
