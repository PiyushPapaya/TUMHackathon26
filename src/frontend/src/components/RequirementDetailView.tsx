"use client";

import type { Evidence, ExplainView } from "@/src/lib/api";
import { categoryLabel, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreWaterfall } from "@/src/components/ScoreWaterfall";
import { FindingCard } from "@/src/components/FindingCard";
import { AssumptionItem, OfferCheckBox } from "@/src/components/DetailBlocks";
import { DecisionPanel } from "@/src/components/DecisionPanel";
import { AuditTrail } from "@/src/components/AuditTrail";

function numberOrDash(value: number | null | undefined, suffix = "") {
  return typeof value === "number" ? `${value.toLocaleString("en-US")}${suffix}` : "not available";
}

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
  const scoreSource = requirement.signal_ids.length
    ? `${requirement.signal_ids.length} linked findings`
    : "No linked findings";

  return (
    <div className="grid gap-8">
      <header className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-6">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="max-w-4xl text-2xl font-semibold leading-tight text-foreground">
            {requirement.title}
          </h1>
          <StatusBadge status={requirement.status} />
          <EvidenceBadge level={requirement.evidence_level} reason={requirement.rationale} />
        </div>
        <p className="mt-3 max-w-3xl text-sm text-zinc-700 dark:text-zinc-300">{requirement.rationale}</p>
        <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
          {categoryLabel(requirement.category)} · Rank #{requirement.rank} · Effort {requirement.effort} · Score{" "}
          {requirement.score.toFixed(1)} from {scoreSource}
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Description</h2>
          <p className="mt-2 text-foreground">{requirement.description}</p>
        </div>
        <div className="rounded-lg border border-accent/30 dark:border-accent/40 bg-accent/5 dark:bg-accent/10 p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-accent-hover dark:text-accent">
            Acceptance criterion
          </p>
          <p className="mt-2 font-semibold text-foreground">{requirement.acceptance_criterion}</p>
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

      {(detail.robustness_sentence || business) && (
        <section className="grid gap-4 lg:grid-cols-2">
          {detail.robustness_sentence && (
            <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Robustness</h2>
              <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">{detail.robustness_sentence}</p>
            </div>
          )}
          {business && (
            <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Business context</h2>
              <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
                {numberOrDash(business.volume_2025)} vehicles in 2025, {numberOrDash(business.volume_2030)} in 2030,
                growth {numberOrDash(business.growth_pct, "%")}. {business.note}
              </p>
            </div>
          )}
        </section>
      )}

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-zinc-300 dark:border-zinc-700 bg-surface p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Evidence</h2>
          <div className="mt-4 space-y-3">
            {detail.signals.length === 0 && (
              <p className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm text-zinc-500 dark:text-zinc-400">
                No findings linked.
              </p>
            )}
            {detail.signals.map((signal) => (
              <div id={`signal-${signal.id}`} key={signal.id}>
                <FindingCard signal={signal} evidence={evidenceBySignal.get(signal.id) ?? []} />
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border-2 border-dashed border-zinc-300 dark:border-zinc-700 bg-surface p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Assumptions & uncertainties
          </h2>
          <ul className="mt-4 space-y-2">
            {requirement.assumptions.map((text, i) => (
              <AssumptionItem key={`assumption-${i}`} label="Assumption" text={text} />
            ))}
            {requirement.uncertainties.map((text, i) => (
              <AssumptionItem key={`uncertainty-${i}`} label="Uncertainty" text={text} />
            ))}
            {conflicts.map((conflict, i) => (
              <AssumptionItem key={`conflict-${i}`} label="Conflicting evidence" text={conflict.statement} />
            ))}
            {requirement.assumptions.length === 0 && requirement.uncertainties.length === 0 && conflicts.length === 0 && (
              <li className="rounded-sm border border-dashed border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm text-zinc-500 dark:text-zinc-400">
                No assumptions, uncertainties, or conflicts recorded.
              </li>
            )}
          </ul>
        </div>
      </section>

      {detail.web_sources && detail.web_sources.length > 0 && (
        <section className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Web sources</h2>
          <div className="mt-3 grid gap-3">
            {detail.web_sources.map((source) => (
              <article key={source.id} id={`evidence-${source.id}`} className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-foreground">{source.publisher}</span>
                  <span className="rounded-full border border-zinc-300 dark:border-zinc-700 px-2 py-0.5 text-xs font-semibold text-zinc-600 dark:text-zinc-400">
                    trust: {source.trust}
                  </span>
                  {source.url && (
                    <a className="font-semibold text-accent-hover dark:text-accent underline underline-offset-2" href={source.url} target="_blank" rel="noopener noreferrer">
                      Source link
                    </a>
                  )}
                </div>
                <p className="mt-2 text-zinc-700 dark:text-zinc-300">{source.text}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      <OfferCheckBox offerCheck={requirement.offer_check} />
      <DecisionPanel requirement={requirement} onChanged={onRefresh} />

      <section className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Requirement audit trail</h2>
        <div className="mt-4">
          <AuditTrail requirementId={requirement.id} compact />
        </div>
      </section>
    </div>
  );
}
