"""Ein einziger Zugang zu OpenAI für alle Pfade (Owner: Lead).

Warum zentral:
- Cache: Gleiche Anfrage -> Antwort aus data/cache/ (spart Credits, Demo ohne Netz).
- DEMO_MODUS=true: NUR Cache, nie Netz. Fehlt ein Eintrag, gibt es einen klaren Fehler
  statt einer hängenden Demo.
- JSON-Ausgabe gegen ein Pydantic-Schema, damit kein Pfad freien Text parsen muss.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from pydantic import BaseModel

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "cache"


def _cache_path(model: str, system: str, user: str, schema_name: str) -> Path:
    key = hashlib.sha256(f"{model}|{system}|{user}|{schema_name}".encode()).hexdigest()[:24]
    return CACHE_DIR / f"{schema_name}_{key}.json"


def ask_json(system: str, user: str, schema: type[BaseModel], model: str | None = None,
             tools: list[dict] | None = None) -> BaseModel:
    """Fragt das Modell und liefert ein validiertes Pydantic-Objekt.

    tools: z. B. [{"type": "web_search"}] für Pfad B (Webrecherche mit Quellen).
    """
    model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    path = _cache_path(model, system, user + json.dumps(tools or []), schema.__name__)
    if path.exists():
        return schema.model_validate_json(path.read_text(encoding="utf-8"))
    if os.getenv("DEMO_MODUS", "false").lower() == "true":
        raise RuntimeError(f"DEMO_MODUS: kein Cache-Eintrag für {schema.__name__} ({path.name}).")

    from openai import OpenAI  # erst hier importieren: Tests laufen ohne Key

    client = OpenAI()
    response = client.responses.parse(
        model=model,
        input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        text_format=schema,
        tools=tools or [],
    )
    result = response.output_parsed
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
