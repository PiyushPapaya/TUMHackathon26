"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuditTrail } from "@/src/components/AuditTrail";
import { getAuditVerify, getScenarios, type AuditVerifyResult, type Scenario } from "@/src/lib/api";
import { ThemeToggle } from "@/src/components/ThemeToggle";

export function AuditPageClient() {
  const [verify, setVerify] = useState<AuditVerifyResult | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getAuditVerify(), getScenarios()])
      .then(([nextVerify, nextScenarios]) => {
        setVerify(nextVerify);
        setScenarios(nextScenarios);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Decision audit</p>
              <h1 className="mt-1 text-2xl font-semibold text-foreground">Audit trail</h1>
              <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
                Every AI, system, and PM action is listed with rationale and payload.
              </p>
            </div>
            <nav className="flex flex-wrap gap-2">
              <Link className="inline-flex min-h-11 items-center rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background" href="/">
                Requirements
              </Link>
              <ThemeToggle />
            </nav>
          </div>

          <div className="mt-5 flex flex-wrap items-end gap-3">
            <div
              className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-semibold ${
                verify?.valid
                  ? "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                  : "border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300"
              }`}
            >
              {verify
                ? verify.valid
                  ? `Chain valid ✓ · ${verify.checked} events checked`
                  : `Chain invalid · broken at #${verify.broken_at_seq ?? "unknown"}`
                : "Checking chain..."}
            </div>
            <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
              Scenario filter
              <select
                value={scenarioId}
                onChange={(event) => setScenarioId(event.target.value)}
                className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-3 font-normal text-foreground focus:border-accent focus:outline-none"
              >
                <option value="">All scenarios</option>
                {scenarios.map((scenario) => (
                  <option key={scenario.id} value={scenario.id}>
                    {scenario.model_name} {scenario.market}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </header>

        {error && (
          <div className="mb-4 rounded-sm border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
            {error}
          </div>
        )}

        <AuditTrail scenarioId={scenarioId || undefined} />
      </div>
    </main>
  );
}
