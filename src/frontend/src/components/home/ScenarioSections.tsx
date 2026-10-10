"use client";

import { useEffect, useRef } from "react";
import { Button } from "@/src/components/ui/Button";
import { Eyebrow } from "@/src/components/ui/Typography";
import { Reveal } from "@/src/components/ui/Reveal";
import { MediaImage } from "./MediaImage";
import type { HomeData } from "./useHomeData";

const TINTS = ["#16202e", "#241a26", "#1a2620", "#2a2318"];

// Leichter Parallax ohne GSAP: Das Hintergrundbild wandert langsamer als die Seite.
function useParallax() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const el = ref.current;
    if (!el?.parentElement) return;
    const parent = el.parentElement;
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = parent.getBoundingClientRect();
        el.style.transform = `translateY(${(r.top / window.innerHeight) * -60}px)`;
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(raf);
    };
  }, []);
  return ref;
}

function ScenarioBlock({ data, index }: { data: HomeData; index: number }) {
  const s = data.scenarios[index];
  const f = data.funnels[s.id];
  const ref = useParallax();
  return (
    <section className="relative flex min-h-[85vh] items-end overflow-hidden bg-[var(--black)] text-white">
      <div
        ref={ref}
        className="absolute -inset-y-16 inset-x-0"
        style={{ background: `radial-gradient(ellipse at 70% 30%, ${TINTS[index % TINTS.length]} 0%, #0a0a0b 70%)` }}
      >
        <MediaImage src={`/media/scenarios/${s.id}.jpg`} alt={`${s.model_name}, ${s.market}`} />
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" aria-hidden="true" />
      <Reveal className="relative mx-auto w-full max-w-[1400px] px-6 pb-16 lg:px-10">
        <Eyebrow light>{s.derivative} · {s.market}</Eyebrow>
        <h2 className="mt-3 text-4xl font-light leading-tight sm:text-6xl">The {s.model_name} in the {s.market}.</h2>
        <p className="mt-5 text-white/80">
          {f
            ? `${f.evidence.toLocaleString("en-US")} customer voices · ${f.signals} findings · ${f.requirements} requirements`
            : "Numbers load from the backend."}
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Button href={`/cockpit?scenario=${s.id}`}>Open in cockpit</Button>
          <Button variant="outline-light" href="/overview">Discover</Button>
        </div>
      </Reveal>
    </section>
  );
}

export function ScenarioSections({ data }: { data: HomeData }) {
  return (
    <div id="scenarios">
      {data.scenarios.map((s, i) => <ScenarioBlock key={s.id} data={data} index={i} />)}
    </div>
  );
}
