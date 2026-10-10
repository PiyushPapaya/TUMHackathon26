"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getOverview, getScenarios, type OverviewView, type Scenario } from "@/src/lib/api";
import { EvidenceBadge } from "@/src/components/badges";

const DEFAULT_SCENARIO_ID = "G60-US";

const WORKFLOW = [
  { stage: "Ingest", mode: "AI autonomous", owner: "Path A", text: "Excel and PDF inputs become evidence IDs." },
  { stage: "Findings", mode: "AI autonomous", owner: "Path A", text: "Recurring signals are grouped with quotes." },
  { stage: "Web", mode: "AI autonomous", owner: "Path B", text: "External sources confirm trends and competitors." },
  { stage: "Requirements", mode: "Human required", owner: "Path C", text: "AI proposes measurable PM-ready requirements." },
  { stage: "Prioritization", mode: "Human required", owner: "Path C", text: "Formula ranks, PM can change weights." },
  { stage: "Decision", mode: "Human required", owner: "Path D", text: "Approve, reject, edit, or challenge." },
  { stage: "Documentation", mode: "AI autonomous", owner: "Lead", text: "Audit trail and export are generated." },
];

function FunnelStep({ label, value, max }: { label: string; value: number; max: number }) {
  const width = Math.max(22, Math.min(100, (value / Math.max(max, 1)) * 100));
  return (
    <div className="mx-auto grid w-full max-w-3xl gap-2" style={{ width: `${width}%` }}>
      <div className="animate-funnel rounded-lg border border-blue-200 bg-blue-50 px-5 py-4 text-center shadow-sm">
        <p className="text-3xl font-semibold text-[#0b1f3a]">{value.toLocaleString("en-US")}</p>
        <p className="mt-1 text-sm font-semibold uppercase tracking-wide text-blue-800">{label}</p>
      </div>
    </div>
  );
}

export function OverviewPageClient() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState(DEFAULT_SCENARIO_ID);
  const [overview, setOverview] = useState<OverviewView | null>(null);
  const [loading, setLoading] = useState(true);
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
    getOverview(scenarioId)
      .then((loaded) => {
        if (!cancelled) {
          setOverview(loaded);
          setError(null);
        }
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

  const funnel = overview?.funnel;
  const maxFunnel = funnel?.evidence ?? 1;

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Demo start</p>
              <h1 className="mt-1 text-2xl font-semibold text-[#0b1f3a]">Evidence-to-decision overview</h1>
              <p className="mt-1 max-w-2xl text-sm text-slate-600">
                One funnel from customer voices to PM-approved requirements, with AI and human responsibility separated.
              </p>
            </div>
            <nav className="flex flex-wrap gap-2">
              <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/">
                Requirements
              </Link>
              <Link className="inline-flex min-h-11 items-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-[#0b1f3a] hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" href="/audit">
                Audit trail
              </Link>
            </nav>
          </div>
          <label className="mt-5 grid max-w-xs gap-1 text-sm font-semibold text-slate-700">
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
                  {scenario.model_name} {scenario.market}
                </option>
              ))}
            </select>
          </label>
        </header>

        {error && (
          <div className="mb-4 rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error}
          </div>
        )}

        {loading && !error && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
            Loading overview...
          </div>
        )}

        {overview && !loading && (
          <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
            <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Funnel</h2>
              <div className="mt-6 grid gap-3">
                <FunnelStep label="customer voices" value={funnel?.evidence ?? 0} max={maxFunnel} />
                <FunnelStep label="findings" value={funnel?.signals ?? 0} max={maxFunnel} />
                <FunnelStep label="requirements" value={funnel?.requirements ?? 0} max={maxFunnel} />
                <FunnelStep label="approved" value={funnel?.approved ?? 0} max={maxFunnel} />
              </div>
              {funnel?.note && <p className="mt-5 text-center text-sm text-slate-500">{funnel.note}</p>}
            </section>

            <aside className="grid gap-4">
              <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Top proposals</h2>
                <div className="mt-3 grid gap-3">
                  {overview.top3.map((item) => (
                    <Link
                      key={item.id}
                      href={`/requirements/${item.id}`}
                      className="rounded-md border border-slate-200 bg-slate-50 p-3 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-[#0b1f3a]">#{item.rank}</span>
                        <EvidenceBadge level={item.evidence_level} reason={item.level_label} />
                      </div>
                      <p className="mt-2 text-sm font-semibold text-[#0b1f3a]">{item.title}</p>
                      <p className="mt-1 text-xs text-slate-500">Score {item.score.toFixed(1)}</p>
                    </Link>
                  ))}
                </div>
              </section>
              <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Evidence levels</h2>
                <div className="mt-3 grid grid-cols-2 gap-2">
                  {(["A", "B", "C", "D"] as const).map((level) => (
                    <div key={level} className="rounded-md border border-slate-200 bg-slate-50 p-3">
                      <EvidenceBadge level={level} reason="Distribution across current requirements" />
                      <p className="mt-2 text-xl font-semibold text-[#0b1f3a]">{overview.level_distribution[level]}</p>
                    </div>
                  ))}
                </div>
              </section>
            </aside>

            <section className="xl:col-span-2 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Workflow</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-7">
                {WORKFLOW.map((step, index) => (
                  <article key={step.stage} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold text-slate-500">0{index + 1}</p>
                    <h3 className="mt-2 font-semibold text-[#0b1f3a]">{step.stage}</h3>
                    <p className="mt-2 rounded-full border border-slate-300 bg-white px-2 py-1 text-xs font-semibold text-slate-700">
                      {step.mode}
                    </p>
                    <p className="mt-3 text-xs text-slate-600">{step.text}</p>
                    <p className="mt-3 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{step.owner}</p>
                  </article>
                ))}
              </div>
            </section>

            {overview.warnings.length > 0 && (
              <section className="xl:col-span-2 rounded-lg border border-amber-300 bg-amber-50 p-5 text-sm text-amber-900">
                <h2 className="text-sm font-semibold uppercase tracking-wide">Warnings</h2>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {overview.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
