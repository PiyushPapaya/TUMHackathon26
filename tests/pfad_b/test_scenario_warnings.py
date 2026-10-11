"""Warnungen kommen aus config/scenarios, nicht aus einem veralteten Bundle (Textkorrektur ohne Pipeline-Lauf)."""

import json

from core.store import ROOT, ScenarioState


def test_warnings_follow_config_not_stale_bundle():
    config = json.loads((ROOT / "config" / "scenarios" / "F70-EU.json").read_text(encoding="utf-8"))
    bundle = {"scenario": {**{k: v for k, v in config.items() if k != "data"}, "warnings": ["veralteter Text"]},
              "evidence": [], "signals": [], "requirements": []}
    assert ScenarioState(bundle).scenario.warnings == config["warnings"]
