"""Ticket L3: Pipeline nutzt derive_all, schreibt discarded.json und das Bundle trägt die Verworfenen.

Warum: Der PM soll sehen, was die KI vorgeschlagen und wir als Out-of-scope verworfen haben.
Der Prüfpfad (SQLite) lebt im Store, darum reicht die Pipeline die Verworfenen nur im Bundle weiter.
"""

import json

import pipeline
from core.audit import AuditLog
from core.store import Store
from requirements_engine import derive

DISCARDED = [{"title": "Meet US homologation rules", "reason": "regulatory", "signal_ids": ["SIG-1"]}]
CFG = {
    "id": "T-US", "derivative": "T", "model_name": "Testmodell", "market": "US", "countries": ["US"],
    "competitors": [], "data": {"option_list_file": "gibt-es-nicht.pdf"},
}


def _bundle_ordner(tmp_path, monkeypatch):
    """Pipeline schreibt/liest in einen Temp-Ordner, nie in data/processed."""
    monkeypatch.setattr(pipeline, "OUT_DIR", tmp_path)
    ordner = tmp_path / "T-US"
    ordner.mkdir()
    for stufe, inhalt in {"signals": [], "web_evidence": [], "web_signals": [], "evidence": [], "context": {}}.items():
        (ordner / f"{stufe}.json").write_text(json.dumps(inhalt), encoding="utf-8")
    return ordner


def test_requirements_stufe_nutzt_derive_all_und_schreibt_discarded(tmp_path, monkeypatch):
    ordner = _bundle_ordner(tmp_path, monkeypatch)
    monkeypatch.setattr(derive, "derive_all", lambda *a, **k: ([], DISCARDED))

    pipeline.run_stage("requirements", CFG)

    assert json.loads((ordner / "discarded.json").read_text(encoding="utf-8")) == DISCARDED
    assert json.loads((ordner / "requirements.json").read_text(encoding="utf-8")) == []


def test_bundle_enthaelt_verworfene(tmp_path, monkeypatch):
    ordner = _bundle_ordner(tmp_path, monkeypatch)
    (ordner / "requirements.json").write_text("[]", encoding="utf-8")
    (ordner / "discarded.json").write_text(json.dumps(DISCARDED), encoding="utf-8")

    pipeline.bundle_stage(CFG)

    bundle = json.loads((tmp_path / "T-US.json").read_text(encoding="utf-8"))
    assert bundle["discarded"] == DISCARDED


def test_store_schreibt_requirement_discarded_ins_audit(tmp_path, monkeypatch):
    _bundle_ordner(tmp_path, monkeypatch)
    ordner = tmp_path / "T-US"
    (ordner / "requirements.json").write_text("[]", encoding="utf-8")
    (ordner / "discarded.json").write_text(json.dumps(DISCARDED), encoding="utf-8")
    pipeline.bundle_stage(CFG)
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path))  # Store liest nur *.json im Hauptordner

    store = Store(AuditLog(tmp_path / "audit.db"))
    store.load_all()

    events = [e for e in store.audit.events("T-US") if e.event_type == "REQUIREMENT_DISCARDED"]
    assert len(events) == 1
    assert events[0].rationale == "regulatory"
    assert events[0].payload["title"] == "Meet US homologation rules"
    assert events[0].payload["signal_ids"] == ["SIG-1"]


def test_bundle_kaltstart_hat_abdeckung_kontext_und_zeitstempel(tmp_path, monkeypatch):
    """Welle 2: Bundle trägt Datenabdeckung (Badge), Absatz-Kontext und Chancen-Karte für die Ansichten."""
    ordner = _bundle_ordner(tmp_path, monkeypatch)
    (ordner / "requirements.json").write_text("[]", encoding="utf-8")
    study = {"id": "EV-1", "source_type": "study", "source_name": "S", "derivative": "T", "market": "US", "text": "x"}
    (ordner / "evidence.json").write_text(json.dumps([study]), encoding="utf-8")
    opportunity = {"attribute": "a", "importance": 1, "dissatisfaction": 1}
    context = {"sales": {"volume_2030": 1}, "opportunities": [opportunity]}
    (ordner / "context.json").write_text(json.dumps(context), encoding="utf-8")

    pipeline.bundle_stage(CFG)

    bundle = json.loads((tmp_path / "T-US.json").read_text(encoding="utf-8"))
    assert bundle["scenario"]["data_coverage"] == {"feedback": 0, "study": 1, "sales": 0, "options": 0, "web": 0,
                                                   "external": 0, "badge": "Kaltstart"}
    assert bundle["context"] == {"sales": {"volume_2030": 1}} and len(bundle["opportunities"]) == 1
    assert bundle["funnel"]["generated_at"]
