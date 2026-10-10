"""Challenge-Antwort der KI (Ticket C6), mit Fake-KI. Synthetische Daten, kein BMW-Text.

Regeln, die wir festnageln:
- Die KI darf nur Beleg-IDs aus der Eingabe nennen (Halluzinationsschutz), erfundene fliegen raus.
- Ein Beleg ist nie gleichzeitig Beleg und Gegenbeleg.
- Fällt die KI aus (kein Netz, Demo-Cache-Fehlschlag), kommt die regelbasierte Antwort statt eines Fehlers.
- Das Rückgabeformat bleibt gleich, weil API und Oberfläche es schon benutzen.
"""

from core.models import (
    Category,
    Evidence,
    EvidenceLevel,
    OfferCheck,
    Requirement,
    Signal,
    SignalKind,
    SourceType,
)
from requirements_engine import challenge
from requirements_engine.challenge import ChallengeAnswer, answer_challenge

KEYS = {"answer", "supporting_evidence_ids", "counter_evidence_ids", "suggested_change"}

REQ = Requirement(
    id="REQ-1", title="Controls without looking", description="d", acceptance_criterion="90 % in 3 s",
    category=Category.INFOTAINMENT_DIGITAL, signal_ids=["SIG-1"], score=40, rank=1, score_breakdown={},
    rationale="r", evidence_level=EvidenceLevel.A, assumptions=[], uncertainties=["Older customers?"],
    offer_check=OfferCheck(status="unknown"),
)
SIGNALS = [Signal(id="SIG-1", kind=SignalKind.COMPLAINT, category=Category.INFOTAINMENT_DIGITAL, title="t",
                  summary="s", evidence_ids=[], mention_count=10, source_types=[SourceType.FEEDBACK])]


def _ev(eid: str, polarity: int) -> Evidence:
    return Evidence(id=eid, source_type=SourceType.FEEDBACK, source_name="x", derivative="G60", market="US",
                    text=f"synthetisch {eid}", polarity=polarity)


EVIDENCE = [_ev("EV-N1", -1), _ev("EV-N2", -1), _ev("EV-P1", 1)]


def _fake(monkeypatch, answer: ChallengeAnswer) -> None:
    monkeypatch.setattr(challenge, "ask_json", lambda *a, **k: answer)


def test_erfundene_ids_werden_entfernt(monkeypatch):
    _fake(monkeypatch, ChallengeAnswer(answer="a", supporting_evidence_ids=["EV-N1", "EV-ERFUNDEN"],
                                       counter_evidence_ids=["EV-P1", "EV-FALSCH"], suggested_change=None))
    result = answer_challenge(REQ, "Is this only a US issue?", SIGNALS, EVIDENCE)
    assert result["supporting_evidence_ids"] == ["EV-N1"]
    assert result["counter_evidence_ids"] == ["EV-P1"]


def test_beleg_ist_nie_zugleich_gegenbeleg(monkeypatch):
    _fake(monkeypatch, ChallengeAnswer(answer="a", supporting_evidence_ids=["EV-N1"],
                                       counter_evidence_ids=["EV-N1", "EV-P1"]))
    result = answer_challenge(REQ, "q", SIGNALS, EVIDENCE)
    assert result["counter_evidence_ids"] == ["EV-P1"]


def test_rueckgabeformat_und_vorschlag(monkeypatch):
    _fake(monkeypatch, ChallengeAnswer(answer="Mostly yes.", supporting_evidence_ids=["EV-N1"],
                                       suggested_change="Narrow the criterion to 2 seconds."))
    result = answer_challenge(REQ, "q", SIGNALS, EVIDENCE)
    assert set(result) == KEYS
    assert result["suggested_change"] == "Narrow the criterion to 2 seconds."


def test_ki_fehler_gibt_regelbasierte_antwort(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("DEMO_MODUS: kein Cache-Eintrag")

    monkeypatch.setattr(challenge, "ask_json", boom)
    result = answer_challenge(REQ, "q", SIGNALS, EVIDENCE)
    assert set(result) == KEYS and result["supporting_evidence_ids"]  # nicht leer: die API-Tests verlassen sich darauf


def test_leere_ki_antwort_wird_regelbasiert_ergaenzt(monkeypatch):
    _fake(monkeypatch, ChallengeAnswer(answer="", supporting_evidence_ids=[], counter_evidence_ids=[]))
    result = answer_challenge(REQ, "q", SIGNALS, EVIDENCE)
    assert result["answer"]


def test_prompt_enthaelt_hoechstens_30_belege_und_beide_seiten(monkeypatch):
    seen = {}

    def spy(system, user, schema, **kw):
        seen["user"] = user
        return ChallengeAnswer(answer="a")

    monkeypatch.setattr(challenge, "ask_json", spy)
    many = [_ev(f"EV-N{n:02d}", -1) for n in range(60)] + [_ev(f"EV-P{n:02d}", 1) for n in range(5)]
    answer_challenge(REQ, "q", SIGNALS, many)
    assert sum(1 for e in many if e.id in seen["user"]) == 30
    assert "EV-P00" in seen["user"]  # die wenigen Gegenstimmen dürfen nicht untergehen


def test_prompt_zaehlt_beschwerden_nie_als_gegenbeleg():
    # Echter Fund (Sa 21:30): Auf "What speaks against it?" nannte die KI 25 Beschwerden als Gegenbelege,
    # weil sie "widerspricht dem Zielwert" las. Beschwerden stützen die Anforderung; der Prompt muss das sagen.
    from requirements_engine.challenge import SYSTEM_PROMPT

    assert "Never list a complaint as counter-evidence" in SYSTEM_PROMPT
    assert "verdict" in SYSTEM_PROMPT
