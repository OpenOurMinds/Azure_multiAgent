"use client";

export interface RiskMetricsPanelProps {
  riskScore: number | null;
  volatilityPct?: number | null;
  positionLimitPct?: number;
  className?: string;
}

export function RiskMetricsPanel({
  riskScore,
  volatilityPct = null,
  positionLimitPct = 10,
  className,
}: RiskMetricsPanelProps) {
  return (
    <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 ${className ?? ""}`}>
      <h3 className="mb-2 text-sm font-semibold text-[var(--foreground)]">Risk / Portfolio</h3>
      <div className="space-y-3 text-xs">
        <div>
          <div className="text-[var(--muted)]">Risk Score</div>
          <div className="text-lg font-semibold text-[var(--foreground)]">{riskScore ?? "—"}</div>
        </div>
        {volatilityPct != null && (
          <div>
            <div className="text-[var(--muted)]">Volatility (ann.)</div>
            <div className="text-[var(--foreground)]">{volatilityPct.toFixed(1)}%</div>
          </div>
        )}
        <div>
          <div className="text-[var(--muted)]">Position limit</div>
          <div className="text-[var(--foreground)]">{positionLimitPct}%</div>
        </div>
      </div>
    </div>
  );
}
