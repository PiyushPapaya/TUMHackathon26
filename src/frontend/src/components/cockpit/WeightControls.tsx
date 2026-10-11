"use client";

import type { WeightKey } from "@/src/lib/api";
import { Button } from "@/src/components/ui/Button";
import { Icon } from "@/src/components/ui/Icon";
import { WEIGHT_LABELS } from "./useCockpit";

// Feintuning für Profis, standardmäßig zugeklappt: Im Demo fragt der PM in eigenen Worten,
// die Slider sind nur die Lupe darunter. Die Begründung baut useCockpit automatisch aus dem Diff.
export function WeightControls({
  weights,
  onChange,
  applying,
  onApply,
  onReset,
}: {
  weights: Record<WeightKey, number>;
  onChange: (next: Record<WeightKey, number>) => void;
  applying: boolean;
  onApply: () => void;
  onReset: () => void;
}) {
  return (
    <details className="group border-b border-[var(--hairline)]">
      <summary className="flex cursor-pointer list-none items-center justify-between py-4 text-sm font-semibold text-[var(--ink)] hover:text-[var(--blue)]">
        <span className="flex items-center gap-3">
          <Icon name="sliders" size={18} />
          Fine-tune weights
        </span>
        <Icon name="down" size={16} className="transition-transform group-open:rotate-180" />
      </summary>
      <div className="grid gap-x-10 gap-y-4 pb-6 sm:grid-cols-2 lg:grid-cols-3">
        {(Object.keys(WEIGHT_LABELS) as WeightKey[]).map((key) => (
          <label key={key} className="grid gap-1 text-sm text-[var(--ink)]">
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
      <div className="flex flex-wrap items-center gap-3 pb-6">
        <Button disabled={applying} onClick={onApply}>{applying ? "Applying..." : "Apply weights"}</Button>
        <Button variant="outline" disabled={applying} onClick={onReset}>Reset to default</Button>
        <p className="text-xs text-[var(--grey-500)]">The change itself is recorded as the rationale.</p>
      </div>
    </details>
  );
}
