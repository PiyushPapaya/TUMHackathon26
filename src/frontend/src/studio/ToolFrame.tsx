"use client";

/**
 * Gemeinsamer Rahmen für jedes Werkzeug: Überschrift und Hilfetext aus baukasten/texte.json,
 * Schalter aus features.json, einheitliche Lade-, Fehler- und Leerzustände.
 * So sieht jede Seite gleich aus, und Texte ändert das Team ohne Code.
 */
import features from "@/baukasten/features.json";
import texte from "@/baukasten/texte.json";
import { useStudio } from "@/src/studio/StudioData";
import type { ToolKey } from "@/src/studio/StudioNav";
import { Notice, PageHead } from "@/src/studio/ui";

export function ToolFrame({
  tool,
  actions,
  children,
}: {
  tool: ToolKey;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  const { loading, error, requirements } = useStudio();
  const text = texte.tools[tool];

  if (!features[tool as keyof typeof features]) {
    return (
      <Notice kind="empty">
        {text.name} is switched off. Set <code>&quot;{tool}&quot;: true</code> in <code>baukasten/features.json</code> to show it.
      </Notice>
    );
  }

  let body: React.ReactNode = children;
  if (error) {
    body = (
      <Notice kind="error">
        {error}. Start the backend with <code>uvicorn main:app --app-dir src/backend --port 8000</code> and reload.
      </Notice>
    );
  } else if (loading) {
    body = <Notice kind="loading">Loading requirements and every quote behind them…</Notice>;
  } else if (requirements.length === 0) {
    body = <Notice kind="empty">No requirements for this scenario yet. Run the pipeline, then reload.</Notice>;
  }

  return (
    <>
      <PageHead title={text.name} help={text.help}>
        {actions}
      </PageHead>
      {body}
    </>
  );
}
