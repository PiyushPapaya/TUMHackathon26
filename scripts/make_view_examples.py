"""Erzeugt src/shared/beispiele/views/*.json: eine echte Antwort pro Ansichts-Endpunkt.

Warum: Pfad D (Frontend) baut gegen diese Dateien, ohne auf echte Daten zu warten. Weil sie
vom laufenden Backend stammen (nicht von Hand geschrieben), stimmen Felder und Typen immer.
Aufruf (Repo-Root):  python scripts/make_view_examples.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))
OUT = ROOT / "src" / "shared" / "beispiele" / "views"

CALLS = {
    "scenarios": ("get", "/api/scenarios", None),
    "overview": ("get", "/api/scenarios/G60-US/overview", None),
    "explain": ("get", "/api/requirements/REQ-G60-US-001/explain", None),
    "whatif": ("post", "/api/scenarios/G60-US/whatif", {"weights": {"future_relevance": 0.4}}),
    "portfolio": ("get", "/api/portfolio", None),
    "compare": ("get", "/api/compare?a=G60-US&b=G60-US", None),
    "opportunities": ("get", "/api/scenarios/G60-US/opportunities", None),
    "trends": ("get", "/api/scenarios/G60-US/trends", None),
    "gaps": ("get", "/api/scenarios/G60-US/gaps", None),
    "evidence": ("get", "/api/scenarios/G60-US/evidence?segment=engine:BEV&size=3", None),
    "audit_timeline": ("get", "/api/audit/timeline?requirement_id=REQ-G60-US-001", None),
    "health": ("get", "/health", None),
}


def main() -> None:
    tmp = Path(tempfile.mkdtemp())
    os.environ.update({"AUDIT_DB": str(tmp / "audit.db"), "PROCESSED_DIR": str(tmp / "leer"), "DEMO_MODUS": "true"})
    from fastapi.testclient import TestClient

    from main import app

    OUT.mkdir(parents=True, exist_ok=True)
    with TestClient(app) as client:
        for name, (method, url, body) in CALLS.items():
            response = client.request(method, url, json=body)
            response.raise_for_status()
            text = json.dumps(response.json(), ensure_ascii=False, indent=1)
            (OUT / f"{name}.json").write_text(text + "\n", encoding="utf-8")
            print(f"  -> views/{name}.json")


if __name__ == "__main__":
    main()
