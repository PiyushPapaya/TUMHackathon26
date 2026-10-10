"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  getRequirementDetail,
  getRequirementExplain,
  type Evidence,
  type ExplainView,
} from "@/src/lib/api";
import { RequirementDetailView } from "@/src/components/RequirementDetailView";

export function RequirementDetailPageClient({ id }: { id: string }) {
  const [detail, setDetail] = useState<ExplainView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [ignoreAssumptions, setIgnoreAssumptions] = useState(false);

  const loadDetail = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const loaded = await getRequirementExplain(id).catch(async () => getRequirementDetail(id));
      setDetail(loaded);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    let cancelled = false;
    getRequirementExplain(id)
      .catch(async () => getRequirementDetail(id))
      .then((loaded) => {
        if (!cancelled) {
          setDetail(loaded);
          setError(null);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

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
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/"
            className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
          >
            Back to list
          </Link>
          <Link
            href="/audit"
            className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
          >
            Open audit trail
          </Link>
        </div>

        {error && (
          <div className="rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error}
          </div>
        )}
        {!error && isLoading && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
            Loading requirement...
          </div>
        )}

        {!error && !isLoading && detail && (
          <RequirementDetailView
            detail={detail}
            evidenceBySignal={evidenceBySignal}
            ignoreAssumptions={ignoreAssumptions}
            onToggleIgnoreAssumptions={setIgnoreAssumptions}
            onRefresh={loadDetail}
          />
        )}
      </div>
    </main>
  );
}
