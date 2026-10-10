"""Scope-Wächter (Ticket C4): Out-of-scope-Entwürfe landen mit Grund im zweiten Rückgabewert.

Brief: Fokus auf Kundenwert, NICHT auf Regulatorik, Engineering-Spezifikationen oder Business-Case.
Warum zurückgeben statt löschen: Der Lead schreibt sie als REQUIREMENT_DISCARDED in den Prüfpfad,
damit der PM sieht, was die KI vorgeschlagen und warum wir es verworfen haben.
"""

import pytest

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all

SCENARIO = Scenario(
    id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"], competitors=[],
)
SIGNALS = [
    Signal(id=f"SIG-{n}", kind=SignalKind.COMPLAINT, category=Category.EXTERIOR, title="t", summary="s",
           evidence_ids=["EV-1"], mention_count=20, source_types=[SourceType.FEEDBACK])
    for n in (1, 2, 3, 4)
]

OUT_OF_SCOPE = [
    ("Meet US homologation rules for headlight beam", "regulatory", "SIG-1"),
    ("Use a 12-bit rotary encoder part for the volume knob", "engineering specification", "SIG-2"),
    ("Lower the base price by 5,000 USD", "price / business case", "SIG-3"),
]


def _drafts(*pairs: tuple[str, bool, str, str]) -> RequirementDrafts:
    return RequirementDrafts(drafts=[
        RequirementDraft(title=title, description="d", acceptance_criterion="c", category=Category.EXTERIOR,
                         signal_ids=[sid], in_scope=in_scope, scope_reason=reason)
        for title, in_scope, reason, sid in pairs
    ])


def _scope_only(discarded: list[dict]) -> list[dict]:
    """Nur die Scope-Entscheidungen der KI; nicht abgedeckte Befunde prüft test_not_covered.py."""
    return [d for d in discarded if not d["title"].startswith("Not covered:")]


@pytest.mark.parametrize(("title", "reason", "signal_id"), OUT_OF_SCOPE)
def test_out_of_scope_wird_mit_grund_zurueckgegeben(monkeypatch, title, reason, signal_id):
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: _drafts((title, False, reason, signal_id)))
    reqs, discarded = derive_all(SCENARIO, SIGNALS, [], {})
    assert reqs == []
    assert _scope_only(discarded) == [{"title": title, "reason": reason, "signal_ids": [signal_id]}]


def test_gemischte_liste_trennt_sauber(monkeypatch):
    answer = _drafts(
        (OUT_OF_SCOPE[0][0], False, OUT_OF_SCOPE[0][1], "SIG-1"),
        ("Rear seats with more knee room", True, "", "SIG-4"),
        (OUT_OF_SCOPE[2][0], False, OUT_OF_SCOPE[2][1], "SIG-3"),
    )
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: answer)
    reqs, discarded = derive_all(SCENARIO, SIGNALS, [], {})
    assert [r.title for r in reqs] == ["Rear seats with more knee room"]
    assert {d["reason"] for d in _scope_only(discarded)} == {"regulatory", "price / business case"}
    assert reqs[0].rank == 1  # der Rang zählt nur, was im Scope blieb


def test_rang_und_ids_ueberspringen_keine_luecken(monkeypatch):
    answer = _drafts(("Out", False, "regulatory", "SIG-1"), ("In A", True, "", "SIG-2"), ("In B", True, "", "SIG-3"))
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: answer)
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {})
    assert sorted(r.id for r in reqs) == ["REQ-G60-US-001", "REQ-G60-US-002"]
    assert sorted(r.rank for r in reqs) == [1, 2]
