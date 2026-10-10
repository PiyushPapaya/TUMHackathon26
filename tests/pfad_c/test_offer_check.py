"""Abgleich Anforderung gegen Optionsliste (Ticket C5), mit Fake-KI. Synthetische Optionen, kein BMW-Text.

Sicherheitsregeln, die wir hier festnageln:
- Die KI muss eine Nummer (option_id) aus der Liste nennen, erfundene Nummern führen zu "unknown".
- Der Status (standard/optional) kommt aus dem Parser, nicht aus der KI: Sie darf ihn nicht umdeuten.
- Fällt die KI aus (kein Netz, Demo-Cache-Fehlschlag), bleibt "unknown", es stürzt nichts ab.
"""

from requirements_engine import offer_check
from requirements_engine.offer_check import OfferAnswer, check, load_offer

OFFER = [
    {"name": "TRAVEL PAKET", "code": "7LK", "status": "optional", "contents": ["Automatische Heckklappe"],
     "note": ""},
    {"name": "Launch Control", "code": "", "status": "standard", "contents": [], "note": ""},
]


def _fake(monkeypatch, answer: OfferAnswer) -> None:
    monkeypatch.setattr(offer_check, "ask_json", lambda *a, **k: answer)


def test_treffer_liefert_code_und_status_aus_dem_parser(monkeypatch):
    _fake(monkeypatch, OfferAnswer(status="standard", option_id="O1", note="tailgate is in the package"))
    result = check("Hands-free tailgate", OFFER)
    assert (result.status, result.option_code) == ("optional", "7LK")  # Parser sagt optional, nicht die KI
    assert "TRAVEL PAKET" in result.note


def test_serienausstattung_hat_keinen_code(monkeypatch):
    _fake(monkeypatch, OfferAnswer(status="standard", option_id="O2"))
    result = check("Launch control", OFFER)
    assert (result.status, result.option_code) == ("standard", None)


def test_erfundene_nummer_wird_unknown(monkeypatch):
    _fake(monkeypatch, OfferAnswer(status="optional", option_id="O99"))
    assert check("Irgendwas", OFFER).status == "unknown"


def test_nicht_im_angebot(monkeypatch):
    _fake(monkeypatch, OfferAnswer(status="not_offered", note="nothing like it"))
    result = check("Frunk", OFFER)
    assert (result.status, result.option_code) == ("not_offered", None)


def test_ki_fehler_wird_unknown(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("DEMO_MODUS: kein Cache-Eintrag")

    monkeypatch.setattr(offer_check, "ask_json", boom)
    result = check("X", OFFER)
    assert result.status == "unknown" and "RuntimeError" in result.note


def test_leere_liste_fragt_die_ki_nicht(monkeypatch):
    monkeypatch.setattr(offer_check, "ask_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("kein Aufruf")))
    assert check("X", []).status == "unknown"


def test_load_offer_nimmt_optionsseiten_und_serienseiten(monkeypatch, tmp_path):
    pages = [
        ["AUSGEWÄHLTE SERIENAUSSTATTUNGEN.", "Launch Control", "■"],
        ["COMFORT PAKET", "7VB", "2.750,–", "□"],
    ]
    monkeypatch.setattr(offer_check, "_page_lines", lambda path: pages)
    offer = load_offer(tmp_path / "x.pdf")
    assert {(o["name"], o["code"], o["status"]) for o in offer} == {
        ("Launch Control", "", "standard"), ("COMFORT PAKET", "7VB", "optional"),
    }


def test_ki_nennt_den_code_statt_der_nummer(monkeypatch):
    # Echter Fund: Die KI antwortete "7LK" statt "O1". Ein Code, der in der Liste steht, ist genauso gültig.
    _fake(monkeypatch, OfferAnswer(status="optional", option_id="7LK", note="package contains it"))
    result = check("Hands-free tailgate", OFFER)
    assert (result.status, result.option_code) == ("optional", "7LK")


def test_erfundener_code_wird_unknown(monkeypatch):
    _fake(monkeypatch, OfferAnswer(status="optional", option_id="ZZZ"))
    assert check("Irgendwas", OFFER).status == "unknown"
