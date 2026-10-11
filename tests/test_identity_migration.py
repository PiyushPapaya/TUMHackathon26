"""Migration must preserve decisions without changing historical audit rows."""

import json

import pytest

from core.audit import AuditLog
from core.identity import migrate_bundle
from core.models import Actor, Evidence, Scenario
from core.store import EXAMPLES_DIR, Store
from evidence_internal.signals import extract_signals


@pytest.fixture
def original(tmp_path, monkeypatch):
    bundle = json.loads((EXAMPLES_DIR / "bundle_G60-US.json").read_text(encoding="utf-8"))
    evidence = [Evidence(id=f"EV-{i}", source_type="feedback", source_name="Synthetic", derivative="G60",
                         market="US", text="Synthetic navigation complaint", polarity=-1,
                         meta={"labels": "Navigation/Difficult to Use"}) for i in range(6)]
    [signal] = extract_signals(Scenario(**bundle["scenario"]), evidence, use_llm=False)
    signal.id = "SIG-G60-US-001"
    bundle["evidence"] = [e.model_dump(mode="json") for e in evidence]
    bundle["signals"] = [signal.model_dump(mode="json")]
    bundle["requirements"] = bundle["requirements"][:1]
    bundle["requirements"][0]["signal_ids"] = [signal.id]
    bundle["discarded"] = [{"title": "Synthetic discarded", "signal_ids": [signal.id], "reason": "Scope"}]
    bundle["context"] = {"counter_evidence": {signal.id: []}}
    folder = tmp_path / "processed"
    folder.mkdir()
    path = folder / "G60-US.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    monkeypatch.setenv("PROCESSED_DIR", str(folder))
    return bundle, evidence, path


def test_id_only_migration_replays_edit_weights_and_preserves_history(original, tmp_path):
    bundle, evidence, path = original
    audit = AuditLog(tmp_path / "audit.db")
    store = Store(audit)
    store.load_all()
    old_id = bundle["requirements"][0]["id"]
    pm = Actor(type="human", name="pm")
    store.decide(old_id, "approve", pm, "Reviewed evidence")
    store.decide(old_id, "edit", pm, "Reviewed protocol", {"acceptance_criterion": "Synthetic: 1 step", "effort": "S"})
    store.set_weights("G60-US", {"reach": 1}, pm, "Reviewed weights")
    hashes = [e.hash for e in audit.events()]
    migrated, transition = migrate_bundle(bundle, evidence)
    audit.append("IDENTITY_MIGRATED", "G60-US", Actor(type="system", name="migration"), "Verified ID-only change",
                 transition)
    path.write_text(json.dumps(migrated), encoding="utf-8")
    restarted = Store(audit)
    restarted.load_all()
    new_id = transition["requirement_ids"][old_id]
    req = restarted.get("G60-US").requirements[new_id]
    assert req.status.value == "approved"
    assert req.acceptance_criterion == "Synthetic: 1 step" and req.effort == "S" and req.version == 2
    assert restarted.get("G60-US").weights == store.get("G60-US").weights
    assert [e.hash for e in audit.events()][:len(hashes)] == hashes
    assert [e.event_type for e in audit.events(requirement_id=new_id)] == [
        "REQUIREMENT_PROPOSED", "PM_APPROVE", "PM_EDIT"]
    assert audit.verify()["valid"]
    assert migrated["discarded"][0]["signal_ids"] == migrated["requirements"][0]["signal_ids"]
    assert set(migrated["context"]["counter_evidence"]) == set(transition["signal_ids"].values())
    # A later content change still cannot inherit the approvals.
    migrated["requirements"][0]["description"] = "Different outcome"
    path.write_text(json.dumps(migrated), encoding="utf-8")
    with pytest.raises(RuntimeError, match="bundle changed"):
        Store(audit).load_all()
    audit.close()


def test_migration_rejects_ambiguous_or_missing_original_groups(original):
    bundle, evidence, _ = original
    with pytest.raises(ValueError, match="missing or ambiguous"):
        migrate_bundle(bundle, evidence[:2])


def test_legacy_audit_warning_is_visible_and_cannot_authorize_migration(original, tmp_path, caplog):
    from core.identity import recorded_fingerprint

    bundle, _, _ = original
    audit = AuditLog(tmp_path / "legacy.db")
    audit.append("PM_APPROVE", "G60-US", Actor(type="human", name="pm"), "Legacy decision",
                 requirement_id=bundle["requirements"][0]["id"])
    store = Store(audit)
    store.load_all()
    assert "source identity cannot be verified" in caplog.text
    assert any("source identity cannot be verified" in warning for warning in store.get("G60-US").scenario.warnings)
    audit.append("IDENTITY_MIGRATED", "G60-US", Actor(type="system", name="migration"), "Invalid transition",
                 {"from_bundle_sha256": "unknown", "bundle_sha256": "new"})
    with pytest.raises(RuntimeError, match="no matching source fingerprint"):
        recorded_fingerprint(audit.events("G60-US"))
    audit.close()


def test_cli_migrates_a_copy_and_refuses_unverified_audits(original, tmp_path, monkeypatch):
    from scripts.migrate_signal_ids import migrate

    bundle, evidence, path = original
    stages = path.parent / "G60-US"
    stages.mkdir()
    (stages / "evidence.json").write_text(json.dumps([e.model_dump(mode="json") for e in evidence]), encoding="utf-8")
    (stages / "requirements.json").write_text(json.dumps(bundle["requirements"]), encoding="utf-8")
    source_db = tmp_path / "source.db"
    audit = AuditLog(source_db)
    store = Store(audit)
    store.load_all()
    old_id = bundle["requirements"][0]["id"]
    store.decide(old_id, "approve", Actor(type="human", name="pm"), "Reviewed original")
    source_hashes = [e.hash for e in audit.events()]
    output = tmp_path / "migrated"
    report = migrate(path.parent, output, source_db)
    assert json.loads(path.read_text(encoding="utf-8")) == bundle
    assert [e.hash for e in audit.events()] == source_hashes
    audit.close()
    monkeypatch.setenv("PROCESSED_DIR", str(output / "processed"))
    copied_audit = AuditLog(output / "audit.db")
    restarted = Store(copied_audit)
    restarted.load_all()
    new_id = report["G60-US"]["requirement_ids"][old_id]
    assert restarted.get("G60-US").requirements[new_id].status.value == "approved"
    assert copied_audit.verify()["valid"]
    copied_audit.close()
    legacy = AuditLog(tmp_path / "legacy.db")
    legacy.append("PM_APPROVE", "G60-US", Actor(type="human", name="pm"), "Unverified source",
                  requirement_id=old_id)
    legacy.close()
    with pytest.raises(ValueError, match="identity unverified"):
        migrate(path.parent, tmp_path / "refused", tmp_path / "legacy.db")
    assert not (tmp_path / "refused").exists()
