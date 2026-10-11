"use client";

import { useState } from "react";
import { getScenarios } from "@/src/lib/api";
import { getCompare } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { ErrorNote, Loading } from "@/src/components/ui/PageHeader";
import { categoryLabel } from "@/src/components/badges";
import { marketLabel } from "@/src/components/ScenarioFilters";
import { PortfolioCellLink } from "./PortfolioCellLink";
import { groupModels, isComparable, pickMarkets } from "./compareModels";

const SELECT = "h-11 border border-[var(--hairline)] bg-white px-3 text-sm font-normal normal-case tracking-normal text-[var(--ink)] disabled:opacity-40";
const LABEL = "grid gap-1 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]";

function CompareResult({ a, b }: { a: string; b: string }) {
  const view = useLoad(`${a}|${b}`, () => getCompare(a, b));
  return (
    <>
      {view.error && <ErrorNote message={view.error} />}
      {view.loading && <Loading what="comparison" />}
      {view.data && (
        <ul className="mt-6 border-t border-[var(--hairline)]">
          {view.data.rows.map((r) => (
            <li key={r.category} className="grid items-center gap-4 border-b border-[var(--hairline)] py-4 md:grid-cols-[200px_1fr_1fr_1.2fr]">
              <span className="text-sm font-semibold">{categoryLabel(r.category)}</span>
              <PortfolioCellLink cell={r.a} />
              <PortfolioCellLink cell={r.b} />
              <span className="text-sm text-[var(--grey-500)]">{r.sentence}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

// Regionsvergleich: erst ein Modell, dann zwei verschiedene Regionen dieses Modells.
// Warum: Nur dasselbe Auto in zwei Märkten zeigt echte Marktunterschiede (z. B. G60 EU gegen G60 US).
// Modelle mit nur einer Region bleiben sichtbar, sind aber nicht wählbar, damit klar ist, warum sie fehlen.
export function MarketCompare() {
  const scenarios = useLoad("compare-scenarios", getScenarios);
  const [wantedModel, setWantedModel] = useState("");
  const [wantedA, setWantedA] = useState("");
  const [wantedB, setWantedB] = useState("");

  const models = groupModels(scenarios.data ?? []);
  const comparable = models.filter(isComparable);
  const model = comparable.find((m) => m.derivative === wantedModel) ?? comparable[0];
  const markets = model?.markets.map((m) => m.market) ?? [];
  const [marketA, marketB] = model ? pickMarkets(markets, wantedA, wantedB) : ["", ""];
  const scenarioOf = (market: string) => model?.markets.find((m) => m.market === market)?.scenarioId;

  function chooseModel(derivative: string) {
    // Neues Modell: Regionen zurücksetzen, pickMarkets nimmt dann die ersten zwei.
    setWantedModel(derivative);
    setWantedA("");
    setWantedB("");
  }

  const regionSelect = (label: string, value: string, other: string, onChange: (v: string) => void) => (
    <label className={LABEL}>
      {label}
      <select className={SELECT} value={value} disabled={!model} onChange={(e) => onChange(e.target.value)}>
        {markets.map((m) => (
          // Die Region der anderen Seite ist gesperrt: dieselbe Region zweimal wäre kein Vergleich.
          <option key={m} value={m} disabled={m === other}>{marketLabel(m)}</option>
        ))}
      </select>
    </label>
  );

  return (
    <section className="mt-16">
      <h2 className="text-3xl font-light">Compare two markets.</h2>
      <p className="mt-2 max-w-2xl text-sm text-[var(--grey-500)]">Same model, two regions. Only models sold in more than one region can be compared.</p>
      {scenarios.error && <ErrorNote message={scenarios.error} />}
      {scenarios.loading && <Loading what="models" />}
      {scenarios.data && (
        <>
          <div className="mt-6 flex flex-wrap gap-4">
            <label className={LABEL}>
              Model
              <select className={SELECT} value={model?.derivative ?? ""} disabled={!model} onChange={(e) => chooseModel(e.target.value)}>
                {!model && <option value="">No model in several regions</option>}
                {models.map((m) => (
                  <option key={m.derivative} value={m.derivative} disabled={!isComparable(m)}>
                    {m.label}{isComparable(m) ? "" : ` – only ${marketLabel(m.markets[0].market)}`}
                  </option>
                ))}
              </select>
            </label>
            {/* Beim Ändern einer Seite die andere festhalten, sonst könnte sie bei drei Regionen mitspringen. */}
            {regionSelect("Region A", marketA, marketB, (v) => { setWantedA(v); setWantedB(marketB); })}
            {regionSelect("Region B", marketB, marketA, (v) => { setWantedB(v); setWantedA(marketA); })}
          </div>
          {!model && (
            <p className="mt-6 border-y border-[var(--hairline)] py-8 text-sm text-[var(--grey-500)]">
              No model has data for more than one region yet, so there is nothing to compare.
            </p>
          )}
          {model && <CompareResult a={scenarioOf(marketA)!} b={scenarioOf(marketB)!} />}
        </>
      )}
    </section>
  );
}
