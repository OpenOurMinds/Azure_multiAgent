"use client";

import React from "react";
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip } from "recharts";

const MOCK_LATENCY = [
    { time: "10:00", ms: 42 },
    { time: "10:05", ms: 38 },
    { time: "10:10", ms: 55 },
    { time: "10:15", ms: 40 },
    { time: "10:20", ms: 45 },
    { time: "10:25", ms: 42 },
];

export interface OperationalMetricsProps {
    apiLatencyMs: number | null;
    className?: string;
}

export function OperationalMetrics({ apiLatencyMs, className }: OperationalMetricsProps) {
    return (
        <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 ${className ?? ""}`}>
            <h3 className="mb-3 text-sm font-semibold text-[var(--foreground)]">Operational Metrics</h3>

            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="rounded bg-[var(--background)] p-2 border border-[var(--border)]">
                    <p className="text-[10px] uppercase tracking-wider text-[var(--muted)] font-bold">Est. Cost</p>
                    <p className="text-lg font-mono text-[var(--fundamental)]">$0.12 <span className="text-[10px] font-normal text-[var(--muted)]">/ run</span></p>
                </div>
                <div className="rounded bg-[var(--background)] p-2 border border-[var(--border)]">
                    <p className="text-[10px] uppercase tracking-wider text-[var(--muted)] font-bold">Success Rate</p>
                    <p className="text-lg font-mono text-[var(--technical)]">98.4%</p>
                </div>
            </div>

            <div className="space-y-3">
                <div>
                    <div className="flex justify-between items-end mb-1">
                        <h4 className="text-xs font-medium text-[var(--muted)]">API Latency Trace</h4>
                        <span className="text-xs font-mono text-[var(--foreground)]">{apiLatencyMs ?? "—"}ms</span>
                    </div>
                    <div className="h-20 w-full opacity-60">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={MOCK_LATENCY}>
                                <defs>
                                    <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--technical)" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="var(--technical)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <YAxis hide domain={['dataMin - 10', 'dataMax + 10']} />
                                <Tooltip
                                    contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", fontSize: '10px' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="ms"
                                    stroke="var(--technical)"
                                    fillOpacity={1}
                                    fill="url(#latencyGradient)"
                                    strokeWidth={1.5}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div>
                    <h4 className="text-xs font-medium text-[var(--muted)] mb-1">Token Monitor (per agent)</h4>
                    <div className="space-y-1.5">
                        {[
                            { label: 'Orch', val: 1240, color: 'var(--accent)' },
                            { label: 'Analyst', val: 850, color: 'var(--fundamental)' },
                            { label: 'Risk', val: 420, color: 'var(--risk)' },
                        ].map(row => (
                            <div key={row.label} className="flex items-center gap-2">
                                <span className="text-[10px] w-12 text-[var(--muted)] uppercase">{row.label}</span>
                                <div className="flex-1 h-1.5 bg-[var(--background)] rounded-full overflow-hidden border border-[var(--border)]">
                                    <div
                                        className="h-full rounded-full transition-all duration-1000"
                                        style={{ width: `${(row.val / 1500) * 100}%`, backgroundColor: row.color }}
                                    />
                                </div>
                                <span className="text-[10px] font-mono w-10 text-right">{row.val}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
