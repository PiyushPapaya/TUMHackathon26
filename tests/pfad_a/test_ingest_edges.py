"""Geplante Pfad-A-Funktionen mit synthetischen Daten und echten Randfällen."""

import pandas as pd

from core.models import Evidence, Scenario
from evidence_internal import feedback
from evidence_internal.context import sales_context
from evidence_internal.signals import extract_signals
from evidence_internal.taxonomy import unmapped_topics


def test_cold_start_without_feedback_file(tmp_path):
    assert feedback.load_feedback({"data": {"feedback_file": None}}, tmp_path) == []


def test_custom_dataset_profile_changes_sheet_and_columns(tmp_path, monkeypatch):
    frame = pd.DataFrame([{"key": "1", "origin": "Source A", "land": "US", "body": "Synthetic comment",
                           "type": "Wants", "topic": "Seats", "subtopic": "", "drive": "BEVE"}])
    frame.to_excel(tmp_path / "mini.xlsx", sheet_name="Custom", index=False)
    profile = {"feedback": {"sheet": "Custom", "columns": {
        "id": "key", "source": "origin", "country": "land", "text": "body", "feedback_type": "type",
        "topic_level2": "topic", "topic_level3": "subtopic", "engine": "drive"}}}
    monkeypatch.setattr(feedback, "load_profile", lambda: profile)
    cfg = {"id": "T-US", "derivative": "T", "market": "US", "countries": ["US"],
           "data": {"feedback_file": "mini.xlsx"}}
    evs = feedback.load_feedback(cfg, tmp_path)
    assert len(evs) == 1 and evs[0].text == "Synthetic comment" and evs[0].meta["engine"] == "BEVE"


def test_uncached_sales_formula_is_unknown_not_zero():
    df = pd.DataFrame({"market_code": ["EU", "CN"], "volume_2024": [50, 30],
                       "volume_2025": [60, None], "volume_2030": [100, "=-D3-C10"]})
    cn = sales_context(df, "CN")
    assert cn["sales"]["volume_2030"] is None
    assert cn["sales"]["share_of_total_2030"] is None and cn["warnings"]
    assert sales_context(df, "EU")["sales"]["share_of_total_2030"] is None


def _feedback(n, engine="BEVE", labels="Seats/Wants"):
    return Evidence(id=f"E{n}", source_type="feedback", source_name="Synthetic", derivative="T", market="US",
                    text="Synthetic customer comment", polarity=-1,
                    meta={"engine": engine, "country": "US", "source": "A", "feedback_type": "Wants",
                          "labels": labels})


def test_segments_count_all_members_instead_of_selected_quotes():
    scenario = Scenario(id="T-US", derivative="T", model_name="Test", market="US", countries=["US"], competitors=[])
    evidence = [_feedback(i, "BEVE" if i < 10 else "ICE") for i in range(15)]
    signals = extract_signals(scenario, evidence, use_llm=False)
    assert len(signals[0].evidence_ids) < 15
    assert signals[0].segments["engine"] == {"BEVE": 10, "ICE": 5}


def test_unknown_topics_are_counted_once_per_comment():
    evidence = [_feedback(1, labels="Alien feature/Wants | Alien feature/Likes"), _feedback(2)]
    assert unmapped_topics(evidence) == {"Alien feature": 1}


def test_opposed_engine_majorities_are_reported_at_ten_comments():
    from evidence_internal.conflicts import segment_conflicts
    from evidence_internal.signals import _build, signal_groups
    scenario = Scenario(id="T-US", derivative="T", model_name="Test", market="US", countries=["US"], competitors=[])
    evidence = [_feedback(i) for i in range(10)]
    for i in range(10, 20):
        ev = _feedback(i, engine="ICE", labels="Seats/Likes")
        ev.polarity = 1
        evidence.append(ev)
    signals, _ = _build(scenario, evidence)
    conflicts = segment_conflicts(signals, evidence, signal_groups(scenario, evidence))
    assert conflicts
    assert any(c["dimension"] == "engine" and c["a_count"] == c["b_count"] == 10
               for rows in conflicts.values() for c in rows)
    reduced = evidence[:-1]
    signals, _ = _build(scenario, reduced)
    assert not segment_conflicts(signals, reduced, signal_groups(scenario, reduced))
