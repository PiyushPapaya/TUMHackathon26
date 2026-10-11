"""W-C12: Beweis für den Scope-Wächter. Hier der Offline-Teil: Aufbau der Testmenge und die Auswertung.

Der Live-Lauf gegen die echte KI steht in scope_eval.py, sein Ergebnis in SCOPE_REPORT.md. Brief: "Focus on customer
value rather than engineering specifications, regulatory requirements, or detailed business-case calculations."
"""

from types import SimpleNamespace

from scope_cases import CASES, signals_for_cases
from scope_eval import score_scope


def test_testmenge_ist_ausgewogen_und_eindeutig():
    ids = [c.id for c in CASES]
    assert len(ids) == len(set(ids)) == 48
    labels = [c.label for c in CASES]
    assert {x: labels.count(x) for x in set(labels)} == {"regulatory": 9, "engineering": 9, "price": 10, "in_scope": 20}


def test_jeder_fall_ist_ein_befund_mit_beschwerde_oder_wunsch():
    signals = signals_for_cases()
    assert [s.id for s in signals] == [c.id for c in CASES]
    assert all(s.kind.value in ("complaint", "unmet_need") and s.mention_count >= 15 for s in signals)
    assert len({s.category for s in signals}) >= 5  # verteilt auf die Blöcke, nicht ein einziger Themenhaufen


def _req(*ids):
    return SimpleNamespace(signal_ids=list(ids))


def _drop(sid, reason="regulatory"):
    return {"title": f"draft {sid}", "reason": reason, "signal_ids": [sid]}


def test_auswertung_zaehlt_erkannte_durchgerutschte_und_zu_unrecht_verworfene():
    oos = [c.id for c in CASES if c.label == "regulatory"]
    fine = [c.id for c in CASES if c.label == "in_scope"]
    result = score_scope(CASES, [_req(oos[0], fine[0]), _req(oos[1])],  # oos[0] durchgerutscht, oos[1] auch
                         [_drop(oos[1]), _drop(oos[2]), _drop(fine[1])])
    reg = result["regulatory"]
    assert reg["total"] == 9 and reg["caught"] == 2 and reg["leaked"] == 1  # oos[1] geteilt: erkannt UND in Anforderung
    assert reg["split"] == 1
    assert result["in_scope"]["wrongly_discarded"] == 1


def test_not_covered_zaehlt_nicht_als_scope_entscheidung():
    sid = next(c.id for c in CASES if c.label == "in_scope")
    result = score_scope(CASES, [], [{"title": "Not covered: x", "reason": "The AI derived no requirement ...",
                                      "signal_ids": [sid]}])
    assert result["in_scope"]["wrongly_discarded"] == 0 and result["in_scope"]["not_covered"] == 1


def test_wetten_gruende_zaehlen_nicht_als_scope_entscheidung():
    sid = next(c.id for c in CASES if c.label == "in_scope")
    bet = {"title": "Bet", "reason": "Bet on the next generation without a stated assumption: not verifiable.",
           "signal_ids": [sid]}
    assert score_scope(CASES, [], [bet])["in_scope"]["wrongly_discarded"] == 0
