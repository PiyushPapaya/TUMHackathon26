// Eigene Marke "ReSpec": drei unruhige Wellen (Kundenstimmen) laufen zu einer geraden Linie mit Punkt zusammen
// (die Anforderung). Quadrat mit 0 px Radius im BMW-Blau-Verlauf. Bewusst kein Roundel, damit es keine Markenprobleme gibt.
export function LogoMark({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" className="shrink-0">
      <defs>
        <linearGradient id="respec-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1c69d4" />
          <stop offset="1" stopColor="#16588e" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" fill="url(#respec-g)" />
      <g fill="none" stroke="#fff" strokeWidth="1.6" strokeLinecap="round">
        <path d="M5 9c3-2 5 3 8 2s5 2 7 5" opacity="0.55" />
        <path d="M5 16c3-4 5 4 8 0s5 0 7 0" opacity="0.8" />
        <path d="M5 23c3 2 5-3 8-2s5-2 7-5" opacity="0.55" />
        <path d="M20 16h5" />
      </g>
      <circle cx="26.6" cy="16" r="1.9" fill="#81c4ff" />
    </svg>
  );
}

export function Logo({ light, size = 32 }: { light?: boolean; size?: number }) {
  return (
    <span className="inline-flex items-center gap-3">
      <LogoMark size={size} />
      <span className={`text-lg tracking-tight ${light ? "text-white" : "text-[var(--ink)]"}`}>
        <span className="font-light">Re</span>
        <span className={`font-semibold ${light ? "text-[var(--m-light)]" : "text-[var(--blue)]"}`}>Spec</span>
      </span>
    </span>
  );
}
