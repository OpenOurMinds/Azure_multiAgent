# Command Center Dashboard — Wireframe & Component Architecture

## 1. Wireframe: Command Center Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  HEADER: Multi-Agent Trading Command Center     [System Health ●] [API Latency 42ms] [User]  │
├──────────────┬──────────────────────────────────────────────────────┬──────────────────────┤
│              │                                                        │                      │
│  AGENT       │  CENTER: Strategy Synthesis + Reasoning Trace          │  RISK / PORTFOLIO   │
│  STATUS      │                                                        │  METRICS            │
│  (Left       │  ┌─────────────────────────────────────────────────┐  │  (Right Sidebar)     │
│   Sidebar)   │  │ Strategy Synthesis View                          │  │                    │
│              │  │ • Direction: BUY / HOLD / SELL  • Confidence      │  │  • Risk Score       │
│  • Orch.     │  │ • Data points from Technical / Fundamental       │  │  • Position limits  │
│  • Classifier│  │   that contributed to recommendation             │  │  • Volatility       │
│  • Technical │  └─────────────────────────────────────────────────┘  │  • HITL Gateway     │
│  • Fundamental│  ┌─────────────────────────────────────────────────┐  │    [Approve] [Reject]│
│  • Risk      │  │ Reasoning Trace (Parallel Streams)               │  │  • Portfolio summary │
│              │  │ ┌─ Technical ─────┐ ┌─ Fundamental ─────┐        │  │                    │
│  [Idle/      │  │ │ Tool: RSI...    │ │ │ Tool: P/E...     │        │  │  • Market intel    │
│   Running]   │  │ │ Tool: Volume... │ │ │ Tool: Earnings.. │        │  │    (mini charts)   │
│              │  │ └─────────────────┘ └───────────────────┘        │  │                    │
│  Registry    │  └─────────────────────────────────────────────────┘  │                    │
│  health      │  ┌─────────────────────────────────────────────────┐  │                    │
│              │  │ Market Intelligence                              │  │                    │
│              │  │ [Candlesticks] [Volume] [Fundamentals table/radar]│  │                    │
│              │  └─────────────────────────────────────────────────┘  │                    │
│              │                                                        │                      │
├──────────────┴──────────────────────────────────────────────────────┴──────────────────────┤
│  FOOTER: Query input [________________________] [Run]   Last strategy: AAPL BUY @ 12:34     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Layout Summary

| Zone | Purpose |
|------|--------|
| **Left sidebar** | Agent Status (Orchestrator, Classifier, Technical, Fundamental, Risk), registry status, per-agent state (idle / running / error). |
| **Center** | Strategy Synthesis View (recommendation + contributing data points); Reasoning Trace (parallel streams of tool calls); Market Intelligence (candlesticks, volume, fundamentals). |
| **Right sidebar** | Risk Score, position limits, volatility; HITL Strategy Approval gateway (Approve / Reject); portfolio and market summary. |
| **Header** | System Health, API latency, user. |
| **Footer** | Query input, Run, last strategy summary. |

---

## 2. React Component Structure

```
App / CommandCenterPage
├── Header
│   ├── SystemHealthMonitor   (API latency, agent registry status)
│   └── UserMenu
├── MainLayout (3-column grid)
│   ├── LeftSidebar
│   │   └── AgentStatusPanel
│   │       ├── AgentStatusCard (per agent: name, status, last activity)
│   │       └── RegistryHealth
│   ├── CenterWorkspace
│   │   ├── StrategySynthesisView
│   │   │   ├── RecommendationCard (direction, confidence)
│   │   │   ├── ContributingDataPoints (citations from Technical/Fundamental)
│   │   │   └── RationaleBlock
│   │   ├── ReasoningTrace
│   │   │   ├── ThoughtLog (unified or per-stream)
│   │   │   │   └── ThoughtLogEntry (parsed reasoning step)
│   │   │   ├── TechnicalStream
│   │   │   │   └── ThoughtLog (agent=technical)
│   │   │   └── FundamentalStream
│   │   │       └── ThoughtLog (agent=fundamental)
│   │   └── MarketIntelligence
│   │       ├── CandlestickChart (Recharts/D3)
│   │       ├── VolumeOverlay
│   │       └── FundamentalsPanel (tables / radar)
│   └── RightSidebar
│       ├── RiskMetricsPanel
│       │   ├── RiskScoreGauge
│       │   ├── PositionLimits
│       │   └── VolatilityIndicator
│       ├── HITLStrategyApproval (gateway)
│       │   ├── PendingStrategyCard
│       │   ├── RiskScoreDisplay
│       │   └── ApproveRejectButtons
│       └── PortfolioSummary
├── Footer
│   ├── QueryInput
│   └── RunButton / LastStrategySummary
└── SSEProvider / WebSocketProvider (streaming state)
```

