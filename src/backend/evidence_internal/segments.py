"""Segment-Zählungen für Befunde.

Die Gruppierung selbst bleibt in signals.py; dieses Modul zählt danach nur die
Kommentar-Metadaten je Dimension, damit UI und Konfliktlogik dieselbe Basis sehen.
"""

from __future__ import annotations

from collections import Counter

from core.models import Evidence, SourceType

DIMENSIONS = ("engine", "country", "source", "feedback_type")


def _parts(value: str) -> list[str]:
    return [part.strip() for part in value.split(" | ") if part.strip()]


def signal_segments(evidence_ids: list[str], by_id: dict[str, Evidence]) -> dict[str, dict[str, int]]:
    """Zählt Feedback-Belege je Antrieb, Land, Quelle und Feedback-Typ."""
    counts = {dim: Counter() for dim in DIMENSIONS}
    for evidence_id in evidence_ids:
        ev = by_id.get(evidence_id)
        if ev is None or ev.source_type != SourceType.FEEDBACK:
            continue
        meta = ev.meta
        for dim in ("engine", "country"):
            if value := meta.get(dim, "").strip():
                counts[dim][value] += 1
        source = meta.get("source_letter") or meta.get("source")
        if source:
            counts["source"][source] += 1
        for feedback_type in _parts(meta.get("feedback_type", "")):
            counts["feedback_type"][feedback_type] += 1
    return {dim: dict(counter.most_common()) for dim, counter in counts.items() if counter}
