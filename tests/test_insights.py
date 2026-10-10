"""Matrix (Heute/Zukunft × Evidenz), Markt-Gegenstück je Anforderung und Entscheidungs-Memo."""

import json
from pathlib import Path

import pytest

from core import req_insights
from core.models import EvidenceLevel, Status
from core.store import ScenarioState

BUNDLE = Path(__file__).resolve().parents[1] / "src" / "shared" / "beispiele" / "bundle_G60-US.json"


def _state(scenario_id: str = "G60-US") -> ScenarioState:
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    if scenario_id != "G60-US":  # synthetischer zweiter Markt: gleiche Daten, andere IDs
        text = json.dumps(bundle).replace("G60-US", scenario_id)
        bundle = json.loads(text)
        bundle["scenario"]["market"] = scenario_id.split("-")[1]
    return ScenarioState(bundle)


@pytest.mark.parametrize(("horizon", "level", "quadrant"), [
    ("today", EvidenceLevel.A, "Sicher & dringend"), ("next_gen", EvidenceLevel.B, "Belegte Zukunftswette"),
    ("today", EvidenceLevel.C, "Schwach belegt, heute"), ("next_gen", EvidenceLevel.D, "Annahme – beobachten"),
])
def test_quadrant_regeln(horizon, level, quadrant):
    assert req_insights.quadrant(horizon, level) == quadrant


def test_matrix_hat_jede_anforderung_mit_luecken_label():
    state = _state()
    matrix = req_insights.matrix(state)
    assert set(matrix["items"]) == set(state.requirements)
    item = matrix["items"]["REQ-G60-US-001"]
    assert item["offer_gap"] == "not_offered" and item["offer_gap_label"] == "Lücke: nicht angeboten"
    assert matrix["items"]["REQ-G60-US-005"]["horizon"] == "next_gen"


def test_compare_findet_gegenstueck_in_anderem_markt():
    rows = req_insights.counterparts(_state(), _state().requirements["REQ-G60-US-003"],
                                     {"G60-EU": _state("G60-EU")})
    assert rows[0]["scenario_id"] == "G60-EU" and rows[0]["match"]["id"] == "REQ-G60-EU-003"


def test_compare_meldet_kein_gegenstueck():
    other = _state("G60-EU")
    for req in other.requirements.values():
        req.title = "Völlig anderes Thema"
    rows = req_insights.counterparts(_state(), _state().requirements["REQ-G60-US-003"], {"G60-EU": other})
    assert rows[0]["match"] is None and rows[0]["sentence"] == "kein Gegenstück"


def test_memo_nur_freigegebene_ids_und_pruefzeile():
    state = _state()
    state.requirements["REQ-G60-US-002"].status = Status.APPROVED
    text = req_insights.memo(state, {"valid": True, "checked": 12})
    assert "REQ-G60-US-002" in text and "REQ-G60-US-001" not in text
    assert "Prüfpfad gültig, 12 Ereignisse" in text


def test_memo_ohne_freigabe_zeigt_top5_als_entwurf():
    text = req_insights.memo(_state(), {"valid": True, "checked": 3})
    assert "Entwurf" in text and text.count("REQ-G60-US-") == 5


def test_api_neue_endpunkte(client):
    assert client.get("/api/scenarios/G60-US/matrix").status_code == 200
    assert client.get("/api/scenarios/X-Y/matrix").status_code == 404
    assert client.get("/api/requirements/REQ-G60-US-001/counterparts").status_code == 200
    assert client.get("/api/requirements/REQ-NOPE/counterparts").status_code == 404
    memo = client.get("/api/scenarios/G60-US/memo")
    assert memo.status_code == 200 and "Prüfpfad gültig" in memo.text
    assert client.get("/api/scenarios/X-Y/memo").status_code == 404
