"use client";

import { useLayoutEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import type { Requirement } from "@/src/lib/api";
import { categoryLabel, ConflictMark, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreBar } from "@/src/components/ScoreBar";

function RankDelta({ oldRank, newRank }: { oldRank?: number; newRank: number }) {
  if (!oldRank || oldRank === newRank) return null;
  const movedUp = oldRank > newRank;
  return (
    <span className={`text-xs font-semibold ${movedUp ? "text-emerald-700" : "text-[var(--m-red)]"}`}>
      {movedUp ? "▲" : "▼"} {Math.abs(oldRank - newRank)}
    </span>
  );
}

// FLIP-Animation (First, Last, Invert, Play): wir merken die Zeilenpositionen vor dem Neuordnen,
// verschieben jede Zeile optisch zurück an den alten Platz und lassen sie dann gleiten.
// Warum: Der Rangwechsel nach "Apply" ist der beste Demo-Moment, die Jury soll ihn sehen.
function useFlip(requirements: Requirement[], animateRanks: boolean) {
  const rowRefs = useRef(new Map<string, HTMLTableRowElement>());
  const lastTops = useRef(new Map<string, number>());

  useLayoutEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    rowRefs.current.forEach((el, id) => {
      el.getAnimations().forEach(animation => animation.cancel());
      const top = el.getBoundingClientRect().top;
      const before = lastTops.current.get(id);
      if (animateRanks && !reduce && before !== undefined && Math.abs(before - top) > 1) {
        el.animate(
          [{ transform: `translateY(${before - top}px)` }, { transform: "translateY(0)" }],
          { duration: 600, easing: "cubic-bezier(0.22, 1, 0.36, 1)" },
        );
      }
      lastTops.current.set(id, top);
    });
  }, [requirements, animateRanks]);

  return (id: string) => (el: HTMLTableRowElement | null) => {
    if (el) rowRefs.current.set(id, el);
    else rowRefs.current.delete(id);
  };
}

// Nur vier Spalten: Rang, was, wie wichtig, wie gut belegt. Status und Konflikt-Details
// stehen auf der Detailseite; ein Konflikt zeigt sich hier nur als kleines Warnzeichen.
export function RequirementsTable({
  requirements,
  previousRanks,
  highlightRanks,
  conflictTitles,
  scenarioId,
}: {
  requirements: Requirement[];
  previousRanks: Record<string, number>;
  highlightRanks: boolean;
  conflictTitles: (r: Requirement) => string[];
  scenarioId: string;
}) {
  const router = useRouter();
  const rowRef = useFlip(requirements, highlightRanks);
  const open = (id: string) => router.push(`/requirements/${id}?scenario=${encodeURIComponent(scenarioId)}`);

  return (
    <div className="overflow-x-auto border-t border-[var(--hairline)]">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">
          <tr className="border-b border-[var(--hairline)]">
            {["Rank", "Requirement", "Score", "Evidence"].map((h) => (
              <th key={h} className="px-4 py-3 font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {requirements.map((req) => {
            const moved = highlightRanks && previousRanks[req.id] !== undefined && previousRanks[req.id] !== req.rank;
            return (
              <tr
                key={req.id}
                ref={rowRef(req.id)}
                role="link"
                tabIndex={0}
                onClick={() => open(req.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    open(req.id);
                  }
                }}
                className={`group cursor-pointer border-b border-[var(--hairline)] transition-colors hover:bg-[var(--grey-100)] focus:bg-[var(--grey-100)] ${
                  moved ? "bg-[#eef4fc]" : "bg-white"
                }`}
              >
                <td className="w-24 px-4 py-5 align-top">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-light tabular-nums text-[var(--ink)]">{req.rank}</span>
                    <RankDelta oldRank={previousRanks[req.id]} newRank={req.rank} />
                  </div>
                </td>
                <td className="px-4 py-5">
                  <p className="text-base font-light text-[var(--ink)] group-hover:text-[var(--blue)]">
                    {req.title}
                  </p>
                  <p className="mt-1 text-xs uppercase tracking-[0.08em] text-[var(--grey-500)]">{categoryLabel(req.category)}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-3"><StatusBadge status={req.status} /><ConflictMark conflictingTitles={conflictTitles(req)} /><span className="text-xs text-[var(--grey-500)]">{({ S: "Small", M: "Medium", L: "Large" })[req.effort]} effort</span></div>
                </td>
                <td className="px-4 py-5">
                  <ScoreBar score={req.score} source={`${req.signal_ids.length} linked findings`} />
                </td>
                <td className="px-4 py-5"><EvidenceBadge level={req.evidence_level} reason={req.rationale} /></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
