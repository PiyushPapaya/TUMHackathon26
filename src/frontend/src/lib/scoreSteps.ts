import type { ScoreFactor, WaterfallStep } from "@/src/lib/api";

// One source for the factor bars: the chart and the "Ranked mainly because of" sentence both read these steps,
// so the points in the text can never drift from the chart (the backend does not rewrite the text after reweighting).

export const FACTOR_ORDER = [
  "customer_pain",
  "reach",
  "satisfaction_gap",
  "competitive_pressure",
  "future_relevance",
  "effort_inverse",
] as const;

export const FACTOR_LABELS: Record<string, string> = {
  customer_pain: "Customer pain",
  reach: "Reach",
  satisfaction_gap: "Satisfaction gap",
  competitive_pressure: "Competitive pressure",
  future_relevance: "Future relevance",
  effort_inverse: "Low effort",
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

/** Factor bars exactly as the chart draws them (without the confidence step). */
export function chartFactorSteps(
  scoreBreakdown: Record<string, ScoreFactor>,
  waterfall: WaterfallStep[] | undefined,
  ignoreAssumptions: boolean,
): WaterfallStep[] {
  const steps = (waterfall?.length ? waterfall : fromBreakdown(scoreBreakdown)).filter((s) => s.factor !== "confidence");
  if (!ignoreAssumptions) return steps;
  // Preview: drop future relevance and spread its weight over the remaining factors.
  const kept = steps.filter((s) => s.factor !== "future_relevance");
  const weightLeft = kept.reduce((sum, s) => sum + (s.weight ?? 0), 0);
  return kept.map((s) => ({
    ...s,
    contribution: weightLeft > 0 ? s.contribution / weightLeft : 0,
    weight: weightLeft > 0 ? (s.weight ?? 0) / weightLeft : 0,
  }));
}

const RANKED_SENTENCE = /^Ranked mainly because of .*?\.(?=\s|$)\s*/;

/** Replaces the stored "Ranked mainly because of ..." sentence with the two biggest bars of the chart. */
export function rationaleWithChartPoints(rationale: string, steps: WaterfallStep[]): string {
  if (!RANKED_SENTENCE.test(rationale)) return rationale;
  const top = [...steps].sort((a, b) => b.contribution - a.contribution).slice(0, 2);
  if (top.length === 0) return rationale;
  const named = top.map((s) => `${(FACTOR_LABELS[s.factor] ?? s.label).toLowerCase()} (${s.contribution.toFixed(1)} pts)`);
  const rest = rationale.replace(RANKED_SENTENCE, "");
  return `Ranked mainly because of ${named.join(" and ")}.${rest ? ` ${rest}` : ""}`;
}
