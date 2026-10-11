import type { Scenario } from "@/src/lib/api";

// Reine Auswahl-Logik für "Compare two markets", getrennt von der Oberfläche, damit sie testbar ist.
// Warum nur dasselbe Modell: Ein Regionsvergleich ist nur fair, wenn dasselbe Auto in beiden Märkten steht
// (z. B. G60 EU gegen G60 US). Modell gegen Modell würde Markt- und Modellunterschiede vermischen.

export interface ComparableModel {
  derivative: string;
  label: string;
  markets: { market: string; scenarioId: string }[];
}

type ScenarioLike = Pick<Scenario, "id" | "derivative" | "market" | "model_name">;

// Alle Modelle mit ihren (verschiedenen) Regionen, in der Reihenfolge der API.
export function groupModels(scenarios: ScenarioLike[]): ComparableModel[] {
  const byModel = new Map<string, ComparableModel>();
  for (const s of scenarios) {
    const model = byModel.get(s.derivative) ?? { derivative: s.derivative, label: s.model_name, markets: [] };
    if (!model.markets.some((m) => m.market === s.market)) model.markets.push({ market: s.market, scenarioId: s.id });
    byModel.set(s.derivative, model);
  }
  return [...byModel.values()];
}

export const isComparable = (model: ComparableModel) => model.markets.length >= 2;

// Nur Modelle mit mindestens zwei verschiedenen Regionen lassen sich vergleichen.
export const comparableModels = (scenarios: ScenarioLike[]) => groupModels(scenarios).filter(isComparable);

// Liefert immer zwei verschiedene Regionen: ungültige oder doppelte Wahl fällt auf die erste freie Region zurück.
// Erwartet mindestens zwei Regionen (garantiert durch comparableModels).
export function pickMarkets(markets: string[], wantedA: string, wantedB: string): [string, string] {
  const a = markets.includes(wantedA) ? wantedA : markets[0];
  const b = markets.includes(wantedB) && wantedB !== a ? wantedB : markets.find((m) => m !== a)!;
  return [a, b];
}
