"use client";

import { Suspense, useState } from "react";
import { getRequirements } from "@/src/lib/api";
import { getGaps, getMatrix, getOpportunities, getTrends } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { useScenarioParam } from "@/src/components/shell/useScenarioParam";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { MatrixView } from "@/src/components/insights/MatrixView";
import { OpportunityMap } from "@/src/components/insights/OpportunityMap";
import { GapsList, TrendsList } from "@/src/components/insights/TrendsAndGaps";

const TABS = [
  ["matrix", "Evidence vs. assumption"],
  ["opportunities", "Opportunities"],
  ["trends", "Trends"],
  ["gaps", "What we do not know"],
] as const;
type Tab = (typeof TABS)[number][0];

const INTRO: Record<Tab, string> = {
  matrix: "Where conclusions rest on evidence today, and where they rely on forward-looking assumptions for the successor.",
  opportunities: "Customer studies: what matters most and where customers are least satisfied.",
  trends: "Three to five years ahead: which needs the next generation should answer, and which assumptions they depend on.",
  gaps: "Honest uncertainty: weakly evidenced proposals and the study that would settle them.",
};

function Insights() {
  const id = useScenarioParam();
  const [tab, setTab] = useState<Tab>("matrix");
  const matrix = useLoad(id + "m", () => Promise.all([getMatrix(id), getRequirements(id)]));
  const opp = useLoad(id + "o", () => getOpportunities(id));
  const trends = useLoad(id + "t", () => getTrends(id));
  const gaps = useLoad(id + "g", () => getGaps(id));
  const current = { matrix, opportunities: opp, trends, gaps }[tab];

  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <PageHeader eyebrow={`Insights · ${id}`} title="Insights.">{INTRO[tab]}</PageHeader>
      <div role="tablist" className="mb-8 flex flex-wrap gap-x-8 border-b border-[var(--hairline)]">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            onClick={() => setTab(key)}
            className={`-mb-px border-b-2 py-3 text-[15px] ${tab === key ? "border-[var(--blue)] font-semibold text-[var(--ink)]" : "border-transparent text-[var(--grey-500)] hover:text-[var(--ink)]"}`}
          >
            {label}
          </button>
        ))}
      </div>
      {current.error && <ErrorNote message={current.error} />}
      {current.loading && <Loading what="insights" />}
      {tab === "matrix" && matrix.data && <MatrixView matrix={matrix.data[0]} requirements={matrix.data[1]} />}
      {tab === "opportunities" && opp.data && <OpportunityMap data={opp.data} />}
      {tab === "trends" && trends.data && <TrendsList data={trends.data} />}
      {tab === "gaps" && gaps.data && <GapsList data={gaps.data} />}
    </main>
  );
}

export default function InsightsPage() {
  return (
    <Suspense fallback={<main className="px-6 py-12 text-sm text-[var(--grey-500)]">Loading...</main>}>
      <Insights />
    </Suspense>
  );
}
