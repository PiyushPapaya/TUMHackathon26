import type { OfferCheck, OfferCheckStatus } from "@/src/lib/api";

export function AssumptionItem({ label, text }: { label: string; text: string }) {
  return (
    <li className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-700">
      <span className="mb-2 inline-flex min-h-6 items-center rounded-full border border-dashed border-slate-400 px-2 text-[10px] font-semibold uppercase tracking-wide text-slate-600">
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
    </section>
  );
}
