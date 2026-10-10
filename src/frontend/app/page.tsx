"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  getExportUrl,
  getRequirements,
  getScenarios,
  putWeights,
  type Requirement,
  type Scenario,
  type WeightKey,
  type Weights,
} from "@/src/lib/api";
import { categoryLabel } from "@/src/components/badges";
import { ScoreBar } from "@/src/components/ScoreBar";
import { ThemeToggle } from "@/src/components/ThemeToggle";

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

export default function RequirementsPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState(DEFAULT_SCENARIO_ID);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
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
    getRequirements(scenarioId)
      .then((nextRequirements) => {
        if (cancelled) return;
        setRequirements(nextRequirements);
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

  const selectedScenario = scenarios.find((scenario) => scenario.id === scenarioId);

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
          <header className="mb-5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Signal2Spec</p>
                <h1 className="mt-1 text-2xl font-semibold text-foreground">PM Cockpit</h1>
                <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
                  Decide what the AI proposes, why it proposes it, and how reliable the evidence is.
                </p>
              </div>
              <nav className="flex flex-wrap gap-2">
                <Link className="inline-flex min-h-11 items-center rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background" href="/overview">
                  Overview
                </Link>
                <Link className="inline-flex min-h-11 items-center rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background" href="/audit">
                  Audit trail
                </Link>
                <a className="inline-flex min-h-11 items-center rounded-sm bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background" href={getExportUrl(scenarioId)} target="_blank" rel="noopener noreferrer">
                  Export CSV
                </a>
                <ThemeToggle />
              </nav>
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <label className="grid gap-1 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                Scenario
                <select
                  value={scenarioId}
                  onChange={(event) => {
                    setLoading(true);
                    setError(null);
                    setScenarioId(event.target.value);
                  }}
                  className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-3 font-normal text-foreground focus:border-accent focus:outline-none"
                >
                  {scenarios.map((scenario) => (
                    <option key={scenario.id} value={scenario.id}>
                      {scenarioLabel(scenario)}
                    </option>
                  ))}
                </select>
              </label>
              {selectedScenario?.headline_numbers && (
                <div className="grid grid-cols-3 gap-2 text-xs text-zinc-600 dark:text-zinc-400">
                  <span className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 px-3 py-2">
                    {selectedScenario.headline_numbers.evidence.toLocaleString("en-US")} customer voices
                  </span>
                  <span className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 px-3 py-2">
                    {selectedScenario.headline_numbers.signals} findings
                  </span>
                  <span className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 px-3 py-2">
                    {selectedScenario.headline_numbers.requirements} requirements
                  </span>
                </div>
              )}
            </div>
          </header>

          {error && (
            <div className="mb-4 rounded-sm border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
              {error}
            </div>
          )}

          <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface">
            {loading && <p className="p-5 text-sm text-zinc-500 dark:text-zinc-400">Loading requirements...</p>}
            {!loading && requirements.length === 0 && (
              <p className="p-5 text-sm text-zinc-500 dark:text-zinc-400">No requirements for this scenario yet.</p>
            )}
            {!loading && requirements.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[900px] text-left text-sm">
                  <thead className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-xs uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                    <tr>
                      <th className="px-4 py-3">Score</th>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {requirements.map((req) => (
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
                        className={`cursor-pointer border-b border-zinc-100 dark:border-zinc-800 transition last:border-0 hover:bg-accent/5 dark:hover:bg-accent/10 focus:bg-accent/5 dark:focus:bg-accent/10 focus:outline-none ${
                          highlightRanks && previousRanks[req.id] !== req.rank ? "bg-accent/5 dark:bg-accent/10" : ""
                        }`}
                      >
                        <td className="px-4 py-4">
                          <ScoreBar score={req.score} source={`${req.signal_ids.length} linked findings`} />
                        </td>
                        <td className="max-w-sm px-4 py-4">
                          <p className="font-semibold text-foreground">{req.title}</p>
                          <p className="mt-1 line-clamp-2 text-xs text-zinc-500 dark:text-zinc-400">{req.description}</p>
                        </td>
                        <td className="px-4 py-4 text-zinc-700 dark:text-zinc-300">{categoryLabel(req.category)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        <aside className="grid h-fit gap-4 xl:sticky xl:top-6">
          <section className="theme-dark-fixed rounded-lg border border-accent/30 bg-accent/5 p-5">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground">Demo navigation</h2>
            <ol className="mt-3 grid gap-2 text-sm text-foreground">
              <li><span className="font-semibold">1.</span> Pick a scenario and scan the ranked list.</li>
              <li><span className="font-semibold">2.</span> Open a row to inspect evidence, assumptions, and score logic.</li>
              <li><span className="font-semibold">3.</span> Approve, reject, edit, or challenge with a rationale.</li>
              <li><span className="font-semibold">4.</span> Open Audit trail to show the decision record.</li>
            </ol>
          </section>

          <section className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Weight controls</h2>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            Move sliders and press Apply weights. Empty rationale uses a demo rationale and still records changed weights.
          </p>
          <div className="mt-4 grid gap-4">
            {(Object.keys(WEIGHT_LABELS) as WeightKey[]).map((key) => (
              <label key={key} className="grid gap-2 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                <span className="flex items-center justify-between gap-3">
                  {WEIGHT_LABELS[key]}
                  <span className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">{weights[key].toFixed(2)}</span>
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
                  className="h-2 accent-[var(--accent)]"
                />
              </label>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={applying}
              onClick={() => applyWeights()}
              className="min-h-11 rounded-sm bg-accent px-4 text-sm font-semibold text-white hover:bg-accent-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:bg-zinc-300 dark:disabled:bg-zinc-700"
            >
              {applying ? "Applying..." : "Apply weights"}
            </button>
            <button
              type="button"
              onClick={resetWeights}
              className="min-h-11 rounded-sm border border-zinc-300 dark:border-zinc-700 bg-surface px-4 text-sm font-semibold text-foreground hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
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
