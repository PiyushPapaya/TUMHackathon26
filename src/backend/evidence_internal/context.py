"""Pfad A: Absatz-Kontext für die Priorisierung (Faktor "reach").

Vertrag (nicht ändern ohne Lead):
    load_context(cfg: dict, raw_dir: Path) -> dict
    {"sales": {"market": "US", "volume_2025": 78000, "volume_2030": 80000, "share_of_total_2030": 0.24}}

Warum: Ein Befund aus einem Markt mit großem Volumen 2030 betrifft mehr künftige Kunden.
Die Optionsliste liest Pfad C selbst (requirements_engine/offer_check.py).
"""

from __future__ import annotations

from pathlib import Path


def load_context(cfg: dict, raw_dir: Path) -> dict:
    """TODO Pfad A: sales_volumes.xlsx, Blatt cfg["data"]["sales_sheet"], Zeile cfg["data"]["sales_market_code"].

    share_of_total_2030 = Volumen des Markts / Summe aller Märkte dieses Modells in 2030.
    """
    raise NotImplementedError("Pfad A: load_context noch nicht gebaut (siehe docs/pfade/PFAD-A.md)")
