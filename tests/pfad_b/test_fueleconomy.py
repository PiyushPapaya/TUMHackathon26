"""W-L10: EPA-Reichweite der Wettbewerber. Ohne Netz: gespeicherte Beispielantworten im Temp-Ordner."""

import json

from core.models import Scenario, SourceType
from evidence_external import fueleconomy

SCENARIO = Scenario(
    id="G60-US", derivative="G60", model_name="BMW 5er", market="US", countries=["US"], competitors=[],
    fueleconomy={"model_year": 2025, "vehicles": {
        "BMW i5 eDrive40": ["BMW", "i5 eDrive40 Sedan"],
        "Tesla Model S": ["Tesla", "Model S"],
        "Mercedes-Benz E 450": ["Mercedes-Benz", "E 450"],  # Verbrenner: keine EPA-Reichweite
    }},
)


def _cache(tmp_path):
    files = {
        "BMW_i5_eDrive40_Sedan_2025.json": {"id": "48316", "year": "2025", "model": "i5 eDrive40 Sedan",
                                            "range": "295", "combE": "32.2"},
        "Tesla_Model_S_2025.json": {"id": "1", "year": "2025", "model": "Model S", "range": "402", "combE": ""},
        "Mercedes-Benz_E_450_2025.json": {"id": "2", "year": "2025", "model": "E 450", "range": "0"},
    }
    for name, data in files.items():
        (tmp_path / name).write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


def test_je_elektroauto_ein_beleg_mit_reichweite(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")  # nie Netz im Test
    evidence = fueleconomy.collect(SCENARIO, _cache(tmp_path))
    assert [e.meta["vehicle"] for e in evidence] == ["BMW i5 eDrive40", "Tesla Model S"]
    assert all(e.source_type == SourceType.EXTERNAL_STAT and e.meta["trust"] == "high" for e in evidence)
    assert "295 miles" in evidence[0].text and "32.2 kWh/100 miles" in evidence[0].text
    assert "kWh" not in evidence[1].text  # fehlender Verbrauch wird nicht erfunden


def test_verbrenner_ohne_reichweite_gibt_keinen_beleg(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    evidence = fueleconomy.collect(SCENARIO, _cache(tmp_path))
    assert all("E 450" not in e.text for e in evidence)


def test_demo_modus_ohne_cache_liefert_leer_statt_netz(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    assert fueleconomy.fetch_vehicle("BMW", "X9", 2025, tmp_path) == {}


def test_ohne_config_keine_belege():
    assert fueleconomy.collect(SCENARIO.model_copy(update={"fueleconomy": {}})) == []
