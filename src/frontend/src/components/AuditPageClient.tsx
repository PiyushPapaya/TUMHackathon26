"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuditTrail } from "@/src/components/AuditTrail";
import { getAuditVerify, getScenarios, type AuditVerifyResult, type Scenario } from "@/src/lib/api";

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
        <header className="mb-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Decision audit</p>
              <h1 className="mt-1 text-2xl font-semibold text-[#0b1f3a]">Audit trail</h1>
              <p className="mt-1 max-w-2xl text-sm text-slate-600">
                Every AI, system, and PM action is listed with rationale and payload.
              </p>
            </div>
            <nav className="flex flex-wrap gap-2">
              <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/overview">
                Overview
              </Link>
              <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/">
                Requirements
              </Link>
            </nav>
          </div>

          <div className="mt-5 flex flex-wrap items-end gap-3">
            <div
              className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-semibold ${
                verify?.valid
                  ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                  : "border-rose-300 bg-rose-50 text-rose-800"
              }`}
            >
              {verify
                ? verify.valid
                  ? `Chain valid ✓ · ${verify.checked} events checked`
                  : `Chain invalid · broken at #${verify.broken_at_seq ?? "unknown"}`
                : "Checking chain..."}
            </div>
            <label className="grid gap-1 text-sm font-semibold text-slate-700">
              Scenario filter
              <select
                value={scenarioId}
                onChange={(event) => setScenarioId(event.target.value)}
                className="min-h-11 rounded-md border border-slate-300 bg-white px-3 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
          <div className="mb-4 rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error}
          </div>
        )}

        <AuditTrail scenarioId={scenarioId || undefined} />
      </div>
    </main>
  );
}
