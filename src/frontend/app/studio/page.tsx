"use client";

/** Startseite der Werkbank: welche Werkzeuge es gibt und was jedes mit der Liste macht. */
import Link from "next/link";
import texte from "@/baukasten/texte.json";
import { useStudio } from "@/src/studio/StudioData";
import { enabledTools } from "@/src/studio/StudioNav";

export default function WorkbenchPage() {
  const { requirements, signals, evidenceById, loading, error } = useStudio();
  const conflicts = signals.filter((s) => s.conflicts_with.length > 0).length / 2;
  const open = requirements.filter((r) => r.status === "proposed").length;

  // Eine Zeile pro Werkzeug mit einer echten Zahl aus den Daten, damit man sieht, worauf es wirkt.
  const facts: Record<string, string> = {
    duel: `${Math.min(requirements.length, 8)} requirements in the ring`,
    arena: `${conflicts} ${conflicts === 1 ? "conflict" : "conflicts"} found`,
    assumptions: "1 forward-looking factor to switch off",
    voices: `${evidenceById.size} quotes behind the list`,
    swipe: `${open} of ${requirements.length} still open`,
  };

  return (
    <div>
      <section className="max-w-3xl pb-12">
        <h1 className="text-5xl font-semibold leading-[1.05] tracking-tight [font-stretch:125%] sm:text-6xl">
          {texte.workbench.title}
        </h1>
        <p className="mt-5 text-lg leading-relaxed text-[var(--ink)]/75">{texte.workbench.intro}</p>
        {error && <p className="mt-4 text-sm text-[var(--complaint)]">{error}</p>}
      </section>

      <ul className="divide-y divide-[var(--ink)]/15 border-y border-[var(--ink)]/15">
        {enabledTools().map((key) => (
          <li key={key}>
            <Link
              href={`/studio/${key}`}
              className="group grid gap-2 py-7 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] sm:grid-cols-[minmax(0,16rem)_1fr_auto] sm:items-baseline sm:gap-8"
            >
              <span className="text-2xl font-semibold tracking-tight [font-stretch:115%] group-hover:text-[var(--accent)]">
                {texte.tools[key].name}
              </span>
              <span className="max-w-xl text-[var(--ink)]/75">{texte.tools[key].short}</span>
              <span className="text-sm text-[var(--ink)]/55 tabular-nums">{loading ? "…" : facts[key]}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
