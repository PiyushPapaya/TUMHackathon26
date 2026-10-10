"""Phase 0 Welle 2: Verträge (Configs, Datensatz-Profil, neue Modellfelder) bleiben konsistent."""

import json
from pathlib import Path

from core.datasets import load_profile
from core.model_parts import coverage_badge
from core.models import Requirement, Scenario, Signal
from evidence_internal import feedback, study

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "src/shared/beispiele/bundle_G60-US.json").read_text(encoding="utf-8"))


def test_alle_szenario_configs_sind_gueltige_szenarien():
    configs = sorted((ROOT / "config/scenarios").glob("*.json"))
    ids = {Scenario(**json.loads(p.read_text(encoding="utf-8"))).id for p in configs}
    assert {"G60-US", "G70-US", "F70-EU", "G60-EU", "G70-EU", "G68-CN"} <= ids


def test_kaltstart_config_hat_keine_feedback_datei():
    cfg = json.loads((ROOT / "config/scenarios/G68-CN.json").read_text(encoding="utf-8"))
    assert cfg["data"]["feedback_file"] is None and cfg["data"]["option_list_file"] is None


def test_profil_entspricht_heutigem_code():
    """Driftet das Profil vom Code weg, liest A12 andere Werte als bisher: hier fällt es auf."""
    profile = load_profile()
    assert profile["feedback"]["sheet"] == feedback.SHEET
    assert profile["feedback"]["polarity_by_feedback_type"] == feedback.POLARITY
    assert tuple(profile["study"]["us_levels_negative"]) == study.NEGATIVE_LEVELS
    assert "_hinweis" not in profile


def test_alte_bundles_bleiben_gueltig_neue_felder_haben_defaults():
    old_req = {k: v for k, v in EXAMPLE["requirements"][0].items()
               if k not in {"horizon", "robustness", "segment_conflicts", "business", "stable_key", "badges"}}
    req = Requirement(**old_req)
    assert req.horizon == "today" and req.robustness is None and req.badges == []
    old_sig = {k: v for k, v in EXAMPLE["signals"][0].items() if k not in {"segments", "study_link"}}
    assert Signal(**old_sig).segments == {}


def test_coverage_badge_regel():
    assert [coverage_badge(n) for n in (0, 19, 999, 1000)] == ["Kaltstart", "dünn", "dünn", "reich"]
