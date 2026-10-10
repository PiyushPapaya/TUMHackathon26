"""W-C1: Stabile Anforderungs-IDs. Gleiche Befunde ergeben dieselbe ID, egal in welcher Reihenfolge die KI antwortet.

Warum: Prüfpfad und PM-Entscheidungen hängen an der ID. Mit einer Zählnummer in KI-Reihenfolge zeigte
nach jedem neuen Lauf "REQ-...-003" auf eine andere Anforderung. Verworfen: ID aus dem Titel (die KI
formuliert ihn jedes Mal anders).
"""

import hashlib
import re

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all, stable_key

SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"],
                    competitors=[])
SIGNALS = [
    Signal(id=f"SIG-{n}", kind=SignalKind.COMPLAINT, category=Category.EXTERIOR, title="t", summary="s",
           evidence_ids=["EV-1"], mention_count=20, source_types=[SourceType.FEEDBACK])
    for n in (1, 2, 3)
]


def _draft(title: str, ids: list[str]) -> RequirementDraft:
    return RequirementDraft(title=title, description="d", acceptance_criterion="c", category=Category.EXTERIOR,
                            signal_ids=ids)


def _run(monkeypatch, *drafts: RequirementDraft):
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=list(drafts)))
    return derive_all(SCENARIO, SIGNALS, [], {})[0]


def test_id_ist_hash_der_sortierten_befund_ids():
    expected = hashlib.sha1(b"SIG-1|SIG-2").hexdigest()[:6]
    assert stable_key(["SIG-2", "SIG-1"]) == stable_key(["SIG-1", "SIG-2"]) == expected


def test_vertauschte_reihenfolge_gibt_gleiche_ids(monkeypatch):
    a, b = _draft("A", ["SIG-1"]), _draft("B", ["SIG-2", "SIG-3"])
    first = {r.title: r.id for r in _run(monkeypatch, a, b)}
    second = {r.title: r.id for r in _run(monkeypatch, b, a)}
    assert first == second
    assert all(re.fullmatch(r"REQ-G60-US-[0-9a-f]{6}", i) for i in first.values())


def test_anderer_titel_gleiche_befunde_gleiche_id(monkeypatch):
    first = _run(monkeypatch, _draft("Wording one", ["SIG-1"]))[0].id
    second = _run(monkeypatch, _draft("Completely different wording", ["SIG-1"]))[0].id
    assert first == second


def test_stable_key_steht_im_feld(monkeypatch):
    req = _run(monkeypatch, _draft("A", ["SIG-1", "SIG-2"]))[0]
    assert req.id == f"REQ-G60-US-{req.stable_key}" and req.stable_key == stable_key(["SIG-1", "SIG-2"])


def test_zwei_entwuerfe_mit_gleichen_befunden_bekommen_verschiedene_ids(monkeypatch):
    # Die KI soll das nicht tun (Prompt), aber eine doppelte ID wäre im Prüfpfad nicht mehr eindeutig.
    reqs = _run(monkeypatch, _draft("A", ["SIG-1"]), _draft("A again", ["SIG-1"]))
    ids = [r.id for r in reqs]
    assert len(set(ids)) == 2 and ids[0] != ids[1]
    assert ids[1].startswith(ids[0] + "-")  # Dublette hängt eine Zählung an, der erste Treffer bleibt stabil
