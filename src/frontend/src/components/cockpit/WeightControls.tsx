"use client";

import type { WeightKey } from "@/src/lib/api";
import { Button } from "@/src/components/ui/Button";
import { DEMO_RATIONALE, WEIGHT_LABELS } from "./useCockpit";

export function WeightControls({
  weights,
  onChange,
  rationale,
  onRationale,
  applying,
  onApply,
  onReset,
}: {
  weights: Record<WeightKey, number>;
  onChange: (next: Record<WeightKey, number>) => void;
  rationale: string;
  onRationale: (v: string) => void;
  applying: boolean;
  onApply: () => void;
  onReset: () => void;
}) {
  return (
    <section className="border border-[var(--hairline)] bg-white p-6">
      <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]">Weight controls</h2>
      <p className="mt-3 text-sm text-[var(--grey-500)]">
        Move sliders and press Apply. An empty rationale uses a demo rationale and still records WEIGHTS_CHANGED.
      </p>
      <div className="mt-5 grid gap-4">
        {(Object.keys(WEIGHT_LABELS) as WeightKey[]).map((key) => (
          <label key={key} className="grid gap-1 text-sm font-semibold text-[var(--ink)]">
            <span className="flex items-center justify-between gap-3">
              {WEIGHT_LABELS[key]}
              <span className="text-xs font-semibold tabular-nums text-[var(--grey-500)]">{weights[key].toFixed(2)}</span>
            </span>
            <input
              type="range"
              className="bmw-range"
              min="0"
              max="0.6"
              step="0.01"
              value={weights[key]}
              onChange={(e) => onChange({ ...weights, [key]: Number(e.target.value) })}
            />
          </label>
        ))}
      </div>
      <label className="mt-5 grid gap-1 text-sm font-semibold text-[var(--ink)]">
        Rationale
        <textarea
          className="min-h-24 border border-[var(--hairline)] px-3 py-2 font-normal text-[var(--ink)]"
          placeholder="Why should the prioritization change?"
          value={rationale}
          onChange={(e) => onRationale(e.target.value)}
        />
      </label>
      <button
        type="button"
        onClick={() => onRationale(DEMO_RATIONALE)}
        className="mt-2 text-sm font-semibold text-[var(--blue)] hover:text-[var(--blue-hover)]"
      >
        Use demo rationale
      </button>
      <div className="mt-5 flex flex-wrap gap-3">
        <Button disabled={applying} onClick={onApply}>{applying ? "Applying..." : "Apply weights"}</Button>
        <Button variant="outline" onClick={onReset}>Reset to default</Button>
      </div>
    </section>
  );
}
