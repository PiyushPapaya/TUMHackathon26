"""Datensatz-Profil laden (Owner: Lead).

Warum: Spalten- und Blattnamen der BMW-Dateien stehen in config/datasets.json statt im Code.
Kommt ein neuer Datensatz mit anderen Namen, ändert man nur die JSON (Pfad A liest das Profil).
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[3] / "config" / "datasets.json"


@cache
def load_profile(path: Path = PROFILE_PATH) -> dict:
    """Profil als Dict; Schlüssel mit "_" sind Kommentare für Menschen und fallen weg."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}
