"""W-C5: Ableitung pro Themenblock und Zusammenführen überlappender Entwürfe.

Warum Blöcke: Ein Aufruf über alle ~55 Befunde ließ die KI Beschwerden vergessen (G60-US: 4 "Not covered") und
deckelte die Zahl der Anforderungen. Drei feste Blöcke (Kategorie -> Block per Tabelle im Code) sind erklärbar und
reproduzierbar. Verworfen: Clustering per KI (nicht reproduzierbar), ein Aufruf je Kategorie (zu kleine Blöcke).
"""

import json

import pytest

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.blocks import BLOCKS, merge_overlapping, split_into_blocks
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all

SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"],
                    competitors=[])


def _sig(sid: str, category: Category, kind=SignalKind.COMPLAINT, mentions=20) -> Signal:
    return Signal(id=sid, kind=kind, category=category, title=f"Title {sid}", summary="s", evidence_ids=["EV"],
                  mention_count=mentions, source_types=[SourceType.FEEDBACK])


def _draft(title: str, ids: list[str], category=Category.EXTERIOR, **kw) -> RequirementDraft:
    return RequirementDraft(title=title, description="d", acceptance_criterion="c", category=category,
                            signal_ids=ids, **kw)


def test_jede_kategorie_hat_genau_einen_block():
    seen = [c for _, cats in BLOCKS for c in cats]
    assert sorted(seen) == sorted(Category) and len(seen) == len(set(seen))


def test_befunde_landen_im_richtigen_block_und_keiner_geht_verloren():
    signals = [_sig("A", Category.DRIVING_EXPERIENCE), _sig("B", Category.INFOTAINMENT_DIGITAL),
               _sig("C", Category.EXTERIOR), _sig("D", Category.RANGE_CHARGING)]
    blocks = dict(split_into_blocks(signals))
    assert [s.id for s in blocks[BLOCKS[0][0]]] == ["A", "D"]
    assert [s.id for s in blocks[BLOCKS[1][0]]] == ["B"] and [s.id for s in blocks[BLOCKS[2][0]]] == ["C"]
    assert sorted(s.id for b in blocks.values() for s in b) == ["A", "B", "C", "D"]


def test_leere_bloecke_werden_uebersprungen():
    assert [name for name, _ in split_into_blocks([_sig("A", Category.EXTERIOR)])] == [BLOCKS[2][0]]


def test_ein_ki_aufruf_pro_nicht_leerem_block_mit_nur_dessen_befunden(monkeypatch):
    calls = []

    def fake(system, user, schema, **kw):
        calls.append(user)
        return RequirementDrafts(drafts=[])

    monkeypatch.setattr(derive, "ask_json", fake)
    derive_all(SCENARIO, [_sig("DRV", Category.DRIVING_EXPERIENCE), _sig("DIG", Category.INFOTAINMENT_DIGITAL)], [], {})
    assert len(calls) == 2
    first, second = (json.loads(c.split("Signals:\n", 1)[1]) for c in calls)
    assert [r["id"] for r in first] == ["DRV"] and [r["id"] for r in second] == ["DIG"]
    assert BLOCKS[0][0] in calls[0] and BLOCKS[1][0] in calls[1]


def test_entwurf_darf_keine_befunde_anderer_bloecke_zitieren(monkeypatch):
    def fake(system, user, schema, **kw):
        return RequirementDrafts(drafts=[_draft("Mixed", ["DRV", "DIG"], Category.DRIVING_EXPERIENCE)]
                                 if BLOCKS[0][0] in user else [])

    monkeypatch.setattr(derive, "ask_json", fake)
    signals = [_sig("DRV", Category.DRIVING_EXPERIENCE), _sig("DIG", Category.INFOTAINMENT_DIGITAL)]
    reqs, _ = derive_all(SCENARIO, signals, [], {})
    assert reqs[0].signal_ids == ["DRV"]  # DIG gehört zu einem anderen Block, die KI sah ihn dort nicht


def _fake_all(monkeypatch, *drafts):
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=list(drafts)))


SIGS = [_sig(f"S{n}", Category.EXTERIOR) for n in range(1, 7)]


