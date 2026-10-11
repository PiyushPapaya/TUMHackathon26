"use client";

import { getPortfolio } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { categoryLabel } from "@/src/components/badges";
import { CLASS_EN, en } from "@/src/components/insights/labels";
import { PortfolioCellLink } from "@/src/components/portfolio/PortfolioCellLink";
import { MarketCompare } from "@/src/components/portfolio/MarketCompare";

// Portfolio: Welche Kundenthemen gelten über Modelle und Märkte hinweg, welche nur lokal?
// Warum: Der Brief will Übertragbarkeit auf andere Fahrzeuge und Märkte sehen.
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
                    {data.scenarios.map((s) => <td key={s.id} className="px-3 py-4"><PortfolioCellLink cell={row.cells[s.id] ?? null} /></td>)}
                    <td className="px-3 py-4 text-[var(--grey-500)]">{en(CLASS_EN, row.class)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <MarketCompare />
        </>
      )}
    </main>
  );
}
