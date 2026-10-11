import Link from "next/link";
import { EvidenceDot } from "@/src/components/badges";

// Kompakter Guide im Assistenten: der Demo-Weg in fünf Schritten plus Ampel-Legende.
// Die ausführliche Seite /guide bleibt für Deep-Links.
const STEPS = [
  ["Pick a model and market", "Scenario selector in the header, or the cards on the home page."],
  ["Ask in your own words", "Top of the cockpit. The AI only sets weights; Python ranks. Apply re-ranks the list."],
  ["Open a row", "Customer voices left, decision right, score math below."],
  ["Decide", "Approve, reject, edit or challenge. A rationale is required."],
  ["Check the audit trail", "Every change with person, time and reason, hash-chained."],
];

const LIGHTS = [
  ["A", "Proven", "many customer voices, several sources"],
  ["C", "Weak", "little evidence, treat with care"],
  ["D", "Assumption", "trend or idea without direct voices"],
] as const;

export function GuideTab() {
  return (
    <div className="flex-1 overflow-y-auto px-6 py-6">
      <ol className="grid gap-5">
        {STEPS.map(([title, text], i) => (
          <li key={title} className="flex gap-4">
            <span className="text-2xl font-extralight tabular-nums text-[var(--blue)]">{i + 1}</span>
            <span>
              <span className="block font-semibold text-[var(--ink)]">{title}</span>
              <span className="mt-1 block text-sm text-[var(--grey-500)]">{text}</span>
            </span>
          </li>
        ))}
      </ol>
      <p className="mt-8 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--grey-500)]">Evidence traffic light</p>
      <ul className="mt-3 grid gap-2">
        {LIGHTS.map(([level, word, text]) => (
          <li key={word} className="flex items-center gap-3 text-sm">
            <EvidenceDot level={level} />
            <span className="font-semibold text-[var(--ink)]">{word}</span>
            <span className="text-[var(--grey-500)]">{text}</span>
          </li>
        ))}
      </ul>
      <Link href="/guide" className="mt-8 inline-block text-sm font-semibold text-[var(--blue)] hover:text-[var(--blue-hover)]">
        Full guide with every function →
      </Link>
    </div>
  );
}
