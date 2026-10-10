import Link from "next/link";
import { Eyebrow } from "@/src/components/ui/Typography";
import { Icon } from "@/src/components/ui/Icon";
import { Reveal } from "@/src/components/ui/Reveal";
import { MediaImage } from "./MediaImage";
import type { HomeData } from "./useHomeData";

// Ein Streifen mit kleinen Karten statt fünf bildschirmhoher Auto-Sektionen.
// Warum: Die Szenarien sind Auswahl, nicht Story. So bleibt die Startseite kurz und die Autos wirken nicht erdrückend.
export function ScenarioStrip({ data }: { data: HomeData }) {
  if (data.scenarios.length === 0) return null;
  return (
    <section id="scenarios" className="bg-[var(--grey-100)] py-20">
      <div className="mx-auto max-w-[1400px] px-6 lg:px-10">
        <Eyebrow>Pick a model and market</Eyebrow>
        <div className="mt-8 grid gap-px bg-[var(--hairline)] sm:grid-cols-2 lg:grid-cols-5">
          {data.scenarios.map((s, i) => {
            const f = data.funnels[s.id];
            return (
              <Reveal key={s.id} delay={i * 80} className="bg-white">
                <Link href={`/cockpit?scenario=${s.id}`} className="group block h-full">
                  <div className="relative aspect-[16/10] overflow-hidden bg-[radial-gradient(ellipse_at_70%_30%,#1b2a3f_0%,#0a0a0b_70%)]">
                    <MediaImage src={`/media/scenarios/${s.id}.jpg`} alt={`${s.model_name}, ${s.market}`} className="transition-transform duration-700 group-hover:scale-105" />
                  </div>
                  <div className="p-5">
                    <p className="text-xs uppercase tracking-[0.14em] text-[var(--grey-500)]">{s.derivative} · {s.market}</p>
                    <p className="mt-1 text-lg font-light text-[var(--ink)] group-hover:text-[var(--blue)]">{s.model_name}</p>
                    <p className="mt-3 flex items-center justify-between text-xs text-[var(--grey-500)]">
                      {f ? `${f.evidence.toLocaleString("en-US")} voices · ${f.requirements} requirements` : "–"}
                      <Icon name="arrow" size={16} className="text-[var(--ink)] transition-transform group-hover:translate-x-1" />
                    </p>
                  </div>
                </Link>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
