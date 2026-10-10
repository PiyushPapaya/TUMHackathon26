"""W-C7: Keine stillen Fehler. Und: Ein Szenario ohne Optionsliste (G68-CN, Kaltstart) läuft sauber durch.

Warum: derive.py schluckte jeden Fehler beim Lesen der Optionsliste (except Exception: return []), und der PM sah nur
"unknown" ohne Grund. Jetzt sagt die Notiz an der Anforderung, WARUM nichts geprüft wurde, und das Log nennt den
Fehler. Nur erwartbare Fehlerarten werden abgefangen (Datei fehlt, Datei kaputt); ein Programmierfehler soll auffallen.
"""

import logging

import pytest

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import challenge, derive, offer_check
from requirements_engine.drafts import RequirementDraft, RequirementDrafts

SCENARIO = Scenario(id="G68-CN", derivative="G68", model_name="5 Series LWB", market="CN", countries=["CN"],
                    competitors=[])
SIGNALS = [Signal(id="SIG-1", kind=SignalKind.COMPLAINT, category=Category.COMFORT_SPACE, title="t", summary="s",
                  evidence_ids=["EV"], mention_count=20, source_types=[SourceType.STUDY])]


@pytest.fixture(autouse=True)
def _fake_llm(monkeypatch):
    draft = RequirementDraft(title="R", description="d", acceptance_criterion="c", category=Category.COMFORT_SPACE,
                             signal_ids=["SIG-1"])
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=[draft]))


def _offer_note(context: dict) -> tuple[str, str]:
    check = derive.derive_all(SCENARIO, SIGNALS, [], context)[0][0].offer_check
    return check.status, check.note


def test_ohne_optionsliste_sagt_die_notiz_warum():
    for context in ({}, {"option_list_path": None}):  # G68-CN: option_list_file ist null in der Config
        status, note = _offer_note(context)
        assert status == "unknown" and "no option list exists for this scenario" in note.lower()


def test_fehlende_datei_wird_benannt_und_geloggt(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        status, note = _offer_note({"option_list_path": str(tmp_path / "gibt_es_nicht.PDF")})
    assert status == "unknown" and "gibt_es_nicht.PDF" in note and "not found" in note
    assert any("gibt_es_nicht.PDF" in r.message for r in caplog.records)


def test_kaputte_datei_wird_benannt_und_geloggt(tmp_path, caplog):
    broken = tmp_path / "kaputt.PDF"
    broken.write_bytes(b"das ist kein pdf")
    with caplog.at_level(logging.WARNING):
        status, note = _offer_note({"option_list_path": str(broken)})
    assert status == "unknown" and "could not be read" in note
    assert any("kaputt.PDF" in r.message for r in caplog.records)


def test_programmierfehler_werden_nicht_verschluckt(monkeypatch, tmp_path):
    pdf = tmp_path / "x.PDF"
    pdf.write_bytes(b"x")

    def boom(path):
        raise KeyError("Bug im Parser")

    monkeypatch.setattr(offer_check, "load_offer", boom)
    with pytest.raises(KeyError):
        derive.derive_all(SCENARIO, SIGNALS, [], {"option_list_path": str(pdf)})


def test_ki_ausfall_beim_optionsabgleich_wird_geloggt(monkeypatch, caplog):
    def fail(*a, **k):
        raise TimeoutError("kein Netz")

    monkeypatch.setattr(offer_check, "ask_json", fail)
    offer = [{"name": "Heated seats", "code": "4GH", "status": "optional", "contents": [], "note": ""}]
    with caplog.at_level(logging.WARNING):
        result = offer_check.check("Seat heating", offer)
    assert result.status == "unknown" and "TimeoutError" in result.note
    assert any("TimeoutError" in r.message for r in caplog.records)


def test_ki_ausfall_bei_der_challenge_wird_geloggt(monkeypatch, caplog):
    def fail(*a, **k):
        raise TimeoutError("kein Netz")

    monkeypatch.setattr(challenge, "ask_json", fail)
    from core.models import Evidence, Requirement

    req = derive.derive_all(SCENARIO, SIGNALS, [], {})[0][0]
    ev = [Evidence(id="EV", source_type=SourceType.STUDY, source_name="s", derivative="G68", market="CN", text="t")]
    assert isinstance(req, Requirement)
    with caplog.at_level(logging.WARNING):
        answer = challenge.answer_challenge(req, "Why?", SIGNALS, ev)
    assert answer["answer"]  # regelbasierte Antwort kommt weiter
    assert any("TimeoutError" in r.message for r in caplog.records)
