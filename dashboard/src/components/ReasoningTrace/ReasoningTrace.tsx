"use client";

import type { ThoughtEvent } from "@/types/streaming";
import { ThoughtLog } from "../ThoughtLog";
import * as Tabs from "@radix-ui/react-tabs";

export interface ReasoningTraceProps {
  events: ThoughtEvent[];
  showToolResults?: boolean;
  maxHeight?: string;
}

/**
 * Multi-Agent Activity Feed: parallel streams for Technical and Fundamental analysts,
 * plus unified log. Displays tool calls (e.g. "Fetching AAPL P/E Ratio", "Calculating RSI") in real time.
 */
export function ReasoningTrace({
  events,
  showToolResults = true,
  maxHeight = "320px",
}: ReasoningTraceProps) {
  const hasTechnical = events.some((e) => "agent" in e && e.agent === "technical_analyst");
  const hasFundamental = events.some((e) => "agent" in e && e.agent === "fundamental_analyst");

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
      <h3 className="mb-2 text-sm font-semibold text-[var(--foreground)]">Reasoning Trace</h3>
      <Tabs.Root defaultValue="all" className="w-full">
        <Tabs.List className="mb-2 flex gap-1 border-b border-[var(--border)] pb-2">
          <Tabs.Trigger
            className="rounded px-2 py-1 text-xs font-medium data-[state=active]:bg-[var(--border)] data-[state=active]:text-[var(--foreground)]"
            value="all"
          >
            All
          </Tabs.Trigger>
          {hasTechnical && (
            <Tabs.Trigger
              className="rounded px-2 py-1 text-xs font-medium text-[var(--technical)] data-[state=active]:bg-[var(--technical)]/20 data-[state=active]:text-[var(--technical)]"
              value="technical"
            >
              Technical
            </Tabs.Trigger>
          )}
          {hasFundamental && (
            <Tabs.Trigger
              className="rounded px-2 py-1 text-xs font-medium text-[var(--fundamental)] data-[state=active]:bg-[var(--fundamental)]/20 data-[state=active]:text-[var(--fundamental)]"
              value="fundamental"
            >
              Fundamental
            </Tabs.Trigger>
          )}
        </Tabs.List>
        <Tabs.Content value="all">
          <ThoughtLog events={events} showToolResults={showToolResults} maxHeight={maxHeight} />
        </Tabs.Content>
        {hasTechnical && (
          <Tabs.Content value="technical">
            <ThoughtLog
              events={events}
              filter={{ agent: "technical_analyst" }}
              showToolResults={showToolResults}
              maxHeight={maxHeight}
            />
          </Tabs.Content>
        )}
        {hasFundamental && (
          <Tabs.Content value="fundamental">
            <ThoughtLog
              events={events}
              filter={{ agent: "fundamental_analyst" }}
              showToolResults={showToolResults}
              maxHeight={maxHeight}
            />
          </Tabs.Content>
        )}
      </Tabs.Root>
    </div>
  );
}
