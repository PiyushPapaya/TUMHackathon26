"""Nicht abgedeckte Beschwerden/Wünsche (Nachprüfung C8): Was die KI auslässt, muss der PM sehen.

Echter Fund: Trotz Prompt-Regel fehlte "Start-Stopp lässt sich nicht dauerhaft abschalten" (22 Nennungen).
Der Code listet solche Befunde mit Grund im zweiten Rückgabewert von derive_all (-> Prüfpfad).
"""

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all

SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"],
                    competitors=[])


def _signal(sid: str, kind: SignalKind, mentions: int = 22) -> Signal:
    return Signal(id=sid, kind=kind, category=Category.DRIVING_EXPERIENCE, title=f"Title {sid}", summary="s",
                  evidence_ids=["EV-1"], mention_count=mentions, source_types=[SourceType.FEEDBACK])


def _answer(monkeypatch, *drafts: tuple[str, list[str], bool]) -> None:
    answer = RequirementDrafts(drafts=[
        RequirementDraft(title=t, description="d", acceptance_criterion="c", category=Category.DRIVING_EXPERIENCE,
                         signal_ids=ids, in_scope=in_scope, scope_reason="" if in_scope else "regulatory")
        for t, ids, in_scope in drafts
    ])
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: answer)


def test_ausgelassene_beschwerde_wird_sichtbar(monkeypatch):
    signals = [_signal("SIG-1", SignalKind.COMPLAINT), _signal("SIG-2", SignalKind.COMPLAINT)]
    _answer(monkeypatch, ("Covered", ["SIG-1"], True))
    reqs, discarded = derive_all(SCENARIO, signals, [], {})
    assert [r.title for r in reqs] == ["Covered"]
    assert discarded == [{"title": "Not covered: Title SIG-2",
                          "reason": "The AI derived no requirement from this complaint (22 mentions); PM to check.",
                          "signal_ids": ["SIG-2"]}]


def test_ausgelassener_wunsch_zaehlt_auch_lob_und_trend_nicht(monkeypatch):
    signals = [_signal("SIG-N", SignalKind.UNMET_NEED, 7), _signal("SIG-D", SignalKind.DELIGHT),
               _signal("SIG-T", SignalKind.TREND)]
    _answer(monkeypatch)
    _, discarded = derive_all(SCENARIO, signals, [], {})
    assert [d["signal_ids"] for d in discarded] == [["SIG-N"]]  # Lob/Trend brauchen keine eigene Anforderung


def test_out_of_scope_befund_gilt_als_behandelt(monkeypatch):
    signals = [_signal("SIG-1", SignalKind.COMPLAINT)]
    _answer(monkeypatch, ("Homologation", ["SIG-1"], False))
    _, discarded = derive_all(SCENARIO, signals, [], {})
    assert [d["title"] for d in discarded] == ["Homologation"]  # schon mit Grund verworfen, nicht doppelt


def test_alles_abgedeckt_ergibt_keine_zusatzeintraege(monkeypatch):
    signals = [_signal("SIG-1", SignalKind.COMPLAINT), _signal("SIG-2", SignalKind.UNMET_NEED)]
    _answer(monkeypatch, ("Both", ["SIG-1", "SIG-2"], True))
    assert derive_all(SCENARIO, signals, [], {})[1] == []
