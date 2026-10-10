"""A3: Absatz-Kontext. Nur erfundene Mini-Zahlen, keine BMW-Werte."""

import pandas as pd
import pytest

from evidence_internal.context import load_context, sales_context

COLUMNS = ["market", "market_code", "volume_2024", "volume_2025", "volume_2030"]


def _sales(*rows):
    return pd.DataFrame(list(rows), columns=COLUMNS)


MINI = _sales(
    ["Europe", "EU", 100, 110, 200],
    ["USA", "US", 50, 60, 100],
    ["Rest of World", "RoW", 20, 25, 100],
)


def test_anteil_ist_markt_durch_summe_aller_maerkte_2030():
    ctx = sales_context(MINI, "US")["sales"]

    assert ctx["market"] == "US"
    assert ctx["volume_2025"] == 60
    assert ctx["volume_2030"] == 100
    assert ctx["share_of_total_2030"] == 0.25  # 100 von 400


def test_markt_code_wird_ohne_leerzeichen_gefunden():
    df = _sales(["USA", " US ", 1, 2, 3], ["Europe", "EU", 1, 2, 1])
    assert sales_context(df, "US")["sales"]["share_of_total_2030"] == 0.75


def test_unbekannter_markt_ist_ein_klarer_fehler():
    with pytest.raises(ValueError, match="CN"):
        sales_context(MINI, "CN")


def test_markt_ohne_absatz_im_modell_gibt_anteil_null():
    # Beispiel F70: in den USA wird das Modell nicht verkauft
    df = _sales(["Europe", "EU", 10, 10, 90], ["USA", "US", 0, 0, 0])
    ctx = sales_context(df, "US")["sales"]
    assert ctx["volume_2030"] == 0
    assert ctx["share_of_total_2030"] == 0.0


def test_summe_null_teilt_nicht_durch_null():
    df = _sales(["Europe", "EU", 0, 0, 0], ["USA", "US", 0, 0, 0])
    assert sales_context(df, "US")["sales"]["share_of_total_2030"] == 0.0


def test_zahlen_sind_normale_python_typen_fuer_json():
    ctx = sales_context(MINI, "US")["sales"]
    assert type(ctx["volume_2025"]) is int
    assert type(ctx["volume_2030"]) is int
    assert type(ctx["share_of_total_2030"]) is float


def test_load_context_liest_blatt_und_marktcode_aus_der_config(tmp_path):
    path = tmp_path / "sales_volumes.xlsx"
    with pd.ExcelWriter(path) as writer:
        MINI.to_excel(writer, sheet_name="G60_G68", index=False)
        _sales(["USA", "US", 1, 1, 1]).to_excel(writer, sheet_name="OTHER", index=False)
    # wie die echten Configs: kein "sales_file"-Feld, der Dateiname ist fest
    cfg = {"data": {"sales_sheet": "G60_G68", "sales_market_code": "US"}}

    assert load_context(cfg, tmp_path)["sales"]["share_of_total_2030"] == 0.25
