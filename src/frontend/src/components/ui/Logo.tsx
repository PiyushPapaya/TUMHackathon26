// Eigene "Signal-Marke": Kreis mit zwei blauen Vierteln und einer Signalwelle.
// Bewusst kein BMW-Roundel, damit es keine Markenprobleme gibt.
export function Logo({ light, size = 32 }: { light?: boolean; size?: number }) {
  const ink = light ? "#ffffff" : "#262626";
  return (
    <span className="inline-flex items-center gap-3">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
        <circle cx="16" cy="16" r="14.5" fill="none" stroke={ink} strokeWidth="1.5" />
        <path d="M16 16V1.5A14.5 14.5 0 0 1 30.5 16z" fill="#1c69d4" />
        <path d="M16 16V30.5A14.5 14.5 0 0 1 1.5 16z" fill="#81c4ff" />
        <path d="M7 16c2-5 4-5 5 0s3 5 5 0 3-5 4 0" fill="none" stroke={ink} strokeWidth="1.5" />
      </svg>
      <span className={`text-lg font-semibold tracking-tight ${light ? "text-white" : "text-[var(--ink)]"}`}>Signal2Spec</span>
    </span>
  );
}
