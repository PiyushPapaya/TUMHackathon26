"""Baukasten (src/frontend/baukasten/): Nicht-Coder ändern dort Texte, Farben und Schalter.

Warum dieser Test: Ein vergessenes Komma oder ein falscher Schlüssel würde den Frontend-Build
brechen, und die Fehlermeldung von Next.js versteht ohne Coding-Erfahrung niemand. Hier steht
in jeder Fehlermeldung, welche Datei und was genau falsch ist.
"""

import json
import re
from pathlib import Path

import pytest

BAUKASTEN = Path(__file__).resolve().parents[1] / "src" / "frontend" / "baukasten"
TOOLS = {"duel", "arena", "assumptions", "voices", "swipe"}


def lade(name: str) -> dict:
    pfad = BAUKASTEN / name
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        pytest.fail(f"{name}, Zeile {err.lineno}: {err.msg}. Oft fehlt ein Komma oder ein Anführungszeichen.")


@pytest.mark.parametrize("name", ["features.json", "farben.json", "texte.json", "stimmen.json", "duell.json"])
def test_jede_datei_ist_gueltiges_json(name):
    assert isinstance(lade(name), dict)


def test_features_sind_an_oder_aus():
    features = lade("features.json")
    assert set(features) == TOOLS, f"features.json braucht genau diese Schalter: {sorted(TOOLS)}"
    for key, wert in features.items():
        assert isinstance(wert, bool), f'features.json: "{key}" muss true oder false sein (ohne Anführungszeichen)'


def test_farben_sind_hex_codes():
    for key, wert in lade("farben.json").items():
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", wert), f'farben.json: "{key}" = {wert} ist kein Hex-Code wie #1C69D4'
    assert {"ink", "paper", "accent", "praise", "complaint", "assumption"} <= set(lade("farben.json"))


def test_jedes_werkzeug_hat_name_kurztext_und_hilfe():
    texte = lade("texte.json")
    assert texte["workbench"]["title"].strip() and texte["workbench"]["intro"].strip()
    for tool in TOOLS:
        for feld in ("name", "short", "help"):
            assert texte["tools"][tool][feld].strip(), f"texte.json: tools.{tool}.{feld} ist leer"


def test_angepinnte_zitate_haben_beleg_id_und_notiz():
    for pick in lade("stimmen.json")["team_picks"]:
        beleg = pick["evidence_id"]
        assert re.fullmatch(r"EV-[A-Z0-9]+-\w+", beleg), f"stimmen.json: {beleg} ist keine Beleg-ID wie EV-G60-0019"
        assert pick["note"].strip(), f"stimmen.json: Notiz zu {pick['evidence_id']} fehlt"


def test_duell_hat_sinnvolle_rundenzahl():
    duell = lade("duell.json")
    assert isinstance(duell["rounds"], int) and 3 <= duell["rounds"] <= 20, "duell.json: rounds zwischen 3 und 20"
    assert duell["question"].strip()
