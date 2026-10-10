/**
 * Kleine Bausteine nur für die Detailseite (D3): Annahme/Unsicherheit-Zeile (gestrichelt,
 * Design-Regel PFAD-D) und die "Already offered?"-Box aus Requirement.offer_check.
 * Eigene Datei, damit app/requirements/[id]/page.tsx unter ~200 Zeilen bleibt.
 */
import type { OfferCheck, OfferCheckStatus } from "@/src/lib/api";

export function AssumptionItem({ label, text }: { label: string; text: string }) {
  return (
    <li className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-3 text-sm text-zinc-700">
      <span className="mb-1 inline-block rounded-full border border-dashed border-zinc-400 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
        {label}
      </span>
      <p>{text}</p>
    </li>
  );
}

const OFFER_STYLE: Record<OfferCheckStatus, { label: string; className: string }> = {
  not_offered: { label: "No — not offered today", className: "border-rose-300 bg-rose-50 text-rose-800" },
  optional: { label: "Yes — available as an option", className: "border-blue-300 bg-blue-50 text-blue-800" },
  standard: { label: "Yes — standard equipment", className: "border-emerald-300 bg-emerald-50 text-emerald-800" },
  unknown: { label: "Not checked yet", className: "border-zinc-300 bg-zinc-50 text-zinc-600" },
};

export function OfferCheckBox({ offerCheck }: { offerCheck: OfferCheck }) {
  const style = OFFER_STYLE[offerCheck.status as OfferCheckStatus] ?? OFFER_STYLE.unknown;
  return (
    <div className={`rounded-lg border p-4 ${style.className}`}>
      <p className="text-xs font-semibold uppercase tracking-wide">Already offered?</p>
      <p className="mt-1 font-medium">
        {style.label}
        {offerCheck.option_code ? ` (${offerCheck.option_code})` : ""}
      </p>
      {offerCheck.note && <p className="mt-1 text-sm">{offerCheck.note}</p>}
    </div>
  );
}
