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
  const [showIntake, setShowIntake] = useState(false);
  const [objective, setObjective] = useState("");
  const [constraints, setConstraints] = useState("Mathematical complexity, Energy boundaries");
  const [heuristics, setHeuristics] = useState("rigor: 0.98, efficiency: 500");

  const { strategy, riskScore } = useMemo(() => {
    let s: SecuritiesTradingStrategy | null = null;
    let r: number | null = null;
    for (let i = events.length - 1; i >= 0; i--) {
      const e = events[i];
      if (e.type === "strategy") s = e.payload;
      if (e.type === "risk_score") r = e.payload;
      if (s != null && r != null) break;
    }
    return { strategy: s, riskScore: r };
  }, [events]);

  const handleStartMission = () => {
    const payload = {
      objective,
      constraints: constraints.split(",").map(c => c.trim()),
      heuristics: { rigor: 0.98, efficiency: 500 },
      host_auth: "0xHOST_PRIVATE_KEY_SIG_V2026",
      amount: 2500000
    };
    runQuery(JSON.stringify(payload));
    setShowIntake(false);
  };

  const lastStrategySummary = strategy
    ? `${strategy.security ?? "—"} ${strategy.direction} @ ${new Date().toLocaleTimeString()}`
    : "—";

  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)] text-[var(--foreground)] selection:bg-[var(--fundamental)]/30">
      <header className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2 bg-[var(--card)] shadow-md relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-[var(--fundamental)] animate-pulse" />
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 rounded bg-gradient-to-br from-[var(--fundamental)] to-[var(--technical)] shadow-[0_0_10px_var(--fundamental)]" />
          <div className="flex flex-col">
            <h1 className="text-sm font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-[var(--foreground)] to-[var(--muted)] uppercase">
              Earth Intelligence System <span className="text-[var(--fundamental)]">v2.0</span>
            </h1>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--fundamental)] animate-ping" />
              <span className="text-[9px] font-mono text-[var(--fundamental)] uppercase tracking-widest">Fortress State Active</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <SystemHealthMonitor health={health} />
          <button
            onClick={() => setShowIntake(true)}
            className="px-3 py-1 rounded border border-[var(--fundamental)]/30 bg-[var(--fundamental)]/10 text-[var(--fundamental)] text-[10px] font-black uppercase tracking-widest hover:bg-[var(--fundamental)]/20 transition-all shadow-[0_0_10px_rgba(var(--fundamental-rgb),0.2)]"
          >
            New Mission
          </button>
        </div>
      </header>

      <main className="grid flex-1 grid-cols-[260px_1fr_280px] gap-4 p-4 overflow-hidden relative">
        {showIntake && (
          <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-[var(--card)] border border-[var(--fundamental)]/30 rounded-lg shadow-2xl p-6 space-y-4">
              <h2 className="text-lg font-black tracking-tighter uppercase italic">Host Mission Briefing</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] font-bold text-[var(--muted)] uppercase mb-1 block">Objective</label>
                  <textarea
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    className="w-full bg-[var(--background)] border border-[var(--border)] rounded p-2 text-sm h-20 outline-none focus:border-[var(--fundamental)]"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-[var(--muted)] uppercase mb-1 block">Constraints</label>
                  <input
                    value={constraints}
                    onChange={(e) => setConstraints(e.target.value)}
                    className="w-full bg-[var(--background)] border border-[var(--border)] rounded p-2 text-sm outline-none focus:border-[var(--fundamental)]"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button onClick={() => setShowIntake(false)} className="flex-1 py-2 rounded border border-[var(--border)] text-[var(--muted)] text-[11px] font-bold uppercase">ABORT</button>
                <button onClick={handleStartMission} className="flex-1 py-2 rounded bg-gradient-to-r from-[var(--fundamental)] to-[var(--technical)] text-white text-[11px] font-black uppercase tracking-widest shadow-lg">DEEP THINKING</button>
              </div>
            </div>
          </div>
        )}

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
                <Tabs.Trigger value="trace" className="pb-2 text-[10px] font-bold uppercase tracking-widest text-[var(--muted)] data-[state=active]:text-[var(--foreground)]">Reasoning Trace</Tabs.Trigger>
                <Tabs.Trigger value="workflow" className="pb-2 text-[10px] font-bold uppercase tracking-widest text-[var(--muted)] data-[state=active]:text-[var(--foreground)]">Workflow Graph</Tabs.Trigger>
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
            <div className="flex-none h-[220px]"><MarketIntelligence /></div>
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
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 flex-1 overflow-hidden">
            <h3 className="text-[10px] font-black text-[var(--foreground)] uppercase tracking-widest mb-3">Mission Success Criteria</h3>
            <div className="space-y-2 text-[10px] text-[var(--muted)]">
              <p>99.9% Robustness Verification</p>
              <p>RSA-OTK Handshake Verified</p>
              <p>Zero-Trust Vault Active</p>
            </div>
          </div>
        </aside>
      </main>

      <footer className="flex items-center gap-4 border-t border-[var(--border)] px-4 py-3 bg-[var(--card)] shadow-[0_-2px_10px_rgba(0,0,0,0.05)] relative z-10">
        <input
          type="text"
          placeholder="QUICK_INTAKE (Objective only)..."
          className="flex-1 rounded bg-[var(--background)] border border-[var(--border)] px-4 py-2 text-sm outline-none focus:border-[var(--fundamental)] font-mono"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const q = (e.target as HTMLInputElement).value.trim();
              if (q) runQuery(JSON.stringify({ objective: q, constraints: [], heuristics: {}, host_auth: "sim", amount: 0 }));
            }
          }}
        />
        <button onClick={() => setShowIntake(true)} className="px-4 py-2 border rounded text-xs font-bold uppercase tracking-widest text-[var(--muted)] hover:bg-[var(--background)] transition-colors">Full Briefing</button>
        <button onClick={clearEvents} className="border rounded px-4 py-2 text-xs font-bold text-[var(--muted)] uppercase">Reset</button>
        <span className="text-[10px] font-mono text-[var(--muted)] border border-[var(--border)] px-2 py-1 rounded bg-[var(--background)]">LAST: {lastStrategySummary}</span>
      </footer>

      <AgentTerminal selectedAgentId={selectedAgentId} onClose={() => setSelectedAgentId(null)} />
    </div>
  );
}
