"""Vergleich über Szenarien: Portfolio-Matrix und Markt-Vergleich (Owner: Lead).

Warum: BMW will "scale across vehicle lines and markets". Die Matrix zeigt, ob ein Thema
eine Plattform-Entscheidung ist (überall oben) oder nur ein Modell bzw. einen Markt betrifft.
Die Klassen sind Regeln in Python, damit der PM sie nachrechnen kann.
"""

from __future__ import annotations

from core.models import Category, Requirement
from core.views import LEVEL_LABEL, coverage

TOP_N = 5  # "oben" heißt: mindestens eine Anforderung des Themas unter den ersten 5


def _best_per_category(requirements) -> dict[str, Requirement]:
    best: dict[str, Requirement] = {}
    for req in sorted(requirements, key=lambda r: r.rank):
        best.setdefault(req.category.value, req)
    return best


def _cell(req: Requirement | None) -> dict | None:
    if req is None:
        return None
    return {"requirement_id": req.id, "title": req.title, "rank": req.rank, "score": req.score,
            "evidence_level": req.evidence_level, "level_label": LEVEL_LABEL[req.evidence_level.value]}


def classify(top_scenarios: list, all_scenarios: list) -> str:
    """Regel: in ≥ 2/3 aller Szenarien oben = plattformweit; nur ein Modell = modellspezifisch;
    nur ein Markt = marktspezifisch; sonst gemischt. Keine Nennung oben = nicht oben."""
    if not top_scenarios:
        return "nicht oben"
    if len(top_scenarios) >= max(2, round(len(all_scenarios) * 2 / 3)):
        return "plattformweit"
    if len(top_scenarios) == 1:
        return "einzeln"
    if len({s.derivative for s in top_scenarios}) == 1:
        return "modellspezifisch"
    if len({s.market for s in top_scenarios}) == 1:
        return "marktspezifisch"
    return "gemischt"


def portfolio(states: dict) -> dict:
    """Matrix Kategorie × Szenario mit bestem Rang und Evidenzstufe je Zelle."""
    scenario_ids = sorted(states)
    best = {sid: _best_per_category(states[sid].requirements.values()) for sid in scenario_ids}
    scenarios = [states[sid].scenario for sid in scenario_ids]
    rows = []
    for cat in Category:
        cells = {sid: _cell(best[sid].get(cat.value)) for sid in scenario_ids}
        top = [states[sid].scenario for sid in scenario_ids if cells[sid] and cells[sid]["rank"] <= TOP_N]
        rows.append({"category": cat.value, "cells": cells, "class": classify(top, scenarios),
                     "top_in": [s.id for s in top]})
    rows.sort(key=lambda r: (-len(r["top_in"]), r["category"]))
    return {
        "scenarios": [{"id": s.id, "model_name": s.model_name, "market": s.market,
                       "data_coverage": coverage(states[s.id]).model_dump()} for s in scenarios],
        "rows": rows, "top_n": TOP_N,
        "rule": "plattformweit = in mind. 2/3 der Szenarien unter den Top 5; modell-/marktspezifisch = nur ein "
                "Modell bzw. ein Markt; einzeln = nur ein Szenario.",
    }


def compare(state_a, state_b) -> dict:
    """Gleiche Themen nebeneinander: Rang und Unzufriedenheit (Studie) in Szenario A und B."""
    best_a = _best_per_category(state_a.requirements.values())
    best_b = _best_per_category(state_b.requirements.values())
    opp_a = {o.get("category"): o.get("dissatisfaction") for o in state_a.opportunities}
    opp_b = {o.get("category"): o.get("dissatisfaction") for o in state_b.opportunities}
    rows = []
    for cat in Category:
        a, b = best_a.get(cat.value), best_b.get(cat.value)
        if not a and not b:
            continue
        rank_diff = (a.rank - b.rank) if a and b else None
        rows.append({"category": cat.value, "a": _cell(a), "b": _cell(b), "rank_diff": rank_diff,
                     "dissatisfaction_a": opp_a.get(cat.value), "dissatisfaction_b": opp_b.get(cat.value),
                     "sentence": _compare_sentence(cat.value, a, b, state_a.scenario.id, state_b.scenario.id)})
    rows.sort(key=lambda r: min(x["rank"] for x in (r["a"], r["b"]) if x))
    return {"a": state_a.scenario.id, "b": state_b.scenario.id, "rows": rows}


def _compare_sentence(category: str, a, b, id_a: str, id_b: str) -> str:
    if a and not b:
        return f"{category}: nur in {id_a} eine Anforderung (Rang {a.rank})."
    if b and not a:
        return f"{category}: nur in {id_b} eine Anforderung (Rang {b.rank})."
    if a.rank == b.rank:
        return f"{category}: in beiden Märkten Rang {a.rank}."
    higher, lower = (id_a, id_b) if a.rank < b.rank else (id_b, id_a)
    return f"{category}: in {higher} wichtiger (Rang {min(a.rank, b.rank)} vs. {max(a.rank, b.rank)} in {lower})."
