"""Prompt-Linse: Der PM fragt in eigenen Worten, das Cockpit zeigt die passenden Top 5 (Owner: Lead).

Beispiel: "Familien in den USA, Fokus Laden und Platz".

Warum so gebaut (KI schlägt vor, Python rechnet, PM entscheidet):
- Das LLM übersetzt die Frage NUR in Gewichte, Kategorien und "nur Lücken". Es sieht keine
  Anforderungen und nennt keine IDs; so kann es keine Quelle und keinen Treffer erfinden.
- Rang und Score rechnet scoring.score() auf Kopien; der Store bleibt unverändert. Übernehmen
  passiert erst, wenn der PM im Cockpit "Gewichte übernehmen" drückt (PUT /weights, mit Audit).
- Die Begründung je Treffer sind die zwei größten Faktoren aus score_breakdown; deren Sätze
  stammen aus den Daten, nicht aus dem Modell.
- Das LLM bekommt keine BMW-Daten (nur Frage + Faktor-/Kategorienamen). Deshalb dürfen die
  Antworten für die Demo-Fragen in data/demo_cache/ committet werden.
- Fällt das LLM aus (kein Netz, kein Cache-Eintrag), greifen Schlüsselwort-Regeln.
Verworfen: LLM sortiert die Anforderungen selbst (nicht reproduzierbar, IDs halluzinierbar).
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from core.llm import ask_json
from core.models import Category, Requirement
from requirements_engine import scoring

TOP_N = 5
GAP_STATUSES = ("not_offered", "optional")  # heute nicht oder nur gegen Aufpreis im Angebot
FOCUS_WEIGHT = 0.4  # Regel-Fallback: so viel Gewicht bekommt ein genannter Faktor

SYSTEM_PROMPT = f"""You translate a BMW product manager's question into a prioritization lens.
Do not answer the question. Return:
- weights: one entry per factor that matters, weight 0..1. Factors: {", ".join(scoring.DEFAULT_WEIGHTS)}.
  customer_pain = complaints; reach = many customers; satisfaction_gap = low study scores;
  competitive_pressure = competitors are better; future_relevance = trends in 3-5 years; effort_inverse = quick wins.
