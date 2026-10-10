"""Ein einziger Zugang zu OpenAI für alle Pfade (Owner: Lead).

Warum zentral:
- Cache: Gleiche Anfrage -> Antwort aus data/cache/ (spart Credits, Demo ohne Netz).
- data/demo_cache/ liegt im Repo (bewusst committet, nur geprüfte Webantworten ohne BMW-Daten),
  damit die Demo auch auf einem fremden Laptop ohne Netz und ohne eigenen Cache läuft.
- .env wird hier geladen, damit jeder Einstieg (API, pipeline.py, Skripte) den Key findet.
- DEMO_MODUS=true: NUR Cache, nie Netz. Fehlt ein Eintrag, gibt es einen klaren Fehler
  statt einer hängenden Demo.
- JSON-Ausgabe gegen ein Pydantic-Schema, damit kein Pfad freien Text parsen muss.
- Robust für den Nachtlauf: Timeout, 2 Wiederholungen, leere Antwort = Fehler, Cache atomar schreiben
  (ein Abbruch mitten im Schreiben darf keine halbe Datei hinterlassen, die später als Treffer gilt).
  Der Cache-Schlüssel bleibt unverändert, sonst wäre data/demo_cache/ wertlos.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / "data" / "cache"
DEMO_CACHE_DIR = ROOT / "data" / "demo_cache"
RETRIES = 2              # nach dem ersten Versuch noch 2 Mal; Netzfehler im Nachtlauf sind meist kurz
TIMEOUT_SECONDS = 180.0  # Websuche braucht teils über eine Minute; ohne Limit hängt der Lauf ewig
BACKOFF_SECONDS = 2.0


def lade_env(pfad: Path = ROOT / ".env") -> None:
    # override=False: Was die Shell schon gesetzt hat (z. B. in CI), gewinnt gegen die Datei.
    load_dotenv(pfad, override=False)


def _cache_path(model: str, system: str, user: str, schema_name: str, ordner: Path | None = None) -> Path:
    key = hashlib.sha256(f"{model}|{system}|{user}|{schema_name}".encode()).hexdigest()[:24]
    return (ordner or CACHE_DIR) / f"{schema_name}_{key}.json"


def ask_json(system: str, user: str, schema: type[BaseModel], model: str | None = None,
             tools: list[dict] | None = None) -> BaseModel:
    """Fragt das Modell und liefert ein validiertes Pydantic-Objekt.

    tools: z. B. [{"type": "web_search"}] für Pfad B (Webrecherche mit Quellen).
    """
    lade_env()
    model = model or os.getenv("OPENAI_MODEL") or "gpt-5-mini"  # leerer Wert in .env zählt als nicht gesetzt
    anfrage = (model, system, user + json.dumps(tools or []), schema.__name__)
    path = _cache_path(*anfrage)
    for kandidat in (path, _cache_path(*anfrage, ordner=DEMO_CACHE_DIR)):
        cached = _read_cache(kandidat, schema)
        if cached is not None:
            return cached
    if os.getenv("DEMO_MODUS", "false").lower() == "true":
        raise RuntimeError(f"DEMO_MODUS: kein Cache-Eintrag für {schema.__name__} ({path.name}).")

    result = _ask_with_retries(model, system, user, schema, tools or [])
    _write_atomic(path, result.model_dump_json(indent=2))
    return result


def _read_cache(path: Path, schema: type[BaseModel]) -> BaseModel | None:
    """Kaputte oder veraltete Cache-Datei zählt als kein Treffer (statt den ganzen Lauf abzubrechen)."""
    if not path.exists():
        return None
    try:
        return schema.model_validate_json(path.read_text(encoding="utf-8"))
    except (ValidationError, ValueError):
        return None


def _write_atomic(path: Path, text: str) -> None:
    """Erst in eine Temp-Datei, dann umbenennen: os.replace ist atomar, es gibt nie eine halbe Datei."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _ask_with_retries(model: str, system: str, user: str, schema: type[BaseModel], tools: list[dict]) -> BaseModel:
    last_error: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            result = _call_openai(model, system, user, schema, tools)
            if result is None:  # passiert bei Verweigerung oder abgeschnittener Antwort
                raise RuntimeError(f"Leere Antwort für {schema.__name__}")
            return result
        except Exception as err:  # Netz, Rate-Limit, Timeout, leere Antwort: alle gleich behandeln
            last_error = err
            if attempt < RETRIES:
                time.sleep(BACKOFF_SECONDS * (attempt + 1))
    raise RuntimeError(f"LLM nach {RETRIES + 1} Versuchen gescheitert ({schema.__name__}): {last_error}")


def _call_openai(model: str, system: str, user: str, schema: type[BaseModel], tools: list[dict]) -> BaseModel | None:
    """Der einzige Netzaufruf. Eigene Funktion, damit Tests ihn ohne Key ersetzen können."""
    from openai import OpenAI  # erst hier importieren: Tests laufen ohne Key

    client = OpenAI(timeout=TIMEOUT_SECONDS, max_retries=0)  # Wiederholen regeln wir selbst (sichtbar)
    response = client.responses.parse(
        model=model,
        input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        text_format=schema,
        tools=tools,
    )
    return response.output_parsed
