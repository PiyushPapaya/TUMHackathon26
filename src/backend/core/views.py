"""Fertige Antworten pro Ansicht ("View-Models") für das PM-Cockpit (Owner: Lead).

Warum: Das Frontend soll nur anzeigen, nie rechnen. Jede Zahl, jedes Label und jeder Satz
entsteht hier in Python, damit Frontend, CSV und Pitch dieselben Werte zeigen und alles
ohne Browser testbar ist (tests/test_views.py). Reine Funktionen: lesen den Zustand, ändern nichts.
"""

from __future__ import annotations

from collections import Counter

from core.model_parts import DataCoverage, coverage_badge
from core.models import Requirement, Signal, SourceType
from requirements_engine import scoring

LEVEL_LABEL = {"A": "stark belegt", "B": "mittel belegt", "C": "schwach belegt", "D": "Annahme"}
FACTOR_LABEL = {
    "customer_pain": "Kundenschmerz", "reach": "Reichweite (Kunden × Volumen)",
    "satisfaction_gap": "Zufriedenheitslücke (Studie)", "competitive_pressure": "Wettbewerbsdruck",
    "future_relevance": "Zukunftsrelevanz", "effort_inverse": "Geringer Aufwand",
}
TRUST_ORDER = {"high": 0, "medium": 1, "low": 2}
ENGINE_LABEL = {"BEVE": "BEV"}  # BMW schreibt "BEVE"; im UI heißt es überall BEV


def coverage(state) -> DataCoverage:
    """Abdeckung aus dem Bundle; ältere Bundles ohne Feld: aus den Belegen zählen."""
    cov = state.scenario.data_coverage
    if any(v for k, v in cov.model_dump().items() if k != "badge"):
        return cov.model_copy(update={"badge": coverage_badge(cov.feedback)})
    counts = Counter(e.source_type for e in state.evidence.values())
    feedback = state.funnel.get("evidence", 0) - sum(c for t, c in counts.items() if t != SourceType.FEEDBACK)
    feedback = max(feedback, 0) if counts.get(SourceType.FEEDBACK) else 0
    return DataCoverage(
        feedback=feedback, study=counts.get(SourceType.STUDY, 0), sales=counts.get(SourceType.SALES, 0),
        options=counts.get(SourceType.OPTION_LIST, 0), web=counts.get(SourceType.WEB, 0),
        external=counts.get(SourceType.EXTERNAL_STAT, 0) + counts.get(SourceType.FEEDBACK_EXTERNAL, 0),
        badge=coverage_badge(feedback),
    )


def _ranked(state) -> list[Requirement]:
    return sorted(state.requirements.values(), key=lambda r: r.rank)


def scenario_card(state) -> dict:
    """Eine Kachel im Szenario-Wähler."""
    ranked = _ranked(state)
    cov = coverage(state)
    return {
        **state.scenario.model_dump(mode="json"), "data_coverage": cov.model_dump(), "badge": cov.badge,
        "headline_numbers": {
            "evidence": state.funnel.get("evidence", 0), "signals": len(state.signals),
            "requirements": len(ranked), "top_title": ranked[0].title if ranked else None,
        },
    }


def warnings(state) -> list[str]:
    """Config-Warnungen + Regeln, die der PM sehen muss, bevor er der Liste vertraut."""
    out = list(state.scenario.warnings)
    unmapped = state.context.get("unmapped_topics") or {}
    if unmapped:
        out.append(f"{len(unmapped)} Themen ohne Kategorie ({sum(unmapped.values())} Kommentare), "
                   "nicht in der Priorisierung.")
    without = [r.id for r in state.requirements.values() if r.evidence_level.value == "D" and not r.assumptions]
    if without:
        out.append(f"{len(without)} Annahme-Anforderungen ohne ausgeschriebene Annahme: {', '.join(without)}")
    return out


def overview(state) -> dict:
    """Startseite: Trichter, Top 3, Stufen-Verteilung, Warnungen, Quellen-Mix."""
    ranked = _ranked(state)
    levels = Counter(r.evidence_level.value for r in ranked)
    approved = sum(r.status.value == "approved" for r in ranked)
    return {
        "scenario_id": state.scenario.id,
        "funnel": {**state.funnel, "signals": len(state.signals), "requirements": len(ranked), "approved": approved},
        "top3": [{"id": r.id, "title": r.title, "score": r.score, "rank": r.rank, "evidence_level": r.evidence_level,
                  "level_label": LEVEL_LABEL[r.evidence_level.value], "badges": r.badges} for r in ranked[:3]],
        "level_distribution": {lvl: levels.get(lvl, 0) for lvl in "ABCD"},
        "warnings": warnings(state),
        "source_mix": coverage(state).model_dump(),
        "generated_at": state.funnel.get("generated_at"),
    }


def _linked(state, req: Requirement) -> list[Signal]:
    return [state.signals[s] for s in req.signal_ids if s in state.signals]


