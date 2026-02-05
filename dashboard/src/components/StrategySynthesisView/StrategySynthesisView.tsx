"use client";

import type { SecuritiesTradingStrategy } from "@/types/streaming";
import { clsx } from "clsx";

export interface StrategySynthesisViewProps {
  strategy: SecuritiesTradingStrategy | null;
  contributingHighlights?: { technical?: string[]; fundamental?: string[] };
  className?: string;
}

/**
 * Central workspace: Orchestrator's final strategy with data points from each
 * sub-agent that contributed to the Buy/Hold/Sell recommendation.
 */
export function StrategySynthesisView({
  strategy,
  contributingHighlights,
  className,
}: StrategySynthesisViewProps) {
  if (!strategy) {
    return (
      <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 ${className ?? ""}`}>
        <p className="text-sm text-[var(--muted)]">Run a query to see the synthesized strategy.</p>
      </div>
    );
  }

  const directionColor =
    strategy.direction === "BUY"
      ? "text-[var(--technical)]"
      : strategy.direction === "SELL"
        ? "text-[var(--risk)]"
        : "text-[var(--muted)]";

  return (
    <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 ${className ?? ""}`}>
      <h3 className="mb-3 text-sm font-semibold text-[var(--foreground)]">Strategy Synthesis</h3>

      <div className="mb-4 flex items-center gap-4">
        <span className="text-lg font-bold text-[var(--foreground)]">{strategy.security ?? "—"}</span>
        <span className={clsx("text-xl font-bold", directionColor)}>{strategy.direction}</span>
        <span className="rounded bg-[var(--border)] px-2 py-0.5 text-xs font-medium">
          Confidence: {strategy.confidence}
        </span>
      </div>

      <div className="grid gap-3 text-sm">
        <section>
          <h4 className="mb-1 text-xs font-medium text-[var(--technical)]">Technical (contributing)</h4>
          <p className="text-[var(--foreground)]">{strategy.technical_summary}</p>
          {contributingHighlights?.technical?.length ? (
            <ul className="mt-1 list-inside list-disc text-[var(--muted)]">
              {contributingHighlights.technical.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          ) : null}
        </section>
        <section>
          <h4 className="mb-1 text-xs font-medium text-[var(--fundamental)]">Fundamental (contributing)</h4>
          <p className="text-[var(--foreground)]">{strategy.fundamental_summary}</p>
          {contributingHighlights?.fundamental?.length ? (
            <ul className="mt-1 list-inside list-disc text-[var(--muted)]">
              {contributingHighlights.fundamental.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          ) : null}
        </section>
        <section>
          <h4 className="mb-1 text-xs font-medium text-[var(--risk)]">Risk</h4>
          <p className="text-[var(--foreground)]">{strategy.risk_assessment}</p>
        </section>
        <section>
          <h4 className="mb-1 text-xs font-medium text-[var(--muted)]">Rationale</h4>
          <p className="text-[var(--foreground)]">{strategy.rationale}</p>
        </section>
        {strategy.conditions.length > 0 && (
          <section>
            <h4 className="mb-1 text-xs font-medium text-[var(--muted)]">Conditions</h4>
            <ul className="list-inside list-disc text-[var(--foreground)]">
              {strategy.conditions.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </section>
        )}
        {strategy.warnings.length > 0 && (
          <section>
            <h4 className="mb-1 text-xs font-medium text-[var(--risk)]">Warnings</h4>
            <ul className="list-inside list-disc text-[var(--risk)]">
              {strategy.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
