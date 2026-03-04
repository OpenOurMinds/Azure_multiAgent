"use client";

import React, { useState, useRef, useEffect } from "react";
import { clsx } from "clsx";

export interface AgentTerminalProps {
    selectedAgentId: string | null;
    onClose: () => void;
}

export function AgentTerminal({ selectedAgentId, onClose }: AgentTerminalProps) {
    const [messages, setMessages] = useState<{ role: "user" | "agent"; content: string }[]>([]);
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = () => {
        if (!input.trim() || !selectedAgentId) return;

        const userMsg = input.trim();
        setMessages(prev => [...prev, { role: "user", content: userMsg }]);
        setInput("");

        // Simulate agent response
        setTimeout(() => {
            setMessages(prev => [...prev, { role: "agent", content: `Direct response from ${selectedAgentId}: I have received your instruction and am processing it within the multi-agent context.` }]);
        }, 800);
    };

    if (!selectedAgentId) return null;

    return (
        <div className="fixed inset-y-0 right-0 w-80 bg-[var(--card)] border-l border-[var(--border)] shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-300">
            <div className="flex items-center justify-between p-3 border-b border-[var(--border)] bg-[var(--background)]">
                <h3 className="text-sm font-semibold flex items-center gap-2 text-[var(--foreground)]">
                    <span className="h-2 w-2 rounded-full bg-[var(--fundamental)] animate-pulse" />
                    Terminal: {selectedAgentId}
                </h3>
                <button
                    onClick={onClose}
                    className="text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                >
                    ✕
                </button>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs"
            >
                <div className="text-[var(--muted)]">
                    &gt; Initializing direct bridge to {selectedAgentId}...
                    <br />
                    &gt; Bridge established. You can now send low-level instructions.
                </div>
                {messages.map((m, i) => (
                    <div
                        key={i}
                        className={clsx(
                            "p-2 rounded border",
                            m.role === "user" ? "bg-[var(--border)]/50 border-[var(--border)] ml-4" : "bg-[var(--background)] border-[var(--fundamental)]/30 mr-4"
                        )}
                    >
                        <span className={clsx("font-bold mb-1 block", m.role === "user" ? "text-[var(--muted)]" : "text-[var(--fundamental)]")}>
                            {m.role === "user" ? "USER" : selectedAgentId.toUpperCase()}
                        </span>
                        {m.content}
                    </div>
                ))}
            </div>

            <div className="p-3 border-t border-[var(--border)] bg-[var(--background)]">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === "Enter" && handleSend()}
                        placeholder="Direct instruction..."
                        className="flex-1 bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1.5 text-xs outline-none focus:ring-1 focus:ring-[var(--fundamental)]"
                    />
                    <button
                        onClick={handleSend}
                        className="bg-[var(--fundamental)] text-white px-3 py-1.5 rounded text-xs font-bold hover:opacity-90 transition-opacity"
                    >
                        SEND
                    </button>
                </div>
            </div>
        </div>
    );
}
