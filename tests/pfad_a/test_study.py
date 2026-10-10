"""A2: Studien-Tabellen -> Belege. Nur synthetische Mini-Daten, keine BMW-Werte."""

import numpy as np
import pandas as pd
import pytest

from evidence_internal import loaders
from evidence_internal.study import load_study, parse_cn_eu_study, parse_us_study

CFG_G60 = {"id": "G60-US", "derivative": "G60", "market": "US", "countries": ["US"]}
CFG_G70 = {"id": "G70-US", "derivative": "G70", "market": "US", "countries": ["US"]}
CFG_F70 = {"id": "F70-EU", "derivative": "F70", "market": "EU", "countries": ["DE"]}

LEVELS = ["I Hate It", "A Failure", "Unsatisfactory", "Satisfactory", "Excellent", "Delightful", "I Love It"]
NAN = np.nan


def _us_df(*blocks, extra_blank_in=()):
    """blocks = (Attribut, 7 Werte G60, 7 Werte G70). Kopfzeile = Zeile des ersten Attributs, wie im Original."""
    rows = []
    for number, (name, g60, g70) in enumerate(blocks):
        if number == 0:
            rows.append([name, NAN, "BMW 5 Series G60", "BMW 7 Series G70 "])  # Leerzeichen am Ende wie im Original
        else:
            rows.append([name, NAN, NAN, NAN])
        rows.append(["Sample total", "% of column, sample base", 1, 1])
        if name in extra_blank_in:  # zwei Blöcke der echten Datei haben hier eine leere Zeile
            rows.append([NAN, NAN, NAN, NAN])
        for level, a, b in zip(LEVELS, g60, g70, strict=True):
            rows.append([level, "% of column, sample base", a, b])
    return pd.DataFrame(rows)


def _values(neg=(0.05, 0.04, 0.05), top2=(0.2, 0.26)):
    middle = (0.2, 0.2)
    return [*neg, *middle[:1], *middle[1:], *top2]


def test_us_beleg_hat_satz_kennzahlen_und_stabile_id():
    df = _us_df(("Rear roominess", _values(), _values()))
    [ev] = parse_us_study(df, "BMW 5 Series G60", CFG_G60)

    assert ev.id == "EV-G60-US-ST-01"
    assert ev.source_type == "study"
    assert ev.text == "Rear roominess: 14 % dissatisfied, 46 % top-2 (US study 2025)"
    assert ev.meta["attribute"] == "Rear roominess"
    assert ev.meta["neg_share"] == "0.14"
    assert ev.meta["top2"] == "0.46"
    assert ev.polarity == -1
    assert (ev.derivative, ev.market) == ("G60", "US")


def test_modellspalte_wird_ohne_leerzeichen_am_ende_gefunden():
    df = _us_df(("Rear roominess", _values(neg=(0.0, 0.0, 0.0)), _values(neg=(0.1, 0.1, 0.1))))
    [ev] = parse_us_study(df, "BMW 7 Series G70", CFG_G70)  # in der Datei: "BMW 7 Series G70 "
    assert ev.meta["neg_share"] == "0.30"


def test_unbekannte_modellspalte_ist_ein_klarer_fehler():
    df = _us_df(("Rear roominess", _values(), _values()))
    with pytest.raises(ValueError, match="BMW 3 Series"):
        parse_us_study(df, "BMW 3 Series", CFG_G60)


def test_schwelle_zehn_prozent_haelt_gegen_gleitkomma_rundung():
    # 0.01 + 0.06 + 0.03 ergibt in Python 0.0999..., fachlich sind es genau 10 %.
    neg = (0.01, 0.06, 0.03)
    assert sum(neg) < 0.10
    df = _us_df(("Edge", _values(neg=neg), _values()))
    [ev] = parse_us_study(df, "BMW 5 Series G60", CFG_G60)
    assert ev.polarity == -1


def test_polaritaet_positiv_bei_top2_ab_60_prozent_sonst_neutral():
    df = _us_df(
        ("Loved", _values(neg=(0.01, 0.01, 0.01), top2=(0.3, 0.35)), _values()),
        ("Meh", _values(neg=(0.02, 0.02, 0.02), top2=(0.2, 0.2)), _values()),
    )
    loved, meh = parse_us_study(df, "BMW 5 Series G60", CFG_G60)
    assert loved.polarity == 1
    assert meh.polarity == 0


