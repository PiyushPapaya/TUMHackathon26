"""Assistent-Endpunkt /api/ask: nur echte IDs aus dem Store, nichts wird gespeichert."""


def test_ask_nennt_nur_echte_anforderungen(client, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")  # Regel-Fallback, kein Netz
    res = client.post("/api/ask", json={"question": "What matters most for families?", "actor": "pm.test"})
    assert res.status_code == 200
    body = res.json()
    assert body["top"], "mindestens ein Treffer erwartet"
    for row in body["top"]:
        detail = client.get(f"/api/requirements/{row['requirement_id']}")
        assert detail.status_code == 200, row["requirement_id"]


def test_ask_schreibt_keinen_pruefpfad(client, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "true")
    before = len(client.get("/api/audit").json())
    client.post("/api/ask", json={"question": "charging", "actor": "pm.test"})
    assert len(client.get("/api/audit").json()) == before


def test_ask_leere_frage_ist_422(client):
    assert client.post("/api/ask", json={"question": "", "actor": "pm"}).status_code == 422
    assert client.post("/api/ask", json={"question": "   ", "actor": "pm"}).status_code == 422
