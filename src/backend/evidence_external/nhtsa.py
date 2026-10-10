"""Pfad B, L22: NHTSA-Beschwerden als zweite, unabhängige Kundenquelle (nur US-Szenarien).

Warum NHTSA: US-Behördendaten, öffentlich, ohne Key, gemeinfrei. Jede Beschwerde ist eine echte
Kundenstimme mit ODI-Nummer, also prüfbar. Damit stützen sich US-Befunde nicht nur auf BMWs eigene
Feedback-Datei. Grenze (ehrlich im Pitch): NHTSA sammelt vor allem Sicherheits- und Defektthemen,
kaum Komfort- oder Designwünsche. Deshalb ordnen wir nur klar zuordenbare Komponenten einer
Kategorie zu; der Rest ("UNKNOWN OR OTHER") zählt nur in der Wettbewerbs-Statistik.

Cache: jede Antwort liegt in data/external_cache/nhtsa/ und ist committet (Offline-Demo, gleicher Stand
für alle). DEMO_MODUS=true liest nur den Cache.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from core.models import Category, Evidence, Scenario, Signal, SignalKind, SourceType

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "data" / "external_cache" / "nhtsa"
API = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
MIN_COMPLAINTS = 3  # unter 3 Beschwerden je Thema kein eigener Befund (Einzelfall, kein Muster)

# NHTSA-Komponente (Teilstring) -> unsere Kategorie. Reihenfolge zählt: spezifisch vor allgemein.
COMPONENT_CATEGORY = [
    ("TRACTION BATTERY", Category.RANGE_CHARGING), ("CHARGING", Category.RANGE_CHARGING),
    ("FORWARD COLLISION", Category.DRIVER_ASSISTANCE), ("LANE DEPARTURE", Category.DRIVER_ASSISTANCE),
    ("BACK OVER", Category.DRIVER_ASSISTANCE), ("VEHICLE SPEED CONTROL", Category.DRIVER_ASSISTANCE),
    ("STEERING", Category.DRIVING_EXPERIENCE), ("SUSPENSION", Category.DRIVING_EXPERIENCE),
    ("SERVICE BRAKES", Category.DRIVING_EXPERIENCE), ("ELECTRONIC STABILITY", Category.DRIVING_EXPERIENCE),
    ("SEAT", Category.INTERIOR), ("VISIBILITY", Category.EXTERIOR), ("LATCHES", Category.COMFORT_SPACE),
    ("ELECTRICAL SYSTEM", Category.QUALITY_PERCEPTION), ("POWER TRAIN", Category.QUALITY_PERCEPTION),
]


def category_for(components: str) -> Category | None:
    upper = components.upper()
    return next((cat for key, cat in COMPONENT_CATEGORY if key in upper), None)


def _url(make: str, model: str, year: int) -> str:
    return f"{API}?{urlencode({'make': make, 'model': model, 'modelYear': year})}"


def fetch(make: str, model: str, year: int, cache_dir: Path | None = None) -> list[dict]:
    """Beschwerden für ein Fahrzeug; erst Cache, dann Netz (außer im Demo-Modus)."""
    folder = cache_dir or CACHE_DIR
    path = folder / f"{make}_{model}_{year}.json".replace(" ", "_").replace("/", "-")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("results", [])
    if os.getenv("DEMO_MODUS", "false").lower() == "true":
        return []  # Demo ohne Netz: fehlender Eintrag = keine Beschwerden, Pipeline läuft weiter
    import httpx  # erst hier: Tests und Demo brauchen kein Netz

    response = httpx.get(_url(make, model, year), timeout=30)
    # NHTSA meldet "kein Fahrzeug/Jahr bekannt" als 400; das heißt 0 Beschwerden, kein Fehler
    data = {"count": 0, "results": []} if response.status_code == 400 else response.raise_for_status().json()
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data.get("results", [])


def _complaint_evidence(scenario: Scenario, item: dict, model: str, year: int, now: datetime) -> Evidence:
    components = item.get("components", "")
    category = category_for(components)
    return Evidence(
        id=f"EV-{scenario.id}-NHTSA-{item['odiNumber']}", source_type=SourceType.FEEDBACK_EXTERNAL,
        source_name="NHTSA-Beschwerde", derivative=scenario.derivative, market=scenario.market,
        text=item.get("summary", "").strip(), url=_url("BMW", model, year), retrieved_at=now, polarity=-1,
        meta={"odi": str(item["odiNumber"]), "components": components, "model": model, "model_year": str(year),
              "country": "US", "trust": "high", "publisher": "NHTSA",
              "category": category.value if category else ""},
    )


def _competitor_stat(scenario: Scenario, rival: str, counts: dict[str, int], bmw_total: int,
                     now: datetime, number: int) -> Evidence:
    total = sum(counts.values())
    years = "/".join(str(y) for y in scenario.nhtsa.get("model_years", []))
    return Evidence(
        id=f"EV-{scenario.id}-NHTSA-STAT-{number:02d}", source_type=SourceType.EXTERNAL_STAT,
        source_name="NHTSA-Statistik", derivative=scenario.derivative, market=scenario.market,
        text=(f"NHTSA complaints model years {years}: {rival} {total}, {scenario.model_name} {bmw_total} "
              "(absolute counts, not per vehicle sold)."),
        url=API, retrieved_at=now, meta={"trust": "high", "publisher": "NHTSA", "competitor": rival,
                                          "competitor_total": str(total), "bmw_total": str(bmw_total)},
    )


def collect(scenario: Scenario, cache_dir: Path | None = None) -> tuple[list[Evidence], list[Signal]]:
    """BMW-Beschwerden -> Belege + ein Befund je Kategorie (ab 3 Beschwerden); Wettbewerber -> Statistik."""
    cfg = scenario.nhtsa
    if not cfg:
        return [], []
    now = datetime.now(UTC)
    evidence: dict[str, Evidence] = {}
    for model in cfg.get("bmw_models", []):
        for year in cfg.get("model_years", []):
            for item in fetch("BMW", model, year, cache_dir):
                ev = _complaint_evidence(scenario, item, model, year, now)
                if ev.text:
                    evidence.setdefault(ev.id, ev)  # gleiche ODI-Nummer bei mehreren Modellen nur einmal
    stats = []
    for number, (rival, (make, models)) in enumerate(cfg.get("competitors", {}).items(), start=1):
        counts = {f"{m} {y}": len(fetch(make, m, y, cache_dir)) for m in models for y in cfg.get("model_years", [])}
        stats.append(_competitor_stat(scenario, rival, counts, len(evidence), now, number))
    return [*evidence.values(), *stats], _signals(scenario, list(evidence.values()), stats)


def _signals(scenario: Scenario, complaints: list[Evidence], stats: list[Evidence]) -> list[Signal]:
    by_cat: dict[str, list[Evidence]] = {}
    for ev in complaints:
        if ev.meta["category"]:
            by_cat.setdefault(ev.meta["category"], []).append(ev)
    signals = []
    for number, (cat, items) in enumerate(sorted(by_cat.items(), key=lambda kv: -len(kv[1])), start=1):
        if len(items) < MIN_COMPLAINTS:
            continue
        top = Counter(c.strip() for ev in items for c in ev.meta["components"].split(",")).most_common(2)
        parts = " und ".join(name.title() for name, _ in top)
        signals.append(Signal(
            id=f"SIG-{scenario.id}-NHTSA-{number:02d}", kind=SignalKind.COMPLAINT, category=Category(cat),
            title=f"US-Behördenbeschwerden: {parts}",
            summary=f"{len(items)} NHTSA-Beschwerden zu {parts} ({scenario.model_name}, US).",
            evidence_ids=[e.id for e in items] + [s.id for s in stats], mention_count=len(items),
            source_types=[SourceType.FEEDBACK_EXTERNAL],
        ))
    return signals
