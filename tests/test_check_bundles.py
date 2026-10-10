"""W-L8: Der Bundle-Prüfer meldet Lücken rot und ein vollständiges Bundle grün (kein Git, nur Beispieldaten)."""

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_bundles.py"
SPEC = importlib.util.spec_from_file_location("check_bundles", SCRIPT)
cb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cb)


def _req(n: int, level: str = "B", **over) -> dict:
    base = {"id": f"REQ-{n}", "evidence_level": level, "assumptions": ["a"] if level == "D" else [],
            "robustness": {"label": "robust"}, "signal_ids": ["SIG-1"], "stable_key": f"k{n}"}
    return {**base, **over}


def _bundle(sid="G60-US", reqs=None, feedback=10) -> dict:
    return {"scenario": {"id": sid, "data_coverage": {"feedback": feedback}}, "requirements": reqs or [],
            "signals": [{"id": "SIG-1", "evidence_ids": ["EV-1"]}], "evidence": [{"id": "EV-1"}]}


def _red(checks):
    return [text for ok, text in checks if not ok]


def test_g60_us_mit_zu_wenigen_anforderungen_ist_rot():
    assert any("G60-US hat 3" in t for t in _red(cb.check_scenario(_bundle(reqs=[_req(n) for n in range(3)]))))


def test_g60_us_mit_15_anforderungen_ist_gruen():
    assert not _red(cb.check_scenario(_bundle(reqs=[_req(n) for n in range(15)])))


def test_stufe_d_ohne_annahmen_ist_rot():
    bundle = _bundle(sid="F70-EU", reqs=[_req(1, "D", assumptions=[])])
    assert any("Stufe D ohne Annahmen" in t for t in _red(cb.check_scenario(bundle)))


def test_fehlende_robustheit_ist_rot():
    bundle = _bundle(sid="F70-EU", reqs=[_req(1, robustness=None)])
    assert any("ohne Robustheit: 1 von 1" in t for t in _red(cb.check_scenario(bundle)))


def test_g68_cn_braucht_kaltstart_und_anforderungen():
    assert not _red(cb.check_scenario(_bundle("G68-CN", [_req(1)], feedback=0)))
    assert len(_red(cb.check_scenario(_bundle("G68-CN", [], feedback=5)))) == 2


def test_zitierte_id_ohne_gegenstueck_ist_rot():
    bundle = _bundle(sid="F70-EU", reqs=[_req(1, signal_ids=["SIG-9"])])
    assert any("SIG-9" in t for t in _red(cb.check_scenario(bundle)))


def test_gleiche_befunde_mit_neuer_id_ist_rot():
    old, new = _bundle(reqs=[_req(1)]), _bundle(reqs=[_req(2, stable_key="k1")])
    ok, text = cb.check_stable_ids(new, old)
    assert not ok and "REQ-1" in text
    assert cb.check_stable_ids(old, old)[0]


def test_run_ohne_bundles_meldet_fehlende_dateien_und_fehlende_stufe_d(tmp_path):
    red = _red(cb.run(tmp_path, use_git=False))
    assert any("G60-US.json fehlt" in t for t in red) and any("Stufe D" in t for t in red)


def test_run_liest_dateien_vom_datentraeger(tmp_path):
    (tmp_path / "G60-US.json").write_text(json.dumps(_bundle(reqs=[_req(n, "D") for n in range(15)])))
    results = cb.run(tmp_path, use_git=False)
    assert ("Mindestens eine Anforderung mit Stufe D (Zukunftswette) vorhanden" in [t for ok, t in results if ok])