- categories: only categories the question names, from: {", ".join(c.value for c in Category)}. Empty = all.
- only_gaps: true only if the PM asks for things missing from today's offer.
- interpretation: one sentence in German, what you understood."""

# Regel-Fallback: Schlüsselwort (klein, Deutsch + Englisch) -> Kategorie bzw. Faktor
CATEGORY_WORDS = {
    "range_charging": ("lade", "laden", "reichweite", "charg", "range", "akku", "batterie"),
    "comfort_space": ("platz", "raum", "kofferraum", "stauraum", "familie", "space", "trunk", "komfort"),
    "infotainment_digital": ("bedien", "display", "touch", "infotainment", "app", "software", "navi"),
    "driver_assistance": ("assistenz", "assist", "parken", "autonom", "adas"),
    "driving_experience": ("fahrgefühl", "fahrwerk", "fahrdynamik", "handling", "driving"),
    "quality_perception": ("qualität", "quality", "verarbeitung", "haptik"),
    "interior": ("innenraum", "interieur", "interior", "sitz"),
    "exterior": ("design", "exterieur", "exterior", "optik"),
    "variants_packages": ("paket", "variante", "preis", "package"),
}
FACTOR_WORDS = {
    "future_relevance": ("zukunft", "2030", "trend", "nachfolger", "future"),
    "competitive_pressure": ("wettbewerb", "konkurrenz", "tesla", "competitor"),
    "effort_inverse": ("schnell", "quick", "aufwand", "günstig"),
    "customer_pain": ("beschwerde", "ärger", "problem", "complaint"),
    "reach": ("viele", "volumen", "masse", "reach"),
}
GAP_WORDS = ("lücke", "fehlt", "nicht angeboten", "gap", "missing")


class FactorWeight(BaseModel):
    factor: str
    weight: float


class LensPlan(BaseModel):
    """Antwort-Schema des LLM. Liste statt dict, weil Structured Outputs keine freien Schlüssel erlaubt."""

    weights: list[FactorWeight] = []
    categories: list[str] = []
    only_gaps: bool = False
    interpretation: str = ""


def sanitize(plan: LensPlan) -> dict:
    """Alles verwerfen, was es nicht gibt (Faktor, Kategorie); Gewichte auf 0..1 klemmen und normieren."""
    raw = {w.factor: min(max(w.weight, 0.0), 1.0) for w in plan.weights if w.factor in scoring.DEFAULT_WEIGHTS}
    known = {c.value for c in Category}
    try:
        weights = scoring.normalize_weights(raw)
    except ValueError:  # z. B. alle Gewichte 0
        weights = scoring.normalize_weights({})
    return {"weights": weights, "categories": [c for c in dict.fromkeys(plan.categories) if c in known],
            "only_gaps": plan.only_gaps, "interpretation": plan.interpretation.strip()}


def rule_plan(question: str) -> LensPlan:
    """Ohne LLM: Schlüsselwörter -> Kategorien und Faktoren. Schwach, aber nachvollziehbar."""
    q = question.lower()
    cats = [c for c, words in CATEGORY_WORDS.items() if any(w in q for w in words)]
    factors = [f for f, words in FACTOR_WORDS.items() if any(w in q for w in words)]
    gaps = any(w in q for w in GAP_WORDS)
    parts = ([f"Kategorien: {', '.join(cats)}"] if cats else []) + ([f"Fokus: {', '.join(factors)}"] if factors else [])
    text = "Regel-Linse (ohne KI): " + ("; ".join(parts) if parts else "keine Schlüsselwörter, Standardgewichte")
    return LensPlan(weights=[FactorWeight(factor=f, weight=FOCUS_WEIGHT) for f in factors], categories=cats,
                    only_gaps=gaps, interpretation=text + (", nur Ausstattungslücken." if gaps else "."))


def plan_lens(question: str) -> tuple[dict, str]:
    """LLM-Plan, bei Ausfall Regel-Plan. Liefert (bereinigter Plan, Quelle "ai" | "rules")."""
    try:
        plan = ask_json(SYSTEM_PROMPT, json.dumps({"question": question}, ensure_ascii=False), LensPlan)
        if plan.interpretation.strip():
            return sanitize(plan), "ai"
    except Exception:  # kein Netz, kein Demo-Cache-Eintrag, Schemafehler: die Linse darf nie ausfallen
        pass
    return sanitize(rule_plan(question)), "rules"


def _lens_score(req: Requirement, weights: dict[str, float]) -> tuple[float, list[dict]]:
    """Score mit Linsen-Gewichten (wie views.whatif) + die zwei größten Beiträge als Begründung."""
    values = {k: f.value for k, f in req.score_breakdown.items()}
    values["effort_inverse"] = scoring.effort_factor(req.effort)
    texts = {k: f.explanation for k, f in req.score_breakdown.items()}
    new_score, breakdown = scoring.score(values, texts, req.evidence_level, weights)
    top2 = sorted(breakdown.items(), key=lambda kv: -kv[1].contribution)[:2]
    return new_score, [{"factor": k, "contribution": f.contribution, "sentence": f.explanation} for k, f in top2]


def apply_lens(state, plan: dict) -> tuple[list[dict], str | None]:
    """Filtern und neu rechnen. Leerer Filter -> Hinweis und alle zeigen, statt still nichts."""
    reqs = list(state.requirements.values())
    note = None
    if plan["only_gaps"]:
        reqs = [r for r in reqs if r.offer_check.status in GAP_STATUSES]
    if plan["categories"]:
        filtered = [r for r in reqs if r.category.value in plan["categories"]]
        if not filtered:
            note = f"Keine Anforderung in {', '.join(plan['categories'])}; zeige alle Kategorien."
        reqs = filtered or reqs
    scored = sorted(((r, *_lens_score(r, plan["weights"])) for r in reqs), key=lambda t: -t[1])[:TOP_N]
    top = [{"requirement": r.model_dump(mode="json"), "lens_score": s, "lens_rank": i, "reasons": reasons}
           for i, (r, s, reasons) in enumerate(scored, start=1)]
    return top, note


def run_lens(state, question: str) -> dict:
    plan, source = plan_lens(question)
    top, note = apply_lens(state, plan)
    return {"question": question, "interpretation": plan["interpretation"], "source": source,
            "weights": plan["weights"], "filters": {"categories": plan["categories"], "only_gaps": plan["only_gaps"]},
            "note": note, "top": top}
