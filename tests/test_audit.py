"""Prüfpfad: Ereignisse werden verkettet, Manipulation wird erkannt."""

import sqlite3

import pytest

from core.audit import GENESIS_HASH, AuditLog
from core.models import Actor, ActorType

PM = Actor(type=ActorType.HUMAN, name="pm.test")


def test_chain_links_each_event_to_previous(tmp_path):
    log = AuditLog(tmp_path / "a.db")
    first = log.append("PM_APPROVED", "G60-US", PM, "passt", requirement_id="REQ-1")
    second = log.append("PM_REJECTED", "G60-US", PM, "doch nicht", requirement_id="REQ-1")
    assert first.prev_hash == GENESIS_HASH
    assert second.prev_hash == first.hash
    assert log.verify() == {"valid": True, "broken_at_seq": None, "checked": 2}


def test_tampering_is_detected(tmp_path):
    db = tmp_path / "a.db"
    log = AuditLog(db)
    log.append("PM_APPROVED", "G60-US", PM, "passt", requirement_id="REQ-1")
    log.append("PM_EDITED", "G60-US", PM, "Text geschärft", requirement_id="REQ-1")
    # Jemand ändert nachträglich die Begründung direkt in der Datenbank:
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE audit_events SET rationale = 'gefälscht' WHERE seq = 1")
    result = log.verify()
    assert result["valid"] is False
    assert result["broken_at_seq"] == 1


def test_rationale_is_mandatory(tmp_path):
    log = AuditLog(tmp_path / "a.db")
    with pytest.raises(ValueError):
        log.append("PM_APPROVED", "G60-US", PM, "   ")


def test_filter_by_requirement(tmp_path):
    log = AuditLog(tmp_path / "a.db")
    log.append("PM_APPROVED", "G60-US", PM, "ok", requirement_id="REQ-1")
    log.append("PM_APPROVED", "G60-US", PM, "ok", requirement_id="REQ-2")
    assert [e.requirement_id for e in log.events(requirement_id="REQ-2")] == ["REQ-2"]
