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
