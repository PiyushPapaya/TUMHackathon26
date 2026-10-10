"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";
import type { Chapter } from "./chapters";
import { acquireScrollEngine, releaseScrollEngine } from "./scrollEngine";
import { useCarFrames } from "./useCarFrames";
import { SignalFallback } from "./SignalFallback";
import { MStripe } from "@/src/components/ui/MStripe";

const ROUTE = "M0 150 C200 150 250 60 450 90 S750 170 1000 60";

function subscribeReduced(cb: () => void) {
  const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  mq.addEventListener("change", cb);
  return () => mq.removeEventListener("change", cb);
}
const getReduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const ease = (t: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);
const fmt = (n: number) => n.toLocaleString("en-US");

// Gepinnte Scroll-Szene: Das Auto-Video läuft als Frame-Folge auf einem Canvas, der Scroll-Fortschritt wählt das Bild.
// Warum Frames statt <video>: Video-Scrubbing ruckelt, ein Canvas-Bild pro Scroll-Position ist exakt und flüssig.
export function CarScene({ chapters, onFramesStatus }: { chapters: Chapter[]; onFramesStatus: (s: "loading" | "ready" | "fallback", p: number) => void }) {
  const reduced = useSyncExternalStore(subscribeReduced, getReduced, () => false);
  const { frames, manifest, status, progress } = useCarFrames();
  const sectionRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const routeRef = useRef<SVGPathElement>(null);
  const dotRef = useRef<SVGCircleElement>(null);
  const barRef = useRef<HTMLDivElement>(null);
  const chapterRefs = useRef<(HTMLDivElement | null)[]>([]);
  const figureRefs = useRef<(HTMLElement | null)[][]>([]);
  const chaptersRef = useRef(chapters);
  const updateRef = useRef<((p: number) => void) | null>(null);
  const progressRef = useRef(0);

  // Kommen die Backend-Zahlen erst nach dem Scroll-Setup an, zeichnen wir die Kapitel mit dem aktuellen Fortschritt neu.
  // Sonst blieben die Zähler bei "–", bis der Nutzer das nächste Mal scrollt.
  useEffect(() => {
    chaptersRef.current = chapters;
    updateRef.current?.(progressRef.current);
  }, [chapters]);
  useEffect(() => {
    onFramesStatus(status, progress);
  }, [status, progress, onFramesStatus]);

  useEffect(() => {
    if (reduced) return;
    let trigger: { kill: () => void } | undefined;
    let cancelled = false;

    function draw(p: number) {
      const canvas = canvasRef.current;
      const m = manifest.current;
      if (!canvas || !m) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const target = Math.round(p * (m.count - 1));
      // Nächstes bereits geladenes Bild nehmen, falls das exakte noch fehlt.
      let img: HTMLImageElement | undefined;
      for (let d = 0; d < m.count && !img; d++) img = frames.current[target - d] ?? frames.current[target + d];
      if (!img) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas.clientWidth * dpr;
      const h = canvas.clientHeight * dpr;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      // object-fit: cover von Hand: Bild füllt die Fläche, überstehende Ränder werden abgeschnitten.
      const scale = Math.max(w / img.naturalWidth, h / img.naturalHeight);
      const dw = img.naturalWidth * scale;
      const dh = img.naturalHeight * scale;
      ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
    }

    function update(p: number) {
      progressRef.current = p;
      draw(p);
      if (barRef.current) barRef.current.style.width = `${p * 100}%`;
      const route = routeRef.current;
      if (route) {
        const len = route.getTotalLength();
        route.style.strokeDasharray = `${len}`;
        route.style.strokeDashoffset = `${len * (1 - p)}`;
        const pt = route.getPointAtLength(len * p);
        dotRef.current?.setAttribute("cx", String(pt.x));
        dotRef.current?.setAttribute("cy", String(pt.y));
      }
      const count = chaptersRef.current.length;
      chaptersRef.current.forEach((ch, i) => {
        const local = p * count - i; // 0..1 innerhalb des Kapitels
        const el = chapterRefs.current[i];
        if (el) {
          const fade = Math.min(1, local / 0.15, (1 - local) / 0.15);
          const visible = local >= 0 && local <= 1;
          el.style.opacity = visible ? String(Math.max(0, fade)) : "0";
          el.style.transform = `translateY(${(1 - Math.max(0, Math.min(1, fade))) * 24}px)`;
          el.style.pointerEvents = visible ? "auto" : "none";
        }
        ch.figures.forEach((fig, j) => {
          const node = figureRefs.current[i]?.[j];
          if (node) node.textContent = fig.value === null ? "–" : fmt(Math.round(fig.value * ease(local / 0.6)));
        });
      });
    }

    acquireScrollEngine().then(({ ScrollTrigger }) => {
      if (cancelled || !sectionRef.current) return;
      const st = ScrollTrigger.create({
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom bottom",
        onUpdate: (self) => update(self.progress),
      });
      trigger = st;
      updateRef.current = update;
      update(st.progress);
    });

    return () => {
      cancelled = true;
      trigger?.kill();
      updateRef.current = null;
      releaseScrollEngine();
    };
  }, [reduced, manifest, frames, status]);

  return (
    <section
      id="how"
      ref={sectionRef}
      aria-label="How Signal2Spec works"
      className={`relative bg-[var(--black)] text-white ${reduced ? "" : "h-[300vh] md:h-[450vh]"}`}
    >
      <div className={reduced ? "" : "sticky top-0 h-screen overflow-hidden"}>
        {!reduced && status === "ready" && <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-hidden="true" />}
        {!reduced && status !== "ready" && <SignalFallback />}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-black/40" aria-hidden="true" />

        {!reduced && (
          <svg viewBox="0 0 1000 200" preserveAspectRatio="none" className="absolute inset-x-0 bottom-24 h-32 w-full" aria-hidden="true">
            <path d={ROUTE} fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
            <path ref={routeRef} d={ROUTE} fill="none" stroke="#81c4ff" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
            <circle ref={dotRef} r="5" cx="0" cy="150" fill="#1c69d4" />
          </svg>
        )}

        <div className={reduced ? "mx-auto grid max-w-[1400px] gap-16 px-6 py-24 lg:px-10" : ""}>
          {chapters.map((ch, i) => (
            <div
              key={ch.n}
              ref={(el) => {
                chapterRefs.current[i] = el;
              }}
              className={
                reduced
                  ? ""
                  : "absolute inset-0 mx-auto flex max-w-[1400px] flex-col justify-center px-6 opacity-0 lg:px-10"
              }
            >
              <p className="text-sm font-semibold tracking-[0.16em] text-[var(--m-light)]">{ch.n}</p>
              <h3 className="mt-3 text-5xl font-light leading-none tracking-tight sm:text-7xl">{ch.title}</h3>
              <p className="mt-5 max-w-lg text-lg text-white/80">{ch.text}</p>
              <dl className="mt-8 flex flex-wrap gap-x-12 gap-y-4">
                {ch.figures.map((fig, j) => (
                  <div key={fig.label}>
                    <dd
                      ref={(el) => {
                        (figureRefs.current[i] ??= [])[j] = el;
                      }}
                      className="text-5xl font-extralight tabular-nums sm:text-6xl"
                    >
                      {reduced ? (fig.value === null ? "–" : fmt(fig.value)) : "0"}
                    </dd>
                    <dt className="mt-1 text-xs uppercase tracking-[0.16em] text-white/70">{fig.label}</dt>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </div>

        {!reduced && (
          <div className="absolute inset-x-0 bottom-0">
            <div ref={barRef} style={{ width: 0 }}><MStripe /></div>
          </div>
        )}
      </div>
    </section>
  );
}
