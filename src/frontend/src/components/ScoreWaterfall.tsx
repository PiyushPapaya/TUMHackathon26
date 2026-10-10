/**
 * Score-Wasserfall für die Detailseite (D3). Spiegelt die Formel aus
 * requirements_engine/scoring.py: score = Konfidenz(Evidenzstufe) * Summe(gewicht_i * faktor_i) * 100.
 * Die Konfidenzzahlen selbst (A=1.0 ... D=0.5) holen wir NICHT hierher, sondern rechnen den
 * Abzug aus Zwischensumme und Endscore zurück — sonst müssten zwei Stellen dieselbe Zahl pflegen.
 */
import type { EvidenceLevel, ScoreFactor } from "@/src/lib/api";

const FACTOR_ORDER = [
  "customer_pain",
  "reach",
  "satisfaction_gap",
  "competitive_pressure",
  "future_relevance",
  "effort_inverse",
] as const;

const FACTOR_LABELS: Record<string, string> = {
  customer_pain: "Customer pain",
  reach: "Reach",
  satisfaction_gap: "Satisfaction gap",
  competitive_pressure: "Competitive pressure",
  future_relevance: "Future relevance",
  effort_inverse: "Low effort",
};

const EVIDENCE_LABEL: Record<EvidenceLevel, string> = {
  A: "A · strong",
  B: "B · medium",
  C: "C · weak",
  D: "D · assumption",
};

function FactorRow({ label, factor }: { label: string; factor: ScoreFactor }) {
  // Balkenbreite relativ zum höchstmöglichen Beitrag dieses Faktors (weight * 100),
  // damit ein voll ausgeschöpfter Faktor immer einen vollen Balken zeigt.
  const maxContribution = Math.max(factor.weight * 100, 0.01);
  const width = Math.min(100, (factor.contribution / maxContribution) * 100);
  return (
    <div className="py-2">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 text-sm">
        <span className="font-medium text-[#0b1f3a]">{label}</span>
        <span className="text-zinc-500">
          +{factor.contribution.toFixed(1)} pts
          <span className="ml-1 text-xs text-zinc-400">
            ({factor.value.toFixed(2)} × {factor.weight.toFixed(2)} × 100)
          </span>
        </span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-zinc-100">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${width}%` }} />
      </div>
      <p className="mt-1 text-xs text-zinc-500">{factor.explanation}</p>
    </div>
  );
}

export function ScoreWaterfall({
  scoreBreakdown,
  evidenceLevel,
  finalScore,
}: {
  scoreBreakdown: Record<string, ScoreFactor>;
  evidenceLevel: EvidenceLevel;
  finalScore: number;
}) {
  const known = new Set<string>(FACTOR_ORDER);
  const orderedKeys = [
    ...FACTOR_ORDER.filter((key) => key in scoreBreakdown),
    ...Object.keys(scoreBreakdown).filter((key) => !known.has(key)),
  ];
  const subtotal = orderedKeys.reduce((sum, key) => sum + scoreBreakdown[key].contribution, 0);
  const deduction = Math.max(0, subtotal - finalScore);
  const keptPercent = subtotal > 0 ? Math.round((finalScore / subtotal) * 100) : 100;

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-5">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">Score breakdown</h2>
      <div className="mt-2 divide-y divide-zinc-100">
        {orderedKeys.map((key) => (
          <FactorRow key={key} label={FACTOR_LABELS[key] ?? key} factor={scoreBreakdown[key]} />
        ))}
      </div>

      <div className="mt-4 border-t border-dashed border-zinc-300 pt-3">
        <div className="flex items-baseline justify-between text-sm">
          <span className="text-zinc-600">Subtotal (all factors, full confidence)</span>
          <span className="font-medium text-[#0b1f3a]">{subtotal.toFixed(1)} pts</span>
        </div>
        {deduction > 0 && (
          <div className="mt-1 flex items-baseline justify-between text-sm">
            <span className="text-zinc-600">
              Confidence deduction — evidence level {EVIDENCE_LABEL[evidenceLevel]} keeps {keptPercent}%
            </span>
            <span className="font-medium text-amber-700">-{deduction.toFixed(1)} pts</span>
          </div>
        )}
        <div className="mt-2 flex items-baseline justify-between border-t border-zinc-200 pt-2 text-base">
          <span className="font-semibold text-[#0b1f3a]">Final score</span>
          <span className="font-semibold text-[#0b1f3a]">{finalScore.toFixed(1)} / 100</span>
        </div>
      </div>
    </div>
  );
}
