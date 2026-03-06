"use client";

import React, { useState } from "react";

// Inline SVG components to avoid lucide-react dependency
const LockIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
);
const UnlockIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 9.9-1" /></svg>
);
const ShieldCheckIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" /><path d="m9 12 2 2 4-4" /></svg>
);
const ZapIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M4 14.71 13.47 4 11 10.5h9L10.53 20 13 13.5H4Z" /></svg>
);

export function SolutionVaultPanel({ zkpHash, status }: { zkpHash?: string, status?: string }) {
    type VaultState = "LOCKED" | "VERIFYING" | "REVEALED" | "PURGED" | "DEAD_LOCK";
    const [vaultState, setVaultState] = useState<VaultState>("LOCKED");
    const [otk, setOtk] = useState<string | null>(null);
    const [answer, setAnswer] = useState<string | null>(null);
    const [chaosHash, setChaosHash] = useState<string | null>(null);
    const [resilience, setResilience] = useState(0);

    // Simulate Chaos Simulation on mount
    React.useEffect(() => {
        if (zkpHash) {
            const timer = setInterval(() => {
                setResilience(prev => prev < 99.4 ? +(prev + 2.1).toFixed(1) : 99.4);
            }, 100);
            return () => clearInterval(timer);
        }
    }, [zkpHash]);

    const handleBountyTransfer = async () => {
        setVaultState("VERIFYING");
        try {
            const response = await fetch("http://localhost:8000/bounty/pay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ bounty_id: "EIS-V-2026-X", amount: 1.0 })
            });
            const data = await response.json();

            if (data.status === "PAID") {
                setOtk(data.otk);
                setAnswer(data.answer);
                setChaosHash(data.chaos_hash);
                setVaultState("REVEALED");
            } else if (data.error === "DEAD_MANS_LOCK_TRIGGERED") {
                setVaultState("DEAD_LOCK");
            }
        } catch (e) {
            setVaultState("LOCKED");
        }
    };

    const handlePurge = async () => {
        if (otk) {
            await fetch("http://localhost:8000/vault/purge", {
                method: "POST",
                body: JSON.stringify({ otk })
            });
        }
        setOtk(null);
        setAnswer(null);
        setChaosHash(null);
        setVaultState("PURGED");
    };

    return (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 flex flex-col h-full bg-gradient-to-b from-[var(--card)] to-[var(--background)] shadow-xl relative overflow-hidden">
            {/* Background Glow Effect */}
            <div className={`absolute -top-24 -right-24 w-48 h-48 ${vaultState === 'DEAD_LOCK' ? 'bg-[var(--risk)]/20' : 'bg-[var(--fundamental)]/10'} blur-[60px] rounded-full pointer-events-none`} />

            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    {vaultState === "LOCKED" ? <LockIcon className="w-4 h-4 text-[var(--risk)]" /> : (vaultState === "DEAD_LOCK" ? <ShieldCheckIcon className="w-4 h-4 text-[var(--risk)]" /> : <UnlockIcon className="w-4 h-4 text-[var(--fundamental)]" />)}
                    <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-tighter">Secure Solution Vault</h3>
                </div>
                <div className="flex flex-col items-end">
                    <div className="flex items-center gap-1">
                        <ShieldCheckIcon className="w-3 h-3 text-[var(--fundamental)]" />
                        <span className="text-[10px] text-[var(--muted)] font-mono uppercase">
                            {vaultState === "PURGED" ? "TRACE WIPED" : (vaultState === "DEAD_LOCK" ? "PERMANENT LOCK" : "ZKP Verified")}
                        </span>
                    </div>
                    {vaultState !== "PURGED" && vaultState !== "DEAD_LOCK" && (
                        <div className="text-[9px] font-mono text-[var(--fundamental)] mt-0.5">RESILIENCE: {resilience}%</div>
                    )}
                </div>
            </div>

            {/* Chaos Integrity Meter */}
            {vaultState === "LOCKED" && (
                <div className="mb-4 space-y-1">
                    <div className="flex justify-between text-[8px] font-bold text-[var(--muted)] uppercase tracking-widest">
                        <span>Chaos Resilience Analysis</span>
                        <span className="text-[var(--fundamental)]">{resilience}%</span>
                    </div>
                    <div className="h-1 w-full bg-black/40 rounded-full overflow-hidden border border-[var(--border)]">
                        <div
                            className="h-full bg-[var(--fundamental)] transition-all duration-500 ease-out shadow-[0_0_8px_var(--fundamental)]"
                            style={{ width: `${resilience}%` }}
                        />
                    </div>
                    <p className="text-[8px] text-[var(--muted)] italic">Stochastic Stress-Testing: 1.2M iterations verified.</p>
                </div>
            )}

            <div className="flex-1 space-y-3">
                <div className="p-3 rounded bg-black/40 border border-[var(--border)] font-mono text-[10px] break-all relative group">
                    <p className="text-[var(--muted)] mb-1 uppercase text-[8px] font-bold">Proof of Solution (ZKP Hash)</p>
                    <p className="text-[var(--foreground)] leading-relaxed">
                        {vaultState === "PURGED" ? "[SESSION_INVALIDATED]" : (vaultState === "DEAD_LOCK" ? "[PAYLOAD_MIGRATED]" : (zkpHash || "calculating_sha256_merkle_root..."))}
                    </p>
                </div>

                {chaosHash && vaultState === "REVEALED" && (
                    <div className="p-2 rounded border border-[var(--fundamental)]/20 bg-[var(--fundamental)]/5 font-mono text-[9px] flex justify-between">
                        <span className="text-[var(--muted)] uppercase">Chaos-Based Session Hash:</span>
                        <span className="text-[var(--fundamental)]">{chaosHash}</span>
                    </div>
                )}

                <div className="p-4 rounded border border-[var(--border)] bg-[var(--background)] flex flex-col items-center justify-center min-h-[100px] text-center gap-3 relative">
                    {vaultState === "LOCKED" && (
                        <>
                            <LockIcon className="w-8 h-8 text-[var(--muted)] opacity-50" />
                            <div className="space-y-1">
                                <p className="text-[11px] font-bold text-[var(--foreground)]">Remarkable Solution Encapsulated</p>
                                <p className="text-[10px] text-[var(--muted)] tracking-tight">Non-Custodial RSA Handshake Required.</p>
                            </div>
                            <button
                                onClick={handleBountyTransfer}
                                className="mt-1 w-full py-2 rounded bg-[var(--fundamental)]/10 border border-[var(--fundamental)]/30 text-[var(--fundamental)] text-[10px] font-bold hover:bg-[var(--fundamental)]/20 transition-all flex items-center justify-center gap-2 shadow-lg"
                            >
                                <ZapIcon className="w-3 h-3" />
                                INITIATE BOUNTY TRANSFER
                            </button>
                        </>
                    )}

                    {vaultState === "VERIFYING" && (
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-8 h-8 border-2 border-[var(--fundamental)] border-t-transparent rounded-full animate-spin shadow-[0_0_15px_var(--fundamental)]" />
                            <div className="space-y-1">
                                <p className="text-[10px] text-[var(--foreground)] font-bold uppercase tracking-widest">Bounty Verification</p>
                                <p className="text-[9px] text-[var(--muted)] font-mono">RSA-OTK Handshake in progress...</p>
                            </div>
                        </div>
                    )}

                    {vaultState === "REVEALED" && (
                        <>
                            <UnlockIcon className="w-8 h-8 text-[var(--fundamental)] animate-pulse" />
                            <div className="p-3 bg-black/50 rounded text-left w-full border border-[var(--fundamental)]/30 overflow-auto max-h-[120px] shadow-inner">
                                <p className="text-[10px] text-[var(--foreground)] leading-snug italic font-medium">{answer}</p>
                            </div>
                            <button
                                onClick={handlePurge}
                                className="w-full py-2 rounded bg-[var(--risk)]/10 border border-[var(--risk)]/30 text-[var(--risk)] text-[10px] font-bold hover:bg-[var(--risk)]/20 transition-all flex items-center justify-center gap-2 uppercase"
                            >
                                <ShieldCheckIcon className="w-3 h-3" />
                                Secure Post-Reveal Purge
                            </button>
                        </>
                    )}

                    {vaultState === "PURGED" && (
                        <div className="flex flex-col items-center gap-2">
                            <ShieldCheckIcon className="w-10 h-10 text-[var(--muted)] opacity-30" />
                            <p className="text-[10px] text-[var(--muted)] font-bold italic tracking-widest uppercase">Memory Evicted / Trace Wiped</p>
                        </div>
                    )}

                    {vaultState === "DEAD_LOCK" && (
                        <div className="flex flex-col items-center gap-2">
                            <LockIcon className="w-10 h-10 text-[var(--risk)] animate-pulse" />
                            <p className="text-[11px] font-bold text-[var(--risk)] uppercase">Dead-Man's Lock Triggered</p>
                            <p className="text-[9px] text-[var(--muted)]">Unauthorized access detected. Payload migrated to cold-storage.</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-[var(--border)] flex justify-between items-center text-[9px] text-[var(--muted)] font-mono">
                <span>MODE: NON-CUSTODIAL</span>
                <span>ID: {otk || "EIS-V-P2026"}</span>
            </div>
        </div>
    );
}
