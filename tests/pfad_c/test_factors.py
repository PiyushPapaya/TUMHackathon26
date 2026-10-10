"""Tests für die Faktoren der Priorisierung (Ticket C3): je Faktor ein Beispiel mit erwarteter Zahl.

Die Eingaben sind synthetisch (keine echten BMW-Daten im Repo).
"""

import pytest

from core.models import Category, Evidence, Signal, SignalKind, SourceType
from requirements_engine.factors import compute_factors, rationale_from


def _signal(sid, kind, mentions, evidence_ids, sources=(SourceType.FEEDBACK,)):
    return Signal(
        id=sid, kind=kind, category=Category.INFOTAINMENT_DIGITAL, title="t", summary="s",
        evidence_ids=list(evidence_ids), mention_count=mentions, source_types=list(sources),
    )


def _evidence(eid, source_type=SourceType.FEEDBACK, **meta):
    return Evidence(id=eid, source_type=source_type, source_name="x", derivative="G60", market="US",
                    text="synthetisch", meta=meta)


CONTEXT = {"sales": {"market": "US", "share_of_total_2030": 0.25}}


def _run(signals, evidence, max_mentions=100, forward=False, effort="M"):
    return compute_factors(signals, {e.id: e for e in evidence}, max_mentions, forward, effort, CONTEXT)


def test_customer_pain_gewichtet_nach_art_und_nennungen():
    # 30 Beschwerden (1,0) und 10 Trend-Nennungen (0,3) -> (30*1,0 + 10*0,3) / 40 = 0,825
    sigs = [_signal("S1", SignalKind.COMPLAINT, 30, []), _signal("S2", SignalKind.TREND, 10, [])]
    values, text = _run(sigs, [])
    assert values["customer_pain"] == pytest.approx(0.825)
    assert "40 mentions" in text["customer_pain"]


def test_reach_ist_wurzel_aus_anteil_an_groesster_nennungszahl():
    # Wurzel statt linear: Sonst drückt ein Ausreißer (581 Nennungen Lob) alle anderen auf fast 0.
    values, text = _run([_signal("S1", SignalKind.COMPLAINT, 25, [])], [], max_mentions=100)
    assert values["reach"] == pytest.approx(0.5)  # Wurzel aus 25/100
    assert "US" in text["reach"] and "25 %" in text["reach"] and "square root" in text["reach"]


def test_reach_kleine_themen_zaehlen_wieder():
    values, _ = _run([_signal("S1", SignalKind.COMPLAINT, 7, [])], [], max_mentions=581)
    assert values["reach"] > 0.1  # linear wären es nur 0,012


def test_reach_ohne_nennungen_ist_null():
    values, _ = _run([_signal("S1", SignalKind.COMPLAINT, 0, [])], [], max_mentions=0)
    assert values["reach"] == 0


def test_satisfaction_gap_us_negativanteil_durch_0_25():
    ev = [_evidence("E1", SourceType.STUDY, attribute="A", neg_share="0.10"),
          _evidence("E2", SourceType.STUDY, attribute="B", neg_share="0.20")]
    sigs = [_signal("S1", SignalKind.COMPLAINT, 5, ["E1", "E2"], (SourceType.STUDY,))]
    values, _ = _run(sigs, ev)
    assert values["satisfaction_gap"] == pytest.approx(0.8)  # 0,20 / 0,25


def test_satisfaction_gap_cn_eu_mittelwert():
    ev = [_evidence("E1", SourceType.STUDY, attribute="A", mean="7.5")]
    sigs = [_signal("S1", SignalKind.COMPLAINT, 5, ["E1"], (SourceType.STUDY,))]
    values, _ = _run(sigs, ev)
    assert values["satisfaction_gap"] == pytest.approx(0.5)  # (9 - 7,5) / 3


def test_satisfaction_gap_ohne_studie_ist_null():
    values, text = _run([_signal("S1", SignalKind.COMPLAINT, 5, [])], [])
    assert values["satisfaction_gap"] == 0
    assert "no study data" in text["satisfaction_gap"]


@pytest.mark.parametrize(("trust", "expected"), [("high", 1.0), ("medium", 0.6), ("low", 0.0), ("", 0.0)])
def test_competitive_pressure_nach_vertrauen(trust, expected):
    ev = [_evidence("W1", SourceType.WEB, trust=trust)]
    sigs = [_signal("S1", SignalKind.COMPETITOR_ADVANTAGE, 3, ["W1"], (SourceType.WEB,))]
    values, _ = _run(sigs, ev)
    assert values["competitive_pressure"] == pytest.approx(expected)


@pytest.mark.parametrize(("kind", "forward", "expected"), [
    (SignalKind.TREND, False, 1.0), (SignalKind.COMPLAINT, True, 0.5), (SignalKind.COMPLAINT, False, 0.1),
])
def test_future_relevance(kind, forward, expected):
    values, _ = _run([_signal("S1", kind, 5, [])], [], forward=forward)
    assert values["future_relevance"] == pytest.approx(expected)


def test_aufwand_und_alle_werte_zwischen_0_und_1():
    values, text = _run([_signal("S1", SignalKind.COMPLAINT, 500, [])], [], max_mentions=100, effort="S")
    assert values["effort_inverse"] == 1.0
    assert all(0 <= v <= 1 for v in values.values())  # reach wird bei 1 gedeckelt
    assert set(values) == set(text)


def test_rationale_nennt_die_zwei_groessten_beitraege():
    from core.models import ScoreFactor
    breakdown = {
        "customer_pain": ScoreFactor(value=0.9, weight=0.25, contribution=22.5, explanation="a"),
        "reach": ScoreFactor(value=0.5, weight=0.2, contribution=10.0, explanation="b"),
        "future_relevance": ScoreFactor(value=0.1, weight=0.1, contribution=1.0, explanation="c"),
    }
    sentence = rationale_from(breakdown)
    assert "customer pain" in sentence and "reach" in sentence and "future relevance" not in sentence
