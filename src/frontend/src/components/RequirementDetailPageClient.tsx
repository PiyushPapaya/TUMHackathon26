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
import { ThemeToggle } from "@/src/components/ThemeToggle";

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
            className="inline-flex min-h-11 items-center rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            Back to list
          </Link>
          <Link
            href="/audit"
            className="inline-flex min-h-11 items-center rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            Open audit trail
          </Link>
          <ThemeToggle />
        </div>

        {error && (
          <div className="rounded-sm border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
            {error}
          </div>
        )}
        {!error && isLoading && (
          <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-6 text-sm text-zinc-500 dark:text-zinc-400">
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
