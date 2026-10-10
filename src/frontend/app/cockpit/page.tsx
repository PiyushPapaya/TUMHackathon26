"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useCockpit } from "@/src/components/cockpit/useCockpit";
import { CockpitHero } from "@/src/components/cockpit/CockpitHero";
import { RequirementsTable } from "@/src/components/cockpit/RequirementsTable";
import { WeightControls } from "@/src/components/cockpit/WeightControls";
import { DemoSteps } from "@/src/components/cockpit/DemoSteps";

function Cockpit() {
  const params = useSearchParams();
  const c = useCockpit(params.get("scenario"));

  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <CockpitHero scenario={c.selectedScenario} scenarioId={c.scenarioId} />

      {c.error && (
        <div role="alert" className="mb-6 border border-[var(--m-red)] bg-white px-4 py-3 text-sm text-[var(--m-red)]">
          {c.error}
        </div>
      )}

      <div className="grid gap-10 xl:grid-cols-[1fr_360px]">
        <section className="min-w-0">
          {c.loading && <p className="py-8 text-sm text-[var(--grey-500)]">Loading requirements...</p>}
          {!c.loading && c.requirements.length === 0 && (
            <p className="py-8 text-sm text-[var(--grey-500)]">No requirements for this scenario yet.</p>
          )}
          {!c.loading && c.requirements.length > 0 && (
            <RequirementsTable
              requirements={c.requirements}
              previousRanks={c.previousRanks}
              highlightRanks={c.highlightRanks}
              conflictTitles={c.conflictTitles}
            />
          )}
        </section>

        <aside className="grid h-fit gap-6 xl:sticky xl:top-24">
          <DemoSteps />
          <WeightControls
            weights={c.weights}
            onChange={c.setWeights}
            rationale={c.rationale}
            onRationale={c.setRationale}
            applying={c.applying}
            onApply={() => c.applyWeights()}
            onReset={c.resetWeights}
          />
        </aside>
      </div>

      {c.toast && (
        <div role="status" className="fixed bottom-24 right-6 z-50 border-l-4 border-[var(--blue)] bg-[var(--black)] px-5 py-3 text-sm text-white">
          {c.toast}
        </div>
      )}
    </main>
  );
}

export default function CockpitPage() {
  // useSearchParams braucht Suspense (Next 16).
  return (
    <Suspense fallback={<main className="px-6 py-12 text-sm text-[var(--grey-500)]">Loading...</main>}>
      <Cockpit />
    </Suspense>
  );
}
