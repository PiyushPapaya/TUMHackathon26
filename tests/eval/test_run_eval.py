"""Der Eval-Lauf muss auch Kaltstart und externe Belege korrekt messen."""

import json

import run_eval


def test_cold_start_evaluation_includes_external_sources(tmp_path, monkeypatch):
    from core.models import Evidence
    monkeypatch.setattr(run_eval, "ROOT", tmp_path)
    config = tmp_path / "config" / "scenarios"
    config.mkdir(parents=True)
    cfg = {"id": "T-CN", "derivative": "T", "model_name": "Test", "market": "CN", "countries": ["CN"],
           "competitors": [], "data": {"feedback_file": None}}
    (config / "T-CN.json").write_text(json.dumps(cfg))
    processed = tmp_path / "data" / "processed" / "T-CN"
    processed.mkdir(parents=True)
    external = Evidence(id="X", source_type="external_stat", source_name="Synthetic authority",
                        derivative="T", market="CN", text="Synthetic statistic").model_dump(mode="json")
    stages = {"evidence": [], "signals": [], "external_evidence": [external],
              "external_signals": [{"id": "S", "evidence_ids": ["X"]}],
              "requirements": [{"signal_ids": ["S"], "acceptance_criterion": "Complete in 1 step"}]}
    for name, data in stages.items():
        (processed / f"{name}.json").write_text(json.dumps(data))
    result = run_eval.compute("T-CN")
    assert result["ground_signals"] == result["ground_requirements"] == 1
    assert result["comments"] == 0 and result["verbatim"] is None and result["fidelity"] is None
