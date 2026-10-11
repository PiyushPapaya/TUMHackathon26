"use client";

import { useLoad } from "@/src/lib/useLoad";
import { getProductContext } from "@/src/lib/insights";

// compact: one line for the cockpit, so the ranked list stays above the fold; the full note sits in the tooltip.
export function ProductContext({ scenarioId, compact = false }: { scenarioId: string; compact?: boolean }) {
  const view = useLoad(scenarioId, () => getProductContext(scenarioId));
  const data = view.data;
  const price = (value: number) => new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
  const range = view.loading ? "Loading price reference..." : data?.min_eur != null && data.max_eur != null ? `${price(data.min_eur)} - ${price(data.max_eur)}` : "Price reference unavailable";
  const source = data && data.pages.length > 0 ? `${data.source}, pages ${data.pages.join(", ")}` : "";
  if (compact) {
    return <p className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm" title={data?.note ?? undefined}>
      <span className="text-[var(--grey-500)]">Today&apos;s list price (Germany, incl. VAT)</span>
      <span className="font-semibold tabular-nums">{range}</span>
      {source && <span className="text-xs text-[var(--grey-500)]">Source: {source}. Reference only, not a successor cost.</span>}
    </p>;
  }
  return <section className="border-y border-[var(--hairline)] py-4">
    <div className="flex flex-wrap items-baseline justify-between gap-3">
      <h2 className="text-sm font-semibold">Current vehicle reference</h2>
      <span className="text-sm tabular-nums">{range}</span>
    </div>
    <p className="mt-2 text-xs text-[var(--grey-500)]">{data?.note ?? view.error}</p>
    {data && <p className="mt-2 text-xs text-[var(--grey-500)]">{source && `${source}. `}{data.engines.length > 0 && `Feedback powertrains: ${data.engines.join(", ")}.`}</p>}
  </section>;
}
