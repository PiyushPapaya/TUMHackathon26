"""Tests für derive_all (Ticket C2). Die KI wird durch einen Fake ersetzt: kein Netz, kein Key.

Warum ein Fake: Wir wollen prüfen, was UNSER Code mit der KI-Antwort macht (erfundene IDs
entfernen, Out-of-scope aussortieren, IDs und Rang vergeben), nicht was die KI sagt.
"""

from core.models import Category, EvidenceLevel, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all, derive_requirements

SCENARIO = Scenario(
    id="G60-US", derivative="G60", model_name="5 Series", market="US",
    countries=["US"], competitors=["Tesla"],
)


def _signal(sid: str, mentions: int, sources: list[SourceType]) -> Signal:
    return Signal(
        id=sid, kind=SignalKind.COMPLAINT, category=Category.INFOTAINMENT_DIGITAL,
        title=f"Titel {sid}", summary="Zusammenfassung", evidence_ids=["EV-1"],
        mention_count=mentions, source_types=sources,
    )


SIGNALS = [
    _signal("SIG-1", 30, [SourceType.FEEDBACK, SourceType.STUDY]),
    _signal("SIG-2", 8, [SourceType.FEEDBACK]),
]


def _draft(title: str, signal_ids: list[str], **kwargs) -> RequirementDraft:
    return RequirementDraft(
        title=title, description="Beschreibung", acceptance_criterion="in 1 Handgriff",
        category=Category.INFOTAINMENT_DIGITAL, signal_ids=signal_ids, **kwargs,
    )


def _fake_llm(monkeypatch, drafts: list[RequirementDraft]) -> None:
    monkeypatch.setattr(derive, "ask_json", lambda system, user, schema, **kw: RequirementDrafts(drafts=drafts))


def test_erfundene_signal_id_fliegt_raus(monkeypatch):
    _fake_llm(monkeypatch, [_draft("Volume without looking", ["SIG-1", "SIG-ERFUNDEN"])])
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {})
    assert reqs[0].signal_ids == ["SIG-1"]


def test_entwurf_ohne_gueltigen_befund_wird_verworfen(monkeypatch):
    _fake_llm(monkeypatch, [_draft("Nur erfunden", ["SIG-ERFUNDEN"]), _draft("Echt", ["SIG-2"])])
    reqs, discarded = derive_all(SCENARIO, SIGNALS, [], {})
    assert [r.title for r in reqs] == ["Echt"]
    assert discarded == []  # kein Scope-Problem, nur halluziniert


def test_out_of_scope_landet_im_zweiten_rueckgabewert(monkeypatch):
    out = _draft("Homologation", ["SIG-1"], in_scope=False, scope_reason="regulatory")
    _fake_llm(monkeypatch, [out, _draft("Im Scope", ["SIG-1"])])
    reqs, discarded = derive_all(SCENARIO, SIGNALS, [], {})
    assert [r.title for r in reqs] == ["Im Scope"]
    assert discarded[0]["title"] == "Homologation"
    assert discarded[0]["reason"] == "regulatory"


def test_ids_rang_und_evidenzstufe(monkeypatch):
    _fake_llm(monkeypatch, [_draft("Schwach", ["SIG-2"]), _draft("Stark", ["SIG-1"])])
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {})
    assert [r.id for r in reqs] == ["REQ-G60-US-002", "REQ-G60-US-001"]  # ID nach KI-Reihenfolge
    assert [r.rank for r in reqs] == [1, 2]                              # Rang nach Score
    assert reqs[0].title == "Stark" and reqs[0].evidence_level == EvidenceLevel.A
    assert reqs[0].score > reqs[1].score
    assert all(r.status == "proposed" for r in reqs)


def test_ungueltiger_aufwand_wird_mittel(monkeypatch):
    _fake_llm(monkeypatch, [_draft("X", ["SIG-1"], effort="XXL")])
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {})
    assert reqs[0].effort == "M"


def test_derive_requirements_gibt_nur_die_liste_zurueck(monkeypatch):
    _fake_llm(monkeypatch, [_draft("X", ["SIG-1"])])
    assert [r.title for r in derive_requirements(SCENARIO, SIGNALS, [], {})] == ["X"]


def test_optionsliste_wird_pro_anforderung_abgeglichen(monkeypatch, tmp_path):
    from core.models import OfferCheck

    pdf = tmp_path / "liste.pdf"
    pdf.write_bytes(b"%PDF")  # Inhalt egal: load_offer ist ersetzt, nur der Pfad muss existieren
    _fake_llm(monkeypatch, [_draft("Hands-free tailgate", ["SIG-1"])])
    monkeypatch.setattr(derive, "load_offer", lambda path: [{"name": "TRAVEL PAKET", "code": "7LK"}])
    monkeypatch.setattr(derive, "check", lambda title, offer: OfferCheck(status="optional", option_code="7LK"))
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {"option_list_path": str(pdf)})
    assert (reqs[0].offer_check.status, reqs[0].offer_check.option_code) == ("optional", "7LK")


def test_ohne_optionsliste_bleibt_unknown_und_nichts_stuerzt_ab(monkeypatch, tmp_path):
    _fake_llm(monkeypatch, [_draft("X", ["SIG-1"])])
    for context in ({}, {"option_list_path": str(tmp_path / "gibt-es-nicht.pdf")}):
        reqs, _ = derive_all(SCENARIO, SIGNALS, [], context)
        assert reqs[0].offer_check.status == "unknown"


def test_kaputte_optionsliste_stoppt_die_pipeline_nicht(monkeypatch, tmp_path):
    pdf = tmp_path / "kaputt.pdf"
    pdf.write_bytes(b"kein pdf")
    _fake_llm(monkeypatch, [_draft("X", ["SIG-1"])])

    def boom(path):
        raise ValueError("kein PDF")

    monkeypatch.setattr(derive, "load_offer", boom)
    reqs, _ = derive_all(SCENARIO, SIGNALS, [], {"option_list_path": str(pdf)})
    assert reqs[0].offer_check.status == "unknown"
