import { Button } from "@/src/components/ui/Button";
import { Eyebrow, SectionHeading } from "@/src/components/ui/Typography";
import { Reveal } from "@/src/components/ui/Reveal";
import type { HomeData } from "./useHomeData";

// Wer macht was: KI autonom vs. Mensch-Pflicht. Der Brief verlangt genau diese Trennung im Workflow.
// Früher eine eigene Overview-Seite; jetzt hier, weil Startseite und Overview dasselbe erzählten.
const WORKFLOW = [
  { stage: "Ingest", human: false, text: "Excel and PDF inputs become evidence IDs." },
  { stage: "Findings", human: false, text: "Recurring signals are grouped with quotes." },
  { stage: "Web", human: false, text: "External sources confirm trends and competitors." },
  { stage: "Requirements", human: true, text: "AI proposes measurable, PM-ready requirements." },
  { stage: "Prioritization", human: true, text: "A formula ranks. The PM asks or tunes weights." },
  { stage: "Decision", human: true, text: "Approve, reject, edit or challenge." },
  { stage: "Documentation", human: false, text: "Audit trail and memo are generated." },
];

const fmt = (n: number | undefined) => (typeof n === "number" ? n.toLocaleString("en-US") : "–");

// Log-Skala für die Balken: 4.000 Stimmen gegen 20 Anforderungen wären linear unsichtbar.
// Die Zahl daneben bleibt exakt, der Balken zeigt nur die Verdichtung.
function barWidth(value: number | undefined, max: number | undefined) {
  if (!value || !max) return 2;
  return Math.max(4, (Math.log10(value + 1) / Math.log10(max + 1)) * 100);
}

export function HowItWorks({ data }: { data: HomeData }) {
  const f = data.funnels[data.mainId];
  const rows = [
    { label: "customer voices", value: f?.evidence },
    { label: "findings", value: f?.signals },
    { label: "requirements", value: f?.requirements },
    { label: "approved by PM", value: f?.approved },
  ];

  return (
    <section id="flow" className="mx-auto max-w-[1400px] px-6 py-24 lg:px-10">
      <div className="grid gap-16 lg:grid-cols-[0.9fr_1.1fr]">
        <Reveal>
          <Eyebrow>From voice to decision · {data.mainId}</Eyebrow>
          <SectionHeading className="mt-4">Thousands of voices.<br />A handful of decisions.</SectionHeading>
          <p className="mt-6 max-w-md text-lg text-[var(--grey-500)]">
            The AI does the reading and the counting. The product manager asks, decides and signs off. Every step is traceable.
          </p>
          <div className="mt-10"><Button href={`/cockpit?scenario=${data.mainId}`}>Open cockpit</Button></div>
        </Reveal>

        <div className="divide-y divide-[var(--hairline)] border-y border-[var(--hairline)]">
          {rows.map((row, i) => (
            <Reveal key={row.label} delay={i * 120} className="grid items-center gap-x-8 gap-y-2 py-6 sm:grid-cols-[180px_1fr]">
              <div>
                <p className="text-5xl font-extralight tabular-nums">{fmt(row.value)}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.14em] text-[var(--grey-500)]">{row.label}</p>
              </div>
              <div className="h-[3px] bg-[var(--hairline)]">
                <div className="h-full bg-[var(--blue)] transition-[width] duration-1000" style={{ width: `${barWidth(row.value, f?.evidence)}%` }} />
              </div>
            </Reveal>
          ))}
        </div>
      </div>

      <Reveal className="mt-24">
        <Eyebrow>Who does what</Eyebrow>
        <ol className="mt-6 grid gap-px bg-[var(--hairline)] sm:grid-cols-2 lg:grid-cols-7">
          {WORKFLOW.map((step, i) => (
            <li key={step.stage} className={`p-5 ${step.human ? "bg-[var(--black)] text-white" : "bg-white"}`}>
              <p className={`text-xs tabular-nums ${step.human ? "text-[var(--m-light)]" : "text-[var(--grey-500)]"}`}>0{i + 1}</p>
              <h3 className="mt-3 font-semibold">{step.stage}</h3>
              <p className={`mt-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${step.human ? "text-[var(--m-light)]" : "text-[var(--grey-500)]"}`}>
                {step.human ? "PM in control" : "AI autonomous"}
              </p>
              <p className={`mt-4 text-xs leading-relaxed ${step.human ? "text-white/70" : "text-[var(--grey-500)]"}`}>{step.text}</p>
            </li>
          ))}
        </ol>
      </Reveal>
    </section>
  );
}
