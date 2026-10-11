"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { getScenarios } from "@/src/lib/api";
import { useLoad } from "@/src/lib/useLoad";
import { PageHeader, ErrorNote, Loading } from "@/src/components/ui/PageHeader";
import { ScenarioFilters, EMPTY_SCENARIO_FILTER, matchesScenario } from "@/src/components/ScenarioFilters";
import { ProductContext } from "@/src/components/ProductContext";

export default function ModelsPage() {
  const view = useLoad("models", getScenarios);
  const [filter, setFilter] = useState(EMPTY_SCENARIO_FILTER);
  const scenarios = view.data ?? [];
  const filtered = scenarios.filter(s => matchesScenario(s, filter));
  return <main className="mx-auto max-w-[1400px] px-6 py-10 lg:px-10">
    <PageHeader eyebrow="Vehicle selection" title="Models and markets">Pick a vehicle and market to see which customer requirements matter most for its successor. Filter by model or region.</PageHeader>
    <ScenarioFilters scenarios={scenarios} value={filter} onChange={setFilter} />
    {view.loading && <Loading what="models" />}
    {view.error && <ErrorNote message={view.error} />}
    {!view.loading && !view.error && <p role="status" className="my-5 text-sm text-[var(--grey-500)]">{filtered.length} of {scenarios.length} model and market combinations</p>}
    {/* Erste Reihe (max. 3 Karten) liegt über dem Falz: eager laden, sonst wird das LCP-Bild verzögert. */}
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      {filtered.map((s, i) => <article key={s.id} className="flex min-w-0 flex-col overflow-hidden border border-[var(--hairline)]">
        {/* Jedes der sechs Szenarien hat jetzt ein Foto in public/media/scenarios/ (G68-CN seit 11.10.). */}
        <div className="relative aspect-[16/9] overflow-hidden bg-[var(--grey-100)]"><Image src={`/media/scenarios/${s.id}.jpg`} alt={s.model_name} fill loading={i < 3 ? "eager" : "lazy"} sizes="(min-width: 1280px) 33vw, (min-width: 768px) 50vw, 100vw" className="object-cover" /></div>
        <div className="flex flex-1 flex-col p-5">
          <p className="text-xs text-[var(--grey-500)]">{s.derivative} / {s.market} / Successor {s.successor_horizon}</p>
          <h2 className="mt-2 text-xl font-medium">{s.model_name}</h2>
          <p className="my-4 text-sm text-[var(--grey-500)]">{s.data_coverage?.feedback.toLocaleString("en") ?? "Unavailable"} customer feedback records / {s.headline_numbers?.requirements ?? 0} requirements</p>
          <ProductContext scenarioId={s.id} />
          {s.warnings?.map(w => <p key={w} className="mt-3 text-xs text-amber-800">{w}</p>)}
          <Link href={`/cockpit?scenario=${s.id}`} className="mt-auto block pt-5 text-sm font-semibold text-[var(--blue)]">Open ranked requirements &rarr;</Link>
        </div>
      </article>)}
    </div>
    {!view.loading && !view.error && filtered.length === 0 && <p className="py-10 text-sm">No models match these filters.</p>}
  </main>;
}
