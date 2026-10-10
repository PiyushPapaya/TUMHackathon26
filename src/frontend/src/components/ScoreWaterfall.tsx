import type { EvidenceLevel, ScoreFactor, WaterfallStep } from "@/src/lib/api";

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

const CONFIDENCE: Record<EvidenceLevel, number> = { A: 1, B: 0.85, C: 0.7, D: 0.5 };
const EVIDENCE_LABEL: Record<EvidenceLevel, string> = {
  A: "A · strong",
  B: "B · medium",
  C: "C · weak",
  D: "D · assumption",
};

function fromBreakdown(scoreBreakdown: Record<string, ScoreFactor>): WaterfallStep[] {
  const known = new Set<string>(FACTOR_ORDER);
  const orderedKeys = [
    ...FACTOR_ORDER.filter((key) => key in scoreBreakdown),
    ...Object.keys(scoreBreakdown).filter((key) => !known.has(key)),
  ];
  return orderedKeys.map((key) => ({
    factor: key,
    label: FACTOR_LABELS[key] ?? key,
    value: scoreBreakdown[key].value,
    weight: scoreBreakdown[key].weight,
    contribution: scoreBreakdown[key].contribution,
    sentence: scoreBreakdown[key].explanation,
  }));
}

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

function FactorRow({ step }: { step: WaterfallStep }) {
  if (step.factor === "confidence") {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-3 py-2">
        <div className="flex items-center justify-between gap-4 text-sm">
          <span className="font-semibold text-[#0b1f3a]">{step.label}</span>
          <span className={step.contribution < 0 ? "font-semibold text-amber-700" : "font-semibold text-slate-600"}>
            {step.contribution.toFixed(1)} pts
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-600">{step.sentence}</p>
      </div>
    );
  }

  const maxContribution = Math.max((step.weight ?? 0) * 100, 0.01);
  const width = Math.min(100, Math.max(0, (step.contribution / maxContribution) * 100));
  return (
    <div className="py-2">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 text-sm">
        <span className="font-semibold text-[#0b1f3a]">{step.label}</span>
        <span className="text-slate-600">
          +{step.contribution.toFixed(1)} pts
          {step.weight !== null && (
            <span className="ml-1 text-xs text-slate-500">
              ({step.value.toFixed(2)} x {step.weight.toFixed(2)} x 100)
            </span>
          )}
        </span>
      </div>
      <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${width}%` }} />
      </div>
      <p className="mt-1 text-xs text-slate-600">{step.sentence}</p>
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
  const factorSteps = (waterfall?.length ? waterfall : fromBreakdown(scoreBreakdown)).filter(
    (step) => step.factor !== "confidence",
  );
  const confidenceStep = waterfall?.find((step) => step.factor === "confidence");
  const subtotal = factorSteps.reduce((sum, step) => sum + step.contribution, 0);
  const calculatedDeduction = Math.round((finalScore - subtotal) * 10) / 10;
  const scoreNoAssumptions = scoreWithoutAssumptions(scoreBreakdown, evidenceLevel);

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Score waterfall
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Each contribution shows value x weight x 100. Evidence confidence is applied last.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="rounded-md border border-slate-200 px-3 py-2 text-right">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Final</p>
            <p className="text-lg font-semibold text-[#0b1f3a]">{finalScore.toFixed(1)}</p>
          </div>
          <div className="rounded-md border border-dashed border-slate-300 px-3 py-2 text-right">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">No assumptions</p>
            <p className="text-lg font-semibold text-[#0b1f3a]">{scoreNoAssumptions.toFixed(1)}</p>
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
          Ignore assumptions: compare the normal score with future relevance removed.
        </label>
      )}

      <div className="mt-4 divide-y divide-slate-100">
        {factorSteps.map((step) => (
          <FactorRow key={step.factor} step={step} />
        ))}
      </div>

      <div className="mt-4 grid gap-2 border-t border-slate-200 pt-3">
        <div className="flex items-baseline justify-between text-sm">
          <span className="text-slate-600">Subtotal before evidence confidence</span>
          <span className="font-semibold text-[#0b1f3a]">{subtotal.toFixed(1)} pts</span>
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
