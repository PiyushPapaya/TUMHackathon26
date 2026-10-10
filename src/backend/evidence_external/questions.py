"""Pfad B, B2: Fragen für die Websuche aus den Befunden (Pfad A) und den Wettbewerbern.

Warum feste Regeln statt LLM: Die Fragen bestimmen, was wir im Web finden. Mit einer reinen Funktion
sind sie reproduzierbar, testbar und der Cache (core.llm) trifft bei jedem Lauf dieselben Fragen.

Aufteilung (13 Fragen für G60-US): bis zu 8 Wettbewerbsfragen + 5 feste Trendfragen
+ optional bis zu 3 marktspezifische Trendfragen aus der Config (extra_trend_topics, z. B. China).

Zeitfenster der Trendfragen kommt aus successor_horizon der Config: Horizont -2 bis +1
(Nachfolger 2030 -> "between 2028 and 2031"). Warum genau diese Regel: Sie ergibt für alle
2030er-Szenarien den bisherigen Fragetext, damit der committete Demo-Cache gültig bleibt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.models import Category, Scenario, Signal

MAX_COMPETITOR_QUESTIONS = 8
MAX_EXTRA_TRENDS = 3  # 5 feste + 3 marktspezifische = höchstens 8 Trendfragen

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


def trend_window(scenario: Scenario) -> tuple[int, int]:
    """Von 2 Jahren vor dem Nachfolger bis 1 Jahr danach; unlesbarer Horizont -> 2030."""
    horizon = int(scenario.successor_horizon) if str(scenario.successor_horizon).isdigit() else 2030
    return horizon - 2, horizon + 1


def _trend_questions(scenario: Scenario) -> list[Question]:
    start, end = trend_window(scenario)
    extra = [(Category(c), t) for c, t in scenario.extra_trend_topics[:MAX_EXTRA_TRENDS]]
    return [
        Question(
            text=(f"Which developments in {topic} are expected between {start} and {end} for premium cars "
                  f"in the segment of the {scenario.model_name} in the {scenario.market} market?"),
            kind="trend", category=category,
        )
        for category, topic in TREND_TOPICS + extra
    ]


def build_questions(scenario: Scenario, signals: list[Signal]) -> list[Question]:
    return _competitor_questions(scenario, signals) + _trend_questions(scenario)
