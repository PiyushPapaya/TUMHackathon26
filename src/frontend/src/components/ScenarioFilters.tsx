"use client";

import type { Scenario } from "@/src/lib/api";

export type ScenarioFilter = { query: string; model: string; market: string };
export const EMPTY_SCENARIO_FILTER: ScenarioFilter = { query: "", model: "", market: "" };

// Lesbarer Name einer Region. Eine Stelle für Modelle-Filter und Marktvergleich, damit beide gleich heißen.
const MARKET_LABELS: Record<string, string> = { EU: "Europe", US: "United States", CN: "China" };
export const marketLabel = (market: string) => MARKET_LABELS[market] ?? market;

export function matchesScenario(scenario: Pick<Scenario, "id" | "model_name" | "market">, filter: ScenarioFilter) {
  return (!filter.model || scenario.model_name === filter.model)
    && (!filter.market || scenario.market === filter.market)
    && `${scenario.id} ${scenario.model_name} ${scenario.market}`.toLowerCase().includes(filter.query.toLowerCase().trim());
}

export function ScenarioFilters({ scenarios, value, onChange }: {
  scenarios: Pick<Scenario, "id" | "model_name" | "market">[];
  value: ScenarioFilter;
  onChange: (value: ScenarioFilter) => void;
}) {
  return <div className="grid items-end gap-3 sm:grid-cols-[2fr_1fr_1fr_auto]">
    <label className="field-label">Search models<input type="search" className="field-control" placeholder="Model or market" value={value.query} onChange={e => onChange({ ...value, query: e.target.value })} /></label>
    <label className="field-label">Model<select aria-label="Model" className="field-control" value={value.model} onChange={e => onChange({ ...value, model: e.target.value })}><option value="">All models</option>{[...new Set(scenarios.map(s => s.model_name))].map(m => <option key={m}>{m}</option>)}</select></label>
    <label className="field-label">Region<select aria-label="Region" className="field-control" value={value.market} onChange={e => onChange({ ...value, market: e.target.value })}><option value="">All regions</option>{[...new Set(scenarios.map(s => s.market))].map(m => <option key={m} value={m}>{marketLabel(m)}</option>)}</select></label>
    <button type="button" className="min-h-11 px-3 text-sm font-semibold text-[var(--blue)] disabled:opacity-40" disabled={!value.query && !value.model && !value.market} onClick={() => onChange(EMPTY_SCENARIO_FILTER)}>Clear filters</button>
  </div>;
}
