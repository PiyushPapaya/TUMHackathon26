"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useCockpit } from "@/src/components/cockpit/useCockpit";
import { CockpitHero } from "@/src/components/cockpit/CockpitHero";
import { RequirementFilters } from "@/src/components/cockpit/RequirementFilters";
import { ProductContext } from "@/src/components/ProductContext";
import { WeightControls } from "@/src/components/cockpit/WeightControls";
import { LensPanel } from "@/src/components/cockpit/LensPanel";
import { HowToRead } from "@/src/components/cockpit/HowToRead";

// Eine Spalte, drei Schritte von oben nach unten: fragen → Liste springt → Zeile öffnen.
// Warum keine Seitenleiste mehr: Im 2-Minuten-Demo soll das Auge nicht zwischen Kästen springen.
function Cockpit() {
  const params = useSearchParams();
  const c = useCockpit(params.get("scenario"));

  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <CockpitHero scenario={c.selectedScenario} scenarioId={c.scenarioId} />
      <HowToRead />
      <div className="mb-6"><ProductContext scenarioId={c.scenarioId} compact /></div>

      {c.error && (
        <div role="alert" className="mb-6 border border-[var(--m-red)] bg-white px-4 py-3 text-sm text-[var(--m-red)]">
          {c.error}
        </div>
      )}

      <details className="mb-3 border-b border-[var(--hairline)]">
        <summary className="flex min-h-12 items-center text-sm font-semibold text-[var(--ink)]">Ask a prioritization question</summary>
        <LensPanel
        key={c.scenarioId}
        scenarioId={c.scenarioId}
        applying={c.applying}
        onApply={(weights, question) => c.applyWeights({ ...c.weights, ...weights }, question)}
      />
      </details>

      <WeightControls
        weights={c.weights}
        onChange={c.setWeights}
        applying={c.applying}
        onApply={() => c.applyWeights()}
        onReset={c.resetWeights}
      />

      <section className="mt-6 min-w-0">
        {c.loading && <p className="py-8 text-sm text-[var(--grey-500)]">Loading requirements...</p>}
        {!c.loading && c.requirements.length === 0 && (
          <p className="py-8 text-sm text-[var(--grey-500)]">No requirements for this scenario yet.</p>
        )}
        {!c.loading && c.requirements.length > 0 && (
          <RequirementFilters
            key={c.scenarioId}
            scenarioId={c.scenarioId}
            requirements={c.requirements}
            previousRanks={c.previousRanks}
            highlightRanks={c.highlightRanks}
            conflictTitles={c.conflictTitles}
          />
        )}
      </section>

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
