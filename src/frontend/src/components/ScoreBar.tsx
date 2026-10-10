export function ScoreBar({ score, source }: { score: number; source?: string }) {
  const width = Math.max(0, Math.min(100, score));
  return (
    <div className="min-w-36">
      <div className="flex items-center gap-3">
        <div className="h-2.5 w-28 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
          <div className="h-full rounded-full bg-score-slider" style={{ width: `${width}%` }} />
        </div>
        <span className="w-11 text-right text-sm font-semibold text-foreground">
          {score.toFixed(1)}
        </span>
      </div>
      {source && <p className="mt-1 text-[11px] text-zinc-500 dark:text-zinc-400">{source}</p>}
    </div>
  );
}
