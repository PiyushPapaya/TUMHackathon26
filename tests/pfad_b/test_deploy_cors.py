"""CORS für das gehostete Frontend: Vercel-Vorschauen dürfen zugreifen, fremde Seiten nicht.

Warum: Ohne passende CORS-Regel blockt der Browser jede Anfrage der Vercel-UI an das Render-Backend,
und alle Cockpit-Seiten zeigen nur „Backend not reachable“. Siehe docs/DEPLOY.md.
"""

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cors_app(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_DB", str(tmp_path / "audit.db"))
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "leer"))
    monkeypatch.setenv("DEMO_MODUS", "true")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")
    import main

    # Die Middleware liest die Variablen beim Import, darum hier neu laden.
    main = importlib.reload(main)
    with TestClient(main.app) as client:
        yield client
    monkeypatch.delenv("CORS_ORIGIN_REGEX")
    importlib.reload(main)  # nächste Tests bekommen wieder die Standard-App


def _preflight(client: TestClient, origin: str):
    return client.options("/api/scenarios", headers={"Origin": origin, "Access-Control-Request-Method": "GET"})


def test_vercel_vorschau_darf_zugreifen(cors_app):
    origin = "https://tumhackathon26-git-main-piyush.vercel.app"
    assert _preflight(cors_app, origin).headers.get("access-control-allow-origin") == origin


def test_localhost_bleibt_erlaubt(cors_app):
    assert _preflight(cors_app, "http://localhost:3000").headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_fremde_seite_wird_blockiert(cors_app):
    assert "access-control-allow-origin" not in _preflight(cors_app, "https://evil.example.com").headers
