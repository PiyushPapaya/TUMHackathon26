import type { EvidenceLevel, ScoreFactor, WaterfallStep } from "@/src/lib/api";
import { chartFactorSteps, FACTOR_LABELS } from "@/src/lib/scoreSteps";

const CONFIDENCE: Record<EvidenceLevel, number> = { A: 1, B: 0.85, C: 0.7, D: 0.5 };
const EVIDENCE_LABEL: Record<EvidenceLevel, string> = {
  A: "A · strong",
  B: "B · medium",
  C: "C · weak",
  D: "D · assumption",
};

export function scoreWithoutAssumptions(
  scoreBreakdown: Record<string, ScoreFactor>,
  evidenceLevel: EvidenceLevel,
) {
  const kept = Object.entries(scoreBreakdown).filter(([name]) => name !== "future_relevance");
  const weightLeft = kept.reduce((sum, [, factor]) => sum + factor.weight, 0);
  if (weightLeft <= 0) return 0;
  const raw = kept.reduce((sum, [, factor]) => sum + factor.value * factor.weight, 0);
  return Math.round((raw / weightLeft) * 100 * CONFIDENCE[evidenceLevel] * 10) / 10;
}

function FactorRow({ step, maximum = 100 }: { step: WaterfallStep; maximum?: number }) {
  if (step.factor === "confidence") {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-2">
        <div className="flex items-center justify-between gap-4 text-sm">
          <span className="font-semibold text-[#262626]">Evidence confidence</span>
          <span className={step.contribution < 0 ? "font-semibold text-amber-700" : "font-semibold text-slate-600"}>
            {step.contribution.toFixed(1)} pts
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-600">{step.sentence}</p>
      </div>
    );
  }

  const width = Math.min(100, Math.max(0, (step.contribution / Math.max(maximum, 0.01)) * 100));
  return (
    <div className="py-2">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 text-sm">
        <span className="font-semibold text-[#262626]">{FACTOR_LABELS[step.factor] ?? step.label}</span>
        <span className="text-slate-600">
          +{step.contribution.toFixed(1)} pts
        </span>
      </div>
      <div className="mt-2 h-2.5 w-full overflow-hidden bg-slate-200">
        <div className="h-full bg-blue-600" style={{ width: `${width}%` }} />
      </div>
      <details className="mt-1 text-xs text-slate-600"><summary>Calculation details</summary><p className="mt-1">{step.sentence}</p>{step.weight !== null && <p>{step.value.toFixed(2)} x {step.weight.toFixed(2)} x 100</p>}</details>
    </div>
  );
}

export function ScoreWaterfall({
  scoreBreakdown,
  evidenceLevel,
  finalScore,
  waterfall,
  ignoreAssumptions,
  onToggleIgnoreAssumptions,
}: {
  scoreBreakdown: Record<string, ScoreFactor>;
  evidenceLevel: EvidenceLevel;
  finalScore: number;
  waterfall?: WaterfallStep[];
  ignoreAssumptions?: boolean;
  onToggleIgnoreAssumptions?: (value: boolean) => void;
}) {
  const factorSteps = chartFactorSteps(scoreBreakdown, waterfall, Boolean(ignoreAssumptions));
  const confidenceStep = !ignoreAssumptions ? waterfall?.find((step) => step.factor === "confidence") : undefined;
  const subtotal = factorSteps.reduce((sum, step) => sum + step.contribution, 0);
  const scoreNoAssumptions = scoreWithoutAssumptions(scoreBreakdown, evidenceLevel);
  const displayedScore = ignoreAssumptions ? scoreNoAssumptions : finalScore;
  const calculatedDeduction = Math.round((displayedScore - subtotal) * 10) / 10;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Why this priority?
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Priority score / 100
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="rounded-md border border-slate-200 px-3 py-2 text-right">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">{ignoreAssumptions ? "Preview" : "Final"}</p>
            <p className="text-lg font-semibold text-[#262626]">{displayedScore.toFixed(1)}</p>
          </div>
          <div className="rounded-md border border-dashed border-slate-300 px-3 py-2 text-right">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Without future factor</p>
            <p className="text-lg font-semibold text-[#262626]">{scoreNoAssumptions.toFixed(1)}</p>
          </div>
        </div>
      </div>

      {onToggleIgnoreAssumptions && (
        <label className="mt-4 flex min-h-11 items-center gap-3 rounded-md border border-dashed border-slate-300 px-3 py-2 text-sm text-slate-700">
          <input
            type="checkbox"
            className="h-4 w-4 accent-blue-600"
            checked={Boolean(ignoreAssumptions)}
            onChange={(event) => onToggleIgnoreAssumptions(event.target.checked)}
          />
          Exclude future relevance (preview)
        </label>
      )}

      <div className="mt-4 divide-y divide-slate-100">
        {factorSteps.map((step) => (
          <FactorRow key={step.factor} step={step} maximum={Math.max(...factorSteps.map(s => s.contribution), 1)} />
        ))}
      </div>

      <div className="mt-4 grid gap-2 border-t border-slate-200 pt-3">
        <div className="flex items-baseline justify-between text-sm">
          <span className="text-slate-600">Subtotal before evidence confidence</span>
          <span className="font-semibold text-[#262626]">{subtotal.toFixed(1)} pts</span>
        </div>
        {confidenceStep ? (
          <FactorRow step={confidenceStep} />
        ) : (
          <div className="flex items-baseline justify-between text-sm">
            <span className="text-slate-600">
              Confidence adjustment from {EVIDENCE_LABEL[evidenceLevel]}
            </span>
            <span className="font-semibold text-amber-700">{calculatedDeduction.toFixed(1)} pts</span>
          </div>
        )}
      </div>
    </section>
  );
}
