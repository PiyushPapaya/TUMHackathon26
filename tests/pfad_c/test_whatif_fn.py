"""W-C4: What-if als reine Funktion (Probe-Gewichte, optional "Annahme ignorieren"). Speichert nichts.

Warum eine zweite Stelle neben core/views.py: Die Formel gehört Pfad C und soll genau eine Rechnung haben.
Der Paritätstest unten sorgt dafür, dass Cockpit-Endpunkt und diese Funktion nie unterschiedliche Zahlen zeigen.
"""

from types import SimpleNamespace

import pytest

from core.models import EvidenceLevel, OfferCheck, Requirement, ScoreFactor
from core.views import whatif as view_whatif
from requirements_engine import scoring
from requirements_engine.whatif import whatif

NAMES = list(scoring.DEFAULT_WEIGHTS)


def _req(rid: str, values: dict[str, float], level=EvidenceLevel.A, effort="M") -> Requirement:
    # Wie im echten Lauf: effort_inverse im Breakdown ist der Faktor zum Aufwand der Anforderung.
    values = {**values, "effort_inverse": scoring.effort_factor(effort)}
    breakdown = {n: ScoreFactor(value=values.get(n, 0.0), weight=scoring.DEFAULT_WEIGHTS[n], contribution=0,
                                explanation="x") for n in NAMES}
    score, _ = scoring.score(values, {}, level)
    return Requirement(id=rid, title=rid, description="d", acceptance_criterion="c", category="exterior",
                       signal_ids=["S"], score=score, rank=0, score_breakdown=breakdown, rationale="r",
                       evidence_level=level, assumptions=[], uncertainties=[], effort=effort,
                       offer_check=OfferCheck(status="unknown", note=""))


@pytest.fixture
def reqs():
    pain = _req("PAIN", {"customer_pain": 0.9, "reach": 0.1, "future_relevance": 0.0})  # Schmerz, kaum Reichweite
    reach = _req("REACH", {"customer_pain": 0.5, "reach": 1.0, "future_relevance": 0.0})
    bet = _req("BET", {"customer_pain": 0.3, "reach": 0.3, "future_relevance": 1.0}, EvidenceLevel.D)
    ranked = sorted([pain, reach, bet], key=lambda r: -r.score)
    for rank, req in enumerate(ranked, start=1):  # Ränge aus den echten Scores, nicht von Hand
        req.rank = rank
    return ranked


def test_mehr_gewicht_auf_reach_hebt_die_reichweiten_anforderung(reqs):
    before = {r.id: r.rank for r in reqs}
    rows = {r["id"]: r for r in whatif(reqs, {"reach": 5.0})}
    assert rows["REACH"]["new_rank"] == 1 and rows["REACH"]["rank_change"] == before["REACH"] - 1


def test_ohne_probe_gewichte_aendert_sich_nichts(reqs):
    assert [(r["id"], r["rank_change"]) for r in whatif(reqs, {})] == [(r.id, 0) for r in reqs]


def test_annahme_ignorieren_entspricht_score_without(reqs):
    for row, req in zip(sorted(whatif(reqs, {}, drop="future_relevance"), key=lambda r: r["id"]),
                        sorted(reqs, key=lambda r: r.id), strict=True):
        # scoring.score rundet jeden Faktorbeitrag auf 0,1, score_without rechnet ungerundet: höchstens 0,1 Unterschied.
        # Bewusst die gerundete Rechnung: nur so ergeben die Standardgewichte exakt den heutigen Score.
        assert abs(row["new_score"] - scoring.score_without(req.score_breakdown, req.evidence_level)) <= 0.1


def test_zukunftswette_faellt_ohne_annahme_zurueck(reqs):
    rows = {r["id"]: r for r in whatif(reqs, {}, drop="future_relevance")}
    assert rows["BET"]["new_score"] < rows["BET"]["old_score"]  # ihr Vorsprung bei future_relevance fällt weg


def test_speichert_nichts(reqs):
    before = [(r.id, r.rank, r.score) for r in reqs]
    whatif(reqs, {"reach": 9.0}, drop="future_relevance")
    assert [(r.id, r.rank, r.score) for r in reqs] == before


def test_unbekannter_faktor_wird_abgelehnt(reqs):
    with pytest.raises(ValueError):
        whatif(reqs, {"preis": 1.0})
    with pytest.raises(ValueError):
        whatif(reqs, {}, drop="preis")


def test_paritaet_mit_dem_cockpit_endpunkt(reqs):
    weights = {"reach": 3.0, "customer_pain": 0.5}
    state = SimpleNamespace(requirements={r.id: r for r in reqs})
    assert whatif(reqs, weights) == view_whatif(state, weights)


def test_leere_liste_stuerzt_nicht_ab():
    assert whatif([], {"reach": 1.0}) == []
