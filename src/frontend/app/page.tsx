"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  getExportUrl,
  getRequirements,
  getScenarios,
  getSignals,
  putWeights,
  type Requirement,
  type Scenario,
  type Signal,
  type WeightKey,
  type Weights,
} from "@/src/lib/api";
import { categoryLabel, ConflictBadge, EvidenceBadge, StatusBadge } from "@/src/components/badges";
import { ScoreBar } from "@/src/components/ScoreBar";

const DEFAULT_SCENARIO_ID = "G60-US";
const PM_ACTOR = "pm.demo";
const DEFAULT_WEIGHTS: Record<WeightKey, number> = {
  customer_pain: 0.25,
  reach: 0.2,
  satisfaction_gap: 0.2,
  competitive_pressure: 0.15,
  future_relevance: 0.1,
  effort_inverse: 0.1,
};

const WEIGHT_LABELS: Record<WeightKey, string> = {
  customer_pain: "Customer pain",
  reach: "Reach",
  satisfaction_gap: "Satisfaction gap",
  competitive_pressure: "Competitive pressure",
  future_relevance: "Future relevance",
  effort_inverse: "Low effort",
};

const DEMO_RATIONALE = "Demo adjustment: product management is testing a different prioritization focus.";

function scenarioLabel(scenario: Scenario) {
  return `${scenario.model_name} ${scenario.market}`;
}

function weightsFromRequirements(requirements: Requirement[]): Record<WeightKey, number> {
  const first = requirements[0]?.score_breakdown;
  return {
    customer_pain: first?.customer_pain?.weight ?? DEFAULT_WEIGHTS.customer_pain,
    reach: first?.reach?.weight ?? DEFAULT_WEIGHTS.reach,
    satisfaction_gap: first?.satisfaction_gap?.weight ?? DEFAULT_WEIGHTS.satisfaction_gap,
    competitive_pressure: first?.competitive_pressure?.weight ?? DEFAULT_WEIGHTS.competitive_pressure,
    future_relevance: first?.future_relevance?.weight ?? DEFAULT_WEIGHTS.future_relevance,
    effort_inverse: first?.effort_inverse?.weight ?? DEFAULT_WEIGHTS.effort_inverse,
  };
}

function RankDelta({ oldRank, newRank }: { oldRank?: number; newRank: number }) {
  if (!oldRank || oldRank === newRank) return <span className="text-xs text-slate-400">-</span>;
  const movedUp = oldRank > newRank;
  return (
    <span className={movedUp ? "text-xs font-semibold text-emerald-700" : "text-xs font-semibold text-rose-700"}>
      {movedUp ? "↑" : "↓"} {Math.abs(oldRank - newRank)}
    </span>
  );
}

