"use client";

import { useMemo, useState } from "react";
import {
  postDecision,
  type AiAnswer,
  type Effort,
  type Requirement,
  type RequirementEditableChanges,
} from "@/src/lib/api";

const PM_ACTOR = "pm.demo";
const CHALLENGE_QUESTIONS = [
  "Is this only a US issue?",
  "Is this just a habit of older customers?",
  "What speaks against it?",
];

function EvidenceIdLink({ id }: { id: string }) {
  return (
    <a className="font-semibold text-accent-hover dark:text-accent underline underline-offset-2" href={`#evidence-${id}`}>
      {id}
    </a>
  );
}

function AiAnswerBox({ answer }: { answer: AiAnswer }) {
  return (
    <section className="rounded-lg border border-accent/30 dark:border-accent/40 bg-accent/5 dark:bg-accent/10 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent-hover dark:text-accent">AI challenge answer</p>
      <p className="mt-2 text-sm text-foreground">{answer.answer}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div className="rounded-sm border border-accent/30 dark:border-accent/40 bg-surface p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Supporting evidence</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {answer.supporting_evidence_ids.length ? (
              answer.supporting_evidence_ids.map((id) => <EvidenceIdLink key={id} id={id} />)
            ) : (
              <span className="text-zinc-500 dark:text-zinc-400">None cited.</span>
            )}
          </div>
        </div>
        <div className="rounded-sm border border-yellow-300 bg-yellow-50 p-3 dark:border-yellow-800 dark:bg-yellow-950">
          <p className="text-xs font-semibold uppercase tracking-wide text-yellow-800 dark:text-yellow-300">Counter evidence</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {answer.counter_evidence_ids.length ? (
              answer.counter_evidence_ids.map((id) => <EvidenceIdLink key={id} id={id} />)
            ) : (
              <span className="text-zinc-600 dark:text-zinc-400">None cited.</span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export function DecisionPanel({
  requirement,
  onChanged,
}: {
  requirement: Requirement;
  onChanged: () => Promise<void> | void;
}) {
  const [mode, setMode] = useState<"approve" | "reject" | "edit" | "challenge">("approve");
  const [rationale, setRationale] = useState("");
  const [question, setQuestion] = useState(CHALLENGE_QUESTIONS[0]);
  const [aiAnswer, setAiAnswer] = useState<AiAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState({
    title: requirement.title,
    description: requirement.description,
    acceptance_criterion: requirement.acceptance_criterion,
    effort: requirement.effort,
  });

  const rationaleReady = rationale.trim().length >= 3;
  const isEdit = mode === "edit";
  const isChallenge = mode === "challenge";

  const changes = useMemo<RequirementEditableChanges>(() => {
    const output: RequirementEditableChanges = {};
    if (draft.title.trim() !== requirement.title) output.title = draft.title.trim();
    if (draft.description.trim() !== requirement.description) output.description = draft.description.trim();
    if (draft.acceptance_criterion.trim() !== requirement.acceptance_criterion) {
      output.acceptance_criterion = draft.acceptance_criterion.trim();
    }
    if (draft.effort !== requirement.effort) output.effort = draft.effort;
    return output;
  }, [draft, requirement]);

  async function submit() {
    if (!rationaleReady || busy) return;
    setBusy(true);
    setError(null);
    setAiAnswer(null);
    try {
      const result = await postDecision(requirement.id, {
        action: mode,
        actor: PM_ACTOR,
        rationale: rationale.trim(),
        changes: isEdit ? changes : undefined,
        question: isChallenge ? question.trim() || rationale.trim() : undefined,
      });
      setAiAnswer(result.ai_answer);
      setRationale("");
      await onChanged();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            PM decision
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Actor: <span className="font-semibold text-foreground">{PM_ACTOR}</span>. A rationale is required.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(["approve", "reject", "edit", "challenge"] as const).map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => setMode(action)}
              className={`min-h-11 rounded-sm border px-3 text-sm font-semibold capitalize transition focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background ${
                mode === action
                  ? "border-accent bg-accent text-white"
                  : "border-zinc-300 dark:border-zinc-700 bg-surface text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-900"
              }`}
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {isEdit && (
        <div className="mt-4 grid gap-3">
          <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
            Title
            <input
              className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 font-normal text-foreground focus:border-accent focus:outline-none"
              value={draft.title}
              onChange={(event) => setDraft((value) => ({ ...value, title: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
            Description
            <textarea
              className="min-h-24 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 py-2 font-normal text-foreground focus:border-accent focus:outline-none"
              value={draft.description}
              onChange={(event) => setDraft((value) => ({ ...value, description: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
            Acceptance criterion
            <textarea
              className="min-h-20 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 py-2 font-normal text-foreground focus:border-accent focus:outline-none"
              value={draft.acceptance_criterion}
              onChange={(event) =>
                setDraft((value) => ({ ...value, acceptance_criterion: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300 sm:max-w-40">
            Effort
            <select
              className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 font-normal text-foreground focus:border-accent focus:outline-none"
              value={draft.effort}
              onChange={(event) =>
                setDraft((value) => ({ ...value, effort: event.target.value as Effort }))
              }
            >
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
            </select>
          </label>
        </div>
      )}

      {isChallenge && (
        <div className="mt-4 grid gap-3">
          <div className="flex flex-wrap gap-2">
            {CHALLENGE_QUESTIONS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => setQuestion(preset)}
                className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-3 text-sm font-semibold text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              >
                {preset}
              </button>
            ))}
          </div>
          <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
            Challenge question
            <textarea
              className="min-h-20 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 py-2 font-normal text-foreground focus:border-accent focus:outline-none"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>
        </div>
      )}

      <label className="mt-4 grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
        Rationale
        <textarea
          required
          className="min-h-24 rounded-sm border border-zinc-300 dark:border-zinc-700 px-3 py-2 font-normal text-foreground focus:border-accent focus:outline-none"
          placeholder="Why is this decision justified?"
          value={rationale}
          onChange={(event) => setRationale(event.target.value)}
        />
      </label>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={submit}
          disabled={!rationaleReady || busy}
          className="min-h-11 rounded-sm bg-accent px-5 text-sm font-semibold text-white transition hover:bg-accent-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:bg-zinc-300 dark:disabled:bg-zinc-700"
        >
          {busy ? "Saving..." : `Submit ${mode}`}
        </button>
        {!rationaleReady && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Enter at least 3 characters of rationale.</p>
        )}
        {error && <p className="text-sm font-semibold text-rose-700 dark:text-rose-400">{error}</p>}
      </div>

      {aiAnswer && (
        <div className="mt-4">
          <AiAnswerBox answer={aiAnswer} />
        </div>
      )}
    </section>
  );
}
