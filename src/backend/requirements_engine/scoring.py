"""Priorisierung: transparente, gewichtete Formel in Python (Owner: Pfad C).

Warum in Python und nicht im LLM: Ein Modell rechnet nicht reproduzierbar und kann
nicht erklären, warum Platz 3 vor Platz 4 liegt. Hier ist jeder Punkt nachvollziehbar
(score_breakdown), und der PM kann die Gewichte live ändern (wird im Audit-Trail
protokolliert).

Formel:  score = Konfidenz(Evidenzstufe) * Summe(gewicht_i * faktor_i) * 100
Faktoren sind auf 0..1 normiert. Die Konfidenz bestraft schwach belegte Anforderungen,
statt sie zu verstecken: Der PM sieht sie, aber weiter unten.
"""

from __future__ import annotations

from core.models import EvidenceLevel, ScoreFactor

# Kundensicht + Geschäftssicht, wie auf der BMW-Folie "Prioritization: Customer / Business".
DEFAULT_WEIGHTS: dict[str, float] = {
    "customer_pain": 0.25,         # wie stark stört es Kunden (Defekt/Bedienproblem > Wunsch)
    "reach": 0.20,                 # wie viele Kunden x Absatzvolumen des Markts 2030
    "satisfaction_gap": 0.20,      # Abstand zum Zielwert in der Kundenstudie
    "competitive_pressure": 0.15,  # Wettbewerber bieten es bereits (Webquellen)
    "future_relevance": 0.10,      # Trend in 3-5 Jahren (Annahme!)
    "effort_inverse": 0.10,        # geringer Aufwand = höher (S=1.0, M=0.6, L=0.2)
}

CONFIDENCE = {EvidenceLevel.A: 1.0, EvidenceLevel.B: 0.85, EvidenceLevel.C: 0.7, EvidenceLevel.D: 0.5}
EFFORT_VALUE = {"S": 1.0, "M": 0.6, "L": 0.2}


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Gewichte auf Summe 1 bringen; unbekannte Faktoren ablehnen (Tippfehler im Frontend)."""
    unknown = set(weights) - set(DEFAULT_WEIGHTS)
    if unknown:
        raise ValueError(f"Unbekannte Faktoren: {sorted(unknown)}")
    merged = {**DEFAULT_WEIGHTS, **weights}
    total = sum(merged.values())
    if total <= 0:
        raise ValueError("Mindestens ein Gewicht muss größer als 0 sein.")
    return {k: v / total for k, v in merged.items()}


def score(
    factor_values: dict[str, float],
    explanations: dict[str, str],
    evidence_level: EvidenceLevel,
    weights: dict[str, float] | None = None,
) -> tuple[float, dict[str, ScoreFactor]]:
    """Berechnet Score (0-100) und die Aufschlüsselung pro Faktor."""
    w = normalize_weights(weights or {})
    breakdown: dict[str, ScoreFactor] = {}
    for name, weight in w.items():
        value = min(max(factor_values.get(name, 0.0), 0.0), 1.0)
        breakdown[name] = ScoreFactor(
            value=round(value, 3),
            weight=round(weight, 3),
            contribution=round(value * weight * 100, 1),
            explanation=explanations.get(name, "keine Daten"),
        )
    raw = sum(f.contribution for f in breakdown.values())
    return round(raw * CONFIDENCE[evidence_level], 1), breakdown


def effort_factor(effort: str) -> float:
    return EFFORT_VALUE.get(effort, 0.6)
