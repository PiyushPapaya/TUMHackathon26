"""Bausteine des Vertrags für Welle 2 (Owner: Lead).

Warum eine eigene Datei: models.py bliebe sonst nicht unter 200 Zeilen. Alle Felder hier
sind ADDITIV: Jedes neue Feld in models.py hat einen Default, damit alte Bundles, Tests
und das Frontend weiterlaufen. Diese Datei importiert nichts aus models.py (keine Zyklen).

Grundsatz: Python rechnet diese Werte (Robustheit, Wachstum, Abdeckung), nie das LLM.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Horizon = Literal["today", "next_gen"]  # heute lösbar vs. Wette auf den Nachfolger (3-5 Jahre)


class StudyLink(BaseModel):
    """Zuordnung eines Befunds zu einem Attribut der Kundenstudie (falls möglich)."""

    attribute: str = Field(examples=["Intuitiveness of controls"])
    importance: float | None = None       # 0-1, wie wichtig das Attribut Kunden ist
    dissatisfaction: float | None = None  # 0-1, Anteil Unzufriedener bzw. normierter Abstand zum Bestwert


class Robustness(BaseModel):
    """Wie stabil ist der Rang, wenn man die Gewichte zufällig um ±30 % verschiebt?"""

    rank_min: int
    rank_max: int
    top3_share: float = Field(ge=0, le=1)  # Anteil der Gewichtungen, in denen die Anforderung Top 3 ist
    runs: int = 500


class SegmentConflict(BaseModel):
    """Ein Thema, bei dem zwei Kundengruppen oder Quellen sich widersprechen."""

    dimension: Literal["engine", "country", "source", "study_vs_feedback", "web"]
    segment_a: str = Field(examples=["BEV"])
    segment_b: str = Field(examples=["ICE"])
    statement: str = Field(examples=["BEV-Fahrer kritisieren das Laden (42), ICE-Fahrer loben die Reichweite (18)."])
    a_count: int = 0
    b_count: int = 0
    evidence_ids: list[str] = []


class BusinessContext(BaseModel):
    """Business-Seite aus sales_volumes.xlsx; None-Werte heißen 'nicht verfügbar', nie still 0."""

    volume_2025: int | None = None
    volume_2030: int | None = None
    growth_pct: float | None = None    # 2025 -> 2030 in Prozent
    market_share: float | None = None  # Anteil dieses Markts am Modell-Volumen 2030 (0-1)
    note: str = ""


class DataCoverage(BaseModel):
    """Wie viele Belege pro Quelle ein Szenario hat. Steuert das Badge im Szenario-Wähler."""

    feedback: int = 0
    study: int = 0
    sales: int = 0
    options: int = 0
    web: int = 0
    external: int = 0
    badge: Literal["reich", "dünn", "Kaltstart"] = "Kaltstart"


RICH_FROM = 1000  # ab so vielen Kundenkommentaren gilt ein Szenario als "reich"


def coverage_badge(feedback_count: int) -> str:
    """Regel statt Gefühl: 0 Kommentare = Kaltstart, unter 1.000 = dünn, sonst reich."""
    if feedback_count == 0:
        return "Kaltstart"
    return "dünn" if feedback_count < RICH_FROM else "reich"
