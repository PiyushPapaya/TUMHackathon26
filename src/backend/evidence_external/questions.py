"""Pfad B, B2: Fragen für die Websuche aus den Befunden (Pfad A) und den Wettbewerbern.

Warum feste Regeln statt LLM: Die Fragen bestimmen, was wir im Web finden. Mit einer reinen Funktion
sind sie reproduzierbar, testbar und der Cache (core.llm) trifft bei jedem Lauf dieselben Fragen.

Aufteilung (13 Fragen für G60-US): bis zu 8 Wettbewerbsfragen + 5 feste Trendfragen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.models import Category, Scenario, Signal

MAX_COMPETITOR_QUESTIONS = 8

# Kategorie -> englisches Thema für die Frage (Websuche funktioniert auf Englisch am besten).
TOPIC = {
    Category.EXTERIOR: "exterior design",
    Category.INTERIOR: "interior design and materials",
    Category.COMFORT_SPACE: "comfort, storage and cargo space",
    Category.INFOTAINMENT_DIGITAL: "infotainment, display and controls",
    Category.DRIVING_EXPERIENCE: "driving experience and ride comfort",
    Category.RANGE_CHARGING: "range, charging and charging infrastructure",
    Category.DRIVER_ASSISTANCE: "driver assistance systems",
    Category.QUALITY_PERCEPTION: "perceived build quality",
    Category.VARIANTS_PACKAGES: "trim levels and option packages",
}

# Fünf feste Trendthemen: (Kategorie, Thema). Reihenfolge = Laden, Software, Bedienung, Innenraum, Assistenz.
TREND_TOPICS = [
    (Category.RANGE_CHARGING, "charging speed, real-world range and charging network access"),
    (Category.INFOTAINMENT_DIGITAL, "in-car software, apps and over-the-air updates"),
    (Category.INFOTAINMENT_DIGITAL, "operating concepts (physical buttons vs. touchscreen vs. voice)"),
    (Category.INTERIOR, "interior design, space concepts and sustainable materials"),
    (Category.DRIVER_ASSISTANCE, "driver assistance and automated driving (hands-off, Level 2+/3)"),
]


@dataclass(frozen=True)
class Question:
    text: str
    kind: Literal["competitor", "trend"]
    category: Category
    signal_id: str | None = None  # interner Befund, der die Frage auslöst (nur Wettbewerb)
    competitor: str | None = None


def _competitor_questions(scenario: Scenario, signals: list[Signal]) -> list[Question]:
    """Befund i bekommt Wettbewerber i; reichen die Befunde nicht für 8 Fragen, startet die zweite
    Runde mit dem jeweils nächsten Wettbewerber. So kommt jeder Wettbewerber vor und kein Paar doppelt."""
    findings = [s for s in signals if s.kind in ("complaint", "unmet_need")]
    findings = sorted(findings, key=lambda s: s.mention_count, reverse=True)[:MAX_COMPETITOR_QUESTIONS]
    rivals = scenario.competitors
    if not findings or not rivals:
        return []

    questions: list[Question] = []
    slots = min(MAX_COMPETITOR_QUESTIONS, len(findings) * len(rivals))
    for k in range(slots):
        finding = findings[k % len(findings)]
        rival = rivals[(k + k // len(findings)) % len(rivals)]
        topic = TOPIC[finding.category]
        questions.append(Question(
            text=(f"How does the {rival} handle {topic} compared with the {scenario.model_name} "
                  f"in the {scenario.market} market (2025/2026)? Customers report: \"{finding.title}\"."),
            kind="competitor", category=finding.category, signal_id=finding.id, competitor=rival,
        ))
    return questions


def _trend_questions(scenario: Scenario) -> list[Question]:
    return [
        Question(
            text=(f"Which developments in {topic} are expected between 2028 and 2031 for premium cars "
                  f"in the segment of the {scenario.model_name} in the {scenario.market} market?"),
            kind="trend", category=category,
        )
        for category, topic in TREND_TOPICS
    ]


def build_questions(scenario: Scenario, signals: list[Signal]) -> list[Question]:
    return _competitor_questions(scenario, signals) + _trend_questions(scenario)
