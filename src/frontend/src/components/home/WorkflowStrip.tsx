// Wer macht was: KI autonom vs. Mensch-Pflicht. Der Brief verlangt genau diese Trennung im Workflow.
// Steht im letzten Kapitel der Scroll-Story, direkt nach "Decide.", damit die Verantwortung sichtbar wird.
const WORKFLOW = [
  { stage: "Ingest", human: false, text: "Excel and PDF inputs become evidence IDs." },
  { stage: "Findings", human: false, text: "Recurring signals grouped with quotes." },
  { stage: "Web", human: false, text: "External sources confirm trends." },
  { stage: "Requirements", human: true, text: "AI drafts, PM reviews." },
  { stage: "Prioritization", human: true, text: "Formula ranks, PM asks or tunes." },
  { stage: "Decision", human: true, text: "Approve, reject, edit, challenge." },
  { stage: "Documentation", human: false, text: "Audit trail and memo." },
];

export function WorkflowStrip() {
  return (
    <div>
      <p className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-white/60">
        Who does what
        <span className="flex items-center gap-2"><span className="h-2 w-2 bg-white/30" /> AI autonomous</span>
        <span className="flex items-center gap-2"><span className="h-2 w-2 bg-[var(--blue)]" /> PM in control</span>
      </p>
      <ol className="mt-3 grid grid-cols-2 gap-px bg-white/10 sm:grid-cols-4 lg:grid-cols-7">
        {WORKFLOW.map((step, i) => (
          <li key={step.stage} className={`p-4 backdrop-blur-sm ${step.human ? "bg-[var(--blue)]/85" : "bg-black/60"}`}>
            <p className="text-[11px] tabular-nums text-white/60">0{i + 1}</p>
            <p className="mt-1 text-sm font-semibold text-white">{step.stage}</p>
            <p className="mt-1 hidden text-[11px] leading-snug text-white/70 md:block">{step.text}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
