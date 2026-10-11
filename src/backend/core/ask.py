"""Globaler Frage-Endpunkt fuer die Demo.

Der Endpunkt beantwortet keine Fachfrage frei. Er uebersetzt die Frage in dieselbe
Linse wie `/lens`, sucht die besten Anforderungen je Szenario und gibt nur IDs und
datenbasierte Gruende zurueck. So kann die Demo fragen beantworten, ohne neue
Quellen oder Anforderungen zu erfinden.
"""

from __future__ import annotations

from core import lens

TOP_SCENARIOS = 3
TOP_PER_SCENARIO = 2


def answer(states: dict, question: str) -> dict:
    """PM-Frage -> Top-Anforderungen ueber alle geladenen Szenarien."""
    rows = []
    # Frage EINMAL deuten (ein LLM-Aufruf), dann in jedem Szenario in Python rechnen.
    # Warum: Die Deutung hängt nicht vom Szenario ab; sechs Aufrufe kosteten ~5 s je neuer Frage
    # und konnten dieselbe Frage pro Markt verschieden deuten.
    plan, source = lens.plan_lens(question)
    for scenario_id, state in sorted(states.items()):
        top, _note = lens.apply_lens(state, plan)
        for item in top[:TOP_PER_SCENARIO]:
            req = item["requirement"]
            linked = [state.signals[sid] for sid in req["signal_ids"] if sid in state.signals]
            evidence_ids = sorted({eid for sig in linked for eid in sig.evidence_ids})
            rows.append({
                "scenario_id": scenario_id,
                "requirement_id": req["id"],
                "title": req["title"],
                "rank": req["rank"],
                "score": req["score"],
                "lens_score": item["lens_score"],
                "evidence_level": req["evidence_level"],
                "signal_ids": req["signal_ids"],
                "evidence_ids": evidence_ids[:8],
                "reasons": item["reasons"],
            })
    rows.sort(key=lambda r: (-r["lens_score"], r["scenario_id"], r["rank"]))
    top = rows[:TOP_SCENARIOS * TOP_PER_SCENARIO]
    return {
        "question": question,
        "source": source,
        "interpretation": plan["interpretation"],
        "answer": _sentence(top),
        "top": top,
    }


def _sentence(rows: list[dict]) -> str:
    if not rows:
        return "Keine passenden Anforderungen gefunden."
    best = rows[0]
    return (
        f"Staerkster Treffer ist {best['requirement_id']} in {best['scenario_id']}: "
        f"{best['title']} (Score {best['lens_score']})."
    )
