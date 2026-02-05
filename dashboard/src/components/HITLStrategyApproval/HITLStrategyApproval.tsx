"use client";

import type { SecuritiesTradingStrategy } from "@/types/streaming";
import * as Progress from "@radix-ui/react-progress";

const RISK_THRESHOLD = 60;

export interface HITLStrategyApprovalProps {
  pendingStrategy: SecuritiesTradingStrategy | null;
  riskScore: number | null;
  onApprove: () => void;
  onReject: () => void;
  disabled?: boolean;
  className?: string;
}

/**
 * Human-in-the-loop gateway: pause and request validation for high-risk trades,
 * displaying Risk Score from the Risk Management Agent.
 */
export function HITLStrategyApproval({
  pendingStrategy,
  riskScore,
  onApprove,
  onReject,
  disabled = false,
  className,
}: HITLStrategyApprovalProps) {
  const score = riskScore ?? 0;
  const requiresApproval = score >= RISK_THRESHOLD && pendingStrategy != null;

  return (
    <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 ${className ?? ""}`}>
      <h3 className="mb-2 text-sm font-semibold text-[var(--foreground)]">Strategy Approval</h3>
      <div className="mb-3">
        <div className="mb-1 flex justify-between text-xs">
          <span className="text-[var(--muted)]">Risk Score</span>
          <span className={score >= RISK_THRESHOLD ? "text-[var(--risk)]" : "text-[var(--technical)]"}>
            {score}
          </span>
        </div>
        <Progress.Root
          className="h-2 w-full overflow-hidden rounded-full bg-[var(--border)]"
          value={Math.min(score, 100)}
        >
          <Progress.Indicator
            className="h-full bg-[var(--risk)] transition-transform"
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </Progress.Root>
        <p className="mt-1 text-xs text-[var(--muted)]">
          {score >= RISK_THRESHOLD ? "Human approval required" : "Within policy"}
        </p>
      </div>
      {requiresApproval && (
        <div className="space-y-2">
          <p className="text-xs text-[var(--foreground)]">
            <strong>{pendingStrategy?.security}</strong> — {pendingStrategy?.direction} (confidence:{" "}
            {pendingStrategy?.confidence})
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onApprove}
              disabled={disabled}
              className="flex-1 rounded bg-[var(--technical)] px-2 py-1.5 text-xs font-medium text-black hover:opacity-90 disabled:opacity-50"
            >
              Approve
            </button>
            <button
              type="button"
              onClick={onReject}
              disabled={disabled}
              className="flex-1 rounded bg-[var(--risk)] px-2 py-1.5 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              Reject
            </button>
          </div>
        </div>
      )}
      {!requiresApproval && riskScore != null && (
        <p className="text-xs text-[var(--muted)]">No approval needed for this risk level.</p>
      )}
    </div>
  );
}
