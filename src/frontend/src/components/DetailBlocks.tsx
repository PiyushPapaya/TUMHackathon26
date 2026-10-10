import type { OfferCheck, OfferCheckStatus } from "@/src/lib/api";

export function AssumptionItem({ label, text }: { label: string; text: string }) {
  return (
    <li className="rounded-sm border border-dashed border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm text-zinc-700 dark:text-zinc-300">
      <span className="mb-2 inline-flex min-h-6 items-center rounded-full border border-dashed border-zinc-400 dark:border-zinc-600 px-2 text-[10px] font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400">
        {label}
      </span>
      <p>{text}</p>
    </li>
  );
}

const OFFER_STYLE: Record<OfferCheckStatus, { label: string; className: string }> = {
  not_offered: {
    label: "No - not offered today",
    className: "border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300",
  },
  optional: {
    label: "Yes - available as an option",
    className: "border-accent/40 bg-accent/5 dark:bg-accent/10 text-accent-hover dark:text-accent",
  },
  standard: {
    label: "Yes - standard equipment",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  },
  unknown: {
    label: "Not checked yet",
    className: "border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300",
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
