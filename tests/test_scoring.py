"""Priorisierung und Evidenzstufe: nachvollziehbar und robust gegen Fehleingaben."""

import pytest

from core.models import EvidenceLevel, SourceType
from requirements_engine import evidence_level, scoring

ALL_ONE = {k: 1.0 for k in scoring.DEFAULT_WEIGHTS}


def test_max_score_is_100_with_strong_evidence():
    total, breakdown = scoring.score(ALL_ONE, {}, EvidenceLevel.A)
    assert total == pytest.approx(100, abs=0.5)
    assert set(breakdown) == set(scoring.DEFAULT_WEIGHTS)


def test_weak_evidence_lowers_score_but_keeps_breakdown():
    strong, _ = scoring.score(ALL_ONE, {}, EvidenceLevel.A)
    assumption, breakdown = scoring.score(ALL_ONE, {}, EvidenceLevel.D)
    assert assumption == pytest.approx(strong * 0.5, abs=0.5)
    assert breakdown["customer_pain"].contribution > 0


def test_weights_are_normalized_and_unknown_rejected():
    assert sum(scoring.normalize_weights({"reach": 5}).values()) == pytest.approx(1)
    with pytest.raises(ValueError):
        scoring.normalize_weights({"preis": 0.5})  # Preis ist laut Brief out of scope


def test_values_outside_range_are_clamped():
    total, _ = scoring.score({"customer_pain": 7.0}, {}, EvidenceLevel.A)
    assert total <= 100


@pytest.mark.parametrize(
    ("count", "sources", "future", "expected"),
    [
        (61, {SourceType.FEEDBACK, SourceType.STUDY}, False, EvidenceLevel.A),
        (38, {SourceType.FEEDBACK}, False, EvidenceLevel.B),
        (4, {SourceType.FEEDBACK}, False, EvidenceLevel.C),
        (2, {SourceType.WEB}, True, EvidenceLevel.D),
        (40, {SourceType.FEEDBACK, SourceType.SALES}, False, EvidenceLevel.B),  # Absatz ist kein Kundenbeleg
    ],
)
def test_evidence_level_rules(count, sources, future, expected):
    level, reason = evidence_level.classify(count, sources, future)
    assert level == expected
    assert reason
