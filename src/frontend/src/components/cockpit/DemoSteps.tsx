const STEPS = [
  "Pick a scenario and scan the ranked list.",
  "Open a row to inspect evidence, assumptions, and score logic.",
  "Approve, reject, edit, or challenge with a rationale.",
  "Open Audit trail to show the decision record.",
];

export function DemoSteps() {
  return (
    <section className="border border-[var(--hairline)] bg-[var(--grey-100)] p-6">
      <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]">Demo navigation</h2>
      <ol className="mt-4 grid gap-3 text-sm text-[var(--ink)]">
        {STEPS.map((text, i) => (
          <li key={text} className="flex gap-3">
            <span className="font-light tabular-nums text-[var(--blue)]">0{i + 1}</span>
            <span>{text}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
