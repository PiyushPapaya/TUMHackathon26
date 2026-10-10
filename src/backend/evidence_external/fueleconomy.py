"""Pfad B, W-L10: EPA-Reichweite und Verbrauch der Wettbewerber von fueleconomy.gov (nur US-Szenarien).

Warum: Die Kategorie "Reichweite & Laden" braucht einen harten Vergleich. Die EPA-Werte sind amtlich,
kostenlos und ohne Key; Hersteller-Prospekte (WLTP) sind dagegen nicht mit US-Werten vergleichbar.
Grenze (ehrlich im Pitch): Es sind Prüfstandswerte, kein Alltagsverbrauch, und je Fahrzeug nur die in
der Config gewählte Ausstattung (Räder ändern die Reichweite).

Ablauf je Fahrzeug: Modelljahr + Marke + exakter Modellname -> Fahrzeug-ID -> Werte. Die Antwort liegt
in data/external_cache/fueleconomy/ und ist committet (Offline-Demo). DEMO_MODUS=true liest nur den Cache.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from core.models import Evidence, Scenario, SourceType

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "data" / "external_cache" / "fueleconomy"
API = "https://www.fueleconomy.gov/ws/rest/vehicle"
HEADERS = {"Accept": "application/json"}  # ohne diesen Header liefert die API XML


def _cache_path(folder: Path, make: str, model: str, year: int) -> Path:
    name = f"{make}_{model}_{year}.json"
    return folder / "".join(c if c.isalnum() or c in "._-" else "_" for c in name)


def _get(url: str) -> dict:
    import httpx  # erst hier: Tests und Demo brauchen kein Netz

    response = httpx.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_vehicle(make: str, model: str, year: int, cache_dir: Path | None = None) -> dict:
    """Fahrzeugdatensatz der EPA; leer, wenn unbekannt oder (Demo) nicht im Cache."""
    folder = cache_dir or CACHE_DIR
    path = _cache_path(folder, make, model, year)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if os.getenv("DEMO_MODUS", "false").lower() == "true":
        return {}
    options = _get(f"{API}/menu/options?{urlencode({'year': year, 'make': make, 'model': model})}")
    items = options.get("menuItem") or []
    if isinstance(items, dict):  # bei genau einer Variante liefert die API ein Objekt statt Liste
        items = [items]
    data = _get(f"{API}/{items[0]['value']}") if items else {}
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def _number(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _vehicle_evidence(scenario: Scenario, label: str, data: dict, number: int, now: datetime) -> Evidence | None:
    range_miles = _number(data.get("range"))
    if not range_miles:  # kein Elektroauto oder keine EPA-Reichweite: kein Beleg statt Fantasiewert
        return None
    kwh = _number(data.get("combE"))
    text = (f"EPA rated range {range_miles:.0f} miles ({range_miles * 1.609:.0f} km) for {label} "
            f"(model year {data.get('year', '')}, {data.get('model', '')})")
    if kwh:
        text += f", combined consumption {kwh:.1f} kWh/100 miles"
    return Evidence(
        id=f"EV-{scenario.id}-EPA-{number:02d}", source_type=SourceType.EXTERNAL_STAT,
        source_name="EPA fueleconomy.gov", derivative=scenario.derivative, market=scenario.market,
        text=text + ".", url=f"{API}/{data.get('id', '')}", retrieved_at=now,
        meta={"trust": "high", "publisher": "EPA", "vehicle": label, "epa_range_miles": f"{range_miles:.0f}",
              "model_year": str(data.get("year", "")), "category": "range_charging"},
    )


def collect(scenario: Scenario, cache_dir: Path | None = None) -> list[Evidence]:
    """Ein Beleg je Fahrzeug aus scenario.fueleconomy; ohne Config oder ohne Reichweite leer."""
    cfg = scenario.fueleconomy
    if not cfg:
        return []
    now = datetime.now(UTC)
    year = int(cfg.get("model_year", 2025))
    evidence = []
    for label, (make, model) in cfg.get("vehicles", {}).items():
        ev = _vehicle_evidence(scenario, label, fetch_vehicle(make, model, year, cache_dir), len(evidence) + 1, now)
        if ev:
            evidence.append(ev)
    return evidence
