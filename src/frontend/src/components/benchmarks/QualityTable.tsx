import type { QualityMetric, ScenarioQuality } from "@/src/lib/insights";

// Die Frage, die der PM mit der Zeile beantwortet. Die genauen Zahlen je Szenario stehen im Tooltip der Zelle.
const QUESTION: Record<string, string> = {
  grounding: "Does every cited source really exist? Checked ID by ID.",
  measurable: "Syntax heuristic only: a number does not prove measurability. Review the outcome, procedure, threshold, sample and baseline for relative targets.",
  rank_stability: "Simulation: 200 runs with every weight changed by up to ±20%. How much of the top 5 survives?",
  first_stays_first: "Same simulation: how often does the #1 proposal stay #1?",
  strong_evidence: "Share of proposals backed by several sources or many mentions. Thin data stays visible as C/D.",
  triangulated: "Share of BMW-internal findings that web or authority data also confirms.",
};

// Eine Zeile je Prüffrage, eine Spalte je Szenario. Warum Tabelle statt Kacheln:
// Der PM sieht sofort, welches Szenario wo schwach ist (z. B. dünne Daten in EU), ohne zu klicken.
function Cell({ metric }: { metric: QualityMetric }) {
  const color = metric.ok === false ? "text-[var(--m-red)]" : metric.ok ? "text-[var(--blue)]" : "text-[var(--ink)]";
  return (
    <td className="px-3 py-4 align-top" title={metric.explain}>
      <span className={`text-lg font-light tabular-nums ${color}`}>{metric.value.toFixed(0)}{metric.unit}</span>
      {metric.ok === false && <span className="ml-2 text-xs font-semibold uppercase text-[var(--m-red)]">below target</span>}
    </td>
  );
}

export function QualityTable({ rows }: { rows: ScenarioQuality[] }) {
  const metrics = rows[0]?.metrics ?? [];
  const fmt = (n: number) => n.toLocaleString("en-US");
  return (
    <div className="overflow-x-auto border-t border-[var(--hairline)]">
      <table className="w-full min-w-[900px] text-left text-sm">
        <thead className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">
          <tr>
            <th className="px-3 py-3 font-semibold">Check</th>
            <th className="px-3 py-3 font-semibold">Target</th>
            {rows.map((r) => <th key={r.scenario_id} className="px-3 py-3 font-semibold">{r.scenario_id}</th>)}
          </tr>
        </thead>
        <tbody>
          <tr className="border-t border-[var(--hairline)] align-top">
            <td className="px-3 py-4">
              <span className="font-semibold">Evidence → proposals</span>
              <p className="mt-1 max-w-xs text-xs text-[var(--grey-500)]">Customer voices condensed into findings, then into ranked proposals. Out-of-scope drafts are kept visible.</p>
            </td>
            <td className="px-3 py-4 text-[var(--grey-500)]">–</td>
            {rows.map((r) => (
              <td key={r.scenario_id} className="px-3 py-4 tabular-nums">
                {fmt(r.funnel.evidence)} → {r.funnel.signals} → <strong>{r.funnel.requirements}</strong>
                {r.funnel.discarded > 0 && <span className="block text-xs text-[var(--grey-500)]">{r.funnel.discarded} discarded</span>}
              </td>
            ))}
          </tr>
          {metrics.map((m) => (
            <tr key={m.key} className="border-t border-[var(--hairline)] align-top">
              <td className="px-3 py-4">
                <span className="font-semibold">{m.label}</span>
                <p className="mt-1 max-w-xs text-xs text-[var(--grey-500)]">{QUESTION[m.key] ?? ""}</p>
              </td>
              <td className="px-3 py-4 text-[var(--grey-500)]">{m.target === null ? "info" : m.target === 100 ? "100%" : `≥ ${m.target}%`}</td>
              {rows.map((r) => <Cell key={r.scenario_id} metric={r.metrics.find((x) => x.key === m.key)!} />)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
