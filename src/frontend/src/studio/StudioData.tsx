"use client";

/**
 * Gemeinsame Daten für alle Werkbank-Seiten: Szenario, Anforderungen, Befunde und alle Belege.
 * Warum ein Context: Jede Seite braucht dieselben Daten, und beim Wechsel zwischen den Werkzeugen
 * soll nichts neu laden. Belege gibt es nur über die Detail-Endpunkte, darum lädt `loadAll` sie einmal pro Szenario.
 */
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  getRequirementDetail,
  getRequirements,
  getScenarios,
  getSignals,
  type Evidence,
  type Requirement,
  type Scenario,
  type Signal,
} from "@/src/lib/api";

export const PM_ACTOR = "pm.demo";

interface StudioState {
  scenarios: Scenario[];
  scenarioId: string;
  setScenarioId: (id: string) => void;
  requirements: Requirement[];
  signals: Signal[];
  evidenceById: Map<string, Evidence>;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

const StudioContext = createContext<StudioState | null>(null);

export function useStudio(): StudioState {
  const state = useContext(StudioContext);
  if (!state) throw new Error("useStudio must be used inside the studio layout");
  return state;
}

export function StudioDataProvider({ children }: { children: React.ReactNode }) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState("G60-US");
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [evidenceById, setEvidenceById] = useState<Map<string, Evidence>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAll = useCallback(async (id: string) => {
    const [reqs, sigs] = await Promise.all([getRequirements(id), getSignals(id)]);
    const details = await Promise.all(reqs.map((r) => getRequirementDetail(r.id)));
    const evidence = new Map<string, Evidence>();
    for (const d of details) for (const e of d.evidence) evidence.set(e.id, e);
    return { reqs, sigs, evidence };
  }, []);

  const reload = useCallback(async () => {
    try {
      const { reqs, sigs, evidence } = await loadAll(scenarioId);
      setRequirements(reqs);
      setSignals(sigs);
      setEvidenceById(evidence);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }, [loadAll, scenarioId]);

  useEffect(() => {
    getScenarios()
      .then(setScenarios)
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const { reqs, sigs, evidence } = await loadAll(scenarioId);
        if (cancelled) return;
        setRequirements(reqs);
        setSignals(sigs);
        setEvidenceById(evidence);
        setError(null);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [loadAll, scenarioId]);

  return (
    <StudioContext.Provider
      value={{ scenarios, scenarioId, setScenarioId, requirements, signals, evidenceById, loading, error, reload }}
    >
      {children}
    </StudioContext.Provider>
  );
}