def test_blocktrenner_wird_ueber_labels_gelesen_nicht_ueber_feste_zeilenzahl():
    df = _us_df(
        ("First", _values(neg=(0.01, 0.01, 0.01)), _values()),
        ("Shifted", _values(neg=(0.1, 0.1, 0.1)), _values()),
        ("Last", _values(neg=(0.02, 0.02, 0.02)), _values()),
        extra_blank_in=("Shifted",),
    )
    first, shifted, last = parse_us_study(df, "BMW 5 Series G60", CFG_G60)
    assert shifted.meta["neg_share"] == "0.30"
    assert last.meta["attribute"] == "Last"
    assert last.meta["neg_share"] == "0.06"


def test_attribut_ohne_wert_fuer_das_modell_faellt_weg_ids_bleiben_stabil():
    gap = [NAN] * 7
    df = _us_df(("A", _values(), _values()), ("B", gap, _values()), ("C", _values(), _values()))
    evidence = parse_us_study(df, "BMW 5 Series G60", CFG_G60)
    assert [e.meta["attribute"] for e in evidence] == ["A", "C"]
    # Die Nummer ist die Blockposition, damit ST-03 bei jedem Modell dasselbe Attribut meint.
    assert [e.id for e in evidence] == ["EV-G60-US-ST-01", "EV-G60-US-ST-03"]


def _cn_eu_df():
    return pd.DataFrame([
        [NAN, "Dataset country", NAN, NAN, NAN, NAN],
        [NAN, "China", NAN, "EU", NAN, NAN],  # Land nur in der ersten Spalte der Gruppe
        ["Overall product satisfaction", "BMW 5 Series G68", "BMW 7 Series G70", "BMW 1 Series F70",
         "BMW 5 Series G60", "BMW 7 Series G70"],
        ["Mean", 8.1, 8.2, 8.46, 8.4, 8.5],
        ["Exterior styling", NAN, NAN, NAN, NAN, NAN],
        ["Mean", 7.0, 7.1, 9.0, 9.5, 7.2],
        ["Level of equipment", NAN, NAN, NAN, NAN, NAN],
        ["Mean", 6.0, 6.1, 7.4, 7.0, 7.45],
    ])  # fmt: skip


def test_cn_eu_liest_die_spalte_des_modells_im_richtigen_land():
    evidence = parse_cn_eu_study(_cn_eu_df(), "EU", "BMW 1 Series F70", CFG_F70)

    assert [e.id for e in evidence] == ["EV-F70-EU-ST-01", "EV-F70-EU-ST-02", "EV-F70-EU-ST-03"]
    assert evidence[0].meta == {"attribute": "Overall product satisfaction", "mean": "8.46"}
    assert evidence[0].text == "Overall product satisfaction: mean 8.5 (EU study 2025)"
    # Schwellen: < 7,5 negativ, >= 9,0 positiv, dazwischen neutral
    assert [e.polarity for e in evidence] == [0, 1, -1]


def test_cn_eu_gleiches_modell_in_zwei_laendern_waehlt_das_land_nicht_die_erste_spalte():
    cfg = {**CFG_G70, "market": "EU"}
    eu = parse_cn_eu_study(_cn_eu_df(), "EU", "BMW 7 Series G70", cfg)
    china = parse_cn_eu_study(_cn_eu_df(), "China", "BMW 7 Series G70", cfg)
    assert eu[0].meta["mean"] == "8.50"  # Spalte 5, nicht Spalte 2
    assert china[0].meta["mean"] == "8.20"


def test_load_study_liest_blatt_ohne_kopfzeile_aus_der_excel(tmp_path):
    path = tmp_path / "studies.xlsx"
    with pd.ExcelWriter(path) as writer:
        _us_df(("Rear roominess", _values(), _values())).to_excel(
            writer, sheet_name="US_2025", header=False, index=False
        )
        _cn_eu_df().to_excel(writer, sheet_name="CN_EU_2025", header=False, index=False)

    us_cfg = {**CFG_G60, "data": {"study_file": "studies.xlsx", "study_sheet": "US_2025",
                                  "study_column": "BMW 5 Series G60"}}  # fmt: skip
    eu_cfg = {**CFG_F70, "data": {"study_file": "studies.xlsx", "study_sheet": "CN_EU_2025",
                                  "study_column": "BMW 1 Series F70"}}  # fmt: skip

    assert [e.id for e in load_study(us_cfg, tmp_path)] == ["EV-G60-US-ST-01"]
    assert len(load_study(eu_cfg, tmp_path)) == 3


def test_load_all_evidence_haengt_studie_an_das_feedback(monkeypatch):
    sentinel_fb, sentinel_st = ["fb"], ["st"]
    monkeypatch.setattr(loaders, "load_feedback", lambda cfg, raw_dir: sentinel_fb)
    monkeypatch.setattr(loaders, "load_study", lambda cfg, raw_dir: sentinel_st)
    assert loaders.load_all_evidence({}, None) == ["fb", "st"]
