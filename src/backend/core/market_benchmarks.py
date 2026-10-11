"""Benchmarks Teil 2: Wo steht das BMW-Modell gegen den Wettbewerb? Nur amtliche US-Daten (Owner: Lead).

Warum genau diese zwei Zahlen:
  - EPA-Reichweite und Verbrauch (fueleconomy.gov): Reichweite ist im BMW-Feedback ein Top-Thema, und EPA
    misst alle Hersteller gleich. Hersteller-Prospekte (WLTP) mischen Normen und sind nicht vergleichbar.
  - NHTSA-Beschwerden: unabhängige Kundenstimme, für BMW und Wettbewerber nach derselben Methode gezählt.
Verworfen: Preise und Testberichte aus dem Web. Sie ändern sich täglich und sind je Quelle anders gemessen.
Grenzen (ehrlich auf der Seite): EPA = Prüfstand, kein Alltag. NHTSA = absolute Zahlen, nicht je
verkauftem Auto; ein Modell mit mehr Absatz hat automatisch mehr Beschwerden.

Liest nur die committeten Caches in data/external_cache/ (kein Netz): die Seite lädt offline und sofort.
"""

from __future__ import annotations

import json
from pathlib import Path

from evidence_external import fueleconomy, nhtsa

MILES_TO_KM = 1.609
ROOT = Path(__file__).resolve().parents[3]


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _number(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _range_rows(cfg: dict, fuel_dir: Path) -> list[dict]:
    year = int(cfg.get("model_year", 2025))
    rows = []
    for label, (make, model) in cfg.get("vehicles", {}).items():
        data = _read(fueleconomy.cache_path(fuel_dir, make, model, year))
        miles, kwh = _number(data.get("range")), _number(data.get("combE"))
        if not miles:  # nicht im Cache oder kein E-Auto: weglassen statt schätzen
            continue
        rows.append({"name": label, "is_bmw": make == "BMW", "range_km": round(miles * MILES_TO_KM),
                     "kwh_per_100km": round(kwh / MILES_TO_KM, 1) if kwh else None})
    rows.sort(key=lambda r: -r["range_km"])
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def _complaints(make: str, models: list[str], years: list[int], nhtsa_dir: Path) -> int | None:
    """Eindeutige ODI-Nummern: dieselbe Beschwerde unter zwei Modellnamen zählt einmal (wie nhtsa.collect)."""
    paths = [nhtsa.cache_file(nhtsa_dir, make, m, y) for m in models for y in years]
    if not paths or any(not path.exists() for path in paths):
        return None
    odis = {item["odiNumber"] for path in paths for item in _read(path).get("results", [])
            if item.get("odiNumber") is not None}
    return len(odis)


def _complaint_rows(cfg: dict, bmw_name: str, nhtsa_dir: Path) -> list[dict]:
    years = cfg.get("model_years", [])
    rows = [{"name": bmw_name, "is_bmw": True,
             "complaints": _complaints("BMW", cfg.get("bmw_models", []), years, nhtsa_dir)}]
    for rival, (make, models) in cfg.get("competitors", {}).items():
        rows.append({"name": rival, "is_bmw": False, "complaints": _complaints(make, models, years, nhtsa_dir)})
    return sorted((r for r in rows if r["complaints"] is not None), key=lambda r: r["complaints"])


def _sentence(rows: list[dict], gap: int | None) -> str:
    bmw = next((r for r in rows if r["is_bmw"]), None)
    if not bmw or gap is None:
        return "No EPA comparison available."
    if gap >= 0:
        return f"{bmw['name']} leads EPA range with {bmw['range_km']} km (+{gap} km to the best competitor)."
    leader = rows[0]
    return (f"Best BMW ({bmw['name']}, {bmw['range_km']} km) is #{bmw['rank']} of {len(rows)}; "
            f"{leader['name']} leads with {leader['range_km']} km ({gap} km).")


def scenario_market(cfg: dict, fuel_dir: Path, nhtsa_dir: Path) -> dict | None:
    """Ein Szenario; None, wenn die Config weder EPA- noch NHTSA-Daten nennt (z. B. EU, China)."""
    if not cfg.get("fueleconomy") and not cfg.get("nhtsa"):
        return None
    ranges = _range_rows(cfg.get("fueleconomy", {}), fuel_dir)
    best_bmw = next((r["range_km"] for r in ranges if r["is_bmw"]), None)
    best_rival = next((r["range_km"] for r in ranges if not r["is_bmw"]), None)
    gap = best_bmw - best_rival if best_bmw is not None and best_rival is not None else None
    name = cfg.get("model_name", cfg["id"])
    return {"scenario_id": cfg["id"], "model_name": name, "range": ranges, "range_gap_km": gap,
            "range_sentence": _sentence(ranges, gap),
            "complaints": _complaint_rows(cfg["nhtsa"], name, nhtsa_dir) if cfg.get("nhtsa") else [],
            "complaint_years": cfg.get("nhtsa", {}).get("model_years", []),
            "limits": "EPA = lab test, not real-world driving. NHTSA = absolute counts, not per vehicle sold. "
                      "Models with incomplete complaint caches are omitted, never counted as zero."}


def market_all(scenario_ids: list[str], root: Path = ROOT) -> list[dict]:
    out = []
    for sid in sorted(scenario_ids):
        cfg = _read(root / "config" / "scenarios" / f"{sid}.json")
        result = scenario_market(cfg, fueleconomy.CACHE_DIR, nhtsa.CACHE_DIR) if cfg else None
        if result:
            out.append(result)
    return out
