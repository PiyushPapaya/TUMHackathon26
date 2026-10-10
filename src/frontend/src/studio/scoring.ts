/**
 * Score-Rechnung im Browser für die Werkbank. Gleiche Formel wie
 * src/backend/requirements_engine/scoring.py, damit Zahlen im UI und im Backend übereinstimmen:
 * Score = Summe(Wert × normiertes Gewicht × 100) × Sicherheit der Evidenzstufe.
 */
import type { EvidenceLevel, Requirement } from "@/src/lib/api";

export const FACTORS = [
  { key: "customer_pain", label: "Customer pain", assumption: false },
  { key: "reach", label: "Reach", assumption: false },
  { key: "satisfaction_gap", label: "Satisfaction gap", assumption: false },
  { key: "competitive_pressure", label: "Competitive pressure", assumption: false },
  { key: "future_relevance", label: "Future relevance", assumption: true },
  { key: "effort_inverse", label: "Low effort", assumption: false },
] as const;

export type FactorKey = (typeof FACTORS)[number]["key"];
export type Weights = Record<FactorKey, number>;

export const CONFIDENCE: Record<EvidenceLevel, number> = { A: 1, B: 0.85, C: 0.7, D: 0.5 };

const round1 = (n: number) => Math.round(n * 10) / 10;

/** Aktuelle (normierte) Gewichte aus der Aufschlüsselung lesen; das Backend liefert sie mit. */
export function currentWeights(req: Requirement | undefined): Weights {
  const w = {} as Weights;
  for (const f of FACTORS) w[f.key] = req?.score_breakdown[f.key]?.weight ?? 0;
  return w;
}

/** Score ohne die ausgeschalteten Faktoren; die übrigen Gewichte werden neu auf 1 normiert (wie normalize_weights). */
export function scoreWithout(req: Requirement, excluded: ReadonlySet<FactorKey>): number {
  let weighted = 0;
  let weightSum = 0;
  for (const f of FACTORS) {
    const part = req.score_breakdown[f.key];
    if (!part || excluded.has(f.key)) continue;
    weighted += part.value * part.weight;
    weightSum += part.weight;
  }
  if (weightSum <= 0) return 0;
  return round1((weighted / weightSum) * 100 * CONFIDENCE[req.evidence_level]);
}

/**
 * Duell → Gewichte: Gewinnt A gegen B, bekommt jeder Faktor, bei dem A besser ist, den Vorsprung gutgeschrieben.
 * Faktoren, die bei deinen Siegern immer vorne lagen, zählen dir offenbar mehr.
 * Ein kleiner Anteil der bisherigen Gewichte bleibt als Startwert, damit wenige Runden nichts auf null setzen.
 */
export function weightsFromDuels(wins: { winner: Requirement; loser: Requirement }[], start: Weights): Weights {
  const tally = {} as Weights;
  for (const f of FACTORS) tally[f.key] = 0;
  for (const { winner, loser } of wins) {
    for (const f of FACTORS) {
      const lead = (winner.score_breakdown[f.key]?.value ?? 0) - (loser.score_breakdown[f.key]?.value ?? 0);
      if (lead > 0) tally[f.key] += lead;
    }
  }
  const tallySum = Object.values(tally).reduce((a, b) => a + b, 0);
  const result = {} as Weights;
  for (const f of FACTORS) {
    const learned = tallySum > 0 ? tally[f.key] / tallySum : start[f.key];
    result[f.key] = 0.25 * start[f.key] + 0.75 * learned;
  }
  const total = Object.values(result).reduce((a, b) => a + b, 0) || 1;
  for (const f of FACTORS) result[f.key] = Math.round((result[f.key] / total) * 1000) / 1000;
  return result;
}

/** Alle Paare der besten Anforderungen, deterministisch gemischt (kein Zufall, damit die Demo gleich abläuft). */
export function duelPairs(reqs: Requirement[], rounds: number): [Requirement, Requirement][] {
  const pool = reqs.slice(0, 8);
  const pairs: [Requirement, Requirement][] = [];
  for (let gap = 1; gap < pool.length; gap++) {
    for (let i = 0; i + gap < pool.length; i++) pairs.push([pool[i], pool[i + gap]]);
  }
  // Jedes zweite Paar tauschen, damit der höher Gerankte nicht immer links steht.
  return pairs.slice(0, rounds).map((p, i) => (i % 2 ? [p[1], p[0]] : p));
}
