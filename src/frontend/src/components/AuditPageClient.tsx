"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AuditTrail } from "@/src/components/AuditTrail";
import { getAuditVerify, getScenarios, type AuditVerifyResult, type Scenario } from "@/src/lib/api";
import { ErrorNote, PageHeader } from "@/src/components/ui/PageHeader";

export function AuditPageClient() {
  const params = useSearchParams();
  const router = useRouter();
  const [verify, setVerify] = useState<AuditVerifyResult | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const scenarioId = params.get("scenario") ?? "";
  const requirementId = params.get("requirement") ?? "";
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
      <PageHeader eyebrow="Decision history" title="Audit trail">
        Every AI proposal and every product manager decision, in order, with its reason. Select an entry on the left to see the details on the right.
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
              ? `Integrity verified / ${verify.checked} events checked`
              : `Chain invalid · broken at #${verify.broken_at_seq ?? "unknown"}`
            : "Checking chain..."}
        </div>
        {ok && <p className="max-w-xs self-center text-xs text-[var(--grey-500)]">Each entry is chained to the previous one, so any later change to the history would be detected.</p>}
        <label className="grid gap-1 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">
          Scenario filter
          <select
            value={scenarioId}
            onChange={(event) => router.replace(event.target.value ? `/audit?scenario=${encodeURIComponent(event.target.value)}` : "/audit")}
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
      {requirementId && <div className="mb-4 flex flex-wrap items-center gap-4 text-sm"><span>Requirement: {requirementId}</span><button className="min-h-11 text-[var(--blue)]" onClick={() => router.replace(scenarioId ? `/audit?scenario=${encodeURIComponent(scenarioId)}` : "/audit")}>Show all requirements</button></div>}
      <AuditTrail scenarioId={scenarioId || undefined} requirementId={requirementId || undefined} />
    </main>
  );
}
