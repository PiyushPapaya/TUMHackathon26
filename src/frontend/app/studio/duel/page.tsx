"use client";

/**
 * Duell-Modus: Der PM wählt mehrmals die wichtigere von zwei Anforderungen. Aus den Siegern
 * leiten wir Gewichte ab (src/studio/scoring.ts) und zeigen sie neben den aktuellen.
 * Übernehmen geht nur mit Begründung über PUT /weights, damit es im Audit Trail steht.
 * Warum: Viele PMs können "A ist wichtiger als B" sicherer sagen als "Reichweite = 20 %".
 */
import { useMemo, useState } from "react";
import duell from "@/baukasten/duell.json";
import { EvidenceBadge } from "@/src/components/badges";
import { putWeights, type Requirement } from "@/src/lib/api";
import { currentWeights, duelPairs, FACTORS, weightsFromDuels } from "@/src/studio/scoring";
import { PM_ACTOR, useStudio } from "@/src/studio/StudioData";
import { ToolFrame } from "@/src/studio/ToolFrame";
import { Button, ReasonField, reasonIsValid } from "@/src/studio/ui";

type Win = { winner: Requirement; loser: Requirement };

export default function DuelPage() {
  const { requirements, scenarioId, reload } = useStudio();
  const pairs = useMemo(() => duelPairs(requirements, duell.rounds), [requirements]);
  const [wins, setWins] = useState<Win[]>([]);
  const [reason, setReason] = useState("");
  const [saved, setSaved] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const start = currentWeights(requirements[0]);
  const suggested = weightsFromDuels(wins, start);
  const round = wins.length;
  const done = pairs.length > 0 && round >= pairs.length;

  function pick(winner: Requirement, loser: Requirement) {
    setWins((w) => [...w, { winner, loser }]);
  }

  async function apply() {
    setSaveError(null);
    try {
      await putWeights(scenarioId, { weights: suggested, actor: PM_ACTOR, rationale: `Duel (${round} rounds): ${reason}` });
      await reload();
      setSaved("Weights applied. The ranking in the cockpit uses them now, and the change is in the audit trail.");
    } catch (err) {
      setSaveError((err as Error).message);
    }
  }

  const restart = (
    <Button variant="quiet" onClick={() => { setWins([]); setSaved(null); }} disabled={round === 0}>
      Start over
    </Button>
  );

  return (
    <ToolFrame tool="duel" actions={restart}>
      {pairs.length < 1 ? null : !done ? (
        <section aria-live="polite">
          <div className="mb-4 flex items-baseline justify-between gap-4">
            <p className="text-xl font-medium">{duell.question}</p>
            <p className="text-sm tabular-nums text-[var(--ink)]/60">
              Round {round + 1} of {pairs.length}
            </p>
          </div>
          <div className="mb-6 h-1 overflow-hidden rounded-full bg-[var(--ink)]/10">
            <div className="h-full bg-[var(--accent)] transition-all duration-500" style={{ width: `${(round / pairs.length) * 100}%` }} />
          </div>
          <div key={round} className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-stretch">
            <Contender req={pairs[round][0]} onPick={() => pick(pairs[round][0], pairs[round][1])} />
            <span className="self-center text-center text-2xl font-semibold text-[var(--ink)]/40 [font-stretch:125%]">or</span>
            <Contender req={pairs[round][1]} onPick={() => pick(pairs[round][1], pairs[round][0])} />
          </div>
        </section>
      ) : (
        <section className="grid gap-10 lg:grid-cols-[1.2fr_1fr]">
          <div>
            <h2 className="mb-1 text-2xl font-semibold [font-stretch:115%]">What your choices say</h2>
            <p className="mb-6 text-[var(--ink)]/70">
              Grey is the weight today, blue is what your {round} picks suggest. Factors where your winners were always ahead grow.
            </p>
            <div className="space-y-4">
              {FACTORS.map((f) => (
                <div key={f.key}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>{f.label}{f.assumption && <span className="ml-2 text-[var(--assumption)]">assumption</span>}</span>
                    <span className="tabular-nums text-[var(--ink)]/70">
                      {Math.round(start[f.key] * 100)}% → <strong className="text-[var(--accent)]">{Math.round(suggested[f.key] * 100)}%</strong>
                    </span>
                  </div>
                  <div className="relative h-3 rounded-full bg-[var(--ink)]/10">
                    <div className="absolute inset-y-0 left-0 rounded-full bg-[var(--ink)]/25" style={{ width: `${start[f.key] * 100}%` }} />
                    <div className="absolute inset-y-[3px] left-0 rounded-full bg-[var(--accent)] transition-all duration-700" style={{ width: `${suggested[f.key] * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-4 rounded-lg border border-[var(--ink)]/15 bg-white p-6">
            <h2 className="text-lg font-semibold">Apply these weights?</h2>
            <p className="text-sm text-[var(--ink)]/70">The whole list gets re-ranked with them. You can always go back to the default.</p>
            <ReasonField id="duel-reason" value={reason} onChange={setReason} />
            <Button onClick={apply} disabled={!reasonIsValid(reason) || saved !== null}>Apply weights</Button>
            {saved && <p role="status" className="text-sm text-[var(--praise)]">{saved}</p>}
            {saveError && <p role="alert" className="text-sm text-[var(--complaint)]">{saveError}</p>}
          </div>
        </section>
      )}
    </ToolFrame>
  );
}

/** Eine Seite des Duells: groß, ganz klickbar, mit Beleg-Stufe, damit man nicht nur nach Titel wählt. */
function Contender({ req, onPick }: { req: Requirement; onPick: () => void }) {
  return (
    <button
      onClick={onPick}
      className="group flex min-h-64 animate-[duel-in_.35s_ease-out] flex-col justify-between rounded-xl border-2 border-[var(--ink)]/15 bg-white p-7 text-left transition hover:-translate-y-0.5 hover:border-[var(--accent)] focus-visible:border-[var(--accent)] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[var(--accent)]/25 motion-reduce:animate-none motion-reduce:transition-none"
    >
      <div>
        <h3 className="text-2xl font-semibold leading-snug tracking-tight [font-stretch:112%] group-hover:text-[var(--accent)]">{req.title}</h3>
        <p className="mt-3 text-[15px] leading-relaxed text-[var(--ink)]/70">{req.description}</p>
      </div>
      <div className="mt-6 flex items-center justify-between gap-3">
        <EvidenceBadge level={req.evidence_level} reason={req.rationale} />
        <span className="text-sm font-semibold text-[var(--accent)] opacity-0 transition group-hover:opacity-100 group-focus-visible:opacity-100">
          Pick this one
        </span>
      </div>
    </button>
  );
}
