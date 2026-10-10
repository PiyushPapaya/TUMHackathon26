"use client";

/** Kopfzeile der Werkbank: Werkzeuge (nur die eingeschalteten aus baukasten/features.json) und Szenario-Wahl. */
import Link from "next/link";
import { usePathname } from "next/navigation";
import features from "@/baukasten/features.json";
import texte from "@/baukasten/texte.json";
import { useStudio } from "@/src/studio/StudioData";

export type ToolKey = keyof typeof texte.tools;

export const TOOL_ORDER: ToolKey[] = ["duel", "arena", "assumptions", "voices", "swipe"];

export const enabledTools = (): ToolKey[] => TOOL_ORDER.filter((key) => features[key as keyof typeof features]);

export function StudioNav() {
  const pathname = usePathname();
  const { scenarios, scenarioId, setScenarioId } = useStudio();

  const link = (href: string, label: string) => {
    const active = pathname === href;
    return (
      <Link
        key={href}
        href={href}
        aria-current={active ? "page" : undefined}
        className={`shrink-0 whitespace-nowrap rounded-md px-2.5 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
          active ? "bg-[var(--ink)] text-white" : "text-[var(--ink)]/70 hover:text-[var(--ink)]"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--ink)]/10 bg-[var(--paper)]/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-x-5 px-4 py-3 sm:px-8">
        <Link href="/studio" className="shrink-0 text-lg font-bold tracking-tight [font-stretch:125%]">
          Signal2Spec
        </Link>
        <nav aria-label="Workbench tools" className="-mx-1 flex min-w-0 flex-1 items-center gap-0.5 overflow-x-auto px-1">
          {link("/", "Cockpit")}
          {link("/studio", texte.workbench.title)}
          {enabledTools().map((key) => link(`/studio/${key}`, texte.tools[key].name))}
        </nav>
        <label className="flex shrink-0 items-center gap-2 text-sm">
          <span className="hidden text-[var(--ink)]/60 md:inline">Scenario</span>
          <select
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="rounded-md border border-[var(--ink)]/25 bg-white px-2 py-1.5 text-sm focus:border-[var(--accent)] focus:outline-none"
          >
            {scenarios.length === 0 && <option value={scenarioId}>{scenarioId}</option>}
            {scenarios.map((s) => (
              <option key={s.id} value={s.id} title={`${s.model_name}, ${s.market}`}>
                {s.id}
              </option>
            ))}
          </select>
        </label>
      </div>
    </header>
  );
}
