"""Was-wäre-wenn (Pfad C, W-C4): neue Reihenfolge für Probe-Gewichte, optional ohne eine Annahme. Speichert NICHTS.

Warum reine Funktion: Der PM probiert Gewichte aus (Regler, "Annahmen ignorieren"), ohne dass der Prüfpfad
volläuft oder ein Status kippt. Die Rechnung ist dieselbe wie im Score (scoring.score): Ein Faktor "ignorieren"
heißt, sein Gewicht auf 0 setzen; nach dem Normalisieren ist das scoring.score_without bis auf Rundung (höchstens
0,1 Punkte, weil scoring.score jeden Faktorbeitrag rundet; Test beweist es). Mit Standardgewichten ergibt sich dafür
exakt der heutige Score, also Rang-Änderung 0.
Verworfen: eigene Formel für das Cockpit (zwei Wahrheiten); Ergebnis im Store ablegen (kein Probieren ohne Spur).
"""

from __future__ import annotations

from core.models import Requirement
from requirements_engine import scoring


def whatif(requirements: list[Requirement], weights: dict[str, float], drop: str | None = None) -> list[dict]:
    """Neue Rangliste: {id, title, evidence_level, old_rank, new_rank, rank_change, old_score, new_score}.

    weights: Probe-Gewichte (unvollständig erlaubt, Rest bleibt Standard). drop: Faktor, der nicht zählen soll,
    z. B. "future_relevance" für "Annahmen ignorieren". rank_change > 0 heißt: nach oben gerückt.
    """
    if drop is not None and drop not in scoring.DEFAULT_WEIGHTS:
        raise ValueError(f"Unbekannter Faktor: {drop}")
    probe = scoring.normalize_weights(weights)  # prüft auch auf unbekannte Faktoren
    if drop is not None:
        probe = scoring.normalize_weights({**probe, drop: 0.0})
    scored = []
    for req in requirements:
        values = {name: factor.value for name, factor in req.score_breakdown.items()}
        values["effort_inverse"] = scoring.effort_factor(req.effort)  # der PM kann den Aufwand ändern
        new_score, _ = scoring.score(values, {}, req.evidence_level, probe)
        scored.append((req, new_score))
    scored.sort(key=lambda pair: -pair[1])
    return [{"id": r.id, "title": r.title, "evidence_level": r.evidence_level, "old_rank": r.rank, "new_rank": i,
             "rank_change": r.rank - i, "old_score": r.score, "new_score": s}
            for i, (r, s) in enumerate(scored, start=1)]
