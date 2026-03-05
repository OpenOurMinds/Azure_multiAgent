"use client";

import React from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from "recharts";

const MOCK_GENOME_DATA = [
    { subject: 'Compute', A: 95, fullMark: 100 },
    { subject: 'Complexity', A: 98, fullMark: 100 },
    { subject: 'Fragility', A: 15, fullMark: 100 },
    { subject: 'Institutional', A: 85, fullMark: 100 },
    { subject: 'Verification', A: 90, fullMark: 100 },
];

export function ProblemGenomeView() {
    return (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 flex flex-col h-full overflow-hidden">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-[var(--foreground)] uppercase tracking-wider">Problem Genome</h3>
                <span className="text-[10px] font-bold bg-[var(--risk)]/20 text-[var(--risk)] px-2 py-0.5 rounded border border-[var(--risk)]/30">UNBEATABLE</span>
            </div>

            <div className="flex-1 w-full opacity-80">
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={MOCK_GENOME_DATA}>
                        <PolarGrid stroke="var(--border)" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--muted)', fontSize: 10 }} />
                        <Radar
                            name="Genome"
                            dataKey="A"
                            stroke="var(--fundamental)"
                            fill="var(--fundamental)"
                            fillOpacity={0.4}
                        />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 text-[10px]">
                <div className="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
                    <p className="text-[var(--muted)] font-bold mb-1">TIER</p>
                    <p className="font-mono text-[var(--foreground)]">FORMAL (MIL-01)</p>
                </div>
                <div className="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
                    <p className="text-[var(--muted)] font-bold mb-1">FRAGILITY</p>
                    <p className="font-mono text-[var(--foreground)]">15% RESISTANT</p>
                </div>
            </div>
        </div>
    );
}
