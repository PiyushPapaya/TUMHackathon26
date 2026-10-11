"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import type { EvidenceLevel } from "@/src/lib/api";

export type FieldData = { findings: number | null; bars: { score: number; level: EvidenceLevel }[] };
export type FieldHandle = { setProgress: (p: number) => void };

// Ampel-Farben wie badges.tsx (A/B grün, C gelb, D rot), dazu das Signal-Blau für "noch nicht bewertet".
const RGB = { blue: [129, 196, 255], A: [16, 185, 129], B: [16, 185, 129], C: [251, 191, 36], D: [226, 39, 24] } as const;
const clamp = (t: number) => Math.min(1, Math.max(0, t));
const ease = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
const mix = (a: number, b: number, t: number) => a + (b - a) * t;

type P = { sx: number; sy: number; cx: number; cy: number; bar: number; t: number; phase: number; delay: number; dx: number; dy: number };

// Daten-Story als Partikel: Punkte = Kundenstimmen, ziehen sich zu Findings zusammen, färben sich in der Ampel
// und werden zur Rangliste. Alle Mengen (Findings, Balken, Scores, Stufen) kommen aus dem Backend.
// Warum Canvas statt DOM/SVG: 1.200 bewegte Punkte bleiben so flüssig, auch auf dem Laptop im Demo.
export const VoiceField = forwardRef<FieldHandle, { data: FieldData }>(function VoiceField({ data }, ref) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const progress = useRef(0);
  const mouse = useRef({ x: -9999, y: -9999 });

  useImperativeHandle(ref, () => ({ setProgress: (p) => { progress.current = p; } }), []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const mobile = window.innerWidth < 768;
    const count = mobile ? 420 : 1200;
    const bars = data.bars.length ? data.bars : Array.from({ length: 12 }, (_, i) => ({ score: 80 - i * 5, level: "B" as EvidenceLevel }));
    const clusters = Math.max(8, Math.min(60, data.findings ?? 40));
    const maxScore = Math.max(...bars.map((b) => b.score), 1);
    // Feste Zufallsfolge, damit das Bild bei jedem Laden gleich aussieht (Demo-Video, Screenshots).
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    // Cluster-Größen ungleich (Potenzverteilung): wenige große Themen, viele kleine, wie in echten Daten.
    const parts: P[] = Array.from({ length: count }, () => {
      const c = Math.floor(Math.pow(rnd(), 1.8) * clusters);
      const angle = rnd() * Math.PI * 2;
      const r = Math.sqrt(rnd());
      return { sx: rnd(), sy: rnd(), cx: c, cy: angle, bar: c % bars.length, t: r, phase: rnd() * 6.28, delay: rnd() * 0.35, dx: 0, dy: 0 };
    });

    let w = 0, h = 0, dpr = 1, raf = 0, visible = true;
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
    };
    resize();

    function frame(time: number) {
      raf = requestAnimationFrame(frame);
      if (!visible || !ctx) return;
      const s = progress.current * 5; // 5 Kapitel
      const toCluster = (k: number) => ease((s - 0.55 - k) / 0.8);
      const toColor = ease((s - 1.7) / 0.6);
      const toBar = (k: number) => ease((s - 2.55 - k) / 0.85);
      // Partikel-Bühne: rechts neben dem Kapiteltext (Desktop), ganze Fläche auf dem Handy.
      const x0 = mobile ? 0.08 * w : 0.5 * w, x1 = mobile ? 0.92 * w : 0.85 * w; // rechts bleibt Platz für die Kapitel-Navigation
      const y0 = 0.14 * h, y1 = 0.8 * h;
      const fw = x1 - x0, fh = y1 - y0;
      const barGap = Math.min(28, (fh * 0.8) / bars.length);
      const barTop = y0 + (fh - barGap * (bars.length - 1)) / 2 - (mobile ? 0 : 0.05 * h);
      const tsec = time / 1000;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      // Rang-Spuren und Nummern erscheinen mit den Balken.
      const barsIn = toBar(0.2);
      if (barsIn > 0.01) {
        ctx.globalAlpha = barsIn;
        ctx.font = "11px system-ui, sans-serif";
        bars.forEach((bar, i) => {
          const y = barTop + i * barGap;
          ctx.fillStyle = "rgba(255,255,255,0.08)";
          ctx.fillRect(x0 + 34, y, fw - 34, 1);
          // Durchgehende Linie in Ampelfarbe: Länge = Score, so liest man die Rangliste auch ohne Punkte.
          const [r, g, b] = RGB[bar.level];
          ctx.fillStyle = `rgba(${r},${g},${b},0.55)`;
          ctx.fillRect(x0 + 40, y, (bar.score / maxScore) * (fw - 40) * barsIn, 2);
          ctx.fillStyle = "rgba(255,255,255,0.45)";
          ctx.fillText(String(i + 1).padStart(2, "0"), x0, y + 4);
        });
      }
      ctx.globalAlpha = mobile ? 0.55 : 1;
      ctx.globalCompositeOperation = "lighter";

      for (const p of parts) {
        // 1) verstreut, leicht atmend
        let x = x0 - 0.1 * fw + p.sx * fw * 1.15 + Math.sin(tsec * 0.6 + p.phase) * 6;
        let y = y0 + p.sy * fh + Math.cos(tsec * 0.5 + p.phase) * 6;
        // 2) Cluster auf einer Sonnenblumen-Spirale (gleichmäßig, ohne Überlappung)
        const ga = p.cx * 2.39996;
        const rr = Math.sqrt((p.cx + 0.5) / clusters);
        const ccx = x0 + fw / 2 + Math.cos(ga) * rr * fw * 0.46;
        const ccy = y0 + fh / 2 + Math.sin(ga) * rr * fh * 0.46;
        const spread = 4 + 14 * Math.sqrt(1 - p.cx / clusters);
        const k1 = toCluster(p.delay);
        x = mix(x, ccx + Math.cos(p.cy) * p.t * spread, k1);
        y = mix(y, ccy + Math.sin(p.cy) * p.t * spread, k1);
        // 3) Balken: Länge = echter Score der Anforderung
        const k2 = toBar(p.delay);
        const len = (bars[p.bar].score / maxScore) * (fw - 40);
        x = mix(x, x0 + 40 + p.t * len, k2);
        y = mix(y, barTop + p.bar * barGap + (p.cy / 6.28 - 0.5) * 3, k2);
        // Maus schiebt Punkte sanft weg, sie federn zurück.
        const mx = x - mouse.current.x, my = y - mouse.current.y;
        const d = Math.hypot(mx, my);
        const push = d < 90 ? ((90 - d) / 90) * 22 : 0;
        p.dx += ((d ? (mx / d) * push : 0) - p.dx) * 0.12;
        p.dy += ((d ? (my / d) * push : 0) - p.dy) * 0.12;

        const level = bars[p.bar].level;
        const [r1, g1, b1] = RGB.blue, [r2, g2, b2] = RGB[level];
        const alpha = mix(0.6, 0.95, Math.max(k1 * 0.6, toColor, k2));
        ctx.fillStyle = `rgba(${mix(r1, r2, toColor) | 0},${mix(g1, g2, toColor) | 0},${mix(b1, b2, toColor) | 0},${alpha})`;
        const size = mix(1.8, 2, k2);
        ctx.fillRect(x + p.dx, y + p.dy, size, size);
      }
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
    }
    raf = requestAnimationFrame(frame);

    // Nur zeichnen, solange die Szene sichtbar ist: spart Akku und CPU auf dem Rest der Seite.
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; });
    io.observe(canvas);
    const onMove = (e: PointerEvent) => {
      const r = canvas.getBoundingClientRect();
      mouse.current = { x: e.clientX - r.left, y: e.clientY - r.top };
    };
    const onLeave = () => { mouse.current = { x: -9999, y: -9999 }; };
    window.addEventListener("pointermove", onMove, { passive: true });
    document.addEventListener("pointerleave", onLeave);
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(raf);
      io.disconnect();
      window.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerleave", onLeave);
      window.removeEventListener("resize", resize);
    };
  }, [data]);

  return (
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_45%,#122036_0%,#0a0a0b_70%)]" aria-hidden="true">
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  );
});
