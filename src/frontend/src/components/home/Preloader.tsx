"use client";

import { useEffect, useState } from "react";

// Dünne blaue Linie plus Prozent, bis Poster und Frames geladen sind. Nach 2,5 s verschwindet sie in jedem Fall,
// damit eine langsame Leitung die Seite nie blockiert.
export function Preloader({ progress, done }: { progress: number; done: boolean }) {
  const [timedOut, setTimedOut] = useState(false);
  useEffect(() => {
    const t = window.setTimeout(() => setTimedOut(true), 2500);
    return () => window.clearTimeout(t);
  }, []);
  const hidden = done || timedOut;
  return (
    <div
      aria-hidden={hidden}
      className={`fixed inset-0 z-[60] flex flex-col items-center justify-center bg-[var(--black)] text-white transition-opacity duration-700 ${
        hidden ? "pointer-events-none opacity-0" : "opacity-100"
      }`}
    >
      <p className="text-sm tabular-nums tracking-[0.2em]">{Math.round(progress * 100)}%</p>
      <div className="mt-4 h-px w-48 bg-white/20">
        <div className="h-full bg-[var(--blue)] transition-[width] duration-200" style={{ width: `${progress * 100}%` }} />
      </div>
    </div>
  );
}
