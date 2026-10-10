"use client";

/**
 * Konflikt-Arena: Befunde, die sich widersprechen (Signal.conflicts_with), stehen nebeneinander,
 * jeder mit eigenen Zitaten und den Anforderungen, die auf ihm beruhen.
 * Warum: Der Brief verlangt "a clear understanding of conflicting evidence". Wir mitteln nicht, wir zeigen beide Seiten.
 */
import Link from "next/link";
import { categoryLabel } from "@/src/components/badges";
import type { Signal } from "@/src/lib/api";
import { useStudio } from "@/src/studio/StudioData";
import { ToolFrame } from "@/src/studio/ToolFrame";
import { Notice, QuoteCard } from "@/src/studio/ui";

const KIND_LABEL: Record<Signal["kind"], string> = {
  complaint: "Complaint",
  unmet_need: "Unmet need",
  delight: "Delight",
  competitor_advantage: "Competitor advantage",
  trend: "Trend",
};

export default function ArenaPage() {
  const { signals } = useStudio();
  const byId = new Map(signals.map((s) => [s.id, s]));

  // Jedes Paar nur einmal (A gegen B, nicht zusätzlich B gegen A).
  const pairs: [Signal, Signal][] = [];
  for (const s of signals) {
    for (const otherId of s.conflicts_with) {
      const other = byId.get(otherId);
      if (other && s.id < other.id) pairs.push([s, other]);
    }
  }

  return (
    <ToolFrame tool="arena">
      {pairs.length === 0 ? (
        <Notice kind="empty">No conflicting findings in this scenario. That is a result too: the evidence points one way.</Notice>
      ) : (
        <div className="space-y-16">
          {pairs.map(([left, right]) => (
            <section key={`${left.id}-${right.id}`} aria-label={`${left.title} versus ${right.title}`}>
              <p className="mb-4 text-sm text-[var(--ink)]/60">
                {categoryLabel(left.category)}: {left.mention_count + right.mention_count} mentions on both sides
              </p>
              <div className="grid gap-6 lg:grid-cols-2 lg:divide-x lg:divide-[var(--ink)]/15">
                <div className="lg:pr-6">
                  <Side signal={left} />
                </div>
                <div className="lg:pl-6">
                  <Side signal={right} />
                </div>
              </div>
            </section>
          ))}
        </div>
      )}
    </ToolFrame>
  );
}

function Side({ signal }: { signal: Signal }) {
  const { evidenceById, requirements } = useStudio();
  const quotes = signal.evidence_ids.map((id) => evidenceById.get(id)).filter((e) => e !== undefined);
  const linked = requirements.filter((r) => r.signal_ids.includes(signal.id));
  const missingIds = signal.evidence_ids.filter((id) => !evidenceById.has(id));
  const hidden = missingIds.length;

  return (
    <div>
      <p className="text-sm font-medium text-[var(--ink)]/60">{KIND_LABEL[signal.kind]}</p>
      <h2 className="mt-1 text-3xl font-semibold leading-tight tracking-tight [font-stretch:115%]">{signal.title}</h2>
      <p className="mt-3 text-[var(--ink)]/75">{signal.summary}</p>
      <p className="mt-4 text-4xl font-semibold tabular-nums [font-stretch:125%]">
        {signal.mention_count}
        <span className="ml-2 text-base font-normal text-[var(--ink)]/60">mentions</span>
      </p>

      <div className="mt-6 grid gap-3">
        {quotes.slice(0, 3).map((e) => (
          <QuoteCard key={e.id} evidence={e} />
        ))}
        {hidden > 0 && (
          <p className="text-xs text-[var(--ink)]/55">
            {hidden} more {hidden === 1 ? "source" : "sources"} ({missingIds.join(", ")}) are not linked to a requirement yet.
          </p>
        )}
      </div>

      <div className="mt-6">
        <p className="mb-2 text-sm font-medium">Requirements built on this side</p>
        {linked.length === 0 ? (
          <p className="text-sm text-[var(--ink)]/55">None yet.</p>
        ) : (
          <ul className="space-y-1">
            {linked.map((r) => (
              <li key={r.id}>
                <Link href="/studio/swipe" className="text-[var(--accent)] underline-offset-2 hover:underline">
                  #{r.rank} {r.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
