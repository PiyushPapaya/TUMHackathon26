"""W-C3: Zukunftswetten ("next_gen") mit Stufe D, nur mit Annahmen.

Brief: "Make clear where your conclusions are based on available evidence and where they rely on
forward-looking assumptions." Vorher gab es in den echten Läufen 0 x D: Die Jury sah keine Annahme.
Regeln im Code, nicht in der KI: Eine Wette ohne Annahme ist wertlos (verworfen), eine Wette ohne Trend-Befund
ist erfunden (verworfen), und ob sie D heißt, entscheidet allein die Zahl direkter Kundennennungen.
"""

import pytest

from core.models import Category, EvidenceLevel, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive, evidence_level
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all

FEEDBACK, STUDY, WEB = SourceType.FEEDBACK, SourceType.STUDY, SourceType.WEB
SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"],
                    competitors=[])


def _signal(sid, kind, mentions, sources) -> Signal:
    return Signal(id=sid, kind=kind, category=Category.RANGE_CHARGING, title=f"Title {sid}", summary="s",
                  evidence_ids=["EV-1"], mention_count=mentions, source_types=sources)


SIGNALS = [
    _signal("SIG-TREND", SignalKind.TREND, 2, [WEB]),
    _signal("SIG-WISH", SignalKind.UNMET_NEED, 6, [FEEDBACK]),
    _signal("SIG-BIG", SignalKind.COMPLAINT, 40, [FEEDBACK, STUDY]),
]


def _draft(title, ids, horizon="next_gen", assumptions=("Charging network doubles by 2030",), **kw):
    return RequirementDraft(title=title, description="d", acceptance_criterion="c", category=Category.RANGE_CHARGING,
                            signal_ids=list(ids), horizon=horizon, assumptions=list(assumptions),
                            forward_looking=True, **kw)


def _run(monkeypatch, *drafts):
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=list(drafts)))
    return derive_all(SCENARIO, SIGNALS, [], {})


def test_wette_mit_annahme_und_trend_wird_stufe_d(monkeypatch):
    reqs, _ = _run(monkeypatch, _draft("Bet", ["SIG-TREND", "SIG-WISH"]))
    bet = next(r for r in reqs if r.title == "Bet")
    assert bet.horizon == "next_gen" and bet.evidence_level == EvidenceLevel.D
    assert bet.assumptions and "Zukunftswette" in bet.badges


def test_wette_ohne_annahme_wird_verworfen_mit_grund(monkeypatch):
    reqs, discarded = _run(monkeypatch, _draft("Bet", ["SIG-TREND"], assumptions=()))
    assert all(r.title != "Bet" for r in reqs)
    assert any(d["title"] == "Bet" and "assumption" in d["reason"].lower() for d in discarded)


def test_wette_ohne_trend_befund_wird_verworfen(monkeypatch):
    reqs, discarded = _run(monkeypatch, _draft("Invented bet", ["SIG-WISH"]))
    assert all(r.title != "Invented bet" for r in reqs)
    assert any(d["title"] == "Invented bet" and "trend" in d["reason"].lower() for d in discarded)


def test_starke_kundenbelege_machen_aus_der_wette_keine_annahme(monkeypatch):
    reqs, _ = _run(monkeypatch, _draft("Backed bet", ["SIG-TREND", "SIG-BIG"]))
    bet = next(r for r in reqs if r.title == "Backed bet")
    assert bet.evidence_level == EvidenceLevel.A and bet.horizon == "next_gen"  # 40 Nennungen + Studie tragen es
    assert "Annahme" not in bet.badges


def test_heute_anforderung_bleibt_heute_ohne_badge(monkeypatch):
    reqs, _ = _run(monkeypatch, _draft("Today", ["SIG-BIG"], horizon="today", assumptions=()))
    today = next(r for r in reqs if r.title == "Today")
    assert today.horizon == "today" and "Zukunftswette" not in today.badges


@pytest.mark.parametrize(("customer", "expected"), [(0, EvidenceLevel.D), (14, EvidenceLevel.D),
                                                    (15, EvidenceLevel.B)])
def test_classify_stufe_d_haengt_an_direkten_kundennennungen(customer, expected):
    level, reason = evidence_level.classify(30, {FEEDBACK, WEB}, forward_looking=True, next_gen=True,
                                            customer_mentions=customer)
    assert level == expected
    assert reason


def test_prompt_verlangt_wetten_mit_annahmen_und_trend():
    prompt = derive.SYSTEM_PROMPT
    assert 'horizon="next_gen"' in prompt and "MUST cite at least one trend signal" in prompt
    assert "MUST list at least one concrete assumption" in prompt


def test_prompt_haelt_wetten_kundenorientiert():
    # Echter Fund (Sa 22:10): Die Level-3-Wette enthielt "certified" und "independent safety validation", die
    # Cockpit-Wette zwei fremde Themen samt Sensoren, und Titel begannen mit "Bet:". Brief: Kundenwert statt
    # Regulatorik und Engineering. Regulierung gehört in die Annahmen, das Badge zeigt die Wette.
    prompt = derive.SYSTEM_PROMPT
    assert 'never start a title with "Bet"' in prompt
    assert "Regulation, certification and approvals belong in `assumptions`" in prompt
    assert "name no components" in prompt and "ONE customer outcome" in prompt
