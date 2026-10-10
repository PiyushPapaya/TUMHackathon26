import Link from "next/link";
import type { Requirement } from "@/src/lib/api";
import type { MatrixView as Matrix } from "@/src/lib/insights";
import { EvidenceBadge } from "@/src/components/badges";
import { en, OFFER_GAP_EN, QUADRANT_EN } from "./labels";

// 2x2-Matrix: Spalten heute vs. Nachfolger-Horizont, Zeilen stark vs. schwach belegt.
// Warum: Der Brief verlangt, Belege und Zukunftsannahmen klar zu trennen. Hier sieht man es auf einen Blick.
const GRID = ["Sicher & dringend", "Belegte Zukunftswette", "Schwach belegt, heute", "Annahme – beobachten"];

export function MatrixView({ matrix, requirements }: { matrix: Matrix; requirements: Requirement[] }) {
  const byQuadrant = (q: string) => requirements.filter((r) => matrix.items[r.id]?.quadrant === q);
  return (
    <div>
      <div className="mb-3 grid grid-cols-2 gap-px text-xs font-semibold uppercase tracking-[0.12em] text-[var(--grey-500)]">
        <span>Today</span>
        <span>Successor ({matrix.successor_horizon})</span>
      </div>
      <div className="grid gap-px bg-[var(--hairline)] md:grid-cols-2">
        {GRID.map((q) => (
          <section key={q} className="min-h-48 bg-white p-6">
            <h3 className="text-xl font-light">{en(QUADRANT_EN, q)}</h3>
            <ul className="mt-4 grid gap-3">
              {byQuadrant(q).map((r) => (
                <li key={r.id} className="border-t border-[var(--hairline)] pt-3">
                  <div className="flex items-start justify-between gap-3">
                    <Link href={`/requirements/${r.id}`} className="text-sm text-[var(--ink)] hover:text-[var(--blue)]">
                      #{r.rank} {r.title}
                    </Link>
                    <EvidenceBadge level={r.evidence_level} />
                  </div>
                  <p className="mt-1 text-xs text-[var(--grey-500)]">{en(OFFER_GAP_EN, matrix.items[r.id].offer_gap)}</p>
                </li>
              ))}
              {byQuadrant(q).length === 0 && <li className="text-sm text-[var(--grey-500)]">Nothing here.</li>}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