---

## 3. ThoughtLog Component — Parsing Agent Reasoning Steps

**Responsibility:** Consume a stream of "thought" events from the backend and render them as a chronological or per-agent log. Each event is parsed into a structured step (e.g. tool_call, reasoning, conclusion).

### Event Shape (from backend SSE)

```ts
type ThoughtEvent =
  | { type: 'classification'; payload: ClassifierOutput }
  | { type: 'analyst_start'; agent: AgentId; instruction: string }
  | { type: 'thought'; agent: AgentId; step: string; payload: unknown }
  | { type: 'tool_call'; agent: AgentId; tool: string; args: Record<string, unknown> }
  | { type: 'tool_result'; agent: AgentId; tool: string; result: string }
  | { type: 'analyst_end'; agent: AgentId; summary: string }
  | { type: 'strategy'; payload: SecuritiesTradingStrategy }
  | { type: 'risk_score'; score: number; label: string };
```

### ThoughtLog Parsing Logic

- **classification** → Show "Intent classified as …" with analysis_type and security.
- **analyst_start** → Start a stream section for that agent (Technical / Fundamental).
- **thought** → Internal reasoning step: display `step` + optional `payload` (e.g. "Evaluating trend").
- **tool_call** → "Fetching …" / "Calculating …" (e.g. "Fetching AAPL P/E Ratio", "Calculating RSI"); show tool name and sanitized args.
- **tool_result** → Collapsible or inline result snippet for that tool.
- **analyst_end** → End stream section and show summary.
- **strategy** → Hand off to StrategySynthesisView.
- **risk_score** → Hand off to RiskMetricsPanel and HITL gateway.

### Component API

```tsx
interface ThoughtLogProps {
  events: ThoughtEvent[];           // or from SSE hook
  filter?: { agent?: AgentId };    // optional filter to one stream
  showToolResults?: boolean;
  maxHeight?: string;
}
```

Rendered structure: list of `ThoughtLogEntry` items; each entry maps one event to a single line or block (icon, agent badge, message, timestamp). Tool calls are highlighted (e.g. "Fetching AAPL P/E Ratio") so the Reasoning Trace clearly shows parallel activity of Fundamental and Technical analysts.

---

## 4. Data Flow

- **SSE/WebSocket:** Backend streams `ThoughtEvent` (and optionally market data) to the client.
- **State:** React context or store holds: `thoughtEvents[]`, `currentStrategy`, `riskScore`, `agentStatus`, `systemHealth`.
- **HITL:** When `risk_score` exceeds threshold, show HITL gateway; strategy is "pending" until Approve/Reject; result sent back to backend.

---

## 5. Tech Stack

| Concern | Choice |
|--------|--------|
| Framework | Next.js (App Router) |
| Styling | Tailwind CSS |
| Charts | Recharts (candlesticks, volume, radar) |
| Accessible UI | Radix UI |
| State / Streaming | React state + SSE hook (or WebSocket) |
| Observability | SystemHealthMonitor (latency, agent status from backend) |

This wireframe and component structure define the Command Center layout, the Reasoning Trace with parallel streams, and the ThoughtLog component that parses and displays agent reasoning steps before the final strategy conclusion.

---

## 6. Implementation (Dashboard)

- **Dashboard app**: `dashboard/` — Next.js 14 (App Router), Tailwind CSS, Radix UI (Tabs, Progress), Recharts (AreaChart, BarChart).
- **Streaming**: `hooks/useThoughtStream.ts` — SSE client to `GET /stream?query=...`; falls back to mock events if backend unavailable.
- **Backend**: `api/stream_server.py` — FastAPI app with `GET /health` and `GET /stream?query=...` that runs the orchestrator and yields ThoughtEvent SSE messages.
- **Run**:
  - Backend: from repo root, `uvicorn api.stream_server:app --reload --port 8000`
  - Dashboard: `cd dashboard && npm install && npm run dev` (set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local` for real streaming).
