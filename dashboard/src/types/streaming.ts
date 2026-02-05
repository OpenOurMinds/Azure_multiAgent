/**
 * Event shapes for multi-agent observability and Reasoning Trace.
 * Backend SSE should emit these event types.
 */

export type AgentId = "orchestrator" | "classifier" | "technical_analyst" | "fundamental_analyst" | "risk_analyst";

export interface ClassifierPayload {
  analysis_type: string;
  security: string | null;
  sector: string | null;
  time_horizon: string | null;
  raw_intent: string;
}

export interface SecuritiesTradingStrategy {
  security: string | null;
  direction: "BUY" | "SELL" | "HOLD";
  confidence: "LOW" | "MEDIUM" | "HIGH";
  technical_summary: string;
  fundamental_summary: string;
  risk_assessment: string;
  rationale: string;
  conditions: string[];
  warnings: string[];
}

export type ThoughtEvent =
  | { type: "classification"; payload: ClassifierPayload }
  | { type: "analyst_start"; agent: AgentId; instruction: string }
  | { type: "thought"; agent: AgentId; step: string; payload?: unknown }
  | { type: "tool_call"; agent: AgentId; tool: string; args: Record<string, unknown> }
  | { type: "tool_result"; agent: AgentId; tool: string; result: string }
  | { type: "analyst_end"; agent: AgentId; summary: string }
  | { type: "strategy"; payload: SecuritiesTradingStrategy }
  | { type: "risk_score"; score: number; label: string };

export interface AgentStatus {
  id: AgentId;
  status: "idle" | "running" | "error";
  lastActivityAt: string | null;
  latencyMs: number | null;
}

export interface SystemHealth {
  apiLatencyMs: number | null;
  agents: AgentStatus[];
  registryHealthy: boolean;
}
