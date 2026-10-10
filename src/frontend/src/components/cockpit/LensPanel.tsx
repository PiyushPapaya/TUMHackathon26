"use client";

import { useState } from "react";
import Link from "next/link";
import type { Weights } from "@/src/lib/api";
import { postLens, type LensResult } from "@/src/lib/insights";
import { Button } from "@/src/components/ui/Button";
import { EvidenceBadge } from "@/src/components/badges";
import { PM_ACTOR, WEIGHT_LABELS } from "./useCockpit";

const EXAMPLES = ["Families in the US, focus on charging and space", "What matters most for the 2030 successor?", "Where are we weakest against competitors?"];

// Prompt-Linse: Der PM fragt in eigenen Worten. Die KI liefert nur Gewichte und Filter, nie IDs,
// Python rechnet die Top 5 auf Kopien. Erst "Apply" schreibt in den Prüfpfad, der PM behält die Kontrolle.
export function LensPanel({
  scenarioId,
  onApply,
  applying,
}: {
  scenarioId: string;
  onApply: (weights: Weights, question: string) => void;
  applying: boolean;
}) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<LensResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(text: string) {
    if (!text.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await postLens(scenarioId, text.trim(), PM_ACTOR));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mb-10 border border-[var(--hairline)] bg-white p-6">
      <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]">Ask in your own words</h2>
      <form
        className="mt-4 flex flex-wrap gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          ask(question);
        }}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Families in the US, focus on charging and space"
          aria-label="Question for the prioritization lens"
          className="h-[52px] min-w-64 flex-1 border border-[var(--hairline)] px-4"
        />
        <Button type="submit" disabled={busy}>{busy ? "Thinking..." : "Re-rank"}</Button>
      </form>
      <div className="mt-3 flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button key={ex} type="button" onClick={() => { setQuestion(ex); ask(ex); }} className="border border-[var(--hairline)] px-3 py-1.5 text-xs hover:border-[var(--ink)]">
            {ex}
          </button>
        ))}
      </div>
      {error && <p role="alert" className="mt-4 text-sm text-[var(--m-red)]">{error}</p>}
      {result && (
        <div className="mt-6 border-t border-[var(--hairline)] pt-6">
          <p className="text-sm">
            <span className="mr-2 border border-[var(--hairline)] px-2 py-0.5 text-xs font-semibold">{result.source === "ai" ? "AI interpretation" : "Rule-based"}</span>
            {result.interpretation}
          </p>
          <p className="mt-2 text-xs text-[var(--grey-500)]">
            Suggested weights: {Object.entries(result.weights).map(([k, v]) => `${WEIGHT_LABELS[k as keyof typeof WEIGHT_LABELS] ?? k} ${Number(v).toFixed(2)}`).join(" · ")}
          </p>
          <ol className="mt-4 grid gap-3">
            {result.top.map((t) => (
              <li key={t.requirement.id} className="flex flex-wrap items-baseline gap-3 border-t border-[var(--hairline)] pt-3">
                <span className="text-2xl font-light tabular-nums">{t.lens_rank}</span>
                <Link href={`/requirements/${t.requirement.id}`} className="flex-1 hover:text-[var(--blue)]">{t.requirement.title}</Link>
                <EvidenceBadge level={t.requirement.evidence_level} />
                <span className="w-full pl-9 text-xs text-[var(--grey-500)]">{t.reasons.map((r) => r.sentence).join(" · ")}</span>
              </li>
            ))}
          </ol>
          <p className="mt-4 text-xs text-[var(--grey-500)]">Nothing is stored yet. Apply these weights to re-rank the list and record your rationale.</p>
          <div className="mt-3">
            <Button disabled={applying} onClick={() => onApply(result.weights, result.question)}>Apply these weights</Button>
          </div>
        </div>
      )}
    </section>
  );
}
