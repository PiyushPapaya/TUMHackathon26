"""Benchmarks: Qualität der KI-Vorschläge (je Szenario) und Marktvergleich aus amtlichen Daten (EPA, NHTSA)."""

import json
from pathlib import Path

from core import benchmarks, market_benchmarks
from core.store import ScenarioState

BUNDLE = Path(__file__).resolve().parents[2] / "src" / "shared" / "beispiele" / "bundle_G60-US.json"


def _state() -> ScenarioState:
    return ScenarioState(json.loads(BUNDLE.read_text(encoding="utf-8")))


def _metric(result: dict, key: str) -> dict:
    return next(m for m in result["metrics"] if m["key"] == key)


def test_qualitaet_beispiel_bundle_ist_voll_belegt():
    result = benchmarks.quality(_state())
    grounding = _metric(result, "grounding")
    assert grounding["value"] == 100.0 and grounding["ok"] is True
    assert result["funnel"]["requirements"] == len(_state().requirements)
    for metric in result["metrics"]:
        assert 0 <= metric["value"] <= 100, metric["key"]


def test_grounding_findet_haengende_id():
    state = _state()
    first = next(iter(state.requirements.values()))
    first.signal_ids.append("SIG-GIBT-ES-NICHT")
    grounding = _metric(benchmarks.quality(state), "grounding")
    assert grounding["value"] < 100 and grounding["ok"] is False


def test_messbar_zaehlt_kriterien_mit_zahl():
    state = _state()
    for req in state.requirements.values():
        req.acceptance_criterion = "ohne Zahl"
    assert _metric(benchmarks.quality(state), "measurable")["value"] == 0.0


def test_numbers_never_claim_acceptance_is_testable():
    state = _state()
    for req in state.requirements.values():
        req.acceptance_criterion = "Make the 2025 model better"
    metric = _metric(benchmarks.quality(state), "measurable")
    assert metric["value"] == 100.0
    assert metric["ok"] is None and metric["target"] is None
    assert "does not prove" in metric["explain"] and "heuristic" in metric["label"]


def test_stabilitaet_ist_reproduzierbar():
    """Gleicher Seed -> gleiche Zahl. Sonst zeigt die Seite bei jedem Laden einen anderen Wert."""
    a = _metric(benchmarks.quality(_state()), "rank_stability")["value"]
    b = _metric(benchmarks.quality(_state()), "rank_stability")["value"]
    assert a == b


def _write(folder: Path, name: str, data: dict) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


def test_markt_reichweite_rang_und_beschwerden(tmp_path):
    fuel, nhtsa = tmp_path / "fuel", tmp_path / "nhtsa"
    _write(fuel, "BMW_i5_2025.json", {"range": "300", "combE": "32.2"})
    _write(fuel, "Rival_X_2025.json", {"range": "400", "combE": "28.0"})
    # gleiche ODI-Nummer in zwei Modellen zählt nur einmal (wie in nhtsa.collect)
    _write(nhtsa, "BMW_I5_2025.json", {"results": [{"odiNumber": 1}, {"odiNumber": 2}]})
    _write(nhtsa, "BMW_540I_2025.json", {"results": [{"odiNumber": 2}]})
    _write(nhtsa, "RIVAL_X_2025.json", {"results": [{"odiNumber": 9}]})
    cfg = {"id": "G60-US", "model_name": "BMW 5er",
           "fueleconomy": {"model_year": 2025, "vehicles": {"BMW i5": ["BMW", "i5"], "Rival X": ["Rival", "X"]}},
           "nhtsa": {"model_years": [2025], "bmw_models": ["I5", "540I"], "competitors": {"Rival X": ["RIVAL", ["X"]]}}}
    result = market_benchmarks.scenario_market(cfg, fuel, nhtsa)
    bmw = next(v for v in result["range"] if v["is_bmw"])
    assert bmw["rank"] == 2 and bmw["range_km"] == 483
    assert result["range_gap_km"] == -161  # bester BMW minus bester Wettbewerber
    complaints = {c["name"]: c["complaints"] for c in result["complaints"]}
    assert complaints == {"BMW 5er": 2, "Rival X": 1}


def test_markt_ohne_konfiguration_ist_leer(tmp_path):
    assert market_benchmarks.scenario_market({"id": "G60-EU"}, tmp_path, tmp_path) is None


def test_endpunkt_liefert_beide_teile(client):
    data = client.get("/api/benchmarks").json()
    assert data["quality"] and data["quality"][0]["scenario_id"] == "G60-US"
    assert isinstance(data["market"], list)


def test_missing_complaint_cache_is_unknown_not_zero(tmp_path):
    assert market_benchmarks._complaints("BMW", ["I5"], [2025], tmp_path) is None
    _write(tmp_path, "BMW_I5_2025.json", {"results": []})
    assert market_benchmarks._complaints("BMW", ["I5"], [2025], tmp_path) == 0
