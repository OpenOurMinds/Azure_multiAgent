"use client";

import type { ThoughtEvent } from "@/types/streaming";
import type { AgentId } from "@/types/streaming";
import { ThoughtLogEntry } from "./ThoughtLogEntry";

export interface ThoughtLogProps {
  events: ThoughtEvent[];
  filter?: { agent?: AgentId };
  showToolResults?: boolean;
  maxHeight?: string;
  className?: string;
}

/**
 * Parses and displays a stream of agent reasoning steps (thoughts, tool calls, results)
 * before the final strategy conclusion. Used inside Reasoning Trace.
 */
export function ThoughtLog({
  events,
  filter,
  showToolResults = true,
  maxHeight = "320px",
  className,
}: ThoughtLogProps) {
  const filtered =
    filter?.agent != null
      ? events.filter((e) => "agent" in e && e.agent === filter.agent)
      : events;

  return (
    <div
      className={`scrollbar-thin flex flex-col gap-1.5 overflow-y-auto ${className ?? ""}`}
      style={{ maxHeight }}
    >
      {filtered.length === 0 ? (
        <div className="py-4 text-center text-sm text-[var(--muted)]">No reasoning steps yet.</div>
      ) : (
        filtered.map((event, i) => (
          <ThoughtLogEntry key={i} event={event} showToolResults={showToolResults} />
        ))
      )}
    </div>
  );
}
