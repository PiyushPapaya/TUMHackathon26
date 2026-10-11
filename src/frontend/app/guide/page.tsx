import { Button } from "@/src/components/ui/Button";
import { HairlineCard } from "@/src/components/ui/HairlineCard";
import { Eyebrow, SectionHeading } from "@/src/components/ui/Typography";

// Static guide: explains every cockpit function in plain words.
// Why its own page: jury and team see what to click without prior knowledge. Also shown in the floating side panel.

const STEPS = [
  ["1. Pick a scenario", "Choose model and market in the header (for example 5 Series G60 US). The cockpit then shows how many customer voices, findings and requirements the AI evaluated."],
  ["2. Read the ranked list", "Every row is an AI proposal. Rank is the order by score. The thin line shows the score (0-100), \"linked findings\" the number of pieces of evidence behind it."],
  ["3. Open a row", "A click shows the description, assumptions, the math behind the score (waterfall), all evidence and web sources."],
  ["4. Decide", "In the detail view you can approve, reject, edit or challenge a proposal (for example \"Does this only apply in the US?\"). Every decision needs a rationale."],
  ["5. Check the audit trail", "The audit trail lists every change with person, time and rationale, so it stays clear who decided what and why."],
];

const FEATURES = [
  ["Weight controls", "Sliders change what matters to you. \"Apply weights\" recomputes the ranking (the backend normalizes the sum to 1) and writes WEIGHTS_CHANGED to the audit trail. The change itself (for example \"Customer pain +0.10\") is stored as the rationale; a question asked in your own words is stored as the rationale when you apply it. \"Reset to default\" resets the sliders but applies nothing yet."],
  ["Ask in your own words", "Dark panel at the top of the cockpit. The AI turns your question into weights only, Python ranks. \"Apply & re-rank\" moves the list and stores your question as the rationale."],
  ["Conflicting evidence", "Small yellow \"!\" next to a title: two findings cited by this requirement contradict each other (for example many customers praise the range while others say it falls short). The detail view shows both sides."],
  ["Status", "Proposed (new), Challenged (questioned), Approved, Rejected."],
  ["Assistant", "Blue button bottom right. Ask what to build first, what a label means, or where to go. It only cites requirements that exist in the data."],
  ["Export", "Downloads the current ranking as CSV, JSON or Markdown, for example for Excel or a ticket system."],
];

const EVIDENCE = [
  ["Green · Proven (A/B)", "Direct customer mentions from one or more sources. A is the strongest."],
  ["Yellow · Weak (C)", "Little evidence. Treat with care."],
  ["Red · Assumption (D)", "Assumption or trend without direct customer voices, for example for the next vehicle generation."],
];

const WEIGHTS = [
  ["Customer pain", "How much do customers suffer from the problem?"],
  ["Reach", "How many customers are affected?"],
  ["Satisfaction gap", "How far is satisfaction below the target?"],
  ["Competitive pressure", "Do competitors do it better?"],
  ["Future relevance", "Will the topic matter more for the successor?"],
  ["Low effort", "The lower the effort (S/M/L), the higher the score."],
];

function Card({ title, rows }: { title: string; rows: string[][] }) {
  return (
    <HairlineCard>
      <Eyebrow>{title}</Eyebrow>
      <dl className="mt-5 grid gap-4 text-sm">
        {rows.map(([term, text]) => (
          <div key={term}>
            <dt className="font-semibold text-[var(--ink)]">{term}</dt>
            <dd className="mt-1 text-[var(--grey-500)]">{text}</dd>
          </div>
        ))}
      </dl>
    </HairlineCard>
  );
}

export default function GuidePage() {
  return (
    <main className="mx-auto grid max-w-3xl gap-6 px-6 py-12">
      <header className="pb-4">
        <Eyebrow>Signal2Spec</Eyebrow>
        <SectionHeading as="h1" className="mt-3">Guide to the cockpit.</SectionHeading>
        <p className="mt-4 text-[var(--grey-500)]">
          The AI proposes what to build next. You decide whether that is right, and you see the evidence for every proposal.
        </p>
        <div className="mt-6"><Button href="/cockpit">Back to cockpit</Button></div>
      </header>
      <Card title="Work in 5 steps" rows={STEPS} />
      <Card title="All functions" rows={FEATURES} />
      <Card title="Evidence levels (A to D)" rows={EVIDENCE} />
      <Card title="The six score weights" rows={WEIGHTS} />
    </main>
  );
}
