"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getExportUrl,
  getRequirements,
  getScenarios,
  type Requirement,
  type Scenario,
} from "@/src/lib/api";
import { categoryLabel } from "@/src/components/badges";
import { ScoreBar } from "@/src/components/ScoreBar";

const DEFAULT_SCENARIO_ID = "G60-US";

export default function RequirementsPage() {
  const router = useRouter();

  const [scenarios, setScenarios] = useState<Scenario[] | null>(null);
  const [scenarioId, setScenarioId] = useState<string>(DEFAULT_SCENARIO_ID);
  const [requirements, setRequirements] = useState<Requirement[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFetching, setIsFetching] = useState(true);

  const [promptText, setPromptText] = useState("");
  const [promptNote, setPromptNote] = useState<string | null>(null);

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

  // Anforderungen neu laden bei Szenario-Wechsel.
  useEffect(() => {
    if (!scenarioId) return;
    let cancelled = false;
    (async () => {
      setIsFetching(true);
      try {
        const loadedRequirements = await getRequirements(scenarioId);
        if (cancelled) return;
        setRequirements(loadedRequirements);
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

  const isLoading = scenarios === null || isFetching || requirements === null;

  /** Platzhalter: Das Prompt-Feld ist noch nicht ans Backend angebunden (eigenes Ticket). */
  function handlePromptSubmit() {
    const text = promptText.trim();
    if (!text) return;
    console.log("[prompt submit - placeholder, not wired to backend yet]", text);
    setPromptNote(`Received: "${text}" — not connected to the backend yet.`);
    setPromptText("");
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Top bar: volle Breite, Platz für weitere Elemente später. Halbtransparent, damit der Shader-Hintergrund durchscheint. */}
      <header className="w-full border-b border-zinc-200 bg-white/85 backdrop-blur-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4">
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

      {/* Mitte: Ergebnis-Fenster, 2cm Abstand zu Rand, Top-Bar und Prompt-Leiste */}
      <main className="m-[2cm] flex flex-1 flex-col">
        <div className="flex-1 overflow-hidden rounded-lg border border-zinc-200 bg-white/90 backdrop-blur-sm">
          <div className="h-full overflow-auto">
            {error && (
              <div className="m-4 rounded-md border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
                {error}
              </div>
            )}

            {!error && isLoading && <p className="p-4 text-sm text-zinc-500">Loading…</p>}

            {!error && !isLoading && requirements !== null && requirements.length === 0 && (
              <p className="p-4 text-sm text-zinc-500">No requirements for this scenario yet.</p>
            )}

            {!error && !isLoading && requirements !== null && requirements.length > 0 && (
              <table className="w-full text-left text-sm">
                <thead className="border-b border-zinc-200 bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500">
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
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          router.push(`/requirements/${req.id}`);
                        }
                      }}
                      className="cursor-pointer border-b border-zinc-100 last:border-0 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none"
                    >
                      <td className="px-4 py-3">
                        <ScoreBar score={req.score} />
                      </td>
                      <td className="px-4 py-3 font-medium text-[#0b1f3a]">{req.title}</td>
                      <td className="px-4 py-3 text-zinc-700">{categoryLabel(req.category)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>

      {/* Unten: Prompt-Eingabe, 1cm Abstand zum Rand unten, 2cm links/rechts */}
      <footer className="mx-[3cm] mb-[2cm] flex flex-col gap-2">
        {promptNote && <p className="text-xs text-zinc-500">{promptNote}</p>}
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handlePromptSubmit();
            }}
            placeholder="Ask me your questions..."
            className="flex-1 rounded-md border border-zinc-300 bg-white/90 backdrop-blur-sm px-4 py-4 text-sm text-[#0b1f3a] focus:border-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handlePromptSubmit}
            className="rounded-md bg-blue-600 px-5 py-4 text-sm font-medium text-white hover:bg-blue-700"
          >
            Submit
          </button>
        </div>
      </footer>
    </div>
  );
}
