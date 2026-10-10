"""Gemeinsame Test-Helfer: Backend-Pfad und eine frische Test-App pro Test."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "backend"))


@pytest.fixture
def client(tmp_path, monkeypatch):
    """App mit leerer Audit-DB im Temp-Ordner, damit Tests sich nicht gegenseitig stören."""
    monkeypatch.setenv("AUDIT_DB", str(tmp_path / "audit.db"))
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "leer"))  # nur Beispiel-Bundle, keine lokalen Daten
    monkeypatch.setenv("DEMO_MODUS", "true")  # Tests dürfen nie OpenAI aufrufen
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as test_client:
        yield test_client
