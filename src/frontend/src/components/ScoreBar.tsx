/**
 * Horizontaler Balken für den Score (0-100) mit Zahl daneben, Akzentfarbe Blau
 * nach Design-Regel. Eigene Datei, weil Liste (D2) und Score-Wasserfall (D3)
 * dieselbe Balken-Optik brauchen.
 */
export function ScoreBar({ score }: { score: number }) {
  const width = Math.max(0, Math.min(100, score));
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-28 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
        <div className="h-full rounded-full bg-score-slider" style={{ width: `${width}%` }} />
      </div>
      <span className="w-10 text-right text-sm font-medium text-foreground">
        {Math.round(score)}
      </span>
    </div>
  );
}
