"""Regressionen aus dem Repo-Audit: echte Fehlerfälle statt nur Happy Paths."""

import json
from concurrent.futures import ThreadPoolExecutor

import pytest

import pipeline
from core.audit import AuditLog
from core.models import Actor
from core.store import Store
from requirements_engine.scoring import normalize_weights


@pytest.mark.parametrize("action", ["approve", "reject", "challenge"])
def test_blank_decision_never_mutates_state(client, action):
    rid = "REQ-G60-US-001"
    before = client.get(f"/api/requirements/{rid}").json()
    response = client.post(f"/api/requirements/{rid}/decision", json={
        "action": action, "actor": "pm.test", "rationale": "   "})
    assert response.status_code == 422
    assert client.get(f"/api/requirements/{rid}").json() == before


def test_audit_failure_never_changes_pm_state(tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "missing"))
    store = Store(AuditLog(tmp_path / "audit.db"))
    store.load_all()
    before = store.get("G60-US")
    snapshot = {r.id: r.model_dump() for r in before.requirements.values()}

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(store.audit, "append", fail)
    pm = Actor(type="human", name="pm.test")
    with pytest.raises(OSError):
        store.decide("REQ-G60-US-001", "approve", pm, "Approved after review")
    with pytest.raises(OSError):
        store.set_weights("G60-US", {"reach": 1}, pm, "Focus on reach")
    assert store.get("G60-US").weights == before.weights
    assert {r.id: r.model_dump() for r in store.ranked("G60-US")} == snapshot


def test_independent_audit_connections_keep_chain_valid(tmp_path):
    logs = [AuditLog(tmp_path / "audit.db") for _ in range(4)]
    pm = Actor(type="human", name="pm.test")
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda i: logs[i % 4].append("TEST", "G60-US", pm, f"event {i}"), range(40)))
    assert logs[0].verify() == {"valid": True, "broken_at_seq": None, "checked": 40}


def test_huge_finite_weights_are_normalized_without_overflow():
    weights = normalize_weights({"reach": 1e308, "customer_pain": 1e308})
    assert sum(weights.values()) == pytest.approx(1)
    assert weights["reach"] == pytest.approx(0.5)


def test_missing_pipeline_input_never_uses_another_scenario(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="G68-CN"):
        pipeline.read_stage("G68-CN", "evidence")


def test_markdown_export_contains_requirement_and_sources(client):
    response = client.get("/api/scenarios/G60-US/export?format=md")
    assert response.status_code == 200
    assert "REQ-G60-US-001" in response.text
    assert "Acceptance criterion" in response.text
    assert "Evidence" in response.text


def test_challenge_receives_conflicting_signal_evidence(client, monkeypatch):
    from api import routes
    from core.models import Evidence, Signal

    state = client.app.state.store.get("G60-US")
    req = state.requirements["REQ-G60-US-001"]
    signal = state.signals[req.signal_ids[0]]
    extra = Evidence(id="EV-COUNTER", source_type="feedback", source_name="Synthetic counter",
                     derivative="G60", market="US", text="Satisfied with existing controls", polarity=1)
    state.evidence[extra.id] = extra
    conflict = Signal.model_validate({**signal.model_dump(), "id": "SIG-COUNTER",
                                     "evidence_ids": [extra.id], "conflicts_with": [signal.id]})
    state.signals[conflict.id] = conflict
    signal.conflicts_with = [conflict.id]
    captured = []

    def answer(req, question, signals, evidence):
        captured.extend(e.id for e in evidence)
        return {"answer": "Counter-evidence considered", "supporting_evidence_ids": [],
                "counter_evidence_ids": [extra.id], "suggested_change": None}

    monkeypatch.setattr(routes, "answer_challenge", answer)
    response = client.post(f"/api/requirements/{req.id}/decision", json={
        "action": "challenge", "actor": "pm.test", "rationale": "Review counter-evidence"})
    assert response.status_code == 200 and extra.id in captured


def test_invalid_json_audit_payload_is_reported_as_tampering(tmp_path):
    log = AuditLog(tmp_path / "audit.db")
    log.append("TEST", "G60-US", Actor(type="human", name="pm"), "Review")
    log._conn.execute("UPDATE audit_events SET payload = ? WHERE seq = 1", ("{invalid",))
    log._conn.commit()
    assert log.verify()["valid"] is False


def test_real_bundle_has_no_synthetic_external_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT_DIR", tmp_path)
    folder = tmp_path / "T-US"
    folder.mkdir()
    for stage in ("evidence", "signals", "web_evidence", "web_signals", "requirements"):
        (folder / f"{stage}.json").write_text("[]", encoding="utf-8")
    cfg = {"id": "T-US", "derivative": "T", "model_name": "Test", "market": "US",
           "countries": ["US"], "competitors": [], "data": {}}
    pipeline.bundle_stage(cfg)
    bundle = json.loads((tmp_path / "T-US.json").read_text(encoding="utf-8"))
    assert bundle["evidence"] == [] and bundle["signals"] == []


def test_failed_web_research_preserves_existing_stage_files(tmp_path, monkeypatch):
    from evidence_external import claims, web_research
    monkeypatch.setattr(pipeline, "OUT_DIR", tmp_path)
    folder = tmp_path / "T-US"
    folder.mkdir()
    (folder / "signals.json").write_text("[]")
    saved = '[{"text":"previous research"}]'
    (folder / "web_evidence.json").write_text(saved)
    cfg = {"id": "T-US", "derivative": "T", "model_name": "Test", "market": "US", "countries": ["US"],
           "competitors": [], "data": {}}
    claims.FAILED_QUESTIONS.clear()

    def fail(*args):
        claims.FAILED_QUESTIONS.append("timeout")
        return [], []

    monkeypatch.setattr(web_research, "research", fail)
    with pytest.raises(RuntimeError, match="existing stage files were preserved"):
        pipeline.run_stage("web", cfg)
    assert (folder / "web_evidence.json").read_text() == saved


def test_corrupt_audit_is_not_replayed(tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "missing"))
    log = AuditLog(tmp_path / "audit.db")
    log.append("PM_APPROVE", "G60-US", Actor(type="human", name="pm"), "Original decision",
               requirement_id="REQ-G60-US-001")
    log._conn.execute("UPDATE audit_events SET rationale = 'tampered'")
    log._conn.commit()
    with pytest.raises(RuntimeError, match="replay refused"):
        Store(log).load_all()
