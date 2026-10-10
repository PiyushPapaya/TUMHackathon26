"""Pfad A: Absatz-Kontext für die Priorisierung (Faktor "reach").

Vertrag (nicht ändern ohne Lead):
    load_context(cfg: dict, raw_dir: Path) -> dict
    {"sales": {"market": "US", "volume_2025": 78000, "volume_2030": 80000, "share_of_total_2030": 0.253}}

Warum: Ein Befund aus einem Markt mit großem Volumen 2030 betrifft mehr künftige Kunden.
Die Optionsliste liest Pfad C selbst (requirements_engine/offer_check.py).

Warum ohne LLM: Das sind vier Zahlen aus einer Tabelle, Python rechnet sie exakt und reproduzierbar.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

SALES_FILE = "sales_volumes.xlsx"  # die Configs haben kein "sales_file"-Feld (Config gehört dem Lead)


def sales_context(df: pd.DataFrame, market_code: str) -> dict:
    """Rein und ohne Datei testbar: Absatzblatt -> Kontext für den gewählten Markt."""
    codes = df["market_code"].astype(str).str.strip()
    rows = df[codes == market_code.strip()]
    if rows.empty:
        raise ValueError(f"Markt '{market_code}' nicht im Absatzblatt (vorhanden: {sorted(set(codes))})")
    row = rows.iloc[0]

    total_2030 = int(df["volume_2030"].sum())
    volume_2030 = int(row["volume_2030"])
    # Summe 0 (Modell wird nirgends verkauft) -> Anteil 0 statt Division durch 0
    share = round(volume_2030 / total_2030, 3) if total_2030 else 0.0
    return {
        "sales": {
            "market": market_code.strip(),
            "volume_2025": int(row["volume_2025"]),
            "volume_2030": volume_2030,
            "share_of_total_2030": share,
        }
    }


def load_context(cfg: dict, raw_dir: Path) -> dict:
    """Liest Blatt cfg["data"]["sales_sheet"] und wählt die Zeile cfg["data"]["sales_market_code"].

    share_of_total_2030 = Volumen des Markts / Summe aller Märkte dieses Modells in 2030.
    """
    data = cfg["data"]
    path = Path(raw_dir) / data.get("sales_file", SALES_FILE)
    df = pd.read_excel(path, sheet_name=data["sales_sheet"])
    return sales_context(df, data["sales_market_code"])
