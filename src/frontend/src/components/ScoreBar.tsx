/**
 * Horizontaler Balken für den Score (0-100) mit Zahl daneben, Akzentfarbe Blau
 * nach Design-Regel. Eigene Datei, weil Liste (D2) und Score-Wasserfall (D3)
 * dieselbe Balken-Optik brauchen.
 */
export function ScoreBar({ score }: { score: number }) {
  const width = Math.max(0, Math.min(100, score));
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-28 overflow-hidden rounded-full bg-zinc-200">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${width}%` }} />
      </div>
      <span className="w-10 text-right text-sm font-medium text-[#0b1f3a]">
        {Math.round(score)}
      </span>
    </div>
  );
}
