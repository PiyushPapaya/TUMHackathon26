import type { Scenario } from "@/src/lib/api";

// Regel-Router des Assistenten: Stichwort → feste Antwort oder Navigation. Alles andere geht als Datenfrage an /api/ask.
// Warum Regeln statt freiem LLM: Die Antworten über das Produkt sind kurz, fest und überprüfbar, nichts wird erfunden.

export type Link = { href: string; label: string };
export type Routed =
  | { kind: "reply"; text: string; links?: Link[]; navigate?: string }
  | { kind: "top"; scenarioId: string }
  | { kind: "ask"; question: string };

// Nur ganze Wörter (plus Mehrzahl -s/-es) zählen. Warum: Mit reinem includes() steckte "red" in "required"
// und "rot" in "protection", und echte Datenfragen bekamen die Ampel-Erklärung. Ein "*" am Ende erlaubt
// bewusst Wortanfänge ("opportunit*" für opportunity/opportunities).
const escape = (w: string) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const wordPattern = (w: string) =>
  w.endsWith("*") ? `(?<![\\p{L}\\d])${escape(w.slice(0, -1))}` : `(?<![\\p{L}\\d])${escape(w)}(?:e?s)?(?![\\p{L}\\d])`;
const has = (q: string, words: string[]) => words.some((w) => new RegExp(wordPattern(w), "u").test(q));

// "7er us", "g70", "1 series", "china" → Szenario-ID. Markt allein reicht nicht, Modell allein nimmt das erste passende.
export function matchScenario(q: string, scenarios: Scenario[]): Scenario | undefined {
  const models: [string, string[]][] = [
    ["g68", ["g68", "langversion", "long wheelbase", "5 li"]],
    ["g60", ["g60", "5er", "5 series", "5-series", "five"]],
    ["g70", ["g70", "7er", "7 series", "7-series", "seven"]],
    ["f70", ["f70", "1er", "1 series", "1-series", "one series"]],
  ];
  const model = models.find(([, words]) => has(q, words))?.[0];
  if (!model) return undefined;
  const market = has(q, ["us", "usa", "america"]) ? "US" : has(q, ["eu", "europe", "germany"]) ? "EU" : has(q, ["cn", "china"]) ? "CN" : null;
  const candidates = scenarios.filter((s) => s.derivative.toLowerCase() === model || s.id.toLowerCase().startsWith(model));
  return candidates.find((s) => !market || s.market === market) ?? candidates[0];
}

export function routeQuestion(raw: string, ctx: { scenarioId: string; scenarios: Scenario[] }): Routed {
  const q = ` ${raw.toLowerCase().trim()} `;
  const sid = ctx.scenarioId;
  const scenario = matchScenario(q, ctx.scenarios);

  if (has(q, ["red", "green", "yellow", "rot", "grün", "gelb", "ampel", "traffic light", "evidence level", "level a", "level d"])) {
    return {
      kind: "reply",
      text: "The traffic light shows how well a requirement is backed. Green (A/B): proven by many customer voices from several sources. Yellow (C): little evidence, treat with care. Red (D): an assumption or trend without direct customer voices. Hover the label in the list to see the reason.",
      links: [{ href: `/cockpit?scenario=${sid}`, label: "See it in the ranked list" }],
    };
  }
  if (has(q, ["rationale", "begründung", "why is it stored", "audit reason"])) {
    return {
      kind: "reply",
      text: "The rationale is the reason behind a change. When you ask in your own words and apply, your question becomes the rationale. Moving sliders records the change itself, for example \"Customer pain +0.10\". Every decision needs one.",
      links: [{ href: "/audit", label: "Open the audit trail" }],
    };
  }
  if (has(q, ["score", "weight", "gewicht", "formula", "formel", "slider"])) {
    return {
      kind: "reply",
      text: "Score = weighted sum of six factors (customer pain, reach, satisfaction gap, competitive pressure, future relevance, low effort), computed in Python, never by the AI. Ask in your own words to get new weights, or open \"Fine-tune weights\" in the cockpit.",
      links: [{ href: `/cockpit?scenario=${sid}`, label: "Open cockpit" }],
    };
  }
  if (has(q, ["first", "top", "most important", "build next", "priorit*", "zuerst", "wichtigst*"])) {
    return { kind: "top", scenarioId: scenario?.id ?? sid };
  }
  if (has(q, ["audit", "prüfpfad", "history", "who decided", "trail"])) {
    return { kind: "reply", text: "Opening the audit trail: every AI and PM action with person, time and rationale, hash-chained.", navigate: "/audit" };
  }
  if (has(q, ["compare", "vergleich", "markets", "portfolio", "märkte"])) {
    return { kind: "reply", text: "Opening the portfolio: which topics hold across models and markets.", navigate: "/portfolio" };
  }
  if (has(q, ["insight", "trend", "2030", "opportunit*", "gap"]) && !scenario) {
    return { kind: "reply", text: "Opening insights: evidence vs. assumption, opportunities and 2030 trends.", navigate: `/insights?scenario=${sid}` };
  }
  if (has(q, ["evidence browser", "voices", "quotes", "stimmen", "belege"])) {
    return { kind: "reply", text: "Opening the evidence browser: search every customer voice.", navigate: `/evidence?scenario=${sid}` };
  }
  if (has(q, ["memo", "export", "csv", "download"])) {
    return {
      kind: "reply",
      text: "You can export the ranking or a decision memo from the cockpit header.",
      links: [{ href: `/cockpit?scenario=${sid}`, label: "Go to cockpit" }],
    };
  }
  if (has(q, ["guide", "help", "how does", "how do i", "hilfe", "anleitung"])) {
    return { kind: "reply", text: "Switch to the Guide tab above for the five-step walkthrough, or just ask me where to go." };
  }
  if (scenario || has(q, ["cockpit", "ranking", "ranked", "list", "liste"])) {
    const id = scenario?.id ?? sid;
    return { kind: "reply", text: `Opening the ranked list for ${scenario ? `${scenario.model_name} ${scenario.market}` : id}.`, navigate: `/cockpit?scenario=${id}` };
  }
  return { kind: "ask", question: raw.trim() };
}
