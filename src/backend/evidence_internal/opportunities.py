"""Chancen-Karte aus Studienbelegen.

Importance ist eine einfache, nachvollziehbare Proxy-Zahl: je stärker ein Attribut
polarisiert (sehr zufrieden oder unzufrieden), desto wichtiger behandeln wir es.
"""

from __future__ import annotations

from core.models import Evidence, SourceType
from evidence_internal.study_topics import study_category


def _number(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def _dissatisfaction(ev: Evidence) -> float | None:
    neg = _number(ev.meta.get("neg_share"))
    if neg is not None:
        return neg / 100 if neg > 1 else neg
    mean = _number(ev.meta.get("mean"))
    if mean is not None:
        return max(0.0, min((9.0 - mean) / 3.0, 1.0))
    return None


def _importance(ev: Evidence, dissatisfaction: float) -> float | None:
    top2 = _number(ev.meta.get("top2"))
    if top2 is not None:
        top2 = top2 / 100 if top2 > 1 else top2
        return max(dissatisfaction, top2)
    mean = _number(ev.meta.get("mean"))
    if mean is not None:
        return max(dissatisfaction, min(mean / 10.0, 1.0))
    return None


def opportunities_from_evidence(evidence: list[Evidence]) -> list[dict]:
    """Liefert Punkte für Importance-vs.-Dissatisfaction-Ansicht."""
    points = []
    for ev in evidence:
        if ev.source_type != SourceType.STUDY:
            continue
        attribute = ev.meta.get("attribute", "")
        category = study_category(attribute)
        dissatisfaction = _dissatisfaction(ev)
        if category is None or dissatisfaction is None:
            continue
        importance = _importance(ev, dissatisfaction)
        points.append({
            "attribute": attribute,
            "category": category.value,
            "importance": round(importance, 3) if importance is not None else None,
            "dissatisfaction": round(dissatisfaction, 3),
            "evidence_id": ev.id,
        })
    points.sort(key=lambda p: (-(p["importance"] or 0), -p["dissatisfaction"], p["attribute"]))
    return points
