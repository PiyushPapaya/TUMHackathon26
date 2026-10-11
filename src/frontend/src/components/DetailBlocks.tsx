import type { OfferCheck, OfferCheckStatus, SegmentConflict } from "@/src/lib/api";
import { describeSegmentConflict, type ConflictSide } from "@/src/lib/segmentConflicts";

function ConflictSideBox({ side, verb, className }: { side: ConflictSide; verb: string; className: string }) {
  return (
    <div className={`border p-3 ${className}`}>
      <p className="text-xs font-semibold uppercase tracking-wide">{verb}</p>
      <p className="mt-1 font-semibold">{side.label}</p>
      <p className="text-xs tabular-nums">{side.count === null ? "reports satisfaction" : `${side.count} comments`}</p>
    </div>
  );
}

// Beide Seiten nebeneinander statt eines Satzes: Die PM sieht sofort, WER kritisiert und WER lobt.
// Beleg-IDs sind nur Links, wenn der Beleg oben auf der Seite steht (sonst toter Anker).
export function SegmentConflictCard({ conflict, visibleEvidenceIds }: { conflict: SegmentConflict; visibleEvidenceIds: Set<string> }) {
  const view = describeSegmentConflict(conflict);
  const ids = conflict.evidence_ids ?? [];
  return (
    <li className="border border-amber-300 bg-amber-50 p-4 text-sm text-slate-800">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-amber-800">Conflicting evidence · {view.dimensionLabel}</p>
      {!view.isSegmentComparison ? (
        <>
          <p className="mt-1">{conflict.statement}</p>
          <p className="mt-2 text-xs">
            {(conflict.signal_ids ?? []).map((id, i) => (
              <span key={id}>{i > 0 && " · "}<a className="text-[var(--blue)] underline underline-offset-2" href={`#signal-${id}`}>{id}</a></span>
            ))}
          </p>
        </>
      ) : (
        <>
          {view.topic && <p className="mt-1 font-semibold">{view.topic}</p>}
          <div className="mt-3 grid grid-cols-2 gap-2">
            <ConflictSideBox side={view.critical} verb="Mostly criticise" className="border-rose-300 bg-rose-50 text-rose-900" />
            <ConflictSideBox side={view.positive} verb="Mostly praise" className="border-emerald-300 bg-emerald-50 text-emerald-900" />
          </div>
        </>
      )}
      {ids.length > 0 && (
        <p className="mt-3 text-xs text-slate-600">
          Example evidence:{" "}
          {ids.map((id, i) => (
            <span key={id}>
              {i > 0 && ", "}
              {visibleEvidenceIds.has(id) ? <a className="text-[var(--blue)] underline underline-offset-2" href={`#evidence-${id}`}>{id}</a> : id}
            </span>
          ))}
        </p>
      )}
    </li>
  );
}

export function AssumptionItem({ label, text }: { label: string; text: string }) {
  return (
    <li className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-700">
      <span className="mb-2 inline-flex min-h-6 items-center border border-dashed border-slate-400 px-2 text-[10px] font-semibold uppercase tracking-wide text-slate-600">
        {label}
      </span>
      <p>{text}</p>
    </li>
  );
}

const OFFER_STYLE: Record<OfferCheckStatus, { label: string; className: string }> = {
  not_offered: {
    label: "No - not offered today",
    className: "border-rose-300 bg-rose-50 text-rose-800",
  },
  optional: {
    label: "Yes - available as an option",
    className: "border-blue-300 bg-blue-50 text-blue-800",
  },
  standard: {
    label: "Yes - standard equipment",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800",
  },
  unknown: {
    label: "Not checked yet",
    className: "border-slate-300 bg-slate-50 text-slate-700",
  },
};

export function OfferCheckBox({ offerCheck }: { offerCheck: OfferCheck }) {
  const style = OFFER_STYLE[offerCheck.status as OfferCheckStatus] ?? OFFER_STYLE.unknown;
  return (
    <section className={`rounded-lg border p-4 ${style.className}`}>
      <p className="text-xs font-semibold uppercase tracking-wide">Already offered?</p>
      <p className="mt-1 font-semibold">
        {style.label}
        {offerCheck.option_code ? ` (${offerCheck.option_code})` : ""}
      </p>
      {offerCheck.note && <p className="mt-1 text-sm">{offerCheck.note}</p>}
      <p className="mt-3 text-xs">Equipment reference from the supplied option list; availability in the selected market requires verification.</p>
    </section>
  );
}