def test_ueberlappende_entwuerfe_werden_eine_anforderung(monkeypatch):
    _fake_all(monkeypatch, _draft("Big", ["S1", "S2", "S3"], assumptions=["a1"]),
              _draft("Small", ["S3", "S4"], assumptions=["a2"]))  # Überlappung 1 von min(3,2)=2 -> 50 %
    reqs, _ = derive_all(SCENARIO, SIGS, [], {})
    assert len(reqs) == 1 and reqs[0].title == "Big"  # der Entwurf mit mehr Befunden bleibt Haupttext
    assert sorted(reqs[0].signal_ids) == ["S1", "S2", "S3", "S4"] and reqs[0].assumptions == ["a1", "a2"]


def test_unter_50_prozent_bleiben_zwei_anforderungen(monkeypatch):
    _fake_all(monkeypatch, _draft("A", ["S1", "S2", "S3"]), _draft("B", ["S3", "S4", "S5"]))  # 1 von 3 = 33 %
    assert len(derive_all(SCENARIO, SIGS, [], {})[0]) == 2


def test_wette_und_heute_anforderung_werden_nie_verschmolzen():
    today = _draft("Today", ["S1", "S2"])
    bet = _draft("Bet", ["S1", "S2"], horizon="next_gen")
    kept = merge_overlapping([(today, [SIGS[0], SIGS[1]]), (bet, [SIGS[0], SIGS[1]])])
    assert len(kept) == 2


@pytest.mark.parametrize("n", [0, 1])
def test_merge_mit_leerer_oder_einzelner_liste(n):
    items = [(_draft("A", ["S1"]), [SIGS[0]])][:n]
    assert merge_overlapping(items) == items


# --- Wetten dürfen die Kunden einer Heute-Anforderung nicht noch einmal zählen ---------------------------------

def _trend(sid: str) -> Signal:
    return Signal(id=sid, kind=SignalKind.TREND, category=Category.EXTERIOR, title="trend", summary="s",
                  evidence_ids=["EV"], mention_count=2, source_types=[SourceType.WEB])


def test_wette_verliert_kundenbefunde_die_schon_eine_heute_anforderung_traegt():
    from requirements_engine.blocks import separate_bets

    big, own, trend = SIGS[0], SIGS[1], _trend("T1")
    today = _draft("Today", ["S1"])
    bet = _draft("Bet", ["S1", "S2", "T1"], horizon="next_gen", assumptions=["x"])
    kept = separate_bets([(today, [big]), (bet, [big, own, trend])])
    bet_draft, bet_linked = kept[1]
    assert [s.id for s in bet_linked] == ["S2", "T1"] and bet_draft.signal_ids == ["S2", "T1"]
    assert kept[0] == (today, [big])  # die Heute-Anforderung bleibt unberührt


def test_trend_und_wettbewerbsbefunde_bleiben_der_wette_auch_wenn_geteilt():
    from requirements_engine.blocks import separate_bets

    trend = _trend("T1")
    rival = Signal(id="C1", kind=SignalKind.COMPETITOR_ADVANTAGE, category=Category.EXTERIOR, title="r", summary="s",
                   evidence_ids=["EV"], mention_count=1, source_types=[SourceType.WEB])
    kept = separate_bets([(_draft("Today", ["T1", "C1"]), [trend, rival]),
                          (_draft("Bet", ["T1", "C1"], horizon="next_gen"), [trend, rival])])
    assert [s.id for s in kept[1][1]] == ["T1", "C1"]


def test_geliehene_staerke_macht_die_wette_nicht_mehr_zu_stufe_a(monkeypatch):
    # Echter Fund (F70-EU, Sa 22:50): Eine Wette zitierte eine Beschwerde mit 96 Nennungen, die schon eine Heute-
    # Anforderung trug, und stand mit Stufe A und 63,9 Punkten auf Platz 1. Jetzt ist sie ohne die Beschwerde Stufe D.
    sigs = [_sig("BIG", Category.EXTERIOR, mentions=96), _trend("T1")]
    _fake_all(monkeypatch, _draft("Today", ["BIG"]),
              _draft("Bet", ["BIG", "T1"], horizon="next_gen", assumptions=["OTA becomes standard"]))
    reqs, _ = derive_all(SCENARIO, sigs, [], {})
    bet = next(r for r in reqs if r.title == "Bet")
    assert bet.signal_ids == ["T1"] and bet.evidence_level.value == "D"
    assert next(r for r in reqs if r.title == "Today").rank < bet.rank
