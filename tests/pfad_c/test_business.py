"""W-C6: Business-Seite (Volumen 2030, Wachstum 2025 -> 2030, Marktanteil) in Faktoren und Anforderung.

Brief: "thoughtful prioritization"; die BMW-Folie trennt Customer und Business.
Messung (G60-US, Sa 22:45): Reach mit dem Marktanteil zu multiplizieren ist für ALLE Anforderungen eines Szenarios
derselbe Faktor. Es stimmt nur heimlich die Gewichte um (reach faktisch 20 % -> ca. 10 %), 6 von 21 Rängen kippen, die
alte Nr. 3 fällt auf Platz 5. Verworfen. Stattdessen: Zahlen sichtbar machen, Wachstum multiplikativ auf die Zukunft.
"""

import pytest

from core.models import Category, Signal, SignalKind, SourceType
from requirements_engine.business import business_context
from requirements_engine.factors import compute_factors

SALES = {"market": "US", "volume_2025": 78000, "volume_2030": 80000, "share_of_total_2030": 0.253}


def _sig(kind=SignalKind.COMPLAINT, mentions=25) -> Signal:
    return Signal(id="S1", kind=kind, category=Category.EXTERIOR, title="t", summary="s", evidence_ids=[],
                  mention_count=mentions, source_types=[SourceType.FEEDBACK])


def _factors(sales, forward=False, kind=SignalKind.COMPLAINT):
    return compute_factors([_sig(kind)], {}, 100, forward, "M", {"sales": sales} if sales is not None else {})


def test_business_context_rechnet_wachstum_und_uebernimmt_zahlen():
    b = business_context(SALES)
    assert (b.volume_2025, b.volume_2030, b.market_share) == (78000, 80000, 0.253)
    assert b.growth_pct == pytest.approx(2.564, abs=0.001)


def test_fehlende_zahlen_sind_none_nie_null():
    b = business_context({"market": "CN", "volume_2030": 50000})
    assert b.growth_pct is None and b.volume_2025 is None and b.note
    assert business_context({}).volume_2030 is None
    assert business_context({"volume_2025": 0, "volume_2030": 5}).growth_pct is None  # keine Division durch 0


def test_gelieferter_wachstumswert_hat_vorrang():
    assert business_context({**SALES, "growth_pct": 7.5}).growth_pct == 7.5  # z. B. aus W-A5 (Aditya)


def test_reach_wert_haengt_nicht_vom_marktanteil_ab():
    # Guard gegen die verworfene Marktgewichtung: gleiche Nennungen -> gleicher Wert, egal wie groß der Markt ist.
    small = _factors({**SALES, "share_of_total_2030": 0.05})[0]["reach"]
    big = _factors({**SALES, "share_of_total_2030": 0.9})[0]["reach"]
    assert small == big == pytest.approx(0.5)


def test_reach_satz_nennt_anteil_und_volumen():
    text = _factors(SALES)[1]["reach"]
    assert "25 % of 2030 volume" in text and "80,000" in text


def test_hoeheres_wachstum_hebt_die_zukunftsrelevanz():
    low = _factors({**SALES, "volume_2025": 78000, "volume_2030": 79000}, forward=True)[0]["future_relevance"]
    high = _factors({**SALES, "volume_2025": 78000, "volume_2030": 94000}, forward=True)[0]["future_relevance"]
    assert 0.5 < low < high <= 1.0


def test_wachstum_wirkt_multiplikativ_ohne_zukunftsbezug_kaum():
    grow = {**SALES, "volume_2030": 94000}  # +20,5 %
    no_future = _factors(grow)[0]["future_relevance"]
    assert no_future == pytest.approx(0.1 * 1.205, abs=0.005)  # 0,1 bleibt praktisch 0,1, keine pauschale Verschiebung
    assert _factors(grow, kind=SignalKind.TREND)[0]["future_relevance"] == 1.0  # gedeckelt


def test_schrumpfender_markt_senkt_nichts():
    shrink = {**SALES, "volume_2030": 60000}
    assert _factors(shrink, forward=True)[0]["future_relevance"] == pytest.approx(0.5)


def test_zukunftssatz_nennt_das_wachstum_oder_dass_es_fehlt():
    assert "+2.6 %" in _factors(SALES, forward=True)[1]["future_relevance"]
    assert "growth" not in _factors({"market": "US"}, forward=True)[1]["future_relevance"]


def test_ohne_absatzdaten_bleiben_faktoren_wie_vorher():
    values, _ = _factors(None, forward=True)
    assert values["future_relevance"] == pytest.approx(0.5) and values["reach"] == pytest.approx(0.5)


def test_derive_all_fuellt_business(monkeypatch):
    from core.models import Scenario
    from requirements_engine import derive
    from requirements_engine.drafts import RequirementDraft, RequirementDrafts

    scenario = Scenario(id="G60-US", derivative="G60", model_name="5", market="US", countries=["US"], competitors=[])
    draft = RequirementDraft(title="R", description="d", acceptance_criterion="c", category=Category.EXTERIOR,
                             signal_ids=["S1"])
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=[draft]))
    reqs, _ = derive.derive_all(scenario, [_sig()], [], {"sales": SALES})
    assert reqs[0].business.volume_2030 == 80000 and reqs[0].business.market_share == 0.253
    without = derive.derive_all(scenario, [_sig()], [], {})[0][0]
    assert without.business.volume_2030 is None  # kein Absturz, kein Nullwert
