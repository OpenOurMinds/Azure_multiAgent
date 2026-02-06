# Azure Multi-Agent Automated Trading System

Hierarchical multi-agent intelligence system for automated trading, following Microsoft's "Designing Multi-Agent Intelligence" patterns.

## Architecture

- **Central Orchestrator**: Classifies user intent (NLU), delegates to domain agents with shared context, maintains conversation history, and synthesizes a structured **Securities Trading Strategy**.
- **Domain-Specialized Agents**:
  - **Fundamental Analyst**: Earnings, income statement, balance sheet, macro indicators (Yahoo Finance / yfinance).
  - **Technical Analyst**: Price history, volume, moving averages, price summary (Yahoo Finance).
  - **Risk Management**: Volatility, position limit compliance, downside risk (drawdown).
- **Agent Registry**: Selects which analysts to invoke by analysis type and optional sector/security.
- **Context Engineering**: Orchestrator passes `AnalystContext` (security, sector, shared_facts) so analysts avoid redundant tool calls.

## Setup

1. **Environment**

   ```bash
   cp .env.example .env
   # Set: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
   # Optional: ALPHA_VANTAGE_API_KEY, MAX_POSITION_PCT, MAX_VOLATILITY_PCT
   ```

2. **Install**

   ```bash
   pip install -r requirements.txt
   ```

   If your framework uses `as_agent` instead of `create_agent`, replace `create_agent` with `as_agent` in `agents/specialists.py` and `agents/orchestrator.py`.

## Usage

Run the full multi-agent pipeline (classify → delegate → synthesize):

```bash
python main.py
```

Override the default query:

```bash
TRADING_QUERY="Should I buy MSFT based on fundamentals and risk?" python main.py
```

Single-agent example with financial tools (reference only):

```bash
python agent_with_tool.py
```

## Output

The system prints a **Securities Trading Strategy** with:

- `direction`: BUY / SELL / HOLD  
- `confidence`: LOW / MEDIUM / HIGH  
- `technical_summary`, `fundamental_summary`, `risk_assessment`  
- `rationale`, `conditions`, `warnings`  

JSON is also printed for downstream systems.

## Command Center Dashboard

A real-time dashboard for observability and human-in-the-loop control:

- **Layout**: Left sidebar (Agent Status), center (Strategy Synthesis + Reasoning Trace + Market Intelligence), right sidebar (Risk metrics + Strategy Approval).
- **Reasoning Trace**: Parallel streams for Technical and Fundamental analysts; tool calls (e.g. "Fetching AAPL P/E Ratio", "Calculating RSI") in real time via SSE.
- **HITL**: Strategy Approval gateway shows Risk Score and pauses for human validation on high-risk trades.
- **Charts**: Recharts for price/volume and fundamentals; Radix UI for accessible controls.

Run the dashboard:

```bash
cd dashboard && npm install && npm run dev
```

Run the SSE backend (optional; dashboard works with mock events otherwise):

```bash
uvicorn api.stream_server:app --reload --port 8000
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `dashboard/.env.local` to connect to the streaming API. See `docs/COMMAND_CENTER_WIREFRAME.md` for the wireframe and component structure.

## Project Layout

- `main.py` – Entry point; initializes Orchestrator and runs workflow.
- `config.py` – Env and constants.
- `schemas.py` – `ClassifierOutput`, `AnalystContext`, `SecuritiesTradingStrategy`.
- `agents/` – `orchestrator.py`, `registry.py`, `specialists.py`.
- `tools/` – `fundamental_tools.py`, `technical_tools.py`, `risk_tools.py` (real-world APIs).
- `dashboard/` – Next.js Command Center (ThoughtLog, Reasoning Trace, Strategy Synthesis, HITL, System Health).
- `api/stream_server.py` – FastAPI SSE server for streaming agent events.
- `docs/COMMAND_CENTER_WIREFRAME.md` – Wireframe and React component architecture.
