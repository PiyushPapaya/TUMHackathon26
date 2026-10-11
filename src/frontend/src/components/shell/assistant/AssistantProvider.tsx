"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getRequirements, getScenarios, type EvidenceLevel, type Scenario } from "@/src/lib/api";
import { postAsk, postLens, type AskHit } from "@/src/lib/insights";
import { DEFAULT_SCENARIO_ID } from "@/src/components/shell/scenarioLabel";
import { routeQuestion, type Link } from "./intents";
import { AssistantPanel } from "./AssistantPanel";

export type Tab = "chat" | "guide";
export type Hit = { id: string; title: string; scenarioId: string; level: EvidenceLevel; note?: string };
export type Message = { role: "user" | "bot"; text: string; links?: Link[]; hits?: Hit[]; source?: string };

type Ctx = { open: (tab?: Tab) => void; close: () => void };
const AssistantContext = createContext<Ctx>({ open: () => {}, close: () => {} });
export const useAssistant = () => useContext(AssistantContext);

const GREETING: Message = {
  role: "bot",
  text: "Hi, I am the ReSpec assistant. Ask what to build first, what a label means, or where to find something. I only answer with real requirement IDs from the data.",
};

const toHit = (h: AskHit): Hit => ({ id: h.requirement_id, title: h.title, scenarioId: h.scenario_id, level: h.evidence_level, note: h.reasons[0]?.sentence });

// Der Assistent lebt im Layout, damit der Verlauf beim Seitenwechsel erhalten bleibt.
// Er navigiert selbst (router.push), statt nur Links zu nennen: im Demo spart das Klicks.
export function AssistantProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const scenarioId = useSearchParams().get("scenario") ?? DEFAULT_SCENARIO_ID;
  const [isOpen, setOpen] = useState(false);
  const [tab, setTab] = useState<Tab>("chat");
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [busy, setBusy] = useState(false);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  useEffect(() => {
    getScenarios().then(setScenarios).catch(() => setScenarios([]));
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const push = (m: Message) => setMessages((list) => [...list, m]);

  const send = useCallback(
    async (text: string) => {
      if (!text.trim() || busy) return;
      push({ role: "user", text: text.trim() });
      const routed = routeQuestion(text, { scenarioId, scenarios });
      if (routed.kind === "reply") {
        push({ role: "bot", text: routed.text, links: routed.links });
        if (routed.navigate) router.push(routed.navigate);
        return;
      }
      setBusy(true);
      try {
        if (routed.kind === "top") {
          const top = (await getRequirements(routed.scenarioId)).slice(0, 3);
          push({
            role: "bot",
            text: top.length ? `Top of the ranked list for ${routed.scenarioId}:` : "No requirements for this scenario yet.",
            hits: top.map((r) => ({ id: r.id, title: r.title, scenarioId: routed.scenarioId, level: r.evidence_level, note: `Rank ${r.rank} · score ${r.score.toFixed(1)}` })),
            links: [{ href: `/cockpit?scenario=${routed.scenarioId}`, label: "Open the full list" }],
          });
        } else {
          // Rückfall: Läuft ein älteres Backend ohne /api/ask, fragen wir die Linse des aktuellen Szenarios.
          const res = await postAsk(routed.question, "pm.demo").catch(async () => {
            const lens = await postLens(scenarioId, routed.question, "pm.demo");
            return {
              question: lens.question, source: lens.source, interpretation: lens.interpretation, answer: lens.interpretation,
              top: lens.top.map((t) => ({ scenario_id: scenarioId, requirement_id: t.requirement.id, title: t.requirement.title, rank: t.requirement.rank, score: t.lens_score, lens_score: t.lens_score, evidence_level: t.requirement.evidence_level, reasons: t.reasons })),
            };
          });
          push({
            role: "bot",
            text: res.top.length
              ? `${res.interpretation ? `I read this as: ${res.interpretation} ` : ""}Best matches across all models and markets:`
              : "I found no matching requirement. Try a topic like charging, space, infotainment or a model like \"7 Series US\".",
            hits: res.top.map(toHit),
            source: res.source === "rules" ? "Matched by keyword rules on the real data" : "AI set the focus, Python ranked the real data",
          });
        }
      } catch (e) {
        push({ role: "bot", text: `I could not reach the backend (${(e as Error).message}). Is uvicorn running?` });
      } finally {
        setBusy(false);
      }
    },
    [busy, scenarioId, scenarios, router],
  );

  const ctx = useMemo<Ctx>(() => ({ open: (t: Tab = "chat") => { setTab(t); setOpen(true); }, close: () => setOpen(false) }), []);

  return (
    <AssistantContext.Provider value={ctx}>
      {children}
      <AssistantPanel
        isOpen={isOpen}
        tab={tab}
        onTab={setTab}
        onToggle={() => setOpen((v) => !v)}
        messages={messages}
        busy={busy}
        onSend={send}
      />
    </AssistantContext.Provider>
  );
}
