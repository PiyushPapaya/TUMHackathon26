import { Suspense } from "react";
import { OverviewPageClient } from "@/src/components/OverviewPageClient";

export const instant = false;

export default function OverviewPage() {
  // useSearchParams (Szenario aus der URL) braucht Suspense.
  return (
    <Suspense fallback={<main className="px-6 py-12 text-sm text-[var(--grey-500)]">Loading...</main>}>
      <OverviewPageClient />
    </Suspense>
  );
}
