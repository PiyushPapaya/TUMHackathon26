"use client";

import type { Evidence, ExplainView } from "@/src/lib/api";
import { categoryLabel, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreWaterfall } from "@/src/components/ScoreWaterfall";
import { FindingCard } from "@/src/components/FindingCard";
import { AssumptionItem, OfferCheckBox, SegmentConflictCard } from "@/src/components/DetailBlocks";
import { DecisionPanel } from "@/src/components/DecisionPanel";
import { AuditTrail } from "@/src/components/AuditTrail";
import { chartFactorSteps, rationaleWithChartPoints } from "@/src/lib/scoreSteps";

const H2 = "text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]";

function numberOrDash(value: number | null | undefined, suffix = "") {
  return typeof value === "number" ? `${value.toLocaleString("en-US", { maximumFractionDigits: 1 })}${suffix}` : "not available";
}

// Keep the proposal, priority chart and decision together before the evidence details.
export function RequirementDetailView({
  detail,
  evidenceBySignal,
  ignoreAssumptions,
  onToggleIgnoreAssumptions,
  onRefresh,
  scenarioId,
}: {
  detail: ExplainView;
  evidenceBySignal: Map<string, Evidence[]>;
  ignoreAssumptions: boolean;
  onToggleIgnoreAssumptions: (value: boolean) => void;
  onRefresh: () => Promise<void>;
  scenarioId: string;
}) {
  const { requirement } = detail;
  const outlook = detail.outlook ?? requirement.outlook;
  const business = detail.business ?? requirement.business;
  const conflicts = detail.conflicts ?? requirement.segment_conflicts ?? [];
  const webSources = detail.web_sources ?? [];
  // Nur Belege, die oben in einer FindingCard stehen, haben einen Anker; Konflikt-Links zeigen nur dorthin.
  const visibleEvidenceIds = new Set([...evidenceBySignal.values()].flat().map((e) => e.id));
  // Points in the text come from the same bars as the chart, also after reweighting or in the preview.
  const rationale = rationaleWithChartPoints(requirement.rationale, chartFactorSteps(requirement.score_breakdown, detail.waterfall, ignoreAssumptions));
  const hasMoreContext = Boolean(detail.robustness_sentence || business || webSources.length || requirement.offer_check);

  return (
    <div className="grid gap-8">
      <header className="requirement-summary border-b border-[var(--hairline)] pb-6">
        <div className="summary-intro min-w-0">
          <p className={H2}>
            Rank {requirement.rank} · {categoryLabel(requirement.category)} · Score {requirement.score.toFixed(1)}
          </p>
          <h1 className="mt-3 text-2xl font-medium leading-tight text-[var(--ink)] sm:text-3xl">{requirement.title}</h1>
          <div className="mt-5 flex flex-wrap items-center gap-4">
            <EvidenceBadge level={requirement.evidence_level} reason={rationale} />
            <StatusBadge status={requirement.status} />
          </div>
          <p className="mt-5 max-w-2xl text-[var(--grey-500)]">{rationale}</p>
          {/* Key facts at a glance: effort, horizon and market size before any detail. Volume is context, not part of the score. */}
          <dl className="mt-5 grid grid-cols-2 gap-4 border-y border-[var(--hairline)] py-4 text-sm sm:grid-cols-4">
            <div><dt className="text-xs text-[var(--grey-500)]">Engineering effort</dt><dd className="mt-1 font-semibold">{({ S: "Small", M: "Medium", L: "Large" })[requirement.effort]}</dd><dd className="text-xs text-[var(--grey-500)]">preliminary estimate</dd></div>
            <div><dt className="text-xs text-[var(--grey-500)]">Planning horizon</dt><dd className="mt-1 font-semibold">{requirement.horizon === "next_gen" ? "Next generation" : "Current product"}</dd></div>
            <div><dt className="text-xs text-[var(--grey-500)]">Market volume 2030</dt><dd className="mt-1 font-semibold tabular-nums">{numberOrDash(business?.volume_2030)}</dd><dd className="text-xs text-[var(--grey-500)]">projection, vehicles</dd></div>
            <div><dt className="text-xs text-[var(--grey-500)]">Growth 2025 to 2030</dt><dd className="mt-1 font-semibold tabular-nums">{numberOrDash(business?.growth_pct, "%")}</dd></div>
          </dl>
          {outlook && (
            <div className="mt-4 text-sm">
              <p className="font-semibold text-[var(--ink)]">Outlook {outlook.successor_year}: {outlook.direction} <span className="font-normal text-[var(--grey-500)]">· Assumption</span></p>
              <p className="mt-1 text-[var(--grey-500)]">{outlook.sentence}</p>
            </div>
          )}
        </div>
        <div className="summary-chart min-w-0"><ScoreWaterfall scoreBreakdown={requirement.score_breakdown} evidenceLevel={requirement.evidence_level} finalScore={requirement.score} waterfall={detail.waterfall} ignoreAssumptions={ignoreAssumptions} onToggleIgnoreAssumptions={onToggleIgnoreAssumptions} /></div>
        <div className="summary-criterion min-w-0 border-l-2 border-[var(--blue)] bg-[var(--grey-100)] p-4">
          <p className={H2}>Success criterion</p>
          <p className="mt-2 text-sm font-medium text-[var(--ink)]">{requirement.acceptance_criterion}</p>
          <p className="mt-3 text-xs text-[var(--grey-500)]">Before approval, review the observable outcome, test procedure, pass threshold and participant sample. Relative targets also need a measured baseline under the same conditions. Numbers alone do not prove measurability.</p>
          <p className="mt-3 text-sm text-[var(--grey-500)]">{requirement.description}</p>
        </div>
        <div className="summary-decision min-w-0"><DecisionPanel requirement={requirement} onChanged={onRefresh} /></div>
      </header>

      <section>
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
      </section>

      {conflicts.length > 0 && (
        <section>
          <h2 className={H2}>Where customer groups disagree · {conflicts.length}</h2>
          <ul className="mt-4 grid gap-2 md:grid-cols-2">
            {conflicts.map((conflict, i) => <SegmentConflictCard key={`c-${i}`} conflict={conflict} visibleEvidenceIds={visibleEvidenceIds} />)}
          </ul>
        </section>
      )}

      <OfferCheckBox offerCheck={requirement.offer_check} />

      <section>
        <h2 className={H2}>Assumptions and open questions</h2>
        <ul className="mt-4 grid gap-2 md:grid-cols-2">
          {requirement.assumptions.map((text, i) => <AssumptionItem key={`a-${i}`} label="Assumption" text={text} />)}
          {requirement.uncertainties.map((text, i) => <AssumptionItem key={`u-${i}`} label="Uncertainty" text={text} />)}
          {requirement.assumptions.length === 0 && requirement.uncertainties.length === 0 && (
            <li className="border border-dashed border-[var(--hairline)] p-3 text-sm text-[var(--grey-500)]">No assumptions or uncertainties recorded.</li>
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
          </div>
        </details>
      )}

      <section>
        <h2 className={H2}>Decision record</h2>
        <div className="mt-4"><AuditTrail key={requirement.version + ":" + detail.history.length} requirementId={requirement.id} compact /></div>
      </section>
    </div>
  );
}
