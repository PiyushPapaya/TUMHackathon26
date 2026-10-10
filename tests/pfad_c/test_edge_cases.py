"""Randfälle (Ticket C9): Nichts darf abstürzen, und Leeres darf nichts kosten oder erfinden.

Alle Daten sind synthetisch (keine BMW-Texte im Repo). Die KI ist durch Fakes ersetzt.
"""

import pytest

from core.models import (
    Category,
    EvidenceLevel,
    OfferCheck,
    Requirement,
    Scenario,
    Signal,
    SignalKind,
    SourceType,
)
from requirements_engine import challenge, derive, evidence_level, scoring
from requirements_engine.challenge import answer_challenge
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all
from requirements_engine.factors import compute_factors
from requirements_engine.offer_parser import parse_option_lines, parse_series_lines

SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5 Series", market="US", countries=["US"],
                    competitors=[])


def _signal(sid="SIG-1", mentions=20, evidence_ids=("E1",), kind=SignalKind.COMPLAINT, sources=(SourceType.FEEDBACK,)):
    return Signal(id=sid, kind=kind, category=Category.EXTERIOR, title="t", summary="s",
                  evidence_ids=list(evidence_ids), mention_count=mentions, source_types=list(sources))


def _draft(signal_ids, **kw):
    return RequirementDraft(title="T", description="d", acceptance_criterion="c", category=Category.EXTERIOR,
                            signal_ids=list(signal_ids), **kw)


def _fake(monkeypatch, drafts):
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=list(drafts)))


# --- derive_all -------------------------------------------------------------------------------------------

def test_keine_befunde_ruft_die_ki_gar_nicht_erst_auf(monkeypatch):
    def nie(*a, **k):
        raise AssertionError("Ohne Befunde darf die KI nicht gefragt werden (kostet Geld, könnte erfinden).")

    monkeypatch.setattr(derive, "ask_json", nie)
    assert derive_all(SCENARIO, [], [], {}) == ([], [])


def test_ki_liefert_leere_liste(monkeypatch):
    _fake(monkeypatch, [])
    reqs, discarded = derive_all(SCENARIO, [_signal()], [], {})
    assert reqs == []
    assert [d["title"].startswith("Not covered:") for d in discarded] == [True]  # nichts geht still verloren


def test_befund_ohne_belege_fuehrt_nicht_zum_absturz(monkeypatch):
    _fake(monkeypatch, [_draft(["SIG-1"])])
    reqs, _ = derive_all(SCENARIO, [_signal(evidence_ids=())], [], {})
    assert len(reqs) == 1 and reqs[0].score_breakdown["satisfaction_gap"].value == 0


def test_beleg_id_ohne_beleg_im_bestand(monkeypatch):
    _fake(monkeypatch, [_draft(["SIG-1"])])  # der Befund zitiert "E1", aber evidence ist leer
    reqs, _ = derive_all(SCENARIO, [_signal()], [], {})
    assert len(reqs) == 1


def test_anforderung_ohne_studienbeleg_sagt_es_offen(monkeypatch):
    _fake(monkeypatch, [_draft(["SIG-1"])])
    reqs, _ = derive_all(SCENARIO, [_signal()], [], {})
    assert reqs[0].score_breakdown["satisfaction_gap"].explanation == "no study data"


def test_alle_befunde_ohne_nennungen(monkeypatch):
    _fake(monkeypatch, [_draft(["SIG-1"])])
    reqs, _ = derive_all(SCENARIO, [_signal(mentions=0)], [], {})
    assert reqs[0].score_breakdown["reach"].value == 0  # keine Division durch null


def test_entwurf_ohne_signal_ids_wird_verworfen(monkeypatch):
    _fake(monkeypatch, [_draft([])])
    assert derive_all(SCENARIO, [_signal()], [], {})[0] == []


def test_doppelte_signal_ids_zaehlen_nur_einmal(monkeypatch):
    _fake(monkeypatch, [_draft(["SIG-1", "SIG-1", "SIG-1"])])
    reqs, _ = derive_all(SCENARIO, [_signal(mentions=20)], [], {})
    assert reqs[0].signal_ids == ["SIG-1"]
    assert "20 of at most 20" in reqs[0].score_breakdown["reach"].explanation  # nicht 60


def test_faktoren_bleiben_im_bereich_auch_bei_extremen_eingaben():
    values, text = compute_factors([_signal(mentions=10**9)], {}, 1, True, "L", {})
    assert all(0 <= v <= 1 for v in values.values()) and set(values) == set(text)


# --- Gewichte ---------------------------------------------------------------------------------------------

ALLE_NULL = {name: 0.0 for name in scoring.DEFAULT_WEIGHTS}


def test_ein_einziges_gewicht_bestimmt_den_score():
    weights = {**ALLE_NULL, "reach": 1.0}
    total, breakdown = scoring.score({"reach": 0.5}, {}, EvidenceLevel.A, weights)
    assert total == pytest.approx(50.0)
    assert breakdown["reach"].weight == 1.0 and breakdown["customer_pain"].contribution == 0


def test_alle_gewichte_null_wird_abgelehnt():
    with pytest.raises(ValueError):
        scoring.score({}, {}, EvidenceLevel.A, ALLE_NULL)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1])
def test_ungueltige_gewichte_werden_abgelehnt(bad):
    with pytest.raises(ValueError):
        scoring.normalize_weights({"reach": bad})


# --- Evidenzstufe -----------------------------------------------------------------------------------------

def test_stufe_ohne_jede_quelle_sagt_nicht_nur_web():
    level, reason = evidence_level.classify(0, set(), forward_looking=False)
    assert level == EvidenceLevel.C and "web" not in reason.lower()  # sonst steht eine falsche Begründung da


def test_stufe_bei_null_nennungen_mit_zukunftsannahme_ist_d():
    assert evidence_level.classify(0, {SourceType.FEEDBACK}, forward_looking=True)[0] == EvidenceLevel.D


# --- Optionsliste -----------------------------------------------------------------------------------------

def test_parser_mit_leeren_zeilen():
    assert parse_option_lines([]) == [] and parse_series_lines([]) == []
    assert parse_option_lines(["", "\t", "   "]) == []


# --- Challenge --------------------------------------------------------------------------------------------

REQ = Requirement(
    id="REQ-1", title="t", description="d", acceptance_criterion="c", category=Category.EXTERIOR,
    signal_ids=["SIG-1"], score=10, rank=1, score_breakdown={}, rationale="r", evidence_level=EvidenceLevel.C,
    assumptions=[], uncertainties=[], offer_check=OfferCheck(status="unknown"),
)


def test_challenge_ohne_belege_stuerzt_nicht_ab_und_fragt_die_ki_nicht(monkeypatch):
    monkeypatch.setattr(challenge, "ask_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("kein Aufruf")))
    result = answer_challenge(REQ, "Stimmt das?", [], [])
    assert result["supporting_evidence_ids"] == [] and result["counter_evidence_ids"] == []
    assert result["answer"]
