"""Parser der Optionsliste (Ticket C5). Nur synthetische Zeilen: keine echten BMW-Texte im Repo.

Das PDF liefert Text zeilenweise: erst Name, dann Code, Preis und je ein Symbol pro Modellvariante
(■ = Serie, □ = Sonderausstattung), danach bei Paketen die Inhalte als "– ...".
"""

from requirements_engine.offer_parser import parse_option_lines, parse_series_lines

OPTION_PAGE = [
    "COMFORT PAKET", "7VB", "2.750,–", "[2.310,92]", "□", "□", "□", "\t",
    "– Sitzheizung vorn und hinten", "\t", "– Klimaautomatik",
    "EXTERIEUR", "Entfall, Modellschriftzug", "320", "–,–", "■", "■",
    "Beispiel Exterieurpaket", "Im Umfang Testpaket enthalten", "3DP", "550,–", "□", "■", "□",
]


def test_paket_mit_inhalten_wird_option():
    options = parse_option_lines(OPTION_PAGE)
    paket = options[0]
    assert (paket["code"], paket["name"], paket["status"]) == ("7VB", "COMFORT PAKET", "optional")
    assert paket["contents"] == ["Sitzheizung vorn und hinten", "Klimaautomatik"]


def test_ueberschrift_wird_nicht_zum_namen():
    names = [o["name"] for o in parse_option_lines(OPTION_PAGE)]
    assert "Entfall, Modellschriftzug" in names and "EXTERIEUR" not in names


def test_nur_serien_symbole_sind_standard():
    by_code = {o["code"]: o for o in parse_option_lines(OPTION_PAGE)}
    assert by_code["320"]["status"] == "standard"


def test_gemischte_symbole_sind_optional_mit_hinweis():
    by_code = {o["code"]: o for o in parse_option_lines(OPTION_PAGE)}
    assert by_code["3DP"]["status"] == "optional"
    assert by_code["3DP"]["name"] == "Beispiel Exterieurpaket"  # Hinweiszeile ist nicht der Name
    assert "standard on some variants" in by_code["3DP"]["note"]


def test_serienseite_ohne_codes():
    lines = ["AUSGEWÄHLTE SERIENAUSSTATTUNGEN.", "i5 eDrive40", "530e", "520d xDrive", "Launch Control", "■", "■",
             "Sportbremse", "–,–", "1.150,–"]
    items = parse_series_lines(lines)
    assert [i["name"] for i in items] == ["Launch Control", "Sportbremse"]
    assert all(i["status"] == "standard" and i["code"] == "" for i in items)


def test_farbliste_mit_getrennten_spalten_wird_uebersprungen():
    # Namen stehen als Spalte, die Codes folgen als Spalte: die Zuordnung wäre geraten.
    lines = ["Farbe Eins", "Farbe Zwei", "475", "A90", "C1M", "1.120,–", "[941,18]", "□", "□",
             "SITZHEIZUNG PAKET", "7VB", "2.750,–", "□"]
    codes = [o["code"] for o in parse_option_lines(lines)]
    assert codes == ["7VB"]


def test_fussnotensaetze_werden_nie_zum_namen():
    lines = ["Der Assistent ist nur in Verbindung mit Diensten verfügbar.", "sels mit Blickbestätigung ist nutzbar.",
             "Nur in Verbindung mit Paket X", "5AX", "850,–", "[714,29]", "□"]
    option = parse_option_lines(lines)[0]
    assert option["code"] == "5AX" and option["name"] == "Option 5AX"


def test_fussnoten_auf_serienseiten_werden_ignoriert():
    lines = ["Launch Control", "5\t Informationen zu den Diensten finden Sie online.", "www.beispiel.de/seite"]
    assert [i["name"] for i in parse_series_lines(lines)] == ["Launch Control"]
