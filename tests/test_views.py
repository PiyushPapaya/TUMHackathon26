"""L20: fertige Ansichten (View-Models). Läuft gegen das Beispiel-Bundle G60-US."""

from core.insights import quadrant


def test_scenarios_haben_badge_und_kopfzahlen(client):
    card = client.get("/api/scenarios").json()[0]
    assert card["badge"] == "reich" and card["data_coverage"]["feedback"] == 3610
    assert card["headline_numbers"]["top_title"]


def test_overview_zaehlt_stufen_und_top3(client):
    body = client.get("/api/scenarios/G60-US/overview").json()
    assert len(body["top3"]) == 3 and body["top3"][0]["rank"] == 1
    assert sum(body["level_distribution"].values()) == body["funnel"]["requirements"]
    assert any("Themen ohne Kategorie" in w for w in body["warnings"])


def test_explain_wasserfall_summiert_auf_score(client):
    body = client.get("/api/requirements/REQ-G60-US-001/explain").json()
    total = round(sum(step["contribution"] for step in body["waterfall"]), 1)
    assert abs(total - body["requirement"]["score"]) <= 0.2  # Rundung je Faktor
    assert body["waterfall"][-1]["factor"] == "confidence"
    assert body["segments"]["engine"]["ICE"] >= 34 and body["conflicts"]
    assert body["robustness_sentence"].startswith("In 100 %")


def test_whatif_speichert_nichts(client):
    before_audit = len(client.get("/api/audit").json())
    before = [r["id"] for r in client.get("/api/scenarios/G60-US/requirements").json()]
    preview = client.post("/api/scenarios/G60-US/whatif", json={"weights": {"future_relevance": 1.0}}).json()
    assert {p["id"] for p in preview} == set(before)
    assert all(p["rank_change"] == p["old_rank"] - p["new_rank"] for p in preview)
    assert [r["id"] for r in client.get("/api/scenarios/G60-US/requirements").json()] == before
    assert len(client.get("/api/audit").json()) == before_audit


def test_whatif_lehnt_unbekannten_faktor_ab(client):
    assert client.post("/api/scenarios/G60-US/whatif", json={"weights": {"preis": 1}}).status_code == 422


def test_portfolio_und_compare(client):
    body = client.get("/api/portfolio").json()
    assert body["scenarios"][0]["id"] == "G60-US" and len(body["rows"]) == 9
    assert client.get("/api/compare", params={"a": "G60-US", "b": "G60-US"}).json()["rows"][0]["rank_diff"] == 0
    assert client.get("/api/compare", params={"a": "G60-US", "b": "XX"}).status_code == 404


def test_gaps_zeigen_annahmen_und_naechste_studie(client):
    body = client.get("/api/scenarios/G60-US/gaps").json()
    weak = {w["id"]: w for w in body["weak_requirements"]}
    assert weak["REQ-G60-US-005"]["evidence_level"] == "D" and weak["REQ-G60-US-005"]["assumptions"]
    assert body["missing_sources"] == []


def test_trends_enthalten_zukunftswette(client):
    items = client.get("/api/scenarios/G60-US/trends").json()["items"]
    assert any(i["kind"] == "bet" and i["requirement_id"] == "REQ-G60-US-005" for i in items)


def test_opportunities_quadranten_regel():
    assert quadrant(0.8, 0.09) == "Chance" and quadrant(0.8, 0.01) == "Stärke halten"
    assert quadrant(0.2, 0.2) == "Beobachten" and quadrant(0.2, 0.0) == "Nebensache"


def test_opportunities_endpunkt(client):
    points = client.get("/api/scenarios/G60-US/opportunities").json()["points"]
    assert {p["quadrant"] for p in points} == {"Chance", "Stärke halten", "Beobachten", "Nebensache"}


def test_evidence_browser_filtert_nach_segment_und_text(client):
    bev = client.get("/api/scenarios/G60-US/evidence", params={"segment": "engine:BEV"}).json()
    assert bev["total"] >= 1 and all(i["meta"]["engine"] == "BEVE" for i in bev["items"])
    assert client.get("/api/scenarios/G60-US/evidence", params={"q": "Frunk"}).json()["total"] == 1


def test_audit_timeline_hat_saetze(client):
    rows = client.get("/api/audit/timeline", params={"scenario_id": "G60-US"}).json()
    assert rows[0]["sentence"] == "Pipeline-Ergebnis geladen"


def test_export_json_hat_alle_felder(client):
    rows = client.get("/api/scenarios/G60-US/export", params={"format": "json"}).json()
    assert rows[0]["rank"] == 1 and "robustness" in rows[0] and "score_breakdown" in rows[0]
