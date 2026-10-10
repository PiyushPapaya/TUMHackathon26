"""Prompt-Linse: KI wählt nur Gewichte und Filter, Python rechnet die Top 5 (Beispiel-Bundle G60-US)."""

import json
from pathlib import Path

import pytest

from core import lens
from core.store import ScenarioState
from requirements_engine import scoring

BUNDLE = Path(__file__).resolve().parents[1] / "src" / "shared" / "beispiele" / "bundle_G60-US.json"


@pytest.fixture
def state():
    return ScenarioState(json.loads(BUNDLE.read_text(encoding="utf-8")))


def test_regeln_ohne_llm_liefern_top5_mit_echten_ids(state, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")  # kein Cache-Eintrag -> Regel-Fallback
    result = lens.run_lens(state, "Was ist am wichtigsten?")
    assert result["source"] == "rules"
    assert len(result["top"]) == 5
    assert {t["requirement"]["id"] for t in result["top"]} <= set(state.requirements)


def test_schluesselwort_filtert_kategorie(state, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    result = lens.run_lens(state, "Kunden in den USA, Fokus Laden")
    assert result["filters"]["categories"] == ["range_charging"]
    family = lens.run_lens(state, "Familien, Fokus Laden und Platz")["filters"]["categories"]
    assert set(family) == {"range_charging", "comfort_space"}
    assert {t["requirement"]["category"] for t in result["top"]} == {"range_charging"}


def test_unbekannte_faktoren_und_kategorien_der_ki_werden_verworfen(state):
    plan = lens.LensPlan(weights=[lens.FactorWeight(factor="preis", weight=1.0),
                                  lens.FactorWeight(factor="reach", weight=0.9)],
                         categories=["fliegen", "comfort_space"], only_gaps=False, interpretation="Platz")
    clean = lens.sanitize(plan)
    assert set(clean["weights"]) == set(scoring.DEFAULT_WEIGHTS)
    assert clean["weights"]["reach"] > scoring.DEFAULT_WEIGHTS["reach"]
    assert clean["categories"] == ["comfort_space"]


def test_store_bleibt_unveraendert(state, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    before = {r.id: (r.rank, r.score) for r in state.requirements.values()}
    weights_before = dict(state.weights)
    lens.run_lens(state, "Zukunft 2030, Wettbewerb")
    assert {r.id: (r.rank, r.score) for r in state.requirements.values()} == before
    assert state.weights == weights_before


def test_nur_luecken_zeigt_nichts_serienmaessiges(state, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    result = lens.run_lens(state, "Wo haben wir eine Ausstattungslücke?")
    assert result["filters"]["only_gaps"] is True
    assert all(t["requirement"]["offer_check"]["status"] in lens.GAP_STATUSES for t in result["top"])


def test_begruendung_stammt_aus_den_daten(state, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    top = lens.run_lens(state, "egal")["top"][0]
    req = state.requirements[top["requirement"]["id"]]
    known = {f.explanation for f in req.score_breakdown.values()}
    assert len(top["reasons"]) == 2 and all(r["sentence"] in known for r in top["reasons"])


def test_api_linse_schreibt_pruefpfad(client):
    res = client.post("/api/scenarios/G60-US/lens", json={"question": "Fokus Laden", "actor": "pm.test"})
    assert res.status_code == 200 and res.json()["top"]
    last = client.get("/api/audit", params={"scenario_id": "G60-US"}).json()[-1]
    assert last["event_type"] == "AI_LENS_SUGGESTED" and last["payload"]["question"] == "Fokus Laden"
    assert client.get("/api/audit/verify").json()["valid"] is True


def test_api_linse_404_und_leere_frage(client):
    assert client.post("/api/scenarios/X-Y/lens", json={"question": "a", "actor": "pm"}).status_code == 404
    assert client.post("/api/scenarios/G60-US/lens", json={"question": "", "actor": "pm"}).status_code == 422
