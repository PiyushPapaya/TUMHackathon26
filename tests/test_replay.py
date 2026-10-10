"""L19: PM-Entscheidungen und Gewichte überleben einen Server-Neustart (Replay aus audit.db)."""

from core.audit import AuditLog
from core.models import Actor, ActorType
from core.store import Store

PM = Actor(type=ActorType.HUMAN, name="pm.test")


def _neuer_store(db, tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "leer"))  # nur Beispiel-Bundle
    store = Store(AuditLog(db))
    store.load_all()
    return store


def test_entscheidungen_und_gewichte_ueberleben_neustart(tmp_path, monkeypatch):
    db = tmp_path / "audit.db"
    store = _neuer_store(db, tmp_path, monkeypatch)
    store.decide("REQ-G60-US-002", "approve", PM, "Belege überzeugen")
    store.decide("REQ-G60-US-003", "reject", PM, "Zu dünn")
    store.decide("REQ-G60-US-004", "edit", PM, "Schärfer", {"acceptance_criterion": "Öffnet in 1 s", "effort": "S"})
    ranking = [r.id for r in store.set_weights("G60-US", {"future_relevance": 0.6}, PM, "Zukunft zählt")]
    events_vorher = len(store.audit.events())

    neu = _neuer_store(db, tmp_path, monkeypatch)  # simulierter Neustart: gleiche DB, frischer Store
    reqs = neu.get("G60-US").requirements
    assert reqs["REQ-G60-US-002"].status.value == "approved"
    assert reqs["REQ-G60-US-003"].status.value == "rejected"
    assert reqs["REQ-G60-US-004"].acceptance_criterion == "Öffnet in 1 s" and reqs["REQ-G60-US-004"].version == 2
    assert reqs["REQ-G60-US-004"].effort == "S"
    assert [r.id for r in neu.ranked("G60-US")] == ranking
    assert len(neu.audit.events()) == events_vorher  # Neustart schreibt keine doppelten Vorschläge
    assert neu.audit.verify()["valid"]


def test_ereignis_zu_unbekannter_anforderung_wird_uebersprungen(tmp_path, monkeypatch):
    db = tmp_path / "audit.db"
    store = _neuer_store(db, tmp_path, monkeypatch)
    store.audit.append("PM_APPROVE", "G60-US", PM, "alte ID aus früherem Lauf", {}, requirement_id="REQ-ALT-999")
    neu = _neuer_store(db, tmp_path, monkeypatch)
    assert "REQ-ALT-999" not in neu.get("G60-US").requirements
