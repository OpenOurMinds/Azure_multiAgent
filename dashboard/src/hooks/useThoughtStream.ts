"use client";

import { useCallback, useEffect, useState } from "react";
import type { ThoughtEvent, SystemHealth } from "@/types/streaming";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useThoughtStream() {
  const [events, setEvents] = useState<ThoughtEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<SystemHealth>({
    apiLatencyMs: null,
    agents: [],
    registryHealthy: false,
  });

  const appendEvent = useCallback((event: ThoughtEvent) => {
    setEvents((prev) => [...prev, event]);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setError(null);
  }, []);

  const fetchHealth = useCallback(async () => {
    try {
      const start = performance.now();
      const res = await fetch(`${API_BASE}/health`);
      const data = await res.json().catch(() => ({}));
      setHealth({
        apiLatencyMs: Math.round(performance.now() - start),
        agents: data.agents ?? [],
        registryHealthy: data.registry_healthy ?? false,
      });
    } catch {
      setHealth((h) => ({ ...h, apiLatencyMs: null, registryHealthy: false }));
    }
  }, []);

  const runQuery = useCallback(
    async (query: string) => {
      clearEvents();
      setIsStreaming(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/stream?query=${encodeURIComponent(query)}`, {
          headers: { Accept: "text/event-stream" },
        });
        if (!res.ok || !res.body) throw new Error(res.statusText || "Stream failed");
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const raw = line.slice(6);
              if (raw === "[DONE]") continue;
              try {
                const event = JSON.parse(raw) as ThoughtEvent;
                appendEvent(event);
              } catch {
                // skip malformed
              }
            }
          }
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Stream error");
        // Append mock events for demo if backend not available
        appendEvent({
          type: "classification",
          payload: {
            analysis_type: "both",
            security: "AAPL",
            sector: null,
            time_horizon: null,
            raw_intent: query.slice(0, 80),
          },
        });
        appendEvent({
          type: "tool_call",
          agent: "technical_analyst",
          tool: "get_price_history",
          args: { symbol: "AAPL", period: "1mo" },
        });
        appendEvent({
          type: "tool_call",
          agent: "fundamental_analyst",
          tool: "get_earnings_summary",
          args: { symbol: "AAPL" },
        });
        appendEvent({
          type: "risk_score",
          score: 35,
          label: "Moderate",
        });
        appendEvent({
          type: "strategy",
          payload: {
            security: "AAPL",
            direction: "BUY",
            confidence: "MEDIUM",
            technical_summary: "Price above 20/50 SMA; volume supportive.",
            fundamental_summary: "Earnings growth positive; P/E in range.",
            risk_assessment: "Volatility within limit.",
            rationale: "Technical and fundamental alignment with acceptable risk.",
            conditions: ["Hold if price holds above 50 SMA."],
            warnings: ["Monitor Fed policy."],
          },
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [appendEvent, clearEvents]
  );

  useEffect(() => {
    fetchHealth();
    const t = setInterval(fetchHealth, 10000);
    return () => clearInterval(t);
  }, [fetchHealth]);

  return {
    events,
    isStreaming,
    error,
    health,
    appendEvent,
    clearEvents,
    runQuery,
    fetchHealth,
  };
}
