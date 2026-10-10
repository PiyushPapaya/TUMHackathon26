"""Pfad A: Belege -> Befunde (Signals). KI autonom, aber jeder Befund zitiert Beleg-IDs.

Vertrag (nicht ändern ohne Lead):
    extract_signals(scenario: Scenario, evidence: list[Evidence]) -> list[Signal]

Ansatz (Startpunkt, im Pfad verfeinern):
1. Vorgruppieren OHNE LLM über die BMW-Taxonomie (meta vfc2 x Feedback Type). Spart Kosten
   und ist erklärbar. Gruppen < 5 Nennungen zusammenlegen oder verwerfen.
2. Pro großer Gruppe: LLM (core.llm.ask_json) fasst in 1-3 Befunde zusammen:
   kind, category, title, summary und die IDs der 3-5 typischsten Belege.
   Prompt-Regel: nur IDs aus der Eingabe verwenden (wird in Tests geprüft = Halluzinationsschutz).
3. "no_class_found"-Belege: per LLM einer bestehenden Gruppe zuordnen oder ignorieren.
4. Studien-Belege: Attribute mit hohem Negativanteil werden eigene Befunde (kind=complaint)
   oder an passende Feedback-Befunde angehängt (-> 2 Quellenarten -> Evidenzstufe A).
5. Konflikte: gleiches Thema, entgegengesetzte Polarität (z. B. Display gelobt vs.
   Touch-Bedienung kritisiert) -> conflicts_with gegenseitig setzen.
"""

from __future__ import annotations

from core.models import Evidence, Scenario, Signal


def extract_signals(scenario: Scenario, evidence: list[Evidence]) -> list[Signal]:
    raise NotImplementedError("Pfad A: extract_signals noch nicht gebaut (siehe docs/pfade/PFAD-A.md)")
