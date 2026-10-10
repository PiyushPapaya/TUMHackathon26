"""Pfad C: Befunde -> Anforderungen (KI schlägt vor) -> Score (Formel) -> Rang.

Vertrag (nicht ändern ohne Lead):
    derive_requirements(scenario, signals, evidence, context) -> list[Requirement]

Arbeitsteilung KI vs. Code (das zeigen wir der Jury):
- KI (core.llm.ask_json): Befunde zu Anforderungen bündeln, kundenorientiert formulieren,
  messbares Akzeptanzkriterium, Annahmen, Unsicherheiten, grober Aufwand S/M/L,
  Scope-Prüfung (Regulatorik/Technik/Preis -> verwerfen mit Grund).
- Code: Faktorwerte (customer_pain, reach, satisfaction_gap, competitive_pressure,
  future_relevance) aus Zählungen berechnen, Evidenzstufe (evidence_level.classify),
  Score (scoring.score), Rang, OfferCheck gegen context["offer"].

Regeln für den Prompt:
- Nur signal_ids aus der Eingabe; jede Anforderung >= 1 Befund (Test prüft das).
- "customer-facing": beschreibt, was der Kunde erlebt, keine Bauteile.
- Akzeptanzkriterium mit Zahl (wie BMW-Folie: "Range: 600 or 700 mi?").
"""

from __future__ import annotations

from core.models import Evidence, Requirement, Scenario, Signal


def derive_requirements(
    scenario: Scenario, signals: list[Signal], evidence: list[Evidence], context: dict
) -> list[Requirement]:
    raise NotImplementedError("Pfad C: derive_requirements noch nicht gebaut (siehe docs/pfade/PFAD-C.md)")
