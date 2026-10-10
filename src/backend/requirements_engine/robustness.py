"""Rang-Robustheit (Pfad C, W-C2): Wie stabil ist die Reihenfolge, wenn die Gewichte unsicher sind?

Warum: Die Gewichte (25/20/20/15/10/10 %) sind Startwerte, nicht bewiesen. Statt eine Rangzahl als
Wahrheit zu verkaufen, verschieben wir jedes Gewicht 500-mal zufällig um bis zu ±30 % und zählen, wie
sich der Rang ändert. Pitch-Satz: "Die Nr. 1 bleibt in X % aller plausiblen Gewichtungen vorne."
Nur Standardbibliothek und fester Seed: gleiche Eingabe ergibt dieselbe Zahl (Jury kann nachrechnen).
Verworfen: LLM schätzt die Sicherheit (nicht reproduzierbar), Gewichte aus Echtdaten lernen (haben wir nicht).
"""

from __future__ import annotations

import random

from core.model_parts import Robustness
from core.models import Requirement
from requirements_engine.scoring import CONFIDENCE, DEFAULT_WEIGHTS

RUNS = 500
PERTURBATION = 0.3  # jedes Gewicht darf um bis zu ±30 % abweichen
SEED = 42
TOP = 3


def _ranks(rows: list[tuple[list[float], float]], weights: list[float]) -> list[int]:
    """Rang je Zeile (1 = vorn). Gleichstand entscheidet die Listenreihenfolge, damit nichts zufällig kippt."""
    scores = [confidence * sum(w * v for w, v in zip(weights, values, strict=True)) for values, confidence in rows]
    order = sorted(range(len(rows)), key=lambda i: (-scores[i], i))
    ranks = [0] * len(rows)
    for rank, index in enumerate(order, start=1):
        ranks[index] = rank
    return ranks


def compute_robustness(requirements: list[Requirement], runs: int = RUNS, seed: int = SEED) -> dict[str, Robustness]:
    """{Anforderungs-ID: Robustheit}. Die Spanne enthält immer auch den unverschobenen Rang."""
    names = list(DEFAULT_WEIGHTS)
    base_weights = [DEFAULT_WEIGHTS[n] for n in names]
    rows = [([req.score_breakdown[n].value if n in req.score_breakdown else 0.0 for n in names],
             CONFIDENCE[req.evidence_level]) for req in requirements]
    best = _ranks(rows, base_weights)  # Startpunkt: die Rangliste mit den Standardgewichten
    worst = list(best)
    top_hits = [0] * len(rows)
    rng = random.Random(seed)
    for _ in range(runs):
        # Die Summe der Gewichte muss nicht 1 ergeben: Alle Scores skalieren gleich, der Rang bleibt.
        weights = [w * (1 + rng.uniform(-PERTURBATION, PERTURBATION)) for w in base_weights]
        for i, rank in enumerate(_ranks(rows, weights)):
            best[i], worst[i] = min(best[i], rank), max(worst[i], rank)
            top_hits[i] += rank <= TOP
    result = {}
    for i, req in enumerate(requirements):
        low, high = (min(best[i], req.rank), max(worst[i], req.rank)) if req.rank > 0 else (best[i], worst[i])
        result[req.id] = Robustness(rank_min=low, rank_max=high, top3_share=round(top_hits[i] / runs, 3), runs=runs)
    return result
