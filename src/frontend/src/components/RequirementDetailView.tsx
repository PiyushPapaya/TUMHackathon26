"use client";

import type { Evidence, ExplainView } from "@/src/lib/api";
import { categoryLabel, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreWaterfall } from "@/src/components/ScoreWaterfall";
import { FindingCard } from "@/src/components/FindingCard";
import { AssumptionItem, OfferCheckBox } from "@/src/components/DetailBlocks";
import { DecisionPanel } from "@/src/components/DecisionPanel";
import { AuditTrail } from "@/src/components/AuditTrail";

const H2 = "text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]";

function numberOrDash(value: number | null | undefined, suffix = "") {
  return typeof value === "number" ? `${value.toLocaleString("en-US")}${suffix}` : "not available";
}

// Reihenfolge folgt dem Demo-Satz "Was ist es, wer sagt das, ich entscheide":
// Kopf → Kundenstimmen links + Entscheidung rechts (ohne Scrollen) → Score-Logik → Annahmen → Zusatzkontext zugeklappt.
export function RequirementDetailView({
  detail,
  evidenceBySignal,
  ignoreAssumptions,
  onToggleIgnoreAssumptions,
  onRefresh,
}: {
  detail: ExplainView;
  evidenceBySignal: Map<string, Evidence[]>;
  ignoreAssumptions: boolean;
  onToggleIgnoreAssumptions: (value: boolean) => void;
  onRefresh: () => Promise<void>;
}) {
  const { requirement } = detail;
  const business = detail.business ?? requirement.business;
  const conflicts = detail.conflicts ?? requirement.segment_conflicts ?? [];
  const webSources = detail.web_sources ?? [];
  const hasMoreContext = Boolean(detail.robustness_sentence || business || webSources.length || requirement.offer_check);

  return (
    <div className="grid gap-12">
      <header className="grid gap-8 border-b border-[var(--hairline)] pb-10 lg:grid-cols-[1.5fr_1fr]">
        <div>
          <p className={H2}>
            Rank {requirement.rank} · {categoryLabel(requirement.category)} · Score {requirement.score.toFixed(1)}
          </p>
          <h1 className="mt-4 text-4xl font-light leading-tight tracking-tight text-[var(--ink)] sm:text-5xl">{requirement.title}</h1>
          <div className="mt-5 flex flex-wrap items-center gap-4">
            <EvidenceBadge level={requirement.evidence_level} reason={requirement.rationale} />
            <StatusBadge status={requirement.status} />
          </div>
          <p className="mt-5 max-w-2xl text-[var(--grey-500)]">{requirement.rationale}</p>
        </div>
        <div className="h-fit border-l-2 border-[var(--blue)] bg-[var(--grey-100)] p-6">
          <p className={H2}>Acceptance criterion</p>
          <p className="mt-3 text-lg font-light text-[var(--ink)]">{requirement.acceptance_criterion}</p>
          <p className="mt-4 text-sm text-[var(--grey-500)]">{requirement.description}</p>
        </div>
      </header>

      <section className="grid gap-10 lg:grid-cols-[1.3fr_1fr]">
        <div>
          <h2 className={H2}>What customers say · {detail.signals.length} findings</h2>
          <div className="mt-4 space-y-3">
            {detail.signals.length === 0 && <p className="border border-[var(--hairline)] p-3 text-sm text-[var(--grey-500)]">No findings linked.</p>}
            {detail.signals.map((signal) => (
              <div id={`signal-${signal.id}`} key={signal.id}>
                <FindingCard signal={signal} evidence={evidenceBySignal.get(signal.id) ?? []} />
              </div>
            ))}
          </div>
        </div>
        <div className="h-fit lg:sticky lg:top-24">
          <DecisionPanel requirement={requirement} onChanged={onRefresh} />
        </div>
      </section>

      <ScoreWaterfall
        scoreBreakdown={requirement.score_breakdown}
        evidenceLevel={requirement.evidence_level}
        finalScore={requirement.score}
        waterfall={detail.waterfall}
        ignoreAssumptions={ignoreAssumptions}
        onToggleIgnoreAssumptions={onToggleIgnoreAssumptions}
      />

      <section>
        <h2 className={H2}>Assumptions and open questions</h2>
        <ul className="mt-4 grid gap-2 md:grid-cols-2">
          {requirement.assumptions.map((text, i) => <AssumptionItem key={`a-${i}`} label="Assumption" text={text} />)}
          {requirement.uncertainties.map((text, i) => <AssumptionItem key={`u-${i}`} label="Uncertainty" text={text} />)}
          {conflicts.map((conflict, i) => <AssumptionItem key={`c-${i}`} label="Conflicting evidence" text={conflict.statement} />)}
          {requirement.assumptions.length === 0 && requirement.uncertainties.length === 0 && conflicts.length === 0 && (
            <li className="border border-dashed border-[var(--hairline)] p-3 text-sm text-[var(--grey-500)]">No assumptions, uncertainties, or conflicts recorded.</li>
          )}
        </ul>
      </section>

      {hasMoreContext && (
        <details className="group border-y border-[var(--hairline)]">
          <summary className="cursor-pointer list-none py-4 text-sm font-semibold text-[var(--ink)] hover:text-[var(--blue)]">
            More context: robustness, business volume, web sources <span className="text-[var(--grey-500)] group-open:hidden">+</span>
          </summary>
          <div className="grid gap-6 pb-6">
            {detail.robustness_sentence && <p className="text-sm text-[var(--grey-500)]"><b className="text-[var(--ink)]">Robustness.</b> {detail.robustness_sentence}</p>}
            {business && (
              <p className="text-sm text-[var(--grey-500)]">
                <b className="text-[var(--ink)]">Business.</b> {numberOrDash(business.volume_2025)} vehicles in 2025, {numberOrDash(business.volume_2030)} in 2030,
                growth {numberOrDash(business.growth_pct, "%")}. {business.note}
              </p>
            )}
            {webSources.map((source) => (
              <article key={source.id} id={`evidence-${source.id}`} className="border border-[var(--hairline)] p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-[var(--ink)]">{source.publisher}</span>
                  <span className="border border-[var(--hairline)] px-2 py-0.5 text-xs text-[var(--grey-500)]">trust: {source.trust}</span>
                  {source.url && (
                    <a className="font-semibold text-[var(--blue)] underline underline-offset-2" href={source.url} target="_blank" rel="noopener noreferrer">Source link</a>
                  )}
                </div>
                <p className="mt-2 text-[var(--grey-500)]">{source.text}</p>
              </article>
            ))}
            <OfferCheckBox offerCheck={requirement.offer_check} />
          </div>
        </details>
      )}

      <section>
        <h2 className={H2}>Decision record</h2>
        <div className="mt-4"><AuditTrail requirementId={requirement.id} compact /></div>
      </section>
    </div>
  );
}