def waterfall(req: Requirement) -> list[dict]:
    """Score-Wasserfall: Beitrag je Faktor (größter zuerst), am Ende der Abschlag der Evidenzstufe."""
    steps = [{"factor": k, "label": FACTOR_LABEL.get(k, k), "value": f.value, "weight": f.weight,
              "contribution": f.contribution, "sentence": f.explanation}
             for k, f in sorted(req.score_breakdown.items(), key=lambda kv: -kv[1].contribution)]
    raw = round(sum(s["contribution"] for s in steps), 1)
    confidence = scoring.CONFIDENCE[req.evidence_level]
    steps.append({"factor": "confidence", "label": f"Evidenzstufe {req.evidence_level.value}", "value": confidence,
                  "weight": None, "contribution": round(req.score - raw, 1),
                  "sentence": f"{LEVEL_LABEL[req.evidence_level.value]}: Rohwert {raw} × {confidence} = {req.score}"})
    return steps


def segments(linked: list[Signal]) -> dict[str, dict[str, int]]:
    """Segment-Zählung aller verknüpften Befunde zusammengezählt (für die Balken)."""
    out: dict[str, Counter] = {}
    for sig in linked:
        for dim, counts in sig.segments.items():
            for seg, n in counts.items():
                out.setdefault(dim, Counter())[ENGINE_LABEL.get(seg, seg)] += n
    return {dim: dict(c.most_common()) for dim, c in out.items()}


def _quote(ev) -> dict:
    m = ev.meta
    return {"id": ev.id, "text": ev.text, "source_name": ev.source_name, "polarity": ev.polarity,
            "country": m.get("country"), "engine": ENGINE_LABEL.get(m.get("engine", ""), m.get("engine")),
            "source_letter": m.get("source_letter"), "feedback_type": m.get("feedback_type")}


def robustness_sentence(req: Requirement) -> str | None:
    rob = req.robustness
    if rob is None:
        return None
    span = f"Rang {rob.rank_min}" if rob.rank_min == rob.rank_max else f"Rang {rob.rank_min}–{rob.rank_max}"
    return f"In {round(rob.top3_share * 100)} % von {rob.runs} zufälligen Gewichtungen (±30 %) in den Top 3 ({span})."


def explain(state, req: Requirement, history: list) -> dict:
    """Detailseite: alles, was der PM zum Prüfen einer Anforderung braucht."""
    linked = _linked(state, req)
    ev_ids = sorted({e for s in linked for e in s.evidence_ids})
    evidence = [state.evidence[e] for e in ev_ids if e in state.evidence]
    feedback = [e for e in evidence if e.source_type in (SourceType.FEEDBACK, SourceType.FEEDBACK_EXTERNAL)]
    web = [e for e in evidence if e.source_type in (SourceType.WEB, SourceType.EXTERNAL_STAT)]
    by_id = {s.id: s for s in linked}
    signal_conflicts = sorted({tuple(sorted((s.id, o))) for s in linked for o in s.conflicts_with if o in by_id})
    return {
        "requirement": req, "level_label": LEVEL_LABEL[req.evidence_level.value],
        "waterfall": waterfall(req),
        "quotes": [_quote(e) for e in sorted(feedback, key=lambda e: e.polarity)[:5]],
        "segments": segments(linked),
        "conflicts": [c.model_dump() for c in req.segment_conflicts]
        + [{"dimension": "signal", "statement": f'"{by_id[a].title}" widerspricht "{by_id[b].title}"',
            "signal_ids": [a, b]} for a, b in signal_conflicts],
        "assumptions": req.assumptions, "uncertainties": req.uncertainties, "horizon": req.horizon,
        "offer_check": req.offer_check,
        "web_sources": sorted(({"id": e.id, "publisher": e.meta.get("publisher", e.source_name), "url": e.url,
                                "text": e.text, "trust": e.meta.get("trust", "medium")} for e in web),
                              key=lambda w: TRUST_ORDER.get(w["trust"], 3)),
        "study": [s.study_link.model_dump() for s in linked if s.study_link],
        "robustness": req.robustness, "robustness_sentence": robustness_sentence(req),
        "business": req.business,
        "signals": linked, "evidence": evidence, "history": history,
    }


def whatif(state, weights: dict[str, float]) -> list[dict]:
    """Neue Reihenfolge für Probe-Gewichte, OHNE zu speichern (kein Audit, Store unverändert)."""
    w = scoring.normalize_weights(weights)
    scored = []
    for req in state.requirements.values():
        values = {k: f.value for k, f in req.score_breakdown.items()}
        values["effort_inverse"] = scoring.effort_factor(req.effort)
        new_score, _ = scoring.score(values, {}, req.evidence_level, w)
        scored.append((req, new_score))
    scored.sort(key=lambda rs: -rs[1])
    return [{"id": r.id, "title": r.title, "evidence_level": r.evidence_level, "old_rank": r.rank, "new_rank": i,
             "rank_change": r.rank - i, "old_score": r.score, "new_score": s}
            for i, (r, s) in enumerate(scored, start=1)]
