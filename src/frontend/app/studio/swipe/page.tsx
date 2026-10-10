"use client";

/**
 * Entscheidungslauf: offene Anforderungen nacheinander, freigeben oder ablehnen, immer mit Begründung.
 * Schreibt über POST /decision, also landet jede Entscheidung mit Name und Grund im Audit Trail.
 * Warum eine Karte nach der anderen: Der PM soll jede Anforderung einzeln ansehen, nicht die Liste abhaken.
 */
import { useState } from "react";
import { EvidenceBadge } from "@/src/components/badges";
import { postDecision, type DecisionAction } from "@/src/lib/api";
import { PM_ACTOR, useStudio } from "@/src/studio/StudioData";
import { ToolFrame } from "@/src/studio/ToolFrame";
import { AssumptionList, Button, Notice, QuoteCard, ReasonField, reasonIsValid } from "@/src/studio/ui";

export default function SwipePage() {
  const { requirements, signals, evidenceById, reload } = useStudio();
  const [reason, setReason] = useState("");
  const [leaving, setLeaving] = useState<"left" | "right" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [last, setLast] = useState<string | null>(null);

  const open = requirements.filter((r) => r.status === "proposed" || r.status === "challenged");
  const current = open[0];
  const decided = requirements.length - open.length;

  async function decide(action: Extract<DecisionAction, "approve" | "reject">) {
    if (!current) return;
    setError(null);
    setLeaving(action === "approve" ? "right" : "left");
    try {
      await postDecision(current.id, { action, actor: PM_ACTOR, rationale: reason.trim() });
      setLast(`${action === "approve" ? "Approved" : "Rejected"}: ${current.title}`);
      setReason("");
      await reload();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLeaving(null);
    }
  }

  const progress = (
    <p className="text-sm tabular-nums text-[var(--ink)]/60">
      {decided} of {requirements.length} decided
    </p>
  );

  const quotes = current
    ? signals
        .filter((s) => current.signal_ids.includes(s.id))
        .flatMap((s) => s.evidence_ids)
        .map((id) => evidenceById.get(id))
        .filter((e) => e !== undefined)
        .slice(0, 2)
    : [];

  return (
    <ToolFrame tool="swipe" actions={progress}>
      {last && <p role="status" className="mb-4 text-sm text-[var(--ink)]/70">{last}. Saved to the audit trail.</p>}
      {!current ? (
        <Notice kind="empty">Every requirement has a decision. Open the cockpit to see the final list, or export it as CSV there.</Notice>
      ) : (
        <article
          key={current.id}
          className={`mx-auto max-w-3xl rounded-xl border border-[var(--ink)]/15 bg-white p-6 shadow-[0_1px_0_rgba(11,31,58,0.06)] sm:p-9 ${
            leaving === "right" ? "animate-[leave-right_.3s_ease-in_forwards]" : leaving === "left" ? "animate-[leave-left_.3s_ease-in_forwards]" : "animate-[duel-in_.3s_ease-out]"
          }`}
        >
          <div className="flex flex-wrap items-center gap-3 text-sm text-[var(--ink)]/60">
            <span className="font-semibold tabular-nums text-[var(--ink)]">Rank {current.rank}</span>
            <span className="tabular-nums">Score {current.score}</span>
            <EvidenceBadge level={current.evidence_level} reason={current.rationale} />
          </div>
          <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight [font-stretch:115%]">{current.title}</h2>
          <p className="mt-3 text-[var(--ink)]/75">{current.description}</p>
          <div className="mt-5 rounded-lg border-l-4 border-[var(--accent)] bg-[var(--paper)] px-4 py-3">
            <p className="text-sm font-medium">How we would test it</p>
            <p className="mt-1">{current.acceptance_criterion}</p>
          </div>

          {quotes.length > 0 && (
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {quotes.map((e) => <QuoteCard key={e.id} evidence={e} />)}
            </div>
          )}

          <div className="mt-6">
            <AssumptionList items={current.assumptions} />
          </div>

          <div className="mt-8 space-y-4 border-t border-[var(--ink)]/10 pt-6">
            <ReasonField id="swipe-reason" value={reason} onChange={setReason} />
            <div className="flex flex-wrap justify-between gap-3">
              <Button variant="complaint" onClick={() => decide("reject")} disabled={!reasonIsValid(reason) || leaving !== null}>
                Reject
              </Button>
              <Button variant="praise" onClick={() => decide("approve")} disabled={!reasonIsValid(reason) || leaving !== null}>
                Approve
              </Button>
            </div>
            {!reasonIsValid(reason) && <p className="text-xs text-[var(--ink)]/55">Write a short reason to unlock the buttons.</p>}
            {error && <p role="alert" className="text-sm text-[var(--complaint)]">{error}</p>}
          </div>
        </article>
      )}
    </ToolFrame>
  );
}
