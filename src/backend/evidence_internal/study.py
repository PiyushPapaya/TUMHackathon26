"""Pfad A, A2: Kundenstudie-Excel -> Belege (Evidence). Ohne LLM.

Warum ohne LLM: Die Zahlen stehen schon fest in der Tabelle. Rechnen und Formatieren
in Python ist reproduzierbar, ein Modell würde sich bei Prozentwerten verrechnen.

Warum ein Satz pro Attribut: Die Oberfläche zeigt alle Belege gleich, und der PM soll
"14 % unzufrieden" lesen können, ohne die Excel zu öffnen. Die Rohwerte stehen zusätzlich in meta.

Zwei Formate (Blatt ohne Kopfzeile lesen, header=None):
- US_2025: je Attribut ein Block (Attributzeile, "Sample total", 7 Stufen von "I Hate It" bis "I Love It").
- CN_EU_2025: je Attribut eine Attributzeile gefolgt von einer "Mean"-Zeile, Spalten = Modell je Land.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.models import Evidence, SourceType

NEGATIVE_LEVELS = ("I Hate It", "A Failure", "Unsatisfactory")
TOP2_LEVELS = ("Delightful", "I Love It")
ALL_LEVELS = (*NEGATIVE_LEVELS, "Satisfactory", "Excellent", *TOP2_LEVELS)

# Schwellen aus dem Ticket A2 (docs/pfade/PFAD-A.md).
US_NEGATIVE_FROM = 0.10  # ab 10 % Unzufriedenen ist das Attribut ein Problem
US_POSITIVE_FROM = 0.60  # ab 60 % "Delightful" + "I Love It" ist es eine Stärke
MEAN_NEGATIVE_BELOW = 7.5
MEAN_POSITIVE_FROM = 9.0

# Welches Land die Excel in Zeile 2 nennt, wenn die Szenario-Config einen Markt-Code hat.
DATASET_COUNTRY = {"CN": "China"}


def _text(value: object) -> str:
    """NaN/None -> '', sonst getrimmter Text (Modellnamen haben Leerzeichen am Ende)."""
    return "" if pd.isna(value) else str(value).strip()


def _number(value: object) -> float | None:
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)


def _model_position(header_row: pd.Series, model_column: str, allowed: set[int] | None = None) -> int:
    """Spaltenposition des Modells in der Kopfzeile. Fehlt es, brechen wir laut ab statt still 0 Belege zu liefern."""
    wanted = model_column.strip()
    for position, value in enumerate(header_row):
        if _text(value) == wanted and (allowed is None or position in allowed):
            return position
    raise ValueError(f"Modellspalte '{wanted}' nicht in der Studie gefunden")


def _evidence(cfg: dict, number: int, text: str, polarity: int, meta: dict[str, str], study: str) -> Evidence:
    return Evidence(
        id=f"EV-{cfg['id']}-ST-{number:02d}",
        source_type=SourceType.STUDY,
        source_name=f"{study}-Studie 2025",
        derivative=cfg["derivative"],
        market=cfg["market"],
        text=text,
        polarity=polarity,
        meta=meta,
    )


def _percent(share: float) -> str:
    return f"{share * 100:.0f}"


def _us_blocks(df: pd.DataFrame, position: int) -> list[tuple[str, dict[str, float | None]]]:
    """Attribut + Anteile je Stufe. Gelesen wird nach Label, nicht nach Zeilenabstand:
    zwei Blöcke der echten Datei haben eine zusätzliche leere Zeile."""
    blocks: list[tuple[str, dict[str, float | None]]] = []
    for _, row in df.iterrows():
        label = _text(row.iloc[0])
        if not label:
            continue
        if label in ALL_LEVELS:
            blocks[-1][1][label] = _number(row.iloc[position])
        elif label != "Sample total" and _text(row.iloc[1]) == "":
            blocks.append((label, {}))  # Attributzeile: Spalte 1 ist leer, bei Stufen steht dort "% of column..."
    return blocks


def parse_us_study(df: pd.DataFrame, model_column: str, cfg: dict) -> list[Evidence]:
    """Rein und ohne Datei testbar: US-Blatt -> ein Beleg je Attribut für dieses Modell."""
    position = _model_position(df.iloc[0], model_column)
    evidence: list[Evidence] = []
    for number, (attribute, levels) in enumerate(_us_blocks(df, position), start=1):
        if any(levels.get(level) is None for level in ALL_LEVELS):
            continue  # Modell wurde zu diesem Attribut nicht befragt; die Nummer bleibt trotzdem vergeben
        # runden, weil 0.01 + 0.06 + 0.03 in Python 0.0999... ergibt, fachlich aber genau 10 % sind
        neg = round(sum(levels[level] for level in NEGATIVE_LEVELS), 4)  # type: ignore[misc]
        top2 = round(sum(levels[level] for level in TOP2_LEVELS), 4)  # type: ignore[misc]
        polarity = -1 if neg >= US_NEGATIVE_FROM else 1 if top2 >= US_POSITIVE_FROM else 0
        text = f"{attribute}: {_percent(neg)} % dissatisfied, {_percent(top2)} % top-2 (US study 2025)"
        meta = {"attribute": attribute, "neg_share": f"{neg:.2f}", "top2": f"{top2:.2f}"}
        evidence.append(_evidence(cfg, number, text, polarity, meta, "US"))
    return evidence


def _filled_right(row: pd.Series) -> list[str]:
    """Land steht nur in der ersten Spalte seiner Gruppe; nach rechts auffüllen."""
    filled, current = [], ""
    for value in row:
        current = _text(value) or current
        filled.append(current)
    return filled


def parse_cn_eu_study(df: pd.DataFrame, market: str, model_column: str, cfg: dict) -> list[Evidence]:
    """Rein und ohne Datei testbar: CN/EU-Blatt -> ein Beleg je Attribut (Mean-Zeile) für Modell und Markt."""
    country = DATASET_COUNTRY.get(market, market).lower()
    countries = _filled_right(df.iloc[1])
    in_market = {i for i, c in enumerate(countries) if c.lower() == country}
    if not in_market:
        raise ValueError(f"Markt '{market}' nicht in der Studie gefunden")
    position = _model_position(df.iloc[2], model_column, allowed=in_market)

    evidence: list[Evidence] = []
    attribute_count = 0
    for index in range(2, len(df)):
        if _text(df.iloc[index, 0]) != "Mean":
            continue
        attribute_count += 1
        attribute = _text(df.iloc[index - 1, 0])  # beim ersten Attribut ist das zugleich die Modell-Kopfzeile
        mean = _number(df.iloc[index, position])
        if mean is None:
            continue
        polarity = -1 if mean < MEAN_NEGATIVE_BELOW else 1 if mean >= MEAN_POSITIVE_FROM else 0
        text = f"{attribute}: mean {mean:.1f} ({market} study 2025)"
        meta = {"attribute": attribute, "mean": f"{mean:.2f}"}
        evidence.append(_evidence(cfg, attribute_count, text, polarity, meta, market))
    return evidence


def load_study(cfg: dict, raw_dir: Path) -> list[Evidence]:
    """Liest das Studienblatt des Szenarios (Config: study_file, study_sheet, study_column)."""
    data = cfg["data"]
    path = Path(raw_dir) / data["study_file"]
    sheet = data["study_sheet"]
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    if sheet.startswith("US"):
        return parse_us_study(df, data["study_column"], cfg)
    if sheet.startswith("CN_EU"):
        return parse_cn_eu_study(df, cfg["market"], data["study_column"], cfg)
    raise ValueError(f"Unbekanntes Studienblatt '{sheet}'")
