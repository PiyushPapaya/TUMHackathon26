"use client";

import Link from "next/link";
import { getOverview } from "@/src/lib/api";
import { useLoad } from "@/src/lib/useLoad";
import { useScenarioParam } from "@/src/components/shell/useScenarioParam";
import { EvidenceBadge } from "@/src/components/badges";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { Button } from "@/src/components/ui/Button";
import { HairlineCard } from "@/src/components/ui/HairlineCard";
import { Eyebrow } from "@/src/components/ui/Typography";

// Wer macht was: KI autonom vs. Mensch-Pflicht. Der Brief verlangt genau diese Trennung im Workflow.
const WORKFLOW = [
  { stage: "Ingest", human: false, text: "Excel and PDF inputs become evidence IDs." },
  { stage: "Findings", human: false, text: "Recurring signals are grouped with quotes." },
  { stage: "Web", human: false, text: "External sources confirm trends and competitors." },
  { stage: "Requirements", human: true, text: "AI proposes measurable PM-ready requirements." },
  { stage: "Prioritization", human: true, text: "Formula ranks, PM can change weights." },
  { stage: "Decision", human: true, text: "Approve, reject, edit, or challenge." },
  { stage: "Documentation", human: false, text: "Audit trail and export are generated." },
];

function FunnelRow({ label, value, max }: { label: string; value: number; max: number }) {
  const width = Math.max(2, (value / Math.max(max, 1)) * 100);
  return (
    <div className="animate-funnel grid items-center gap-x-6 gap-y-1 py-4 sm:grid-cols-[160px_1fr]">
      <div>
        <p className="text-4xl font-light tabular-nums">{value.toLocaleString("en-US")}</p>
        <p className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">{label}</p>
      </div>
      <div className="h-[3px] bg-[var(--hairline)]">
        <div className="h-full bg-[var(--blue)]" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export function OverviewPageClient() {
  const id = useScenarioParam();
  const { data: overview, error, loading } = useLoad(id, () => getOverview(id));
  const funnel = overview?.funnel;

  return (
    <main className="mx-auto max-w-[1400px] px-6 py-12 lg:px-10">
      <PageHeader
        eyebrow={`Overview · ${id}`}
        title="From voice to decision."
        action={<Button href={`/cockpit?scenario=${id}`}>Open ranked list</Button>}
      >
        One funnel from customer voices to PM-approved requirements, with AI and human responsibility separated.
      </PageHeader>

      {error && <ErrorNote message={error} />}
      {loading && !error && <Loading what="overview" />}

      {overview && (
        <div className="grid gap-12 xl:grid-cols-[1fr_380px]">
          <section>
            <Eyebrow>Funnel</Eyebrow>
            <div className="mt-2 divide-y divide-[var(--hairline)] border-y border-[var(--hairline)]">
              <FunnelRow label="customer voices" value={funnel?.evidence ?? 0} max={funnel?.evidence ?? 1} />
              <FunnelRow label="findings" value={funnel?.signals ?? 0} max={funnel?.evidence ?? 1} />
              <FunnelRow label="requirements" value={funnel?.requirements ?? 0} max={funnel?.evidence ?? 1} />
              <FunnelRow label="approved by PM" value={funnel?.approved ?? 0} max={funnel?.evidence ?? 1} />
            </div>
            {funnel?.note && <p className="mt-4 text-sm text-[var(--grey-500)]">{funnel.note}</p>}
          </section>

          <aside className="grid h-fit gap-8">
            <section>
              <Eyebrow>Top proposals</Eyebrow>
              <div className="mt-3 border-t border-[var(--hairline)]">
                {overview.top3.map((item) => (
                  <Link key={item.id} href={`/requirements/${item.id}`} className="flex items-start gap-4 border-b border-[var(--hairline)] py-4 hover:bg-[var(--grey-100)]">
                    <span className="text-3xl font-light tabular-nums">{item.rank}</span>
                    <span className="flex-1">
                      <span className="block">{item.title}</span>
                      <span className="mt-1 block text-xs text-[var(--grey-500)]">Score {item.score.toFixed(1)}</span>
                    </span>
                    <EvidenceBadge level={item.evidence_level} reason={item.level_label} />
                  </Link>
                ))}
              </div>
            </section>
            <section>
              <Eyebrow>Evidence levels</Eyebrow>
              <div className="mt-3 grid grid-cols-4 gap-px bg-[var(--hairline)]">
                {(["A", "B", "C", "D"] as const).map((level) => (
                  <div key={level} className="bg-white p-3">
                    <p className="text-3xl font-light tabular-nums">{overview.level_distribution[level]}</p>
                    <p className="mt-1 text-xs font-semibold text-[var(--grey-500)]">Level {level}</p>
                  </div>
                ))}
              </div>
            </section>
          </aside>

          <section className="xl:col-span-2">
            <Eyebrow>Workflow: who does what</Eyebrow>
            <div className="mt-3 grid gap-px bg-[var(--hairline)] md:grid-cols-2 xl:grid-cols-7">
              {WORKFLOW.map((step, i) => (
                <article key={step.stage} className="bg-white p-4">
                  <p className="text-xs text-[var(--grey-500)]">0{i + 1}</p>
                  <h3 className="mt-2 font-semibold">{step.stage}</h3>
                  <p className={`mt-2 inline-block border px-2 py-0.5 text-xs font-semibold ${step.human ? "border-[var(--blue)] text-[var(--blue)]" : "border-[var(--hairline)] text-[var(--grey-500)]"}`}>
                    {step.human ? "PM in control" : "AI autonomous"}
                  </p>
                  <p className="mt-3 text-xs text-[var(--grey-500)]">{step.text}</p>
                </article>
              ))}
            </div>
          </section>

          {overview.warnings.length > 0 && (
            <HairlineCard className="xl:col-span-2">
              <Eyebrow>Data warnings</Eyebrow>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm">
                {overview.warnings.map((w) => <li key={w}>{w}</li>)}
              </ul>
            </HairlineCard>
          )}
        </div>
      )}
    </main>
  );
}
