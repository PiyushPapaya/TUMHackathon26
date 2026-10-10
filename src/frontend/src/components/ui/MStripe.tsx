// Dreifarbiger Streifen (hellblau, dunkelblau, rot) als Signatur-Detail.
// Eigenes Design in BMW-Nähe, kein Logo. Dient als Header-Linie und Fortschrittsbalken.
export function MStripe({ className = "", progress }: { className?: string; progress?: number }) {
  const style = progress === undefined ? undefined : { width: `${Math.round(progress * 100)}%` };
  return (
    <div className={`flex h-[3px] overflow-hidden ${className}`} style={style} aria-hidden="true">
      <span className="flex-1" style={{ background: "var(--m-light)" }} />
      <span className="flex-1" style={{ background: "var(--m-dark)" }} />
      <span className="flex-1" style={{ background: "var(--m-red)" }} />
    </div>
  );
}
