"""Was-wäre-wenn (Ticket C10): Score, wenn die Zukunftsannahme als falsch gilt.

Die zwei Beispiele sind VON HAND gerechnet (Zahlen im Kommentar), damit der Test die Formel prüft und nicht
sich selbst. Das Frontend (Lasse) vergleicht seinen Schalter "Annahmen ignorieren" gegen diese Referenz.
"""

import pytest

from core.models import EvidenceLevel
from requirements_engine import scoring
from requirements_engine.scoring import score_without

WERTE = {
    "bsp1": ({"customer_pain": 0.8, "reach": 0.6, "satisfaction_gap": 0.5, "competitive_pressure": 0.0,
              "future_relevance": 1.0, "effort_inverse": 0.6}, EvidenceLevel.A),
    "bsp2": ({"customer_pain": 1.0, "reach": 0.5, "satisfaction_gap": 0.6, "competitive_pressure": 0.0,
              "future_relevance": 0.1, "effort_inverse": 1.0}, EvidenceLevel.B),
}


def _breakdown(name):
    values, level = WERTE[name]
    return scoring.score(values, {}, level)[1], level


def test_beispiel_1_von_hand():
    # Mit Annahme: 0,8*25 + 0,6*20 + 0,5*20 + 0 + 1,0*10 + 0,6*10 = 20+12+10+0+10+6 = 58,0 (Stufe A, x 1,00)
    # Ohne future_relevance: 20+12+10+0+6 = 48, geteilt durch 0,90 (Rest-Gewicht) = 53,33
    breakdown, level = _breakdown("bsp1")
    assert scoring.score(WERTE["bsp1"][0], {}, level)[0] == pytest.approx(58.0, abs=0.05)
    assert score_without(breakdown, level) == pytest.approx(53.3, abs=0.05)


def test_beispiel_2_von_hand_mit_stufe_b():
    # Mit Annahme: 25+10+12+0+0,1*10+10 = 58,0 x 0,85 (Stufe B) = 49,3
    # Ohne: 25+10+12+0+10 = 57, geteilt durch 0,90 = 63,33, mal 0,85 = 53,83
    # (steigt, weil sein niedriger Zukunftswert 0,1 wegfällt: ohne Annahme zählt nur, was belegt ist)
    breakdown, level = _breakdown("bsp2")
    assert scoring.score(WERTE["bsp2"][0], {}, level)[0] == pytest.approx(49.3, abs=0.05)
    assert score_without(breakdown, level) == pytest.approx(53.8, abs=0.05)


def test_ohne_weglassen_ist_der_normale_score():
    breakdown, level = _breakdown("bsp1")
    assert score_without(breakdown, level, drop=None) == scoring.score(WERTE["bsp1"][0], {}, level)[0]


def test_geaenderte_gewichte_werden_beruecksichtigt():
    values, level = WERTE["bsp1"]
    weights = {**{k: 0.0 for k in scoring.DEFAULT_WEIGHTS}, "reach": 0.5, "future_relevance": 0.5}
    breakdown = scoring.score(values, {}, level, weights)[1]
    assert score_without(breakdown, level) == pytest.approx(60.0)  # nur reach 0,6 bleibt, auf 100 % hochgerechnet


def test_wenn_nur_die_annahme_gewichtet_war_ist_der_score_null():
    values, level = WERTE["bsp1"]
    weights = {**{k: 0.0 for k in scoring.DEFAULT_WEIGHTS}, "future_relevance": 1.0}
    breakdown = scoring.score(values, {}, level, weights)[1]
    assert score_without(breakdown, level) == 0.0  # keine Division durch null


def test_unbekannter_faktor_wird_abgelehnt():
    breakdown, level = _breakdown("bsp1")
    with pytest.raises(ValueError):
        score_without(breakdown, level, drop="preis")
