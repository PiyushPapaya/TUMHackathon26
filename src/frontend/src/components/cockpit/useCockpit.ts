"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getRequirements,
  getScenarios,
  getSignals,
  putWeights,
  type Requirement,
  type Scenario,
  type Signal,
  type WeightKey,
  type Weights,
} from "@/src/lib/api";
import { DEFAULT_SCENARIO_ID } from "@/src/components/shell/scenarioLabel";

// State und API-Aufrufe des Cockpits, unverändert aus der alten app/page.tsx übernommen.
// Warum ausgelagert: die Seite bleibt unter 200 Zeilen und die Logik ist getrennt vom Aussehen testbar.
export const PM_ACTOR = "pm.demo";
export const DEFAULT_WEIGHTS: Record<WeightKey, number> = {
  customer_pain: 0.25,
  reach: 0.2,
  satisfaction_gap: 0.2,
  competitive_pressure: 0.15,
  future_relevance: 0.1,
  effort_inverse: 0.1,
};
export const WEIGHT_LABELS: Record<WeightKey, string> = {
  customer_pain: "Customer pain",
  reach: "Reach",
  satisfaction_gap: "Satisfaction gap",
  competitive_pressure: "Competitive pressure",
  future_relevance: "Future relevance",
  effort_inverse: "Low effort",
};

// Begründung für manuelle Slider-Änderungen, automatisch aus dem Unterschied gebaut.
// Warum kein Textfeld mehr: Die Frage in "Ask in your own words" ist schon die Begründung,
// und für Slider reicht ein lesbarer Diff im Prüfpfad ("Customer pain +0.10, Reach -0.05").
export function describeWeightChange(before: Record<WeightKey, number>, after: Weights): string {
  const parts = (Object.keys(WEIGHT_LABELS) as WeightKey[])
    .map((key) => [key, (after[key] ?? before[key]) - before[key]] as const)
    .filter(([, diff]) => Math.abs(diff) >= 0.005)
    .map(([key, diff]) => `${WEIGHT_LABELS[key]} ${diff > 0 ? "+" : ""}${diff.toFixed(2)}`);
  return parts.length ? `Manual weight change: ${parts.join(", ")}` : "Weights re-applied without change.";
}

function weightsFromRequirements(requirements: Requirement[]): Record<WeightKey, number> {
  const first = requirements[0]?.score_breakdown;
  const out = { ...DEFAULT_WEIGHTS };
  (Object.keys(out) as WeightKey[]).forEach((key) => {
    out[key] = first?.[key]?.weight ?? DEFAULT_WEIGHTS[key];
  });
  return out;
}

export function useCockpit(initialScenarioId: string | null) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  // Das Szenario kommt aus der URL (?scenario=, Deep-Link). Ist es unbekannt, nehmen wir das erste vorhandene.
  const [fallbackId, setFallbackId] = useState<string | null>(null);
  const scenarioId = initialScenarioId ?? fallbackId ?? DEFAULT_SCENARIO_ID;
  const [loadedFor, setLoadedFor] = useState<string | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [weights, setWeights] = useState<Record<WeightKey, number>>(DEFAULT_WEIGHTS);
  // Gewichte, mit denen die aktuelle Rangliste gerechnet wurde (Basis für die Auto-Begründung).
  const [appliedWeights, setAppliedWeights] = useState<Record<WeightKey, number>>(DEFAULT_WEIGHTS);
  const [previousRanks, setPreviousRanks] = useState<Record<string, number>>({});
  const [highlightRanks, setHighlightRanks] = useState(false);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    getScenarios()
      .then((loaded) => {
        setScenarios(loaded);
        if (!loaded.some((s) => s.id === scenarioId) && loaded[0]) setFallbackId(loaded[0].id);
      })
      .catch((err: Error) => setError(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getRequirements(scenarioId), getSignals(scenarioId)])
      .then(([nextRequirements, nextSignals]) => {
        if (cancelled) return;
        setRequirements(nextRequirements);
        setSignals(nextSignals);
        setWeights(weightsFromRequirements(nextRequirements));
        setAppliedWeights(weightsFromRequirements(nextRequirements));
        setPreviousRanks({});
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoadedFor(scenarioId);
      });
    return () => {
      cancelled = true;
    };
  }, [scenarioId]);

  const loading = loadedFor !== scenarioId;
  const signalById = useMemo(() => new Map(signals.map((s) => [s.id, s])), [signals]);
  const selectedScenario = scenarios.find((s) => s.id === scenarioId);

  const conflictTitles = useCallback(
    (requirement: Requirement) =>
      requirement.signal_ids.flatMap((id) =>
        (signalById.get(id)?.conflicts_with ?? []).map((cid) => signalById.get(cid)?.title ?? cid),
      ),
    [signalById],
  );

  async function applyWeights(nextWeights: Weights = weights, why?: string) {
    if (applying) return;
    setApplying(true);
    setError(null);
    const before = Object.fromEntries(requirements.map((req) => [req.id, req.rank]));
    try {
      const reranked = await putWeights(scenarioId, {
        weights: nextWeights,
        actor: PM_ACTOR,
        rationale: why?.trim() || describeWeightChange(appliedWeights, nextWeights),
      });
      setPreviousRanks(before);
      setRequirements(reranked);
      setWeights(weightsFromRequirements(reranked));
      setAppliedWeights(weightsFromRequirements(reranked));
      setHighlightRanks(true);
      setToast(why ? "Re-ranked. Your question is saved as the rationale." : "Re-ranked. Change recorded in the audit trail.");
      window.setTimeout(() => setHighlightRanks(false), 2500);
      window.setTimeout(() => setToast(null), 3500);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setApplying(false);
    }
  }

  return {
    scenarioId, selectedScenario, requirements, weights, setWeights,
    previousRanks, highlightRanks, loading, applying, error, toast,
    conflictTitles, applyWeights,
    // Reset wendet die Standardgewichte wirklich an (mit Eintrag im Prüfpfad), statt nur die Regler zu verschieben.
    // Warum: Ein Reglertest hatte G60-US auf "nur Customer pain" gestellt, danach zeigten alle Top-Scores 100.
    resetWeights: () => applyWeights(DEFAULT_WEIGHTS, "Reset to default weights."),
  };
}
