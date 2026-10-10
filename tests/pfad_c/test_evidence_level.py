"""Quellen-Rangfolge in der Evidenzstufe (BMW-Mentor: BMW-Daten zählen mehr als Web/Social Media)."""

import pytest

from core.models import EvidenceLevel, SourceType
from requirements_engine import evidence_level

FEEDBACK, STUDY, WEB = SourceType.FEEDBACK, SourceType.STUDY, SourceType.WEB


@pytest.mark.parametrize(
    ("count", "sources", "expected"),
    [
        (100, {WEB}, EvidenceLevel.C),             # nur Web: egal wie viele Nennungen, nie A oder B
        (100, {FEEDBACK}, EvidenceLevel.B),        # nur BMW-Feedback: B
        (30, {FEEDBACK, WEB}, EvidenceLevel.A),    # BMW-Beleg + Web bestätigt: A
        (30, {FEEDBACK, STUDY}, EvidenceLevel.A),  # zwei BMW-Quellen: A
    ],
)
def test_bmw_daten_zaehlen_mehr_als_web(count, sources, expected):
    level, reason = evidence_level.classify(count, sources, forward_looking=False)
    assert level == expected
    assert reason


def test_nur_web_begruendung_nennt_den_grund():
    _, reason = evidence_level.classify(100, {WEB}, forward_looking=False)
    assert "web" in reason.lower()


@pytest.mark.parametrize(
    ("count", "sources", "expected"),
    [
        (161, {FEEDBACK, STUDY}, EvidenceLevel.A),  # Basis B (15+), zweite Quelle hebt auf A
        (15, {FEEDBACK, STUDY}, EvidenceLevel.A),   # genau an der Schwelle
        (14, {FEEDBACK, STUDY}, EvidenceLevel.B),   # Basis C, zweite Quelle hebt auf B
        (8, {FEEDBACK, STUDY}, EvidenceLevel.B),    # echter Fall: Spracherkennung mit Studie
        (5, {FEEDBACK, STUDY}, EvidenceLevel.B),    # Mindestgrenze für die Hebung
        (4, {FEEDBACK, STUDY}, EvidenceLevel.C),    # darunter zählt auch die Bestätigung nicht
        (15, {FEEDBACK}, EvidenceLevel.B),          # eine Quelle: kein Aufstieg
        (14, {FEEDBACK}, EvidenceLevel.C),
        (581, {FEEDBACK}, EvidenceLevel.B),         # viele Nennungen allein reichen nie für A
        (3, {FEEDBACK, WEB}, EvidenceLevel.C),
        (30, {FEEDBACK, WEB}, EvidenceLevel.A),
    ],
)
def test_zweite_quelle_hebt_die_stufe_um_eine(count, sources, expected):
    level, _ = evidence_level.classify(count, sources, forward_looking=False)
    assert level == expected


def test_begruendung_ist_englisch_und_nennt_die_bestaetigung():
    _, reason = evidence_level.classify(8, {FEEDBACK, STUDY}, forward_looking=False)
    assert "confirmed" in reason and "independent" in reason  # die Oberfläche ist laut Roadmap englisch
