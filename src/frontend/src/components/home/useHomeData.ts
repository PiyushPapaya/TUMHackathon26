"use client";

import { useEffect, useState } from "react";
import { getFunnel, getRequirements, getScenarios, type EvidenceLevel, type Funnel, type Scenario } from "@/src/lib/api";
import { DEFAULT_SCENARIO_ID } from "@/src/components/shell/scenarioLabel";

export type HomeData = {
  scenarios: Scenario[];
  funnels: Record<string, Funnel>;
  // Anzahl Anforderungen je Evidenzstufe im Hauptszenario, direkt aus dem Backend gezählt.
  levels: Record<EvidenceLevel, number> | null;
  topTitle: string | null;
  mainId: string;
};

// Alle Zahlen der Startseite kommen aus dem Backend. Es gibt keine erfundenen Werte:
// fehlt das Backend, bleibt `null` und die Seite zeigt ehrlich "–".
export function useHomeData(): HomeData {
  const [data, setData] = useState<HomeData>({ scenarios: [], funnels: {}, levels: null, topTitle: null, mainId: DEFAULT_SCENARIO_ID });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const scenarios = await getScenarios();
        const mainId = scenarios.find((s) => s.id === DEFAULT_SCENARIO_ID)?.id ?? scenarios[0]?.id;
        if (!mainId) return;
        const [funnelList, reqs] = await Promise.all([
          Promise.all(scenarios.map((s) => getFunnel(s.id).catch(() => null))),
          getRequirements(mainId).catch(() => []),
        ]);
        const funnels: Record<string, Funnel> = {};
        scenarios.forEach((s, i) => {
          const f = funnelList[i];
          if (f) funnels[s.id] = f;
        });
        const levels: Record<EvidenceLevel, number> = { A: 0, B: 0, C: 0, D: 0 };
        reqs.forEach((r) => (levels[r.evidence_level] += 1));
        if (!cancelled) {
          setData({ scenarios, funnels, levels: reqs.length ? levels : null, topTitle: reqs[0]?.title ?? null, mainId });
        }
      } catch {
        /* Backend aus: Seite bleibt mit "–" nutzbar */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}
