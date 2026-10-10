"""Evidenzstufe A-D: feste Regeln statt LLM-Bauchgefühl (Owner: Pfad C).

Warum Regeln: Der Brief will klar sehen, wo eine Aussage auf Belegen beruht und wo
auf Annahmen. Eine Regel ist prüfbar und für den PM in einem Satz erklärbar.
Schwellen sind Startwerte und werden mit den echten Zahlen in Pfad C kalibriert.
"""

from __future__ import annotations

from core.models import EvidenceLevel, SourceType

# Unabhängige Quellenarten. Absatz und Optionsliste sind Kontext, kein Kundenbeleg.
CUSTOMER_SOURCES = {SourceType.FEEDBACK, SourceType.STUDY, SourceType.WEB}


def classify(mention_count: int, source_types: set[SourceType], forward_looking: bool) -> tuple[EvidenceLevel, str]:
    """Liefert Stufe + Begründungssatz für die UI."""
    independent = source_types & CUSTOMER_SOURCES
    if forward_looking and mention_count < 5:
        return EvidenceLevel.D, "Zukunftsannahme: kaum direkte Kundenbelege, beruht auf Trends."
    if len(independent) >= 2 and mention_count >= 20:
        return EvidenceLevel.A, f"{mention_count} Nennungen aus {len(independent)} unabhängigen Quellenarten."
    if mention_count >= 15:
        return EvidenceLevel.B, f"{mention_count} Nennungen, aber nur aus einer Quellenart."
    return EvidenceLevel.C, f"Nur {mention_count} Nennungen: Hinweis, kein belastbarer Befund."
