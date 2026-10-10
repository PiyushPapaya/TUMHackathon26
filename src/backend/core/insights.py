"""Ehrlichkeits- und Zukunfts-Ansichten: Lücken, Trends, Chancen-Karte, Beleg-Browser (Owner: Lead).

Warum: BMW fragt nach "understanding of uncertainty" und "3-5 years ahead". Diese Ansichten
zeigen, wo wir raten (Stufe C/D, fehlende Quellen) und welche Studie BMW als Nächstes
fahren sollte. Alles regelbasiert, kein LLM.
"""

from __future__ import annotations

from core.models import SignalKind, SourceType
from core.views import LEVEL_LABEL, coverage

# Welche Studie schließt die Lücke? Feste Vorschläge je Kategorie, damit es nachvollziehbar bleibt.
NEXT_STUDY = {
    "exterior": "Design-Klinik mit Bildvarianten",
    "interior": "Sitzprobe / Interieur-Klinik",
    "comfort_space": "Raum- und Alltags-Test mit Bestandskunden",
    "infotainment_digital": "Bedien-Usability-Test (Blindbedienung, Aufgabenzeit)",
    "driving_experience": "Probefahrt-Befragung nach Antriebsart",
    "range_charging": "Lade-Tagebuch-Studie mit BEV-Fahrern",
    "driver_assistance": "Assistenz-Akzeptanz-Befragung",
    "quality_perception": "Haptik- und Qualitäts-Klinik",
    "variants_packages": "Conjoint-Analyse zu Paketen und Preisen",
}
COVERAGE_GAP = {
    "feedback": "Keine Kundenkommentare für diesen Markt: Befunde stützen sich nur auf Studie, Absatz und Web.",
    "study": "Keine Kundenstudie: Zufriedenheitslücken sind nicht messbar.",
    "sales": "Keine Absatzzahlen: Reichweite ist geschätzt.",
    "options": "Keine Optionsliste: wir wissen nicht, was es heute schon gibt.",
    "web": "Keine Webbelege: Wettbewerb und Trends fehlen.",
}
QUADRANTS = ("Chance", "Stärke halten", "Beobachten", "Nebensache")
IMPORTANT_FROM = 0.5      # Wichtigkeit ≥ 0,5 = wichtig
DISSATISFIED_FROM = 0.08  # ≥ 8 % Unzufriedene = Problem (US-Studie: Anteil der drei schlechtesten Stufen)


def gaps(state) -> dict:
    """Was wir nicht wissen: schwach belegte Anforderungen, fehlende Quellen, nächste Studie."""
    cov = coverage(state).model_dump()
    weak = [r for r in sorted(state.requirements.values(), key=lambda r: r.rank)
            if r.evidence_level.value in ("C", "D")]
    return {
        "scenario_id": state.scenario.id,
        "weak_requirements": [{
            "id": r.id, "title": r.title, "rank": r.rank, "evidence_level": r.evidence_level,
            "level_label": LEVEL_LABEL[r.evidence_level.value], "assumptions": r.assumptions,
            "why": (r.uncertainties or r.assumptions or [LEVEL_LABEL[r.evidence_level.value]])[0],
            "next_study": NEXT_STUDY.get(r.category.value, "Gezielte Kundenbefragung"),
        } for r in weak],
        "missing_sources": [text for key, text in COVERAGE_GAP.items() if not cov.get(key)],
        "share_weak": round(len(weak) / len(state.requirements), 2) if state.requirements else 0.0,
    }


def trends(state) -> dict:
    """Trendradar: Trend-Befunde und Zukunftswetten mit Horizont heute / Nachfolger."""
    horizon = state.scenario.successor_horizon
    items = []
    for sig in state.signals.values():
        if sig.kind == SignalKind.TREND:
            items.append({"topic": sig.title, "category": sig.category, "horizon": horizon, "kind": "trend",
                          "strength": sig.mention_count, "sources": sig.source_types, "signal_id": sig.id,
                          "evidence_level": None})
    for req in state.requirements.values():
        if req.horizon == "next_gen":
            items.append({"topic": req.title, "category": req.category, "horizon": horizon, "kind": "bet",
                          "strength": req.score, "sources": sorted({t for s in req.signal_ids if s in state.signals
                                                                    for t in state.signals[s].source_types}),
                          "requirement_id": req.id, "evidence_level": req.evidence_level,
                          "assumptions": req.assumptions})
    items.sort(key=lambda i: -i["strength"])
    return {"scenario_id": state.scenario.id, "successor_horizon": horizon, "rings": ["heute", horizon],
            "items": items}


def quadrant(importance: float, dissatisfaction: float) -> str:
    """Importance-Performance-Analyse: wichtig + unzufrieden = Chance."""
    important = importance >= IMPORTANT_FROM
    unhappy = dissatisfaction >= DISSATISFIED_FROM
    if important:
        return "Chance" if unhappy else "Stärke halten"
    return "Beobachten" if unhappy else "Nebensache"


def opportunities(state) -> dict:
    """Chancen-Karte aus der Studie. Quadrant wird hier neu gerechnet, damit die Regel an einer Stelle lebt."""
    points = [{**o, "quadrant": quadrant(o["importance"], o["dissatisfaction"])}
              for o in state.opportunities if o.get("importance") is not None and o.get("dissatisfaction") is not None]
    return {"scenario_id": state.scenario.id, "points": points, "quadrants": list(QUADRANTS),
            "thresholds": {"importance": IMPORTANT_FROM, "dissatisfaction": DISSATISFIED_FROM}}


def evidence_page(state, signal: str | None = None, segment: str | None = None, q: str | None = None,
                  page: int = 1, size: int = 20) -> dict:
    """Beleg-Browser: gefiltert und seitenweise. segment z. B. "engine:BEV" oder "country:KR"."""
    items = list(state.evidence.values())
    if signal:
        ids = set(state.signals[signal].evidence_ids) if signal in state.signals else set()
        items = [e for e in items if e.id in ids]
    if segment and ":" in segment:
        key, value = segment.split(":", 1)
        meta_key = {"source": "source_letter"}.get(key, key)
        values = {value, "BEVE"} if value == "BEV" else {value}
        items = [e for e in items if e.meta.get(meta_key) in values]
    if q:
        items = [e for e in items if q.lower() in e.text.lower()]
    items.sort(key=lambda e: (e.source_type != SourceType.FEEDBACK, e.id))
    page = max(page, 1)
    return {"total": len(items), "page": page, "size": size,
            "items": [e.model_dump(mode="json") for e in items[(page - 1) * size: page * size]]}
