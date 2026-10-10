"""End-to-End über HTTP mit dem Beispiel-Bundle: der Kernflow der Demo."""

REQ = "REQ-G60-US-001"


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["demo_mode"] is True and "G60-US" in body["scenarios"]


def test_requirements_are_ranked_and_complete(client):
    reqs = client.get("/api/scenarios/G60-US/requirements").json()
    assert [r["rank"] for r in reqs] == list(range(1, len(reqs) + 1))
    assert reqs[0]["score"] >= reqs[-1]["score"]
    # Pflichtfelder aus dem Brief: ID, Beschreibung, Befunde, Score, Begründung, Evidenz, Annahmen, Status
    for field in ["id", "description", "signal_ids", "score", "rationale", "evidence_level", "assumptions", "status"]:
        assert field in reqs[0]


def test_detail_links_requirement_to_evidence(client):
    detail = client.get(f"/api/requirements/{REQ}").json()
    assert detail["signals"] and detail["evidence"]
    assert detail["history"][0]["event_type"] == "REQUIREMENT_PROPOSED"


def test_pm_decision_is_audited(client):
    res = client.post(f"/api/requirements/{REQ}/decision",
                      json={"action": "approve", "actor": "pm.test", "rationale": "Belege überzeugen"})
    assert res.status_code == 200
    assert res.json()["requirement"]["status"] == "approved"
    history = client.get("/api/audit", params={"requirement_id": REQ}).json()
    assert history[-1]["event_type"] == "PM_APPROVE"
    assert history[-1]["actor"]["type"] == "human"
    assert client.get("/api/audit/verify").json()["valid"] is True


def test_decision_without_rationale_is_rejected(client):
    res = client.post(f"/api/requirements/{REQ}/decision", json={"action": "approve", "actor": "pm", "rationale": ""})
    assert res.status_code == 422


def test_challenge_returns_ai_answer(client):
    res = client.post(f"/api/requirements/{REQ}/decision",
                      json={"action": "challenge", "actor": "pm.test", "rationale": "Belege?",
                            "question": "Gilt das auch für BEV?"})
    body = res.json()
    assert body["requirement"]["status"] == "challenged"
    assert body["ai_answer"]["supporting_evidence_ids"]


def test_weight_change_reranks_and_is_audited(client):
    before = client.get("/api/scenarios/G60-US/requirements").json()
    after = client.put("/api/scenarios/G60-US/weights",
                       json={"weights": {"future_relevance": 1.0, "customer_pain": 0.0}, "actor": "pm.test",
                             "rationale": "Nachfolger kommt 2030, Zukunft zählt mehr"}).json()
    assert [r["id"] for r in after] != [r["id"] for r in before]
    events = client.get("/api/audit", params={"scenario_id": "G60-US"}).json()
    assert events[-1]["event_type"] == "WEIGHTS_CHANGED"


def test_edit_only_allowed_fields(client):
    res = client.post(f"/api/requirements/{REQ}/decision",
                      json={"action": "edit", "actor": "pm", "rationale": "x", "changes": {"score": 100}})
    assert res.status_code == 422


def test_export_csv(client):
    csv_text = client.get("/api/scenarios/G60-US/export").text
    assert csv_text.splitlines()[0].startswith("id;rank;title")
    assert REQ in csv_text


def test_unknown_ids_give_404(client):
    assert client.get("/api/requirements/REQ-NOPE").status_code == 404
    assert client.get("/api/scenarios/X-Y/requirements").status_code == 404


def test_edit_with_invalid_value_is_rejected_and_not_logged(client):
    res = client.post(f"/api/requirements/{REQ}/decision",
                      json={"action": "edit", "actor": "pm", "rationale": "x", "changes": {"effort": "XXL"}})
    assert res.status_code == 422
    history = client.get("/api/audit", params={"requirement_id": REQ}).json()
    assert all(e["event_type"] != "PM_EDIT" for e in history)


def test_negative_weights_are_rejected(client):
    res = client.put("/api/scenarios/G60-US/weights",
                     json={"weights": {"reach": -1.0}, "actor": "pm", "rationale": "Test negativ"})
    assert res.status_code == 422


def test_export_neutralizes_formulas(client):
    client.post(f"/api/requirements/{REQ}/decision",
                json={"action": "edit", "actor": "pm", "rationale": "Test Injection",
                      "changes": {"title": "=HYPERLINK(\"http://boese.example\")"}})
    csv_text = client.get("/api/scenarios/G60-US/export").text
    assert "'=HYPERLINK" in csv_text and ";=HYPERLINK" not in csv_text
