"""A1: Feedback-Zeilen -> Belege. Nur synthetische Mini-Daten, keine BMW-Texte."""

import pandas as pd

from evidence_internal.feedback import feedback_to_evidence

CFG = {"id": "G60-US", "derivative": "G60", "market": "US", "countries": ["US"]}

COLUMNS = [
    "ID", "Source", "Brand", "Sales Description", "Country", "Derivate (e-code)", "Engine Type",
    "Feedback Type", "Customer Feedback", "Vfc level2 3 Name", "Vfc level2 Name", "Vfc level3 Name",
]  # fmt: skip


def _row(id_, *, feedback_type="Likes", text="Synthetic comment", vfc2="Seats", vfc3="Comfort",
         source="Source A", country="US", engine="ICE"):  # fmt: skip
    return [id_, source, "BMW", "Test", country, "G60", engine, feedback_type, text, f"{vfc2} {vfc3}", vfc2, vfc3]


def _df(*rows):
    return pd.DataFrame(list(rows), columns=COLUMNS)


def test_gleiche_id_wird_ein_beleg_mit_allen_labels():
    df = _df(
        _row(101, feedback_type="Likes", vfc2="Seats"),
        _row(101, feedback_type="Wants", vfc2="Touch screen"),
        _row(101, feedback_type="Defect", vfc2="Seats"),
    )
    evidence = feedback_to_evidence(df, CFG)

    assert len(evidence) == 1
    ev = evidence[0]
    assert ev.id == "EV-G60-US-FB-101"
    assert ev.source_type == "feedback"
    assert ev.meta["labels"] == "Seats/Likes | Touch screen/Wants | Seats/Defect"
    assert ev.meta["vfc2"] == "Seats | Touch screen"
    assert ev.meta["feedback_type"] == "Likes | Wants | Defect"


def test_fremdes_land_fliegt_raus_auch_mit_leerzeichen():
    df = _df(_row(1, country="US"), _row(2, country=" US "), _row(3, country="DE"))
    ids = [e.id for e in feedback_to_evidence(df, CFG)]
    assert ids == ["EV-G60-US-FB-1", "EV-G60-US-FB-2"]


def test_leerer_feedback_typ_ist_neutral():
    df = _df(_row(5, feedback_type=None))
    ev = feedback_to_evidence(df, CFG)[0]
    assert ev.polarity == 0
    assert ev.meta["feedback_type"] == ""


def test_polaritaet_nach_vorzeichen_der_summe():
    positiv = _df(_row(1, feedback_type="Likes"), _row(1, feedback_type="Likes"), _row(1, feedback_type="Wants"))
    negativ = _df(_row(2, feedback_type="Likes"), _row(2, feedback_type="Defect"), _row(2, feedback_type="Wants"))
    gleich = _df(_row(3, feedback_type="Likes"), _row(3, feedback_type="Defect"))
    assert feedback_to_evidence(positiv, CFG)[0].polarity == 1
    assert feedback_to_evidence(negativ, CFG)[0].polarity == -1
    assert feedback_to_evidence(gleich, CFG)[0].polarity == 0


def test_nur_defects_aus_quelle_b_sind_out_of_scope():
    df = _df(
        _row(1, feedback_type="Defect", source="Source B"),  # Werkstattfall -> out
        _row(2, feedback_type="Defect", source="Source A"),  # Online-Bewertung -> in
        _row(3, feedback_type="Defect", source="Source B"),
        _row(3, feedback_type="Wants", source="Source B"),  # nicht alle Labels Defect -> in
    )
    scopes = {e.id: e.meta["scope"] for e in feedback_to_evidence(df, CFG)}
    assert scopes == {"EV-G60-US-FB-1": "out", "EV-G60-US-FB-2": "in", "EV-G60-US-FB-3": "in"}


def test_text_unveraendert_nur_strip_und_quelle_als_buchstabe():
    df = _df(_row(7, text="  Hello,   World!\n", source="Source C"))
    ev = feedback_to_evidence(df, CFG)[0]
    assert ev.text == "Hello,   World!"  # innere Leerzeichen bleiben, damit Zitate wörtlich prüfbar sind
    assert ev.meta["source"] == "C"
    assert ev.meta["engine"] == "ICE"
    assert ev.market == "US"
    assert ev.derivative == "G60"


def test_zeile_ohne_text_wird_uebersprungen():
    df = _df(_row(1, text=None), _row(2, text="   "), _row(3, text="ok"))
    assert [e.id for e in feedback_to_evidence(df, CFG)] == ["EV-G60-US-FB-3"]