export default function RequirementsPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState(DEFAULT_SCENARIO_ID);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [weights, setWeights] = useState<Record<WeightKey, number>>(DEFAULT_WEIGHTS);
  const [rationale, setRationale] = useState("");
  const [previousRanks, setPreviousRanks] = useState<Record<string, number>>({});
  const [highlightRanks, setHighlightRanks] = useState(false);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getScenarios()
      .then((loaded) => {
        setScenarios(loaded);
        if (!loaded.some((scenario) => scenario.id === DEFAULT_SCENARIO_ID) && loaded[0]) {
          setScenarioId(loaded[0].id);
        }
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getRequirements(scenarioId), getSignals(scenarioId)])
      .then(([nextRequirements, nextSignals]) => {
        if (cancelled) return;
        setRequirements(nextRequirements);
        setSignals(nextSignals);
        setWeights(weightsFromRequirements(nextRequirements));
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [scenarioId]);

  const signalById = useMemo(() => new Map(signals.map((signal) => [signal.id, signal])), [signals]);
  const selectedScenario = scenarios.find((scenario) => scenario.id === scenarioId);

  function conflictTitles(requirement: Requirement) {
    return requirement.signal_ids.flatMap((signalId) => {
      const signal = signalById.get(signalId);
      return (signal?.conflicts_with ?? []).map((conflictId) => signalById.get(conflictId)?.title ?? conflictId);
    });
  }

  async function applyWeights(nextWeights: Weights = weights) {
    if (applying) return;
    const appliedRationale = rationale.trim() || DEMO_RATIONALE;
    setApplying(true);
    setError(null);
    const before = Object.fromEntries(requirements.map((req) => [req.id, req.rank]));
    try {
      const reranked = await putWeights(scenarioId, {
        weights: nextWeights,
        actor: PM_ACTOR,
        rationale: appliedRationale,
      });
      setPreviousRanks(before);
      setRequirements(reranked);
      setWeights(weightsFromRequirements(reranked));
      setRationale("");
      setHighlightRanks(true);
      window.setTimeout(() => setHighlightRanks(false), 2000);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setApplying(false);
    }
  }

  function resetWeights() {
    setWeights(DEFAULT_WEIGHTS);
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1fr_360px]">
        <section className="min-w-0">
          <header className="mb-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Signal2Spec</p>
                <h1 className="mt-1 text-2xl font-semibold text-[#0b1f3a]">PM Cockpit</h1>
                <p className="mt-1 max-w-2xl text-sm text-slate-600">
                  Decide what the AI proposes, why it proposes it, and how reliable the evidence is.
                </p>
              </div>
              <nav className="flex flex-wrap gap-2">
                <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/overview">
                  Overview
                </Link>
                <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/audit">
                  Audit trail
                </Link>
                <a className="inline-flex min-h-11 items-center rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href={getExportUrl(scenarioId)} target="_blank" rel="noopener noreferrer">
                  Export CSV
                </a>
              </nav>
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Scenario
                <select
                  value={scenarioId}
                  onChange={(event) => {
                    setLoading(true);
                    setError(null);
                    setScenarioId(event.target.value);
                  }}
                  className="min-h-11 rounded-md border border-slate-300 bg-white px-3 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  {scenarios.map((scenario) => (
                    <option key={scenario.id} value={scenario.id}>
                      {scenarioLabel(scenario)}
                    </option>
                  ))}
                </select>
              </label>
              {selectedScenario?.headline_numbers && (
                <div className="grid grid-cols-3 gap-2 text-xs text-slate-600">
                  <span className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
                    {selectedScenario.headline_numbers.evidence.toLocaleString("en-US")} customer voices
                  </span>
                  <span className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
                    {selectedScenario.headline_numbers.signals} findings
                  </span>
                  <span className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
                    {selectedScenario.headline_numbers.requirements} requirements
                  </span>
                </div>
              )}
            </div>
          </header>

          {error && (
            <div className="mb-4 rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              {error}
            </div>
          )}

          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            {loading && <p className="p-5 text-sm text-slate-500">Loading requirements...</p>}
            {!loading && requirements.length === 0 && (
              <p className="p-5 text-sm text-slate-500">No requirements for this scenario yet.</p>
            )}
            {!loading && requirements.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[900px] text-left text-sm">
                  <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
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
                      const conflicts = conflictTitles(req);
                      return (
                        <tr
                          key={req.id}
                          role="link"
                          tabIndex={0}
                          onClick={() => router.push(`/requirements/${req.id}`)}
                          onKeyDown={(event) => {
                            if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              router.push(`/requirements/${req.id}`);
                            }
                          }}
                          className={`cursor-pointer border-b border-slate-100 transition last:border-0 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none ${
                            highlightRanks && previousRanks[req.id] !== req.rank ? "bg-blue-50" : ""
                          }`}
                        >
                          <td className="px-4 py-4">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-[#0b1f3a]">#{req.rank}</span>
                              <RankDelta oldRank={previousRanks[req.id]} newRank={req.rank} />
                            </div>
                          </td>
                          <td className="max-w-sm px-4 py-4">
                            <p className="font-semibold text-[#0b1f3a]">{req.title}</p>
                            <p className="mt-1 line-clamp-2 text-xs text-slate-500">{req.description}</p>
                          </td>
                          <td className="px-4 py-4">
                            <ScoreBar score={req.score} source={`${req.signal_ids.length} linked findings`} />
                          </td>
                          <td className="px-4 py-4">
                            <EvidenceBadge level={req.evidence_level} reason={req.rationale} />
                          </td>
                          <td className="px-4 py-4 text-slate-700">{categoryLabel(req.category)}</td>
                          <td className="px-4 py-4">
                            <StatusBadge status={req.status} />
                          </td>
                          <td className="px-4 py-4">
                            <ConflictBadge conflictingTitles={conflicts} href={conflicts.length ? `/requirements/${req.id}#signal-${req.signal_ids[0]}` : undefined} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        <aside className="grid h-fit gap-4 xl:sticky xl:top-6">
          <section className="rounded-lg border border-blue-200 bg-blue-50 p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-blue-900">Demo navigation</h2>
            <ol className="mt-3 grid gap-2 text-sm text-blue-950">
              <li><span className="font-semibold">1.</span> Pick a scenario and scan the ranked list.</li>
              <li><span className="font-semibold">2.</span> Open a row to inspect evidence, assumptions, and score logic.</li>
              <li><span className="font-semibold">3.</span> Approve, reject, edit, or challenge with a rationale.</li>
              <li><span className="font-semibold">4.</span> Open Audit trail to show the decision record.</li>
            </ol>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Weight controls</h2>
          <p className="mt-2 text-sm text-slate-600">
            Move sliders and press Apply weights. Empty rationale uses a demo rationale and still records WEIGHTS_CHANGED.
          </p>
          <div className="mt-4 grid gap-4">
            {(Object.keys(WEIGHT_LABELS) as WeightKey[]).map((key) => (
              <label key={key} className="grid gap-2 text-sm font-semibold text-slate-700">
                <span className="flex items-center justify-between gap-3">
                  {WEIGHT_LABELS[key]}
                  <span className="text-xs font-semibold text-slate-500">{weights[key].toFixed(2)}</span>
                </span>
                <input
                  type="range"
                  min="0"
                  max="0.6"
                  step="0.01"
                  value={weights[key]}
                  onChange={(event) =>
                    setWeights((value) => ({ ...value, [key]: Number(event.target.value) }))
                  }
                  className="h-2 accent-blue-600"
                />
              </label>
            ))}
          </div>
          <label className="mt-4 grid gap-1 text-sm font-semibold text-slate-700">
            Rationale
            <textarea
              className="min-h-24 rounded-md border border-slate-300 px-3 py-2 font-normal text-[#0b1f3a] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="Why should the prioritization change?"
              value={rationale}
              onChange={(event) => setRationale(event.target.value)}
            />
          </label>
          <button
            type="button"
            onClick={() => setRationale(DEMO_RATIONALE)}
            className="mt-2 min-h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
          >
            Use demo rationale
          </button>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={applying}
              onClick={() => applyWeights()}
              className="min-h-11 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {applying ? "Applying..." : "Apply weights"}
            </button>
            <button
              type="button"
              onClick={resetWeights}
              className="min-h-11 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
            >
              Reset to default
            </button>
          </div>
          </section>
        </aside>
      </div>
    </main>
  );
}
