"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

// Demo data; in production would come from API/SSE
const DEMO_OHLC = [
  { date: "01", open: 178, high: 182, low: 177, close: 181, volume: 52_000_000 },
  { date: "02", open: 181, high: 183, low: 179, close: 180, volume: 48_000_000 },
  { date: "03", open: 180, high: 184, low: 179, close: 183, volume: 61_000_000 },
  { date: "04", open: 183, high: 185, low: 181, close: 182, volume: 44_000_000 },
  { date: "05", open: 182, high: 186, low: 181, close: 185, volume: 55_000_000 },
  { date: "06", open: 185, high: 187, low: 183, close: 184, volume: 50_000_000 },
  { date: "07", open: 184, high: 188, low: 183, close: 187, volume: 58_000_000 },
];

const DEMO_FUNDAMENTALS = [
  { metric: "P/E", value: 28, avg: 24 },
  { metric: "P/S", value: 7.2, avg: 6 },
  { metric: "ROE", value: 1.48, avg: 1.2 },
  { metric: "Debt/Equity", value: 1.8, avg: 2 },
  { metric: "Revenue growth", value: 8, avg: 6 },
];

export interface MarketIntelligenceProps {
  symbol?: string;
  ohlc?: { date: string; open: number; high: number; low: number; close: number; volume: number }[];
  fundamentals?: { metric: string; value: number; avg: number }[];
  className?: string;
}

export function MarketIntelligence({
  symbol = "AAPL",
  ohlc = DEMO_OHLC,
  fundamentals = DEMO_FUNDAMENTALS,
  className,
}: MarketIntelligenceProps) {
  return (
    <div className={`rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 ${className ?? ""}`}>
      <h3 className="mb-3 text-sm font-semibold text-[var(--foreground)]">Market Intelligence</h3>
      <div className="space-y-4">
        <div>
          <h4 className="mb-1 text-xs font-medium text-[var(--muted)]">Price & Volume — {symbol}</h4>
          <div className="h-40 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={ohlc}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="var(--muted)" />
                <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10 }} stroke="var(--muted)" />
                <Tooltip
                  contentStyle={{ background: "var(--card)", border: "1px solid var(--border)" }}
                  labelStyle={{ color: "var(--foreground)" }}
                />
                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="var(--fundamental)"
                  fill="var(--fundamental)"
                  fillOpacity={0.2}
                  strokeWidth={1.5}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-1 h-12 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ohlc}>
                <Bar dataKey="volume" fill="var(--border)" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <h4 className="mb-1 text-xs font-medium text-[var(--muted)]">Fundamentals vs avg</h4>
          <table className="dense-table w-full text-left">
            <thead>
              <tr className="border-b border-[var(--border)] text-[var(--muted)]">
                <th>Metric</th>
                <th>Value</th>
                <th>Avg</th>
              </tr>
            </thead>
            <tbody className="text-[var(--foreground)]">
              {fundamentals.map((r) => (
                <tr key={r.metric} className="border-b border-[var(--border)]">
                  <td>{r.metric}</td>
                  <td>{r.value}</td>
                  <td>{r.avg}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
