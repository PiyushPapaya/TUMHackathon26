"use client";

import { useState } from "react";
import Link from "next/link";
import { getCompare, getPortfolio, type PortfolioCell } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { EvidenceBadge, categoryLabel } from "@/src/components/badges";
import { CLASS_EN, en } from "@/src/components/insights/labels";

function Cell({ cell }: { cell: PortfolioCell | null }) {
  if (!cell) return <span className="text-[var(--grey-500)]">–</span>;
  return (
    <Link href={`/requirements/${cell.requirement_id}`} className="block hover:text-[var(--blue)]">
      <span className="flex items-center gap-2">
        <span className="text-2xl font-light tabular-nums">{cell.rank}</span>
        <EvidenceBadge level={cell.evidence_level} />
      </span>
      <span className="mt-1 line-clamp-2 block text-xs text-[var(--grey-500)]">{cell.title}</span>
    </Link>
  );
}

// Portfolio: Welche Kundenthemen gelten über Modelle und Märkte hinweg, welche nur lokal?
// Warum: Der Brief will Übertragbarkeit auf andere Fahrzeuge und Märkte sehen.
function Compare({ ids }: { ids: { id: string; label: string }[] }) {
  const [a, setA] = useState("G60-US");
  const [b, setB] = useState("G60-EU");
  const view = useLoad(a + b, () => getCompare(a, b));
  const select = "h-11 border border-[var(--hairline)] bg-white px-3 text-sm";
  return (
    <section className="mt-16">
      <h2 className="text-3xl font-light">Compare two markets.</h2>
      <div className="mt-6 flex flex-wrap gap-4">
        {[[a, setA, "Market A"], [b, setB, "Market B"]].map(([val, set, label]) => (
          <label key={label as string} className="grid gap-1 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">
            {label as string}
            <select className={select} value={val as string} onChange={(e) => (set as (v: string) => void)(e.target.value)}>
              {ids.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
            </select>
          </label>
        ))}
      </div>
      {view.error && <ErrorNote message={view.error} />}
      {view.loading && <Loading what="comparison" />}
      {view.data && (
        <ul className="mt-6 border-t border-[var(--hairline)]">
          {view.data.rows.map((r) => (
            <li key={r.category} className="grid items-center gap-4 border-b border-[var(--hairline)] py-4 md:grid-cols-[200px_1fr_1fr_1.2fr]">
              <span className="text-sm font-semibold">{categoryLabel(r.category)}</span>
              <Cell cell={r.a} />
              <Cell cell={r.b} />
              <span className="text-sm text-[var(--grey-500)]">{r.sentence}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function PortfolioPage() {
  const portfolio = useLoad("p", getPortfolio);
  const data = portfolio.data;
  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <PageHeader eyebrow="Portfolio" title="Across models and markets.">
        Which customer topics are platform-wide, and which belong to one model or one market. Rank 1 is the top proposal of that scenario.
      </PageHeader>
      {portfolio.error && <ErrorNote message={portfolio.error} />}
      {portfolio.loading && <Loading what="portfolio" />}
      {data && (
        <>
          <div className="overflow-x-auto border-t border-[var(--hairline)]">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">
                <tr>
                  <th className="px-3 py-3 font-semibold">Category</th>
                  {data.scenarios.map((s) => <th key={s.id} className="px-3 py-3 font-semibold">{s.id}</th>)}
                  <th className="px-3 py-3 font-semibold">Scope</th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row) => (
                  <tr key={row.category} className="border-t border-[var(--hairline)] align-top">
                    <td className="px-3 py-4 font-semibold">{categoryLabel(row.category)}</td>
                    {data.scenarios.map((s) => <td key={s.id} className="px-3 py-4"><Cell cell={row.cells[s.id] ?? null} /></td>)}
                    <td className="px-3 py-4 text-[var(--grey-500)]">{en(CLASS_EN, row.class)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Compare ids={data.scenarios.map((s) => ({ id: s.id, label: `${s.model_name} ${s.market}` }))} />
        </>
      )}
    </main>
  );
}
