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
    <a className="font-semibold text-blue-700 underline underline-offset-2" href={`#evidence-${id}`}>
      {id}
    </a>
  );
}

function AiAnswerBox({ answer }: { answer: AiAnswer }) {
  return (
    <section className="rounded-lg border border-blue-200 bg-blue-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">AI challenge answer</p>
      <p className="mt-2 text-sm text-blue-950">{answer.answer}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border border-blue-200 bg-white p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Supporting evidence</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {answer.supporting_evidence_ids.length ? (
              answer.supporting_evidence_ids.map((id) => <EvidenceIdLink key={id} id={id} />)
            ) : (
              <span className="text-slate-500">None cited.</span>
            )}
          </div>
        </div>
        <div className="rounded-md border border-yellow-300 bg-yellow-50 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-yellow-800">Counter evidence</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {answer.counter_evidence_ids.length ? (
              answer.counter_evidence_ids.map((id) => <EvidenceIdLink key={id} id={id} />)
            ) : (
              <span className="text-slate-600">None cited.</span>
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
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            PM decision
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Actor: <span className="font-semibold text-[#0b1f3a]">{PM_ACTOR}</span>. A rationale is required.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(["approve", "reject", "edit", "challenge"] as const).map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => setMode(action)}
              className={`min-h-11 rounded-md border px-3 text-sm font-semibold capitalize transition focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                mode === action
                  ? "border-blue-600 bg-blue-600 text-white"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {isEdit && (
        <div className="mt-4 grid gap-3">
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Title
            <input
              className="min-h-11 rounded-md border border-slate-300 px-3 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              value={draft.title}
              onChange={(event) => setDraft((value) => ({ ...value, title: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Description
            <textarea
              className="min-h-24 rounded-md border border-slate-300 px-3 py-2 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              value={draft.description}
              onChange={(event) => setDraft((value) => ({ ...value, description: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Acceptance criterion
            <textarea
              className="min-h-20 rounded-md border border-slate-300 px-3 py-2 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              value={draft.acceptance_criterion}
              onChange={(event) =>
                setDraft((value) => ({ ...value, acceptance_criterion: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700 sm:max-w-40">
            Effort
            <select
              className="min-h-11 rounded-md border border-slate-300 px-3 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
                className="min-h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
              >
                {preset}
              </button>
            ))}
          </div>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">
            Challenge question
            <textarea
              className="min-h-20 rounded-md border border-slate-300 px-3 py-2 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>
        </div>
      )}

      <label className="mt-4 grid gap-1 text-sm font-semibold text-slate-700">
        Rationale
        <textarea
          required
          className="min-h-24 rounded-md border border-slate-300 px-3 py-2 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
          className="min-h-11 rounded-md bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {busy ? "Saving..." : `Submit ${mode}`}
        </button>
        {!rationaleReady && (
          <p className="text-sm text-slate-500">Enter at least 3 characters of rationale.</p>
        )}
        {error && <p className="text-sm font-semibold text-rose-700">{error}</p>}
      </div>

      {aiAnswer && (
        <div className="mt-4">
          <AiAnswerBox answer={aiAnswer} />
        </div>
      )}
    </section>
  );
}
