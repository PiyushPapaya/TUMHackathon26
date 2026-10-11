import type { ScenarioMarket } from "@/src/lib/insights";

// Balken statt Tabelle: Ob der BMW vorne oder hinten liegt, soll man in einer Sekunde sehen.
// BMW in Blau, Wettbewerber in Grau. Werte kommen aus EPA/NHTSA-Caches (core/market_benchmarks.py).
function Bars({ title, unit, rows, better }: {
  title: string; unit: string; better: string;
  rows: { name: string; is_bmw: boolean; value: number; note?: string }[];
}) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">{title} <span className="font-normal normal-case tracking-normal">({better})</span></h4>
      <ul className="mt-3 grid gap-2">
        {rows.map((r) => (
          <li key={r.name} className="grid grid-cols-[minmax(0,180px)_1fr_auto] items-center gap-3 text-sm">
            <span className={`truncate ${r.is_bmw ? "font-semibold" : ""}`} title={r.name}>{r.name}</span>
            <span className="h-2 bg-[var(--grey-100)]">
              <span className="block h-2" style={{ width: `${(r.value / max) * 100}%`, background: r.is_bmw ? "var(--blue)" : "var(--grey-500)" }} />
            </span>
            <span className="tabular-nums">{r.value.toLocaleString("en-US")} {unit}{r.note && <span className="ml-2 text-xs text-[var(--grey-500)]">{r.note}</span>}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function MarketBench({ market }: { market: ScenarioMarket }) {
  const years = market.complaint_years.join("/");
  return (
    <article className="border-t border-[var(--hairline)] py-8">
      <h3 className="text-xl font-light">{market.model_name} <span className="text-[var(--grey-500)]">· {market.scenario_id}</span></h3>
      <p className="mt-2 text-sm">{market.range_sentence}</p>
      <div className="mt-6 grid gap-10 lg:grid-cols-2">
        {market.range.length > 0 && (
          <Bars title="EPA range" unit="km" better="higher is better"
            rows={market.range.map((v) => ({ name: v.name, is_bmw: v.is_bmw, value: v.range_km,
              note: v.kwh_per_100km ? `${v.kwh_per_100km} kWh/100 km` : undefined }))} />
        )}
        {market.complaints.length > 0 && (
          <Bars title={`NHTSA complaints, model years ${years}`} unit="" better="lower is better"
            rows={market.complaints.map((c) => ({ name: c.name, is_bmw: c.is_bmw, value: c.complaints }))} />
        )}
      </div>
      <p className="mt-6 text-xs text-[var(--grey-500)]">Limits: {market.limits} Sources: fueleconomy.gov, api.nhtsa.gov.</p>
    </article>
  );
}
