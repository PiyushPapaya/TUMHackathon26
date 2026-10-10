/**
 * Client-Teil der Detailseite (Ticket D3): holt GET /api/requirements/{id} und zeigt
 * Lade-/Fehlerzustand. `id` kommt als fertiger String vom Server-Wrapper
 * (app/requirements/[id]/page.tsx), damit dort `export const instant = false` stehen darf
 * (dieser Export braucht eine Server-Komponente, siehe Next 16 Cache Components).
 */
"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getRequirementDetail, type Evidence, type RequirementDetail } from "@/src/lib/api";
import { RequirementDetailView } from "@/src/components/RequirementDetailView";

export function RequirementDetailPageClient({ id }: { id: string }) {
  const [detail, setDetail] = useState<RequirementDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setIsLoading(true);
      setError(null);
      try {
        const loaded = await getRequirementDetail(id);
        if (!cancelled) setDetail(loaded);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  // Belege je Befund vorsortieren, damit die Karten nicht bei jedem Render neu filtern.
  const evidenceBySignal = useMemo(() => {
    const byId = new Map<string, Evidence>();
    for (const item of detail?.evidence ?? []) byId.set(item.id, item);
    const bySignal = new Map<string, Evidence[]>();
    for (const signal of detail?.signals ?? []) {
      bySignal.set(
        signal.id,
        signal.evidence_ids.map((evId) => byId.get(evId)).filter((e): e is Evidence => Boolean(e)),
      );
    }
    return bySignal;
  }, [detail]);

  return (
    <div className="min-h-screen bg-zinc-50">
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          ← Back to list
        </Link>

        {error && (
          <div className="mt-4 rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error}
          </div>
        )}
        {!error && isLoading && <p className="mt-4 text-sm text-zinc-500">Loading…</p>}

        {!error && !isLoading && detail && (
          <>
            <RequirementDetailView detail={detail} evidenceBySignal={evidenceBySignal} />
            <div className="mt-8">
              <Link href="/" className="text-sm text-blue-600 hover:underline">
                ← Back to list
              </Link>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
