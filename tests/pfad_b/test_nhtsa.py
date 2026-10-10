"""L22: NHTSA-Beschwerden als zweite Kundenquelle. Ohne Netz: gespeicherte Beispielantworten im Temp-Ordner."""

import json

from core.models import Scenario, SourceType
from evidence_external import nhtsa

SCENARIO = Scenario(
    id="G60-US", derivative="G60", model_name="BMW 5er", market="US", countries=["US"], competitors=[],
    nhtsa={"model_years": [2024], "bmw_models": ["I5", "530I"], "competitors": {"Audi A6": ["AUDI", ["A6 SEDAN"]]}},
)


def _complaint(odi: int, components: str) -> dict:
    return {"odiNumber": odi, "components": components, "summary": f"Complaint {odi} text"}


def _cache(tmp_path):
    files = {
        "BMW_I5_2024.json": [_complaint(1, "SERVICE BRAKES"), _complaint(2, "SERVICE BRAKES,STEERING"),
                             _complaint(3, "STEERING"), _complaint(4, "UNKNOWN OR OTHER")],
        "BMW_530I_2024.json": [_complaint(1, "SERVICE BRAKES"), _complaint(5, "FORWARD COLLISION AVOIDANCE")],
        "AUDI_A6_SEDAN_2024.json": [_complaint(9, "SEATS")],
    }
    for name, results in files.items():
        (tmp_path / name).write_text(json.dumps({"count": len(results), "results": results}), encoding="utf-8")
    return tmp_path


def test_beschwerden_werden_belege_mit_odi_und_hohem_vertrauen(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")  # nie Netz im Test
    evidence, _ = nhtsa.collect(SCENARIO, _cache(tmp_path))
    complaints = [e for e in evidence if e.source_type == SourceType.FEEDBACK_EXTERNAL]
    assert len(complaints) == 5  # ODI 1 steht bei I5 und 530I, zählt aber nur einmal
    assert all(e.meta["trust"] == "high" and e.meta["odi"] and e.url for e in complaints)


def test_befund_erst_ab_3_beschwerden_je_kategorie(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    _, signals = nhtsa.collect(SCENARIO, _cache(tmp_path))
    assert [(s.category.value, s.mention_count) for s in signals] == [("driving_experience", 3)]
    assert signals[0].source_types == [SourceType.FEEDBACK_EXTERNAL]


def test_wettbewerber_statistik_nennt_beide_zahlen(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    evidence, _ = nhtsa.collect(SCENARIO, _cache(tmp_path))
    stat = next(e for e in evidence if e.source_type == SourceType.EXTERNAL_STAT)
    assert "Audi A6 1" in stat.text and "BMW 5er 5" in stat.text and "not per vehicle sold" in stat.text


def test_demo_modus_ohne_cache_liefert_leer_statt_netz(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    assert nhtsa.fetch("BMW", "X9", 2024, tmp_path) == []


def test_ohne_nhtsa_config_keine_belege():
    assert nhtsa.collect(SCENARIO.model_copy(update={"nhtsa": {}})) == ([], [])


def test_kategorie_zuordnung():
    assert nhtsa.category_for("ELECTRICAL SYSTEM: PROPULSION SYSTEM: TRACTION BATTERY").value == "range_charging"
    assert nhtsa.category_for("UNKNOWN OR OTHER") is None
