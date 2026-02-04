"use client";

import type { AgentStatus } from "@/types/streaming";
import { clsx } from "clsx";

const AGENT_NAMES: Record<string, string> = {
  orchestrator: "Orchestrator",
  classifier: "Classifier",
  technical_analyst: "Technical",
  fundamental_analyst: "Fundamental",
  risk_analyst: "Risk",
};

export interface AgentStatusPanelProps {
  agents: AgentStatus[];
  registryHealthy: boolean;
  isStreaming?: boolean;
  className?: string;
}

export function AgentStatusPanel({
  agents,
  registryHealthy,
  isStreaming = false,
  className,
}: AgentStatusPanelProps) {
  const defaultAgents: AgentStatus[] = [
    { id: "orchestrator", status: "idle", lastActivityAt: null, latencyMs: null },
    { id: "classifier", status: "idle", lastActivityAt: null, latencyMs: null },
    { id: "technical_analyst", status: "idle", lastActivityAt: null, latencyMs: null },
    { id: "fundamental_analyst", status: "idle", lastActivityAt: null, latencyMs: null },
    { id: "risk_analyst", status: "idle", lastActivityAt: null, latencyMs: null },
  ];
  const list = agents.length ? agents : defaultAgents;

  return (
    <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 ${className ?? ""}`}>
      <h3 className="mb-2 text-sm font-semibold text-[var(--foreground)]">Agent Status</h3>
      <div className="mb-2 flex items-center gap-2">
        <span
          className={clsx(
            "h-2 w-2 rounded-full",
            registryHealthy ? "bg-[var(--technical)]" : "bg-[var(--risk)]"
          )}
        />
        <span className="text-xs text-[var(--muted)]">
          Registry {registryHealthy ? "healthy" : "unavailable"}
        </span>
      </div>
      <ul className="space-y-1.5">
        {list.map((a) => (
          <li
            key={a.id}
            className={clsx(
              "flex items-center justify-between rounded px-2 py-1.5 text-xs",
              isStreaming && a.status === "running" && "bg-[var(--border)]"
            )}
          >
            <span className="text-[var(--foreground)]">{AGENT_NAMES[a.id] ?? a.id}</span>
            <span className="flex items-center gap-1.5">
              {a.latencyMs != null && <span className="text-[var(--muted)]">{a.latencyMs}ms</span>}
              <span
                className={clsx(
                  "h-1.5 w-1.5 rounded-full",
                  a.status === "running" && "bg-[var(--fundamental)]",
                  a.status === "idle" && "bg-[var(--muted)]",
                  a.status === "error" && "bg-[var(--risk)]"
                )}
              />
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
