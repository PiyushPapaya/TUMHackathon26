/**
 * Alle Abschnitte der Detailseite (Ticket D3) für eine bereits geladene Anforderung.
 * Eigene Datei, damit app/requirements/[id]/page.tsx nur Laden/Fehler regelt und beide
 * Dateien unter ~200 Zeilen bleiben (Jury-Review kappt danach).
 */
import type { Evidence, RequirementDetail } from "@/src/lib/api";
import { categoryLabel, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreWaterfall } from "@/src/components/ScoreWaterfall";
import { FindingCard } from "@/src/components/FindingCard";
import { AssumptionItem, OfferCheckBox } from "@/src/components/DetailBlocks";

export function RequirementDetailView({
  detail,
  evidenceBySignal,
}: {
  detail: RequirementDetail;
  evidenceBySignal: Map<string, Evidence[]>;
}) {
  const { requirement } = detail;

  return (
    <>
      <header className="mt-4">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold text-[#0b1f3a] dark:text-zinc-100">{requirement.title}</h1>
          <StatusBadge status={requirement.status} />
          <EvidenceBadge level={requirement.evidence_level} reason={requirement.rationale} />
        </div>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">{requirement.rationale}</p>
        <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">
          {categoryLabel(requirement.category)} · Rank #{requirement.rank} · Effort {requirement.effort}
        </p>
      </header>

      <section className="mt-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Description</h2>
        <p className="mt-2 text-[#0b1f3a] dark:text-zinc-200">{requirement.description}</p>
      </section>

      <section className="mt-4 rounded-lg border-l-4 border-blue-600 bg-blue-50 p-4 dark:border-blue-500 dark:bg-blue-950">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-300">
          Acceptance criterion
        </p>
        <p className="mt-1 text-[#0b1f3a] dark:text-zinc-200">{requirement.acceptance_criterion}</p>
      </section>

      <section className="mt-8">
        <ScoreWaterfall
          scoreBreakdown={requirement.score_breakdown}
          evidenceLevel={requirement.evidence_level}
          finalScore={requirement.score}
        />
      </section>

      <section className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-zinc-300 bg-surface p-4 dark:border-zinc-700">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Evidence</h2>
          <div className="mt-3 space-y-3">
            {detail.signals.length === 0 && (
              <p className="text-sm text-zinc-400 dark:text-zinc-500">No findings linked.</p>
            )}
            {detail.signals.map((signal) => (
              <FindingCard
                key={signal.id}
                signal={signal}
                evidence={evidenceBySignal.get(signal.id) ?? []}
              />
            ))}
          </div>
        </div>

        <div className="rounded-lg border-2 border-dashed border-zinc-300 bg-surface p-4 dark:border-zinc-700">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Assumptions &amp; uncertainties
          </h2>
          <ul className="mt-3 space-y-2">
            {requirement.assumptions.map((text, i) => (
              <AssumptionItem key={`assumption-${i}`} label="Assumption" text={text} />
            ))}
            {requirement.uncertainties.map((text, i) => (
              <AssumptionItem key={`uncertainty-${i}`} label="Uncertainty" text={text} />
            ))}
            {requirement.assumptions.length === 0 && requirement.uncertainties.length === 0 && (
              <p className="text-sm text-zinc-400 dark:text-zinc-500">No assumptions or uncertainties recorded.</p>
            )}
          </ul>
        </div>
      </section>

      <section className="mt-8">
        <OfferCheckBox offerCheck={requirement.offer_check} />
      </section>
    </>
  );
}
