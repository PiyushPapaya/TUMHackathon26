"use client";

import { useState } from "react";
import Link from "next/link";
import type { Weights } from "@/src/lib/api";
import { postLens, type LensResult } from "@/src/lib/insights";
import { Button } from "@/src/components/ui/Button";
import { EvidenceDot } from "@/src/components/badges";
import { Icon } from "@/src/components/ui/Icon";
import { PM_ACTOR, WEIGHT_LABELS } from "./useCockpit";

const EXAMPLES = ["Families in the US, focus on charging and space", "What matters most for the 2030 successor?", "Where are we weakest against competitors?"];

// Prompt-Linse: Der PM fragt in eigenen Worten. Die KI liefert nur Gewichte und Filter, nie IDs,
// Python rechnet die Top 5 auf Kopien. Erst "Apply" schreibt in den Prüfpfad, und die Frage selbst
// wird dort als Begründung gespeichert. Darum braucht das Cockpit kein eigenes Rationale-Feld.
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

  function apply() {
    if (!result) return;
    onApply(result.weights, result.question);
    // Vorschau schließen: Der Blick soll auf die Rangliste fallen, die gerade neu sortiert wird.
    setResult(null);
  }

  return (
    <section className="relative mb-8 overflow-hidden bg-[var(--black)] p-6 text-white sm:p-10">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_85%_0%,#1b2a3f_0%,transparent_60%)]" aria-hidden="true" />
      <div className="relative">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-white/60">
          <Icon name="chat" size={16} /> Ask in your own words
        </p>
        <form
          className="mt-5 flex flex-wrap gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            ask(question);
          }}
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What should the next model get right?"
            aria-label="Question for the prioritization lens"
            className="h-[60px] min-w-64 flex-1 border border-white/25 bg-white/5 px-5 text-lg font-light text-white placeholder:text-white/40 focus:border-[var(--m-light)] focus:outline-none"
          />
          <Button type="submit" disabled={busy} className="h-[60px]">{busy ? "Thinking..." : "Ask"}</Button>
        </form>
        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => { setQuestion(ex); ask(ex); }}
              className="border border-white/20 px-3 py-1.5 text-xs text-white/80 transition-colors hover:border-white hover:text-white"
            >
              {ex}
            </button>
          ))}
        </div>
        {error && <p role="alert" className="mt-4 text-sm text-[var(--m-light)]">{error}</p>}

        {result && (
          <div className="animate-funnel mt-8 grid gap-8 border-t border-white/15 pt-8 lg:grid-cols-[1fr_1.2fr]">
            <div>
              <p className="text-xl font-light leading-snug">{result.interpretation}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {Object.entries(result.weights).map(([k, v]) => (
                  <span key={k} className="border border-white/20 px-2 py-1 text-[11px] tabular-nums text-white/70">
                    {WEIGHT_LABELS[k as keyof typeof WEIGHT_LABELS] ?? k} {Number(v).toFixed(2)}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-[11px] uppercase tracking-[0.12em] text-white/40">
                {result.source === "ai" ? "AI interpretation" : "Rule-based interpretation"} · AI sets weights only, Python ranks
              </p>
            </div>
            <div>
              <ol className="grid gap-px bg-white/10">
                {result.top.map((t) => (
                  <li key={t.requirement.id} className="flex items-center gap-4 bg-[var(--black)] py-3">
                    <span className="w-6 text-2xl font-light tabular-nums text-white/60">{t.lens_rank}</span>
                    <EvidenceDot level={t.requirement.evidence_level} />
                    <Link href={`/requirements/${t.requirement.id}`} title={t.reasons.map((r) => r.sentence).join(" · ")} className="flex-1 hover:text-[var(--m-light)]">
                      {t.requirement.title}
                    </Link>
                  </li>
                ))}
              </ol>
              <div className="mt-6 flex flex-wrap items-center gap-4">
                <Button disabled={applying} onClick={apply}>Apply &amp; re-rank</Button>
                <p className="text-xs text-white/50">Your question is saved as the rationale in the audit trail.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
