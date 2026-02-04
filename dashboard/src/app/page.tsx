"use client";

import { useMemo } from "react";
import { useThoughtStream } from "@/hooks/useThoughtStream";
import { SystemHealthMonitor } from "@/components/SystemHealthMonitor";
import { AgentStatusPanel } from "@/components/AgentStatusPanel";
import { StrategySynthesisView } from "@/components/StrategySynthesisView";
import { ReasoningTrace } from "@/components/ReasoningTrace";
import { MarketIntelligence } from "@/components/MarketIntelligence";
import { RiskMetricsPanel } from "@/components/RiskMetricsPanel";
import { HITLStrategyApproval } from "@/components/HITLStrategyApproval";
import type { SecuritiesTradingStrategy } from "@/types/streaming";

export default function CommandCenterPage() {
  const { events, isStreaming, error, health, runQuery, clearEvents } = useThoughtStream();

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
      <header className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2">
        <h1 className="text-lg font-semibold">Multi-Agent Trading Command Center</h1>
        <SystemHealthMonitor health={health} />
      </header>

      <main className="grid flex-1 grid-cols-[240px_1fr_260px] gap-4 p-4">
        <aside className="flex flex-col gap-3">
          <AgentStatusPanel
            agents={health.agents}
            registryHealthy={health.registryHealthy}
            isStreaming={isStreaming}
          />
        </aside>

        <div className="flex flex-col gap-4 overflow-hidden">
          <StrategySynthesisView strategy={strategy} />
          <ReasoningTrace events={events} maxHeight="280px" />
          <MarketIntelligence />
        </div>

        <aside className="flex flex-col gap-3">
          <RiskMetricsPanel riskScore={riskScore} positionLimitPct={10} />
          <HITLStrategyApproval
            pendingStrategy={riskScore != null && riskScore >= 60 ? strategy : null}
            riskScore={riskScore}
            onApprove={() => {}}
            onReject={() => {}}
            disabled={!strategy}
          />
        </aside>
      </main>

      <footer className="flex items-center gap-4 border-t border-[var(--border)] px-4 py-2">
        <input
          type="text"
          placeholder="Enter trading query..."
          className="flex-1 rounded border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-[var(--fundamental)]"
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
            const input = document.querySelector<HTMLInputElement>('input[placeholder="Enter trading query..."]');
            const q = input?.value?.trim();
            if (q) runQuery(q);
          }}
          disabled={isStreaming}
          className="rounded bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
        >
          {isStreaming ? "Running…" : "Run"}
        </button>
        <button
          type="button"
          onClick={clearEvents}
          className="rounded border border-[var(--border)] px-3 py-2 text-sm hover:bg-[var(--card)]"
        >
          Clear
        </button>
        <span className="text-xs text-[var(--muted)]">Last: {lastStrategySummary}</span>
      </footer>

      {error && (
        <div className="fixed bottom-4 left-4 rounded border border-[var(--risk)] bg-[var(--card)] px-3 py-2 text-sm text-[var(--risk)]">
          {error}
        </div>
      )}
    </div>
  );
}
