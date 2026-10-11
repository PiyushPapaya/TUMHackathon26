import { useContext, useState } from "react";
import Link from "next/link";
import type { EvidenceLevel, Scenario } from "@/src/lib/api";
import { EvidenceDot } from "@/src/components/badges";
import { Eyebrow, SectionHeading } from "@/src/components/ui/Typography";
import { Reveal } from "@/src/components/ui/Reveal";
import { MediaContext, MediaImage } from "./MediaImage";
import type { HomeData } from "./useHomeData";
import { ScenarioFilters, EMPTY_SCENARIO_FILTER, matchesScenario } from "../ScenarioFilters";

// Fehlt ein Foto (z. B. G68-CN), zeigen wir eine Typo-Karte im selben Stil statt einer leeren Fläche.
function Placeholder({ s }: { s: Scenario }) {
  return (
    <div className="absolute inset-0 flex flex-col justify-end bg-[radial-gradient(ellipse_at_70%_20%,#1b2a3f_0%,#0a0a0b_75%)] p-6 text-white">
      <span className="text-7xl font-extralight leading-none tracking-tight text-white/90">{s.derivative}</span>
      <span className="mt-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--m-light)]">{s.market}</span>
      <span className="absolute inset-x-0 bottom-0 flex h-[3px]" aria-hidden="true">
        <span className="flex-1 bg-[var(--m-light)]" /><span className="flex-1 bg-[var(--m-dark)]" /><span className="flex-1 bg-[var(--m-red)]" />
      </span>
    </div>
  );
}

// Mini-Ampel je Szenario: wie viele Anforderungen sind belegt (grün), schwach (gelb), Annahme (rot).
function Lights({ levels }: { levels?: Record<EvidenceLevel, number> }) {
  if (!levels) return null;
  const rows: [EvidenceLevel, number][] = [["A", levels.A + levels.B], ["C", levels.C], ["D", levels.D]];
  return (
    <span className="flex items-center gap-3">
      {rows.map(([lvl, n]) => (
        <span key={lvl} className="flex items-center gap-1.5 tabular-nums"><EvidenceDot level={lvl} size={8} />{n}</span>
      ))}
    </span>
  );
}

// Raster 3 × 2: jede Karte führt direkt ins Cockpit des Szenarios.
// Warum nicht fünf bildschirmhohe Sektionen: Die Szenarien sind Auswahl, nicht Story.
export function ScenarioStrip({ data }: { data: HomeData }) {
  const media = useContext(MediaContext);
  const [filter, setFilter] = useState(EMPTY_SCENARIO_FILTER);
  const filtered = data.scenarios.filter(s => matchesScenario(s, filter));
  if (data.scenarios.length === 0) return null;
  return (
    <section id="scenarios" className="bg-[var(--grey-100)] py-24">
      <div className="mx-auto max-w-[1400px] px-6 lg:px-10">
        <Reveal className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <Eyebrow>{data.scenarios.length} models and markets</Eyebrow>
            <SectionHeading className="mt-3">Pick a model and market.</SectionHeading>
          </div>
          <p className="max-w-sm text-[var(--grey-500)]">Same pipeline, different data. Each card opens its ranked list.</p>
        </Reveal>
        <div className="mt-8"><ScenarioFilters scenarios={data.scenarios} value={filter} onChange={setFilter} /></div>
        <p role="status" className="mt-4 text-sm text-[var(--grey-500)]">{filtered.length} models and markets</p>
        {filtered.length === 0 && <p className="py-8">No models match these filters.</p>}
        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s, i) => {
            const f = data.funnels[s.id];
            const src = `/media/scenarios/${s.id}.jpg`;
            return (
              <Reveal key={s.id} delay={(i % 3) * 100} className="bg-white">
                <Link href={`/cockpit?scenario=${s.id}`} className="group relative block h-full">
                  <div className="relative aspect-[16/9] overflow-hidden bg-[var(--black)]">
                    {media.includes(src) ? (
                      <MediaImage src={src} alt={`${s.model_name}, ${s.market}`} className="transition-transform duration-[900ms] ease-out group-hover:scale-105" />
                    ) : (
                      <Placeholder s={s} />
                    )}
                    <span className="absolute left-4 top-4 bg-black/60 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-white backdrop-blur">
                      {s.derivative} · {s.market}
                    </span>
                  </div>
                  <div className="p-6">
                    <p className="text-xl font-light text-[var(--ink)] transition-colors group-hover:text-[var(--blue)]">{s.model_name}</p>
                    <p className="mt-1 text-sm text-[var(--grey-500)]">{s.market} market · successor {s.successor_horizon}</p>
                    <div className="mt-5 flex items-center justify-between border-t border-[var(--hairline)] pt-4 text-xs text-[var(--grey-500)]">
                      <span>{f ? `${f.evidence.toLocaleString("en-US")} voices · ${f.requirements} requirements` : "–"}</span>
                      <Lights levels={data.levelsBy[s.id]} />
                    </div>
                  </div>
                  <span className="absolute inset-x-0 bottom-0 h-[2px] origin-left scale-x-0 bg-[var(--blue)] transition-transform duration-500 group-hover:scale-x-100" aria-hidden="true" />
                </Link>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
