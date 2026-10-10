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
export const DEMO_RATIONALE = "Demo adjustment: product management is testing a different prioritization focus.";

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
  const [rationale, setRationale] = useState("");
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
        rationale: (why ?? rationale).trim() || DEMO_RATIONALE,
      });
      setPreviousRanks(before);
      setRequirements(reranked);
      setWeights(weightsFromRequirements(reranked));
      setRationale("");
      setHighlightRanks(true);
      setToast("WEIGHTS_CHANGED recorded");
      window.setTimeout(() => setHighlightRanks(false), 2500);
      window.setTimeout(() => setToast(null), 3500);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setApplying(false);
    }
  }

  return {
    scenarioId, selectedScenario, requirements, weights, setWeights, rationale, setRationale,
    previousRanks, highlightRanks, loading, applying, error, toast,
    conflictTitles, applyWeights, resetWeights: () => setWeights(DEFAULT_WEIGHTS),
  };
}
