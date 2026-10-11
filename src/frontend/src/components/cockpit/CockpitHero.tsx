"use client";

import type { Scenario } from "@/src/lib/api";
import { getExportUrl } from "@/src/lib/api";
import { getMemoUrl } from "@/src/lib/insights";
import { Button } from "@/src/components/ui/Button";
import { Eyebrow } from "@/src/components/ui/Typography";
import { scenarioLabel } from "@/src/components/shell/scenarioLabel";
import { useAssistant } from "@/src/components/shell/assistant/AssistantProvider";
import { Icon } from "@/src/components/ui/Icon";

export function CockpitHero({ scenario, scenarioId }: { scenario?: Scenario; scenarioId: string }) {
  const assistant = useAssistant();
  const n = scenario?.headline_numbers;
  const stats = n
    ? [
        [(scenario?.data_coverage?.feedback ?? n.evidence).toLocaleString("en-US"), scenario?.data_coverage ? "customer feedback" : "evidence records"],
        [String(n.signals), "findings"],
        [String(n.requirements), "requirements"],
      ]
    : [];
  // Kompakter Kopf: Titel links, Zahlen + Exporte rechts. So stehen Ask-Feld und Rangliste ohne Scrollen im Bild.
  return (
    <header className="grid gap-6 pb-8 lg:grid-cols-[1fr_auto] lg:items-end">
      <div>
        <div className="flex flex-wrap items-center gap-4">
          {/* Guide oben links: Wer das Cockpit zum ersten Mal sieht, findet hier die fünf Schritte, ohne die Seite zu verlassen. */}
          <button
            type="button"
            onClick={() => assistant.open("guide")}
            className="inline-flex items-center gap-2 border border-[var(--hairline)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--ink)]"
          >
            <Icon name="evidence" size={14} /> Guide
          </button>
          <Eyebrow>{scenario ? scenarioLabel(scenario) : "ReSpec"}</Eyebrow>
        </div>
        <h1 className="mt-3 text-3xl font-medium">Ranked requirements</h1>
        <p className="mt-2 max-w-xl text-sm text-[var(--grey-500)]">What the successor of this car should do better, ranked by customer evidence. Click a row for the reasons.</p>
      </div>
      <div className="grid gap-5 lg:justify-items-end">
        <dl className="flex flex-wrap gap-8">
          {stats.map(([value, label]) => (
            <div key={label} className="lg:text-right">
              <dd className="text-3xl font-light tabular-nums text-[var(--ink)]">{value}</dd>
              <dt className="text-[11px] uppercase tracking-[0.12em] text-[var(--grey-500)]">{label}</dt>
            </div>
          ))}
        </dl>
        <div className="flex flex-wrap gap-3">
          <Button variant="outline" href={getMemoUrl(scenarioId)} external className="h-11! px-5! text-sm!">Decision memo</Button>
          <Button variant="outline" href={getExportUrl(scenarioId)} external className="h-11! px-5! text-sm!">Export CSV</Button>
        </div>
      </div>
    </header>
  );
}
