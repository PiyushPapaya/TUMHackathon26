"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getExportUrl,
  getRequirements,
  getScenarios,
  getSignals,
  type Requirement,
  type Scenario,
  type Signal,
} from "@/src/lib/api";
import { categoryLabel, ConflictBadge, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreBar } from "@/src/components/ScoreBar";

const DEFAULT_SCENARIO_ID = "G60-US";

export default function RequirementsPage() {
  const router = useRouter();

  const [scenarios, setScenarios] = useState<Scenario[] | null>(null);
  const [scenarioId, setScenarioId] = useState<string>(DEFAULT_SCENARIO_ID);
  const [requirements, setRequirements] = useState<Requirement[] | null>(null);
  const [signals, setSignals] = useState<Signal[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFetching, setIsFetching] = useState(true);

  // Szenarien einmal laden; Standard bleibt G60-US, falls vorhanden, sonst erstes Szenario.
  useEffect(() => {
    getScenarios()
      .then((loaded) => {
        setScenarios(loaded);
        if (!loaded.some((s) => s.id === DEFAULT_SCENARIO_ID) && loaded[0]) {
          setScenarioId(loaded[0].id);
        }
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  // Anforderungen + Befunde (für Konflikt-Check) neu laden bei Szenario-Wechsel.
  useEffect(() => {
    if (!scenarioId) return;
    let cancelled = false;
    (async () => {
      setIsFetching(true);
      try {
        const [loadedRequirements, loadedSignals] = await Promise.all([
          getRequirements(scenarioId),
          getSignals(scenarioId),
        ]);
        if (cancelled) return;
        setRequirements(loadedRequirements);
        setSignals(loadedSignals);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError((err as Error).message);
      } finally {
        if (!cancelled) setIsFetching(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [scenarioId]);

  const signalsById = useMemo(() => {
    const map = new Map<string, Signal>();
    for (const signal of signals ?? []) map.set(signal.id, signal);
    return map;
  }, [signals]);

  /** Titel der gegensätzlichen Befunde, falls ein verknüpfter Befund `conflicts_with` hat. */
  function conflictingTitlesFor(requirement: Requirement): string[] {
    const titles: string[] = [];
    for (const signalId of requirement.signal_ids) {
      const signal = signalsById.get(signalId);
      for (const otherId of signal?.conflicts_with ?? []) {
        titles.push(signalsById.get(otherId)?.title ?? otherId);
      }
    }
    return titles;
  }

  const isLoading = scenarios === null || isFetching || requirements === null || signals === null;

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <h1 className="text-xl font-semibold text-[#0b1f3a]">Signal2Spec · PM Cockpit</h1>
            <p className="text-sm text-zinc-500">Prioritized requirements for product decisions</p>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-zinc-700">
              Scenario
              <select
                value={scenarioId}
                onChange={(e) => setScenarioId(e.target.value)}
                disabled={!scenarios}
                className="rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm text-[#0b1f3a] focus:border-blue-500 focus:outline-none"
              >
                {(scenarios ?? []).map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.model_name} ({s.market})
                  </option>
                ))}
              </select>
            </label>
            <a
              href={getExportUrl(scenarioId)}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              Export CSV
            </a>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {error && (
          <div className="rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error}
          </div>
        )}

        {!error && isLoading && <p className="text-sm text-zinc-500">Loading…</p>}

        {!error && !isLoading && requirements !== null && requirements.length === 0 && (
          <p className="text-sm text-zinc-500">No requirements for this scenario yet.</p>
        )}

        {!error && !isLoading && requirements !== null && requirements.length > 0 && (
          <div className="overflow-hidden rounded-lg border border-zinc-200 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500">
                <tr>
                  <th className="px-4 py-3">Rank</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Evidence</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Conflict</th>
                </tr>
              </thead>
              <tbody>
                {requirements.map((req) => {
                  const conflicts = conflictingTitlesFor(req);
                  return (
                    <tr
                      key={req.id}
                      role="link"
                      tabIndex={0}
                      onClick={() => router.push(`/requirements/${req.id}`)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          router.push(`/requirements/${req.id}`);
                        }
                      }}
                      className="cursor-pointer border-b border-zinc-100 last:border-0 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none"
                    >
                      <td className="px-4 py-3 font-medium text-zinc-500">#{req.rank}</td>
                      <td className="px-4 py-3 font-medium text-[#0b1f3a]">{req.title}</td>
                      <td className="px-4 py-3">
                        <ScoreBar score={req.score} />
                      </td>
                      <td className="px-4 py-3">
                        <EvidenceBadge level={req.evidence_level} reason={req.rationale} />
                      </td>
                      <td className="px-4 py-3 text-zinc-700">{categoryLabel(req.category)}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={req.status} />
                      </td>
                      <td className="px-4 py-3">
                        <ConflictBadge conflictingTitles={conflicts} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
