import Link from "next/link";
import type { GapsView, TrendsView } from "@/src/lib/insights";
import { EvidenceBadge, categoryLabel } from "@/src/components/badges";

export function TrendsList({ data }: { data: TrendsView }) {
  const items = [...data.items].sort((a, b) => b.strength - a.strength);
  return (
    <div className="grid gap-px bg-[var(--hairline)] md:grid-cols-2">
      {items.map((t) => (
        <article key={t.topic} className="bg-white p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">
            {t.kind === "bet" ? `Bet for ${t.horizon}` : "Trend today"} · {categoryLabel(t.category)}
          </p>
          <h3 className="mt-2 text-xl font-light">{t.topic}</h3>
          <div className="mt-3 flex items-center gap-3">
            <EvidenceBadge level={t.evidence_level} />
            <span className="text-xs text-[var(--grey-500)]">Strength {t.strength.toFixed(0)} · {(t.sources ?? []).join(", ")}</span>
          </div>
          {(t.assumptions?.length ?? 0) > 0 && (
            <ul className="mt-4 list-disc pl-5 text-sm text-[var(--grey-500)]">
              {(t.assumptions ?? []).map((a) => <li key={a}>{a}</li>)}
            </ul>
          )}
          {t.requirement_id && (
            <Link className="mt-4 inline-block text-sm text-[var(--blue)] hover:text-[var(--blue-hover)]" href={`/requirements/${t.requirement_id}`}>
              Open requirement ›
            </Link>
          )}
        </article>
      ))}
      {items.length === 0 && <p className="bg-white p-6 text-sm text-[var(--grey-500)]">No trends for this scenario.</p>}
    </div>
  );
}

export function GapsList({ data }: { data: GapsView }) {
  return (
    <div>
      <p className="text-6xl font-extralight tabular-nums">{Math.round(data.share_weak * 100)}%</p>
      <p className="mt-1 text-sm text-[var(--grey-500)]">of requirements rest on weak evidence (level C or D). This is what we do not know yet.</p>
      <div className="mt-8 grid gap-px bg-[var(--hairline)] md:grid-cols-2">
        {data.weak_requirements.map((w) => (
          <article key={w.id} className="bg-white p-6">
            <div className="flex items-start justify-between gap-3">
              <Link href={`/requirements/${w.id}`} className="text-lg font-light hover:text-[var(--blue)]">#{w.rank} {w.title}</Link>
              <EvidenceBadge level={w.evidence_level} />
            </div>
            <p className="mt-3 text-sm">{w.why}</p>
            <p className="mt-3 text-sm"><span className="font-semibold">Next step:</span> {w.next_study}</p>
          </article>
        ))}
        {data.weak_requirements.length === 0 && <p className="bg-white p-6 text-sm text-[var(--grey-500)]">No weak requirements. Every proposal has solid evidence.</p>}
      </div>
      {data.missing_sources.length > 0 && (
        <p className="mt-6 text-sm text-[var(--grey-500)]">Missing sources: {data.missing_sources.join(", ")}</p>
      )}
    </div>
  );
}
