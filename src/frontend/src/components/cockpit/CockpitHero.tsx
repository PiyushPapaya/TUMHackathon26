"use client";

import type { Scenario } from "@/src/lib/api";
import { getExportUrl } from "@/src/lib/api";
import { getMemoUrl } from "@/src/lib/insights";
import { Button } from "@/src/components/ui/Button";
import { Eyebrow, SectionHeading } from "@/src/components/ui/Typography";
import { scenarioLabel } from "@/src/components/shell/scenarioLabel";
import { useAssistant } from "@/src/components/shell/assistant/AssistantProvider";
import { Icon } from "@/src/components/ui/Icon";

export function CockpitHero({ scenario, scenarioId }: { scenario?: Scenario; scenarioId: string }) {
  const assistant = useAssistant();
  const n = scenario?.headline_numbers;
  const stats = n
    ? [
        [n.evidence.toLocaleString("en-US"), "customer voices"],
        [String(n.signals), "findings"],
        [String(n.requirements), "requirements"],
      ]
    : [];
  return (
    <header className="flex flex-wrap items-end justify-between gap-8 pb-10">
      <div>
        {/* Guide oben links: Wer das Cockpit zum ersten Mal sieht, findet hier die fünf Schritte, ohne die Seite zu verlassen. */}
        <button
          type="button"
          onClick={() => assistant.open("guide")}
          className="mb-6 inline-flex items-center gap-2 border border-[var(--hairline)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] transition-colors hover:border-[var(--ink)]"
        >
          <Icon name="evidence" size={14} /> How to use the cockpit
        </button>
        <Eyebrow>{scenario ? scenarioLabel(scenario) : "Signal2Spec"}</Eyebrow>
        <SectionHeading as="h1" className="mt-3">PM cockpit.</SectionHeading>
        <p className="mt-4 max-w-xl text-[var(--grey-500)]">
          Decide what the AI proposes, why it proposes it, and how reliable the evidence is.
        </p>
        <dl className="mt-8 flex flex-wrap gap-10">
          {stats.map(([value, label]) => (
            <div key={label}>
              <dd className="text-3xl font-light tabular-nums text-[var(--ink)]">{value}</dd>
              <dt className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">{label}</dt>
            </div>
          ))}
        </dl>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button variant="outline" href={getMemoUrl(scenarioId)} external>Decision memo</Button>
        <Button variant="outline" href={getExportUrl(scenarioId)} external>Export CSV</Button>
      </div>
    </header>
  );
}
