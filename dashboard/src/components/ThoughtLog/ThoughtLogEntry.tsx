"use client";

import type { ThoughtEvent } from "@/types/streaming";
import { clsx } from "clsx";

const AGENT_COLORS: Record<string, string> = {
  orchestrator: "bg-slate-600",
  classifier: "bg-slate-500",
  technical_analyst: "bg-[var(--technical)] text-black",
  fundamental_analyst: "bg-[var(--fundamental)] text-black",
  risk_analyst: "bg-[var(--risk)] text-white",
};

const AGENT_LABELS: Record<string, string> = {
  orchestrator: "Orch",
  classifier: "NLU",
  technical_analyst: "Tech",
  fundamental_analyst: "Fund",
  risk_analyst: "Risk",
};

function getAgentId(e: ThoughtEvent): string | null {
  if ("agent" in e) return e.agent;
  return null;
}

function getMessage(e: ThoughtEvent): { title: string; detail?: string } {
  switch (e.type) {
    case "classification":
      return {
        title: `Intent: ${e.payload.analysis_type}`,
        detail: e.payload.security ? `Security: ${e.payload.security}` : undefined,
      };
    case "analyst_start":
      return { title: "Started", detail: e.instruction.slice(0, 60) + "..." };
    case "thought":
      return { title: e.step, detail: e.payload != null ? String(e.payload).slice(0, 120) : undefined };
    case "tool_call":
      return {
        title: toolCallToLabel(e.tool, e.args),
        detail: Object.keys(e.args).length ? JSON.stringify(e.args).slice(0, 80) : undefined,
      };
    case "tool_result":
      return { title: `${e.tool} result`, detail: e.result.slice(0, 120) + (e.result.length > 120 ? "…" : "") };
    case "analyst_end":
      return { title: "Done", detail: e.summary.slice(0, 80) + "..." };
    case "risk_score":
      return { title: `Risk score: ${e.score} (${e.label})` };
    case "strategy":
      return { title: `Strategy: ${e.payload.direction}`, detail: e.payload.rationale.slice(0, 80) + "..." };
    default:
      return { title: String((e as { type: string }).type) };
  }
}

function toolCallToLabel(tool: string, args: Record<string, unknown>): string {
  const sym = (args.symbol as string) || "";
  const labels: Record<string, string> = {
    get_earnings_summary: `Fetching ${sym || "..."} earnings`,
    get_income_statement_summary: `Fetching ${sym || "..."} income statement`,
    get_balance_sheet_summary: `Fetching ${sym || "..."} balance sheet`,
    get_macro_indicators: "Fetching macro indicators",
    get_price_history: `Fetching ${sym || "..."} price history`,
    get_volume_analysis: `Analyzing ${sym || "..."} volume`,
    get_moving_averages: `Calculating ${sym || "..."} moving averages`,
    get_price_summary: `Price summary ${sym || "..."}`,
    evaluate_volatility: `Evaluating ${sym || "..."} volatility`,
    evaluate_position_limit_compliance: "Checking position limits",
    evaluate_downside_risk: `Downside risk ${sym || "..."}`,
  };
  return labels[tool] || tool;
}

export function ThoughtLogEntry({ event, showToolResults = true }: { event: ThoughtEvent; showToolResults?: boolean }) {
  const agentId = getAgentId(event);
  const { title, detail } = getMessage(event);

  if (event.type === "tool_result" && !showToolResults) return null;

  const isToolCall = event.type === "tool_call" || event.type === "tool_result";
  const isStrategy = event.type === "strategy";
  const isRisk = event.type === "risk_score";

  return (
    <div
      className={clsx(
        "flex items-start gap-2 rounded border border-[var(--border)] px-2 py-1.5 text-xs",
        isStrategy && "border-[var(--accent)] bg-[var(--card)]",
        isRisk && "border-[var(--risk)]"
      )}
    >
      {agentId && (
        <span
          className={clsx(
            "shrink-0 rounded px-1.5 py-0.5 font-medium",
            AGENT_COLORS[agentId] ?? "bg-slate-600"
          )}
        >
          {AGENT_LABELS[agentId] ?? agentId}
        </span>
      )}
      <div className="min-w-0 flex-1">
        <div className="font-medium text-[var(--foreground)]">{title}</div>
        {detail && <div className="mt-0.5 truncate text-[var(--muted)]">{detail}</div>}
      </div>
    </div>
  );
}
