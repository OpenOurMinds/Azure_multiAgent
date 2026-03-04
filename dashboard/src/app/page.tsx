"use client";

import { useState, useMemo } from "react";
import { useThoughtStream } from "@/hooks/useThoughtStream";
import { SystemHealthMonitor } from "@/components/SystemHealthMonitor";
import { AgentStatusPanel } from "@/components/AgentStatusPanel";
import { StrategySynthesisView } from "@/components/StrategySynthesisView";
import { ReasoningTrace } from "@/components/ReasoningTrace";
import { MarketIntelligence } from "@/components/MarketIntelligence";
import { RiskMetricsPanel } from "@/components/RiskMetricsPanel";
import { HITLStrategyApproval } from "@/components/HITLStrategyApproval";
import { WorkflowGraph } from "@/components/WorkflowGraph/WorkflowGraph";
import { OperationalMetrics } from "@/components/OperationalMetrics/OperationalMetrics";
import { AgentTerminal } from "@/components/AgentTerminal/AgentTerminal";
import { ProblemGenomeView } from "@/components/ProblemGenome/ProblemGenomeView";
import { SolutionVaultPanel } from "@/components/SolutionVault/SolutionVaultPanel";
import type { SecuritiesTradingStrategy } from "@/types/streaming";
import * as Tabs from "@radix-ui/react-tabs";

export default function CommandCenterPage() {
  const { events, isStreaming, error, health, runQuery, clearEvents } = useThoughtStream();
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const { strategy, riskScore } = useMemo(() => {
    let s: SecuritiesTradingStrategy | null = null;
    let r: number | null = null;
    for (let i = events.length - 1; i >= 0; i--) {
      const e = events[i];
      if (e.type === "strategy") s = e.payload;
      if (e.type === "risk_score") r = e.score;
      if (s != null && r != null) break;
    }
    return { strategy: s, riskScore: r };
  }, [events]);

  const lastStrategySummary = strategy
    ? `${strategy.security ?? "—"} ${strategy.direction} @ ${new Date().toLocaleTimeString()}`
    : "—";

  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)] text-[var(--foreground)]">
      <header className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2 bg-[var(--card)] shadow-sm">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 rounded bg-gradient-to-br from-[var(--fundamental)] to-[var(--technical)]" />
          <h1 className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-[var(--foreground)] to-[var(--muted)]">
            Multi-Agent Trading Command Center
          </h1>
        </div>
        <SystemHealthMonitor health={health} />
      </header>

      <main className="grid flex-1 grid-cols-[260px_1fr_280px] gap-4 p-4 overflow-hidden">
        <aside className="flex flex-col gap-4">
          <AgentStatusPanel
            agents={health.agents}
            registryHealthy={health.registryHealthy}
            isStreaming={isStreaming}
            onSelectAgent={setSelectedAgentId}
            selectedAgentId={selectedAgentId}
          />
          <OperationalMetrics apiLatencyMs={health.apiLatencyMs} />
        </aside>

        <div className="flex flex-col gap-4 overflow-hidden">
          <div className="grid grid-cols-3 gap-4 flex-none h-[280px]">
            <StrategySynthesisView strategy={strategy} />
            <ProblemGenomeView />
            <SolutionVaultPanel status="Pending" />
          </div>

          <div className="flex-1 flex flex-col gap-4 overflow-hidden">
            <Tabs.Root defaultValue="trace" className="flex-1 flex flex-col overflow-hidden">
              <Tabs.List className="flex gap-4 border-b border-[var(--border)] mb-2 px-1">
                <Tabs.Trigger value="trace" className="pb-2 text-xs font-semibold uppercase tracking-wider text-[var(--muted)] data-[state=active]:text-[var(--foreground)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--fundamental)] outline-none">
                  Reasoning Trace
                </Tabs.Trigger>
                <Tabs.Trigger value="workflow" className="pb-2 text-xs font-semibold uppercase tracking-wider text-[var(--muted)] data-[state=active]:text-[var(--foreground)] data-[state=active]:border-b-2 data-[state=active]:border-[var(--fundamental)] outline-none">
                  Workflow Graph
                </Tabs.Trigger>
              </Tabs.List>
              <div className="flex-1 overflow-hidden">
                <Tabs.Content value="trace" className="h-full">
                  <ReasoningTrace events={events} maxHeight="100%" />
                </Tabs.Content>
                <Tabs.Content value="workflow" className="h-full">
                  <WorkflowGraph agents={health.agents} isStreaming={isStreaming} className="h-full" />
                </Tabs.Content>
              </div>
            </Tabs.Root>

            <div className="flex-none h-[220px]">
              <MarketIntelligence />
            </div>
          </div>
        </div>

        <aside className="flex flex-col gap-4">
          <RiskMetricsPanel riskScore={riskScore} positionLimitPct={10} />
          <HITLStrategyApproval
            pendingStrategy={riskScore != null && riskScore >= 60 ? strategy : null}
            riskScore={riskScore}
            onApprove={() => { }}
            onReject={() => { }}
            disabled={!strategy}
          />
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 flex-1 overflow-hidden opacity-50 grayscale pointer-events-none">
            <h3 className="mb-2 text-sm font-semibold text-[var(--foreground)]">Success Criteria</h3>
            <div className="space-y-2">
              <div className="h-2 w-full bg-[var(--background)] rounded" />
              <div className="h-2 w-4/5 bg-[var(--background)] rounded" />
              <div className="h-2 w-3/4 bg-[var(--background)] rounded" />
            </div>
          </div>
        </aside>
      </main>

      <footer className="flex items-center gap-4 border-t border-[var(--border)] px-4 py-3 bg-[var(--card)] shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
        <input
          type="text"
          placeholder="Enter trading query (e.g., 'Should I buy MSFT based on fundamentals?')..."
          className="flex-1 rounded-full border border-[var(--border)] bg-[var(--background)] px-5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[var(--fundamental)]/30 transition-all font-medium"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const q = (e.target as HTMLInputElement).value.trim();
              if (q) runQuery(q);
            }
          }}
        />
        <button
          type="button"
          onClick={() => {
            const input = document.querySelector<HTMLInputElement>('input[placeholder*="Enter trading query"]');
            const q = input?.value?.trim();
            if (q) runQuery(q);
          }}
          disabled={isStreaming}
          className="rounded-full bg-gradient-to-r from-[var(--fundamental)] to-[var(--technical)] px-6 py-2.5 text-sm font-bold text-white hover:opacity-90 disabled:opacity-50 shadow-md transition-all active:scale-95"
        >
          {isStreaming ? "PROCESSING…" : "RUN ANALYSIS"}
        </button>
        <div className="h-8 w-px bg-[var(--border)] mx-1" />
        <button
          type="button"
          onClick={clearEvents}
          className="rounded-full border border-[var(--border)] px-5 py-2.5 text-xs font-semibold hover:bg-[var(--background)] transition-colors text-[var(--muted)]"
        >
          RESET
        </button>
        <span className="text-[10px] font-mono text-[var(--muted)] border border-[var(--border)] px-2 py-1 rounded bg-[var(--background)]">
          LAST: {lastStrategySummary}
        </span>
      </footer>

      <AgentTerminal selectedAgentId={selectedAgentId} onClose={() => setSelectedAgentId(null)} />

      {error && (
        <div className="fixed bottom-20 left-4 rounded border border-[var(--risk)] bg-[var(--card)] px-4 py-3 text-sm text-[var(--risk)] shadow-lg animate-bounce">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
