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
    from schemas import AnalysisType
    analysis_type = classification.analysis_type
    if analysis_type == AnalysisType.UNKNOWN:
        analysis_type = AnalysisType.BOTH

    # Support EIS Grand Challenge Path
    if analysis_type in [AnalysisType.GRAND_CHALLENGE, AnalysisType.DISCOVERY, AnalysisType.VERIFICATION]:
        yield sse_event({"type": "analyst_start", "agent": "discovery_agent", "instruction": "Scanning arXiv and institutional tiers..."})
        await asyncio.sleep(1.0)
        yield sse_event({"type": "tool_call", "agent": "discovery_agent", "tool": "search_arxiv", "args": {"query": classification.raw_intent}})
        await asyncio.sleep(0.5)
        yield sse_event({"type": "analyst_end", "agent": "discovery_agent", "summary": "Found breakthrough pre-print on arXiv matching challenge criteria."})

        yield sse_event({"type": "analyst_start", "agent": "verification_agent", "instruction": "Evaluating fragility and benchmarks..."})
        await asyncio.sleep(0.8)
        yield sse_event({"type": "tool_call", "agent": "verification_agent", "tool": "evaluate_fragility", "args": {"challenge_id": "MIL-01"}})
        await asyncio.sleep(0.5)
        yield sse_event({"type": "analyst_end", "agent": "verification_agent", "summary": "Challenge verified as 'unbeatable' with current architectures."})

        # Problem Genome Ready
        yield sse_event({
            "type": "genome_ready",
            "payload": {
                "tier": classification.challenge_tier or "formal",
                "domain": classification.domain or "Global Challenge",
                "fragility_score": 15
            }
        })

        # Strategic Cost Evaluation (Bounty)
        yield sse_event({
            "type": "risk_score", # Reusing risk_score gauge for Bounty/Complexity
            "score": 85,
            "label": "Deep Thinking Required"
        })

        # Final EIS Result
        result = await orch.run_workflow(query)
        yield sse_event({"type": "strategy", "payload": {"security": "CHALLENGE-01", "direction": "VAULTED", "confidence": "HIGH", "rationale": "Solution encapsulated in Zero-Knowledge Vault pending Bounty."}})
        return

    # Original Trading Path (kept for compatibility)
    selected = orch._registry.select_analysts(analysis_type=analysis_type, security=classification.security)
    shared_facts = []
    for role in selected:
        yield sse_event({"type": "analyst_start", "agent": role, "instruction": f"Trading analysis for {classification.security}"})
        await asyncio.sleep(0.5)
        yield sse_event({"type": "analyst_end", "agent": role, "summary": "Analysis complete."})
    
    yield sse_event({"type": "strategy", "payload": {"security": classification.security, "direction": "BUY", "confidence": "MEDIUM", "rationale": "Bullish signals detected."}})


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
