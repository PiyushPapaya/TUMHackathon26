"""A2: deterministic successor assumptions, independent of priority scores."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.audit import AuditLog
from core.models import Category, Evidence, Signal, SignalKind, SourceType
from core.outlook import outlook
from core.store import ScenarioState, Store


def feedback(index, engine, polarity=-1, source_type=SourceType.FEEDBACK):
    return Evidence(id=f"EV-{index}", source_type=source_type, source_name="Feedback",
                    derivative="G60", market="US", text="Customer comment", polarity=polarity,
                    meta={"engine": engine})


def signal(ids, kind=SignalKind.COMPLAINT, category=Category.RANGE_CHARGING):
    return Signal(id="SIG-1", kind=kind, category=category, title="Finding", summary="Summary",
                  evidence_ids=ids, mention_count=len(ids), source_types=[SourceType.FEEDBACK])


def evaluate(critical_engines, remaining_engines, web_signals=()):
    critical = [feedback(i, engine) for i, engine in enumerate(critical_engines)]
    remaining = [feedback(i + len(critical), engine, polarity=1)
                 for i, engine in enumerate(remaining_engines)]
    evidence = {e.id: e for e in critical + remaining}
    return outlook(SimpleNamespace(category=Category.RANGE_CHARGING),
                   [signal([e.id for e in critical])], evidence, web_signals, "2031")


@pytest.mark.parametrize(("critical", "remaining", "expected"), [
    (["BEVE"] * 6 + ["ICE"] * 4, ["ICE"] * 10, "grows"),
    (["ICE"] * 9 + ["PHEV"], ["BEVE"] * 10, "fades"),
    (["BEVE"] * 5 + ["ICE"] * 5, ["BEVE"] * 5 + ["ICE"] * 5, "stays"),
    (["BEV"] * 9, ["ICE"] * 30, "stays"),
    (["ICE"] * 9, ["BEVE"] * 30, "stays"),
    (["ICE"] * 10, ["ICE"] * 20, "stays"),
    (["ICE"] * 9 + ["BEVE"], ["ICE"] * 9 + ["BEVE"], "stays"),
    (["BEV"] * 6 + ["ICE"] * 4, ["BEVE"] * 2 + ["ICE"] * 8, "grows"),
    ([], [], "stays"),
])
def test_segment_rules_and_thresholds(critical, remaining, expected):
    result = evaluate(critical, remaining)
    assert result["direction"] == expected
    assert result["successor_year"] == "2031"
    assert result["assumption"] is True
    if expected != "stays":
        assert "Assumption." in result["sentence"]


def test_category_trend_has_priority_and_identifies_web_source():
    web = feedback("web", "", source_type=SourceType.WEB)
    web.source_name = "Future Mobility Report"
    web.url = "https://example.com/trend"
    trend = signal([web.id], kind=SignalKind.TREND)
    result = outlook(SimpleNamespace(category=Category.RANGE_CHARGING), [], {web.id: web}, [trend], "2032")
    assert result["direction"] == "grows" and result["rule"] == "category_trend"
    assert "Future Mobility Report" in result["sentence"] and "2032" in result["sentence"]
    assert result["evidence_ids"] == [web.id] and result["signal_ids"] == [trend.id]


@pytest.mark.parametrize(("kind", "category"), [
    (SignalKind.COMPETITOR_ADVANTAGE, Category.RANGE_CHARGING),
    (SignalKind.TREND, Category.INTERIOR),
])
def test_other_category_or_non_trend_does_not_grow(kind, category):
    assert evaluate([], [], [signal([], kind=kind, category=category)])["direction"] == "stays"


def test_category_trend_wins_over_ice_segment_shift():
    result = evaluate(["ICE"] * 10, ["BEVE"] * 10, [signal([], kind=SignalKind.TREND)])
    assert result["direction"] == "grows" and result["rule"] == "category_trend"


def test_duplicate_missing_and_external_evidence_do_not_inflate_criticism():
    comments = [feedback(i, "BEVE") for i in range(9)]
    comments += [feedback("other", "ICE", polarity=1),
                 feedback("external", "BEVE", source_type=SourceType.FEEDBACK_EXTERNAL)]
    evidence = {e.id: e for e in comments}
    linked = signal([e.id for e in comments] + ["missing"])
    result = outlook(SimpleNamespace(category=Category.RANGE_CHARGING), [linked, linked], evidence, [], "2030")
    assert result["direction"] == "stays"
    assert result["critical_count"] == 9 and result["scenario_feedback_count"] == 10


def test_store_uses_full_feedback_for_baseline_without_changing_bundle():
    path = Path(__file__).resolve().parents[2] / "src/shared/beispiele/bundle_G60-US.json"
    bundle = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps(bundle, sort_keys=True)
    state = ScenarioState(bundle, feedback_evidence=[feedback(i, "ICE", polarity=1) for i in range(100)])
    assert all(r.outlook["baseline_source"] == "scenario_feedback" for r in state.requirements.values())
    assert all(r.outlook["scenario_feedback_count"] >= 100 for r in state.requirements.values())
    assert json.dumps(bundle, sort_keys=True) == before
    assert [(r.id, r.rank, r.score) for r in state.requirements.values()] == [
        (r["id"], r["rank"], r["score"]) for r in bundle["requirements"]]


def test_load_all_reads_adjacent_scenario_feedback(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[2] / "src/shared/beispiele/bundle_G60-US.json"
    bundle = json.loads(path.read_text(encoding="utf-8"))
    (tmp_path / "G60-US.json").write_text(json.dumps(bundle), encoding="utf-8")
    source = tmp_path / "G60-US"
    source.mkdir()
    extra = [feedback(f"full-{i}", "ICE", polarity=1).model_dump(mode="json") for i in range(100)]
    (source / "evidence.json").write_text(json.dumps(bundle["evidence"] + extra), encoding="utf-8")
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path))
    monkeypatch.setattr("core.store.EXAMPLES_DIR", tmp_path / "no_examples")
    audit = AuditLog(tmp_path / "audit.db")
    try:
        store = Store(audit)
        store.load_all()
        state = store.get("G60-US")
        expected = sum(e["source_type"] == "feedback" for e in bundle["evidence"]) + 100
        assert all(r.outlook["scenario_feedback_count"] == expected for r in state.requirements.values())
        assert all(r.outlook["baseline_source"] == "scenario_feedback" for r in state.requirements.values())
        assert set(state.evidence) == {e["id"] for e in bundle["evidence"]}
    finally:
        audit.close()


def test_api_exposes_outlook_and_radar_without_changing_ranking(client):
    before = client.get("/api/scenarios/G60-US/requirements").json()
    # Example bundles have no category trend; inject a synthetic web finding, without rescoring.
    state = client.app.state.store.get("G60-US")
    trend = signal([], kind=SignalKind.TREND, category=state.requirements[before[0]["id"]].category)
    trend.source_types = [SourceType.WEB]
    state.signals[trend.id] = trend
    for req in state.requirements.values():
        req.outlook = outlook(req, [state.signals[i] for i in req.signal_ids], state.evidence, [trend], "2030")
    enriched = client.get("/api/scenarios/G60-US/requirements").json()
    grown = [r for r in enriched if r["outlook"]["direction"] == "grows"]
    assert grown
    for row in enriched:
        detail = client.get(f"/api/requirements/{row['id']}/explain").json()
        assert detail["outlook"] == row["outlook"] == detail["requirement"]["outlook"]
    radar = client.get("/api/scenarios/G60-US/trends").json()
    items = [i for i in radar["items"] if i["kind"] == "outlook"]
    assert {i["requirement_id"] for i in items} == {r["id"] for r in grown}
    assert all(i["horizon"] == radar["successor_horizon"] and i["assumptions"] for i in items)
    after = client.get("/api/scenarios/G60-US/requirements").json()
    assert [(r["id"], r["rank"], r["score"], r["score_breakdown"]) for r in before] == [
        (r["id"], r["rank"], r["score"], r["score_breakdown"]) for r in after]
