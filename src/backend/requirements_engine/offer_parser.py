"""Parser für die Optionsliste (Preisliste-PDF), reiner Code ohne KI (Owner: Pfad C, Ticket C5).

Warum Code und nicht KI: Das PDF hat eine feste Struktur, ein Parser ist reproduzierbar und
kostet nichts. Die KI kommt erst beim Abgleich (offer_check.py), und nur gegen diese Liste.

Aufbau des PDF-Textes (pymupdf liefert ihn zeilenweise, geprüft am 10.10.):
- Sonderausstattung: Name, (Hinweiszeile), Code, Preis, dann je ein Symbol pro Modellvariante
  (■ = Serie, □ = Sonderausstattung), bei Paketen danach die Inhalte als "– ...".
- Serienausstattung (Übersichtsseiten): Namen ohne Code.
"""

from __future__ import annotations

import re

CODE = re.compile(r"^(?=[0-9A-Z]*\d)[0-9A-Z]{3}$")  # z. B. 7EW, 4MA, 320
PRICE = re.compile(r"^(\d{1,3}(\.\d{3})*,–|–,–|\[[\d.,]+\])$")
MODEL = re.compile(r"^(i\d\b.*|\d{3}[a-z]( xDrive)?)$")  # Spaltenköpfe wie "530e", "i5 eDrive40"
NOTE_START = ("Im Umfang", "Nur in", "Ausstattungsalternative", "Mit ", "Nicht ", "Auch ", "(")
SYMBOLS = {"■", "□"}


def _clean(lines: list[str]) -> list[str]:
    out = [line.replace(" ", " ").replace(" ", " ").strip() for line in lines]
    return [line for line in out if line and not MODEL.match(line)]


def _is_note(line: str) -> bool:
    return line.startswith(NOTE_START)


def _is_name(line: str) -> bool:
    """Ein Name ist kurz und beginnt groß; Fußnoten-Sätze (klein, mit Punkt, mit Link) sind keiner."""
    return (len(line) <= 90 and not line.endswith(".") and not line[0].islower()
            and not re.match(r"^\d+\t", line) and "www." not in line and "Tel." not in line)


def _status(symbols: list[str], note: str) -> tuple[str, str]:
    if "□" in symbols:
        extra = " standard on some variants" if "■" in symbols else ""
        return "optional", (note + extra).strip()
    return ("standard" if "■" in symbols else "unknown"), note


def parse_option_lines(raw_lines: list[str]) -> list[dict]:
    """Optionen mit Code (Sonderausstattung und Pakete) aus den Textzeilen einer Seite."""
    lines = _clean(raw_lines)
    options: list[dict] = []
    buffer: list[str] = []
    current: dict | None = None
    collecting = False  # True, solange hinter einem Code noch Symbole erwartet werden
    orphan_codes = False  # Farblisten: erst Namen, dann Codes als Spalte; die Zuordnung wäre geraten
    for i, line in enumerate(lines):
        if CODE.match(line) and i + 1 < len(lines) and PRICE.match(lines[i + 1]):
            if orphan_codes:  # letzter Code einer Spalte: überspringen statt falsche Paare erzeugen
                orphan_codes, current, buffer, collecting = False, None, [], False
                continue
            names = [b for b in buffer if not _is_note(b) and _is_name(b)]
            notes = [b for b in buffer if _is_note(b)]
            current = {"name": names[-1] if names else f"Option {line}", "code": line, "contents": [],
                       "note": " ".join(notes), "_symbols": []}
            options.append(current)
            buffer, collecting = [], True
        elif CODE.match(line):  # Code ohne Preis dahinter
            orphan_codes, buffer, collecting = True, [], False
        elif line in SYMBOLS:
            if collecting and current is not None:
                current["_symbols"].append(line)
        elif PRICE.match(line):
            continue
        elif line.startswith("–") and current is not None:  # Paketinhalt "– Sitzheizung"
            current["contents"].append(line.lstrip("–").strip())
            collecting = False
        else:
            collecting = False
            buffer.append(line)
    for option in options:
        option["status"], option["note"] = _status(option.pop("_symbols"), option["note"])
    return options


def parse_series_lines(raw_lines: list[str]) -> list[dict]:
    """Serienausstattung ohne Code: jede Namenszeile gilt als Serie (Überschriften in Großbuchstaben nicht)."""
    items, seen = [], set()
    for line in _clean(raw_lines):
        if line in SYMBOLS or PRICE.match(line) or line.isupper():
            continue
        name = line.lstrip("–").strip()
        if name and _is_name(name) and name not in seen:
            seen.add(name)
            items.append({"name": name, "code": "", "status": "standard", "contents": [], "note": ""})
    return items
