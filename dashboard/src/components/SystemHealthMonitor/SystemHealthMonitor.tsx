"use client";

import type { SystemHealth } from "@/types/streaming";
import { clsx } from "clsx";

export interface SystemHealthMonitorProps {
  health: SystemHealth;
  className?: string;
}

export function SystemHealthMonitor({ health, className }: SystemHealthMonitorProps) {
  const ok = health.registryHealthy && health.apiLatencyMs != null && health.apiLatencyMs < 5000;

  return (
    <div className={clsx("flex items-center gap-3 text-xs", className)}>
      <div className="flex items-center gap-1.5">
        <span className={clsx("h-2 w-2 rounded-full", ok ? "bg-[var(--technical)]" : "bg-[var(--risk)]")} />
        <span className="text-[var(--muted)]">System</span>
      </div>
      <div className="text-[var(--muted)]">
        API: {health.apiLatencyMs != null ? `${health.apiLatencyMs}ms` : "—"}
      </div>
      <div className="text-[var(--muted)]">
        Registry: {health.registryHealthy ? "OK" : "—"}
      </div>
    </div>
  );
}
