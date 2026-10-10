"use client";

import Link from "next/link";
import { getExportUrl, type Scenario } from "@/src/lib/api";
import { getMemoUrl } from "@/src/lib/insights";
import { scenarioLabel } from "./scenarioLabel";

const HEAD = "mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]";
const LINK = "block py-2 text-[15px] text-[var(--ink)] hover:text-[var(--blue)]";

// Vier Spalten wie beim BMW-Mega-Menü. Die Szenarien kommen live aus dem Backend,
// nichts ist hartkodiert, damit neue Szenarien (scripts/new_scenario.py) automatisch erscheinen.
export function MegaMenu({
  scenarios,
  scenarioId,
  onNavigate,
}: {
  scenarios: Scenario[];
  scenarioId: string;
  onNavigate: () => void;
}) {
  return (
    <div id="mega-menu" className="absolute left-0 right-0 top-full border-t border-[var(--hairline)] bg-white">
      <div className="mx-auto grid max-w-[1400px] gap-10 px-6 py-10 sm:grid-cols-2 lg:grid-cols-4 lg:px-10">
        <div>
          <p className={HEAD}>Scenarios</p>
          {scenarios.map((s) => (
            <Link key={s.id} className={LINK} href={`/cockpit?scenario=${s.id}`} onClick={onNavigate}>
              {scenarioLabel(s)}
            </Link>
          ))}
        </div>
        <div>
          <p className={HEAD}>Explore</p>
          <Link className={LINK} href={`/cockpit?scenario=${scenarioId}`} onClick={onNavigate}>Ranked list</Link>
          <Link className={LINK} href={`/overview?scenario=${scenarioId}`} onClick={onNavigate}>Overview and funnel</Link>
          <Link className={LINK} href={`/insights?scenario=${scenarioId}`} onClick={onNavigate}>Insights and trends</Link>
          <Link className={LINK} href="/portfolio" onClick={onNavigate}>Portfolio and markets</Link>
          <Link className={LINK} href={`/evidence?scenario=${scenarioId}`} onClick={onNavigate}>Evidence browser</Link>
          <Link className={LINK} href="/audit" onClick={onNavigate}>Audit trail</Link>
        </div>
        <div>
          <p className={HEAD}>Quick actions</p>
          <a className={LINK} href={getMemoUrl(scenarioId)} target="_blank" rel="noopener noreferrer">Decision memo</a>
          {(["csv", "json", "md"] as const).map((fmt) => (
            <a key={fmt} className={LINK} href={getExportUrl(scenarioId, fmt)} target="_blank" rel="noopener noreferrer">
              Export {fmt.toUpperCase()}
            </a>
          ))}
        </div>
        <div>
          <p className={HEAD}>Learn</p>
          <Link className={LINK} href="/guide" onClick={onNavigate}>Guide</Link>
          <Link className={LINK} href="/#how" onClick={onNavigate}>How it works</Link>
        </div>
      </div>
    </div>
  );
}
