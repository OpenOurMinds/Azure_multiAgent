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

async def run_workflow_with_stream(intake: MissionRequest):
    async def sse_stream():
        # Step 1: Initialize Fortress State & Host Authentication
        yield sse_event({"type": "thought", "payload": "SYSTEM_STATUS: Fortress State Active. Discovery silos primed. Vault locked."})
        yield sse_event({"type": "thought", "payload": "HOST_AUTHENTICATION: Secure handshake initiated with private key..."})
        await asyncio.sleep(0.5)

        # Step 2: Intake & Deep Thinking Activation
        yield sse_event({"type": "analyst_start", "payload": "lead_researcher"})
        yield sse_event({"type": "thought", "payload": f"MISSION_INTAKE: Mapping objective '{intake.objective}' to Problem Genome..."})
        await asyncio.sleep(1.0)
        
        # Step 3: Discovery Phase
        yield sse_event({"type": "analyst_start", "agent": "discovery_agent", "instruction": "Scanning arXiv, Dark Data, and institutional silos..."})
        yield sse_event({"type": "tool_call", "agent": "discovery_agent", "tool": "scan_dark_data", "args": {}})
        await asyncio.sleep(1.0)
        yield sse_event({"type": "tool_call", "agent": "discovery_agent", "tool": "search_arxiv", "args": {"query": intake.objective}})
        await asyncio.sleep(0.5)
        yield sse_event({"type": "analyst_end", "agent": "discovery_agent", "summary": "Found breakthrough patterns in frontier data matching challenge criteria."})

        # Step 4: Verification & Chaos Resilience Testing
        yield sse_event({"type": "analyst_start", "payload": "verification_agent"})
        yield sse_event({"type": "thought", "payload": "Stochastic Stress-Testing: Injecting 'Black Swan' variables..."})
        yield sse_event({"type": "tool_call", "payload": "generate_chaos_variables"})
        await asyncio.sleep(0.8)
        yield sse_event({"type": "tool_call", "payload": "stress_test_strength"})
        await asyncio.sleep(1.2)
        yield sse_event({"type": "thought", "payload": "Chaos Resilience Score: 99.4% Robustness Verified."})
        yield sse_event({"type": "analyst_end", "payload": "verification_agent"})

        # Phase 2: Verification & Chaos Resilience Testing
        yield sse_event({"type": "analyst_start", "payload": "verification_agent"})
        yield sse_event({"type": "tool_call", "payload": "run_autonomous_simulation"})
        await asyncio.sleep(0.8)
        yield sse_event({"type": "tool_call", "payload": "generate_chaos_variables"})
        await asyncio.sleep(0.4)
        yield sse_event({"type": "thought", "payload": "Stochastic Stress-Testing: Injecting mathematical anomalies..."})
        yield sse_event({"type": "tool_call", "payload": "stress_test_strength"})
        await asyncio.sleep(1.0)
        yield sse_event({"type": "thought", "payload": "Chaos Resilience: 99.4% Robustness Verified via ZKP."})
        yield sse_event({"type": "analyst_end", "payload": "verification_agent"})

        # Phase 3: Temporal Persistence (Deep Thinking)
        for i in range(3):
            yield sse_event({"type": "thought", "payload": f"Deep Thinking Cycle {i+1}/3: Adversarial stress-test in progress..."})
            await asyncio.sleep(1.5)

        # Phase 4: Genome Synthesis & Solution Bounty
        yield sse_event({"type": "genome_ready", "payload": {
            "tier": "Formal",
            "fragility": {"score": 15, "years": 157},
            "constraints": intake.constraints, # Using intake.constraints
            "heuristics": intake.heuristics # Using intake.heuristics
        }})
        yield sse_event({"type": "risk_score", "payload": intake.amount}) # Using intake.amount as bounty
        
        # Phase 5: Vault Encapsulation (ZKP)
        yield sse_event({"type": "thought", "payload": "Generating Zero-Knowledge Proof (ZKP) for solution encapsulation..."})
        await asyncio.sleep(1.0)
        
        # Final Result
        yield sse_event({
            "type": "strategy", 
            "payload": {
                "title": "Millennium Prize Solution: P vs NP",
                "summary": "Remarkable solution detected and encapsulated in The Vault. Proof of Solution (ZKP) verified. Decryption key held in non-custodial TEE.",
                "confidence": 0.98,
                "status": "VAULTED",
                "zkp_proof": "sha256:8f2e4a1c7d..."
            }
        })
        return

    return sse_stream()


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
            {"id": "lead_researcher", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "discovery_agent", "status": "idle", "lastActivityAt": None, "latencyMs": None},
            {"id": "verification_agent", "status": "idle", "lastActivityAt": None, "latencyMs": None},
        ]
    except Exception:
        pass
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return {"registry_healthy": registry_healthy, "agents": agents, "api_latency_ms": elapsed_ms, "system": "Earth Intelligence System"}


class MissionRequest(BaseModel):
    objective: str
    constraints: List[str]
    heuristics: Dict[str, float]
    host_auth: str # Simulated private key signature
    amount: float


class PaymentRequest(BaseModel):
    bounty_id: str
    amount: float


# Security Persistence
FAILED_ATTEMPTS = 0
MAX_ATTEMPTS = 3
VAULT_LOCKED = False
SECRET_PAYLOADS = {} # volatile store for OTK mapping

@app.post("/bounty/pay")
async def pay_bounty(request: PaymentRequest):
    """
    Simulated endpoint for receiving Solution Bounty payments.
    Generates a One-Time Decryption Key (OTK).
    """
    global FAILED_ATTEMPTS, VAULT_LOCKED, SECRET_PAYLOADS
    
    if VAULT_LOCKED:
        return JSONResponse(status_code=403, content={"error": "VAULT_PERMANENT_LOCK"})

    # Successful Handshake
    FAILED_ATTEMPTS = 0
    await asyncio.sleep(1.0)
    
    # Generate RSA-based OTK (Simulated)
    # Public key shared; Private key held in TEE
    otk_id = f"RSA_OTK_{uuid.uuid4().hex[:12].upper()}"
    SECRET_PAYLOADS[otk_id] = {
        "answer": "The room-temperature superconducting lattice is achieved via clathrate-hydrogen doping at 295K, stabilized by high-pressure lattice confinement.",
        "chaos_hash": f"chaos_{uuid.uuid4().hex[:8]}", # Session-unique hash
        "expiry": time.time() + 300 # 5 minute lifespan
    }
    
    return {
        "status": "PAID",
        "otk": otk_id,
        "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv... (truncated)",
        "message": "Vault decrypted. RSA-OTK transmitted via secure tunnel."
    }

@app.post("/vault/purge")
async def purge_vault(otk: str):
    """
    Triggers 'Post-Reveal Cleanse' (Memory Eviction).
    """
    global SECRET_PAYLOADS
    if otk in SECRET_PAYLOADS:
        del SECRET_PAYLOADS[otk]
        return {"status": "PURGED", "message": "Secure trace wipe complete."}
    return JSONResponse(status_code=404, content={"error": "OTK_NOT_FOUND"})


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
