// Dünne blaue Score-Linie (BMW-Hairline-Stil) statt dickem, rundem Balken.
export function ScoreBar({ score, source }: { score: number; source?: string }) {
  const width = Math.max(0, Math.min(100, score));
  return (
    <div className="min-w-36">
      <div className="flex items-center gap-3">
        <div className="h-[2px] w-28 bg-[var(--hairline)]">
          <div className="h-full bg-[var(--blue)]" style={{ width: `${width}%` }} />
        </div>
        <span className="w-11 text-right text-sm font-semibold text-[#262626]">{score.toFixed(1)}</span>
      </div>
      {source && <p className="mt-1 text-[11px] text-slate-500">{source}</p>}
    </div>
  );
}
