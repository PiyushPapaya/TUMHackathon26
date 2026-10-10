"use client";

import { useEffect, useRef, useState } from "react";

type Manifest = { count: number; pattern: string; width: number; height: number };
export type FrameStatus = "loading" | "ready" | "fallback";

function frameUrl(m: Manifest, i: number) {
  return m.pattern.replace("%04d", String(i + 1).padStart(4, "0"));
}

// Lädt die Auto-Frames progressiv: erst jedes 4. Bild (schnell sichtbar), dann die Lücken.
// Auf dem Handy (< 768 px) nur jedes 2. Bild, das spart Daten und Speicher.
export function useCarFrames() {
  const frames = useRef<(HTMLImageElement | undefined)[]>([]);
  const manifest = useRef<Manifest | null>(null);
  const [state, setState] = useState<{ status: FrameStatus; progress: number }>({ status: "loading", progress: 0 });

  useEffect(() => {
    let cancelled = false;

    async function load(m: Manifest) {
      const stride = window.innerWidth < 768 ? 2 : 1;
      const wanted: number[] = [];
      for (let i = 0; i < m.count; i += stride) wanted.push(i);
      const first = wanted.filter((_, k) => k % 4 === 0);
      const rest = wanted.filter((_, k) => k % 4 !== 0);

      const fetchOne = (i: number) =>
        new Promise<void>((resolve) => {
          const img = new Image();
          img.onload = () => {
            frames.current[i] = img;
            resolve();
          };
          img.onerror = () => resolve();
          img.src = frameUrl(m, i);
        });

      let done = 0;
      const run = async (list: number[], report: boolean) => {
        let next = 0;
        const worker = async () => {
          while (!cancelled && next < list.length) {
            await fetchOne(list[next++]);
            if (report && !cancelled) {
              done += 1;
              setState({ status: "loading", progress: done / list.length });
            }
          }
        };
        await Promise.all(Array.from({ length: 6 }, worker));
      };

      await run(first, true);
      if (cancelled) return;
      setState({ status: frames.current.some(Boolean) ? "ready" : "fallback", progress: 1 });
      await run(rest, false);
    }

    fetch("/media-manifest")
      .then((r) => r.json())
      .then((data) => {
        if (cancelled) return;
        if (!data.available || !data.count) {
          setState({ status: "fallback", progress: 1 });
          return;
        }
        manifest.current = data as Manifest;
        return load(data as Manifest);
      })
      .catch(() => !cancelled && setState({ status: "fallback", progress: 1 }));

    return () => {
      cancelled = true;
    };
  }, []);

  return { frames, manifest, ...state };
}
