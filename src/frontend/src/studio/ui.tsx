/**
 * Kleine UI-Bausteine der Werkbank. Farben kommen als CSS-Variablen aus baukasten/farben.json
 * (gesetzt in app/studio/layout.tsx), damit Nicht-Coder sie ändern können.
 * Design-Regel aus PFAD-D: Belege durchgezogen, Annahmen gestrichelt.
 */
import type { Evidence } from "@/src/lib/api";

export function PageHead({ title, help, children }: { title: string; help: string; children?: React.ReactNode }) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-[var(--ink)]/15 pb-6">
      <div className="max-w-2xl">
        <h1 className="text-4xl font-semibold leading-tight tracking-tight [font-stretch:125%]">{title}</h1>
        <p className="mt-2 text-base text-[var(--ink)]/70">{help}</p>
      </div>
      {children}
    </div>
  );
}

/** Lade-, Fehler- und Leerzustand mit klarer Anweisung statt Spinner ohne Text. */
export function Notice({ kind, children }: { kind: "loading" | "error" | "empty"; children: React.ReactNode }) {
  const tone =
    kind === "error"
      ? "border-[var(--complaint)] text-[var(--complaint)]"
      : "border-[var(--ink)]/20 text-[var(--ink)]/70";
  return (
    <div role={kind === "error" ? "alert" : "status"} className={`rounded-lg border-l-4 bg-white px-5 py-4 ${tone}`}>
      {children}
    </div>
  );
}

const POLARITY = {
  [-1]: { label: "Complaint", color: "var(--complaint)" },
  0: { label: "Neutral", color: "var(--ink)" },
  1: { label: "Praise", color: "var(--praise)" },
} as const;

/** Ein Zitat mit ID und Quelle. Die ID ist sichtbar, weil jede Aussage bis zum Original zurückverfolgbar sein muss. */
export function QuoteCard({ evidence, note, context }: { evidence: Evidence; note?: string; context?: string }) {
  const tone = POLARITY[evidence.polarity];
  return (
    <figure className="flex h-full flex-col rounded-lg border border-[var(--ink)]/15 bg-white p-5">
      <div className="mb-3 h-1 w-10 rounded-full" style={{ background: tone.color }} aria-hidden />
      <blockquote className="flex-1 text-[15px] leading-relaxed">“{evidence.text}”</blockquote>
      {note && (
        <p className="mt-3 rounded-md bg-[var(--accent)]/10 px-3 py-2 text-sm text-[var(--accent)]">Team note: {note}</p>
      )}
      <figcaption className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--ink)]/60">
        <span className="font-semibold" style={{ color: tone.color }}>
          {tone.label}
        </span>
        <span>{evidence.source_name}</span>
        <code className="rounded bg-[var(--paper)] px-1.5 py-0.5 text-[var(--ink)]">{evidence.id}</code>
        {evidence.url && (
          <a href={evidence.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
            Source
          </a>
        )}
      </figcaption>
      {context && <p className="mt-2 text-xs text-[var(--ink)]/50">Supports: {context}</p>}
    </figure>
  );
}

/** Annahmen immer gestrichelt, damit niemand sie mit Belegen verwechselt (Design-Regel PFAD-D). */
export function AssumptionList({ items }: { items: string[] }) {
  if (items.length === 0) return <p className="text-sm text-[var(--ink)]/50">No assumptions listed.</p>;
  return (
    <ul className="space-y-2">
      {items.map((a) => (
        <li key={a} className="rounded-md border border-dashed border-[var(--assumption)] px-3 py-2 text-sm">
          <span className="mr-2 font-semibold text-[var(--assumption)]">Assumption</span>
          {a}
        </li>
      ))}
    </ul>
  );
}

/** Begründung ist Pflicht für jede Entscheidung; das Feld zeigt, warum die Buttons gesperrt sind. */
export function ReasonField({ value, onChange, id }: { value: string; onChange: (v: string) => void; id: string }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium">
        Your reason <span className="font-normal text-[var(--ink)]/60">(required, goes into the audit trail)</span>
      </label>
      <textarea
        id={id}
        rows={2}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-[var(--ink)]/25 bg-white px-3 py-2 text-[15px] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/30"
      />
    </div>
  );
}

const BUTTON = {
  primary: "bg-[var(--accent)] text-white hover:brightness-110",
  quiet: "border border-[var(--ink)]/25 bg-white text-[var(--ink)] hover:border-[var(--ink)]/50",
  praise: "bg-[var(--praise)] text-white hover:brightness-110",
  complaint: "bg-[var(--complaint)] text-white hover:brightness-110",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof BUTTON }) {
  return (
    <button
      {...props}
      className={`rounded-md px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 ${BUTTON[variant]} ${className}`}
    />
  );
}

/** Ab 5 Zeichen gilt eine Begründung als ausgefüllt (verhindert "." als Begründung). */
export const reasonIsValid = (reason: string) => reason.trim().length >= 5;
