"use client";

import { getBenchmarks } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { QualityTable } from "@/src/components/benchmarks/QualityTable";
import { MarketBench } from "@/src/components/benchmarks/MarketBench";

// Benchmarks: zwei Fragen der Jury und jedes BMW-PMs.
// 1. Kann ich den KI-Vorschlägen trauen? (Quellen, Messbarkeit, Stabilität per Simulation)
// 2. Wo steht unser Modell gegen den Wettbewerb? (amtliche EPA/NHTSA-Zahlen, keine Prospektwerte)
export default function BenchmarksPage() {
  const view = useLoad("benchmarks", getBenchmarks);
  const data = view.data;
  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <PageHeader eyebrow="Benchmarks" title="Measured, not claimed.">
        Every number is recomputed from the loaded data each time this page opens. No language model is involved,
        so the same data always gives the same result.
      </PageHeader>
      {view.error && <ErrorNote message={view.error} />}
      {view.loading && <Loading what="benchmarks" />}
      {data && (
        <>
          <section>
            <h2 className="text-3xl font-light">Can a PM trust the proposals?</h2>
            <p className="mb-6 mt-2 max-w-2xl text-sm text-[var(--grey-500)]">
              One column per scenario. Blue meets the target, red is below it. Hover a value for the exact count.
            </p>
            <QualityTable rows={data.quality} />
          </section>
          <section className="mt-16">
            <h2 className="text-3xl font-light">Where does the model stand?</h2>
            <p className="mb-6 mt-2 max-w-2xl text-sm text-[var(--grey-500)]">
              Official US data measured the same way for every brand. Only US scenarios have it; EU and China have no
              comparable public source.
            </p>
            {data.market.length === 0 && <p className="text-sm text-[var(--grey-500)]">No US scenario loaded.</p>}
            {data.market.map((m) => <MarketBench key={m.scenario_id} market={m} />)}
          </section>
        </>
      )}
    </main>
  );
}
