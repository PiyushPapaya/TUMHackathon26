"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";
import type { Chapter } from "./chapters";
import { acquireScrollEngine, releaseScrollEngine } from "./scrollEngine";
import { useCarFrames } from "./useCarFrames";
import { VoiceField, type FieldData, type FieldHandle } from "./VoiceField";
import { WorkflowStrip } from "./WorkflowStrip";
import { MStripe } from "@/src/components/ui/MStripe";

function subscribeReduced(cb: () => void) {
  const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  mq.addEventListener("change", cb);
  return () => mq.removeEventListener("change", cb);
}
const getReduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const ease = (t: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);
const fmt = (n: number) => n.toLocaleString("en-US");

// Gepinnte Scroll-Szene. Gibt es Auto-Frames, läuft das Auto als Canvas-Frame-Folge (exakter als <video>-Scrubbing).
// Sonst erzählt die Partikel-Szene (VoiceField) die Daten: Stimmen → Findings → Ampel → Rangliste → Entscheidung.
export function CarScene({ chapters, field, onFramesStatus }: { chapters: Chapter[]; field: FieldData; onFramesStatus: (s: "loading" | "ready" | "fallback", p: number) => void }) {
  const reduced = useSyncExternalStore(subscribeReduced, getReduced, () => false);
  const { frames, manifest, status, progress } = useCarFrames();
  const sectionRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fieldRef = useRef<FieldHandle>(null);
  const barRef = useRef<HTMLDivElement>(null);
  const railRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const chapterRefs = useRef<(HTMLDivElement | null)[]>([]);
  const figureRefs = useRef<(HTMLElement | null)[][]>([]);
  const chaptersRef = useRef(chapters);
  const updateRef = useRef<((p: number) => void) | null>(null);
  const progressRef = useRef(0);

  // Kommen die Backend-Zahlen erst nach dem Scroll-Setup an, zeichnen wir die Kapitel mit dem aktuellen Fortschritt neu.
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
      const scale = Math.max(w / img.naturalWidth, h / img.naturalHeight);
      ctx.drawImage(img, (w - img.naturalWidth * scale) / 2, (h - img.naturalHeight * scale) / 2, img.naturalWidth * scale, img.naturalHeight * scale);
    }

    function update(p: number) {
      progressRef.current = p;
      draw(p);
      fieldRef.current?.setProgress(p);
      if (barRef.current) barRef.current.style.width = `${p * 100}%`;
      const count = chaptersRef.current.length;
      const active = Math.min(count - 1, Math.floor(p * count));
      railRefs.current.forEach((el, i) => el?.setAttribute("aria-current", i === active ? "step" : "false"));
      chaptersRef.current.forEach((ch, i) => {
        const local = p * count - i; // 0..1 innerhalb des Kapitels
        const el = chapterRefs.current[i];
        if (el) {
          // Erstes Kapitel ist sofort da, letztes bleibt am Ende stehen: kein leerer Bildschirm an den Rändern.
          const fadeIn = i === 0 ? 1 : local / 0.15;
          const fadeOut = i === count - 1 ? 1 : (1 - local) / 0.15;
          const fade = Math.max(0, Math.min(1, fadeIn, fadeOut));
          const visible = i === count - 1 ? local >= 0 : local >= 0 && local <= 1;
          el.style.opacity = visible ? String(fade) : "0";
          el.style.transform = `translateY(${(1 - fade) * 24}px)`;
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
      const st = ScrollTrigger.create({ trigger: sectionRef.current, start: "top top", end: "bottom bottom", onUpdate: (self) => update(self.progress) });
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

  // Klick auf einen Rail-Punkt springt mitten in das Kapitel.
  function jumpTo(i: number) {
    const el = sectionRef.current;
    if (!el) return;
    const span = el.offsetHeight - window.innerHeight;
    window.scrollTo({ top: el.offsetTop + span * ((i + 0.45) / chapters.length), behavior: "smooth" });
  }

  return (
    <section
      id="how"
      ref={sectionRef}
      aria-label="How ReSpec works"
      className={`relative bg-[var(--black)] text-white ${reduced ? "" : "h-[380vh] md:h-[560vh]"}`}
    >
      <div className={reduced ? "" : "sticky top-0 h-screen overflow-hidden"}>
        {!reduced && status === "ready" && <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-hidden="true" />}
        {!reduced && status !== "ready" && <VoiceField ref={fieldRef} data={field} />}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-black/70 via-black/10 to-transparent" aria-hidden="true" />

        <div className={reduced ? "mx-auto grid max-w-[1400px] gap-16 px-6 py-24 lg:px-10" : ""}>
          {chapters.map((ch, i) => (
            <div
              key={ch.n}
              ref={(el) => {
                chapterRefs.current[i] = el;
              }}
              className={reduced ? "" : "absolute inset-0 mx-auto flex max-w-[1400px] flex-col justify-center px-6 opacity-0 lg:px-10"}
            >
              <div className={ch.workflow && !reduced ? "-mt-40 lg:-mt-48" : ""}>
                <p className="text-sm font-semibold tracking-[0.16em] text-[var(--m-light)]">{ch.n}</p>
                <h3 className="mt-3 max-w-xl text-5xl font-light leading-none tracking-tight sm:text-7xl">{ch.title}</h3>
                <p className="mt-5 max-w-lg text-lg text-white/80">{ch.text}</p>
                <dl className="mt-8 flex flex-wrap gap-x-12 gap-y-4">
                  {ch.figures.map((fig, j) => (
                    <div key={fig.label}>
                      <dd
                        ref={(el) => {
                          (figureRefs.current[i] ??= [])[j] = el;
                        }}
                        className={`${ch.figures.length > 3 ? "text-4xl sm:text-5xl" : "text-5xl sm:text-6xl"} font-extralight tabular-nums`}
                      >
                        {reduced ? (fig.value === null ? "–" : fmt(fig.value)) : "0"}
                      </dd>
                      <dt className="mt-1 text-xs uppercase tracking-[0.16em] text-white/70">{fig.label}</dt>
                    </div>
                  ))}
                </dl>
              </div>
              {ch.workflow && (
                <div className={reduced ? "mt-10" : "absolute inset-x-6 bottom-10 lg:left-10 lg:right-28"}>
                  <WorkflowStrip />
                </div>
              )}
            </div>
          ))}
        </div>

        {!reduced && (
          <>
            <nav aria-label="Chapters" className="absolute right-6 top-1/2 hidden -translate-y-1/2 flex-col gap-4 md:flex lg:right-10">
              {chapters.map((ch, i) => (
                <button
                  key={ch.n}
                  type="button"
                  ref={(el) => {
                    railRefs.current[i] = el;
                  }}
                  onClick={() => jumpTo(i)}
                  aria-label={`Chapter ${ch.n}: ${ch.title}`}
                  className="group flex items-center justify-end gap-3 text-[11px] font-semibold tabular-nums text-white/40 hover:text-white aria-[current=step]:text-white"
                >
                  <span className="opacity-0 transition-opacity group-hover:opacity-100 group-aria-[current=step]:opacity-100">{ch.title}</span>
                  <span className="h-px w-6 bg-current transition-all group-aria-[current=step]:w-10 group-aria-[current=step]:bg-[var(--m-light)]" />
                  {ch.n}
                </button>
              ))}
            </nav>
            <div className="absolute inset-x-0 bottom-0">
              <div ref={barRef} style={{ width: 0 }}><MStripe /></div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
