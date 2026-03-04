"use client";

import React, { useMemo } from "react";
import { clsx } from "clsx";
import type { AgentStatus } from "@/types/streaming";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  type: "input" | "agent" | "output";
}

interface Edge {
  from: string;
  to: string;
}

const NODES: Node[] = [
  { id: "query", label: "World Host Intake", x: 50, y: 100, type: "input" },
  { id: "lead_researcher", label: "Lead Researcher", x: 180, y: 100, type: "agent" },
  { id: "discovery_agent", label: "Discovery", x: 350, y: 50, type: "agent" },
  { id: "verification_agent", label: "Verification", x: 350, y: 150, type: "agent" },
  { id: "problem_genome", label: "Problem Genome", x: 520, y: 100, type: "agent" },
  { id: "compute_swarm", label: "Compute Swarm", x: 680, y: 100, type: "agent" },
  { id: "vault", label: "The Vault", x: 800, y: 100, type: "output" },
];

const EDGES: Edge[] = [
  { from: "query", to: "lead_researcher" },
  { from: "lead_researcher", to: "discovery_agent" },
  { from: "lead_researcher", to: "verification_agent" },
  { from: "discovery_agent", to: "problem_genome" },
  { from: "verification_agent", to: "problem_genome" },
  { from: "problem_genome", to: "compute_swarm" },
  { from: "compute_swarm", to: "vault" },
];

export interface WorkflowGraphProps {
  agents: AgentStatus[];
  isStreaming: boolean;
  className?: string;
}

export function WorkflowGraph({ agents, isStreaming, className }: WorkflowGraphProps) {
  const agentMap = useMemo(() => {
    const map = new Map<string, AgentStatus>();
    agents.forEach((a) => map.set(a.id, a));
    return map;
  }, [agents]);

  const getStatus = (nodeId: string) => {
    if (nodeId === "query") return isStreaming ? "running" : "idle";
    if (nodeId === "strategy") return agents.some(a => a.status === "running") ? "idle" : (isStreaming ? "idle" : "completed");
    return agentMap.get(nodeId)?.status ?? "idle";
  };

  return (
    <div className={clsx("relative h-48 w-full overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--card)] p-4", className)}>
      <h3 className="absolute left-3 top-3 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Workflow Graph</h3>
      <svg viewBox="0 0 800 200" className="h-full w-full">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="var(--border)" opacity="0.5" />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Edges */}
        {EDGES.map((edge, i) => {
          const fromNode = NODES.find((n) => n.id === edge.from)!;
          const toNode = NODES.find((n) => n.id === edge.to)!;
          const isActive = getStatus(edge.from) === "running" || getStatus(edge.to) === "running";

          return (
            <path
              key={`${edge.from}-${edge.to}-${i}`}
              d={`M ${fromNode.x + 40} ${fromNode.y} L ${toNode.x - 40} ${toNode.y}`}
              stroke={isActive ? "var(--fundamental)" : "var(--border)"}
              strokeWidth={isActive ? 2 : 1}
              fill="none"
              markerEnd="url(#arrowhead)"
              className={clsx("transition-all duration-500", isActive && "animate-pulse")}
              style={isActive ? { filter: "url(#glow)" } : {}}
            />
          );
        })}

        {/* Nodes */}
        {NODES.map((node) => {
          const status = getStatus(node.id);
          const isActive = status === "running";

          return (
            <g key={node.id} transform={`translate(${node.x},${node.y})`}>
              <rect
                x="-40"
                y="-15"
                width="80"
                height="30"
                rx="4"
                className={clsx(
                  "transition-all duration-300",
                  status === "running" ? "fill-[var(--fundamental)]/20 stroke-[var(--fundamental)] stroke-2" : "fill-[var(--background)] stroke-[var(--border)] stroke-1",
                  status === "completed" && "fill-[var(--technical)]/10 stroke-[var(--technical)]"
                )}
                style={isActive ? { filter: "url(#glow)" } : {}}
              />
              <text
                textAnchor="middle"
                dy=".3em"
                className={clsx(
                  "select-none text-[10px] font-medium",
                  status === "running" ? "fill-[var(--fundamental)]" : "fill-[var(--foreground)]"
                )}
              >
                {node.label}
              </text>
              {status === "running" && (
                <circle r="3" cx="45" cy="0" className="fill-[var(--fundamental)] animate-ping" />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
