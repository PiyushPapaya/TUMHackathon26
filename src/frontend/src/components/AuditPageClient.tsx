"use client";

import { useEffect, useState } from "react";
import { AuditTrail } from "@/src/components/AuditTrail";
import { getAuditVerify, getScenarios, type AuditVerifyResult, type Scenario } from "@/src/lib/api";
import { ErrorNote, PageHeader } from "@/src/components/ui/PageHeader";

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

  const ok = verify?.valid;

  return (
    <main className="mx-auto max-w-[1100px] px-6 py-12 lg:px-10">
      <PageHeader eyebrow="Decision audit" title="Every step on record.">
        Every AI, system, and PM action is listed with rationale and payload. Each entry is chained to the previous one, so changes would be detected.
      </PageHeader>

      <div className="mb-8 flex flex-wrap items-end gap-4">
        <div
          role="status"
          className={`inline-flex h-11 items-center border px-4 text-sm font-semibold ${
            verify ? (ok ? "border-emerald-700 text-emerald-800" : "border-[var(--m-red)] text-[var(--m-red)]") : "border-[var(--hairline)] text-[var(--grey-500)]"
          }`}
        >
          {verify
            ? ok
              ? `Chain valid ✓ · ${verify.checked} events checked`
              : `Chain invalid · broken at #${verify.broken_at_seq ?? "unknown"}`
            : "Checking chain..."}
        </div>
        <label className="grid gap-1 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">
          Scenario filter
          <select
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
            className="h-11 border border-[var(--hairline)] bg-white px-3 text-sm font-normal normal-case tracking-normal text-[var(--ink)]"
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

      {error && <ErrorNote message={error} />}
      <AuditTrail scenarioId={scenarioId || undefined} />
    </main>
  );
}
