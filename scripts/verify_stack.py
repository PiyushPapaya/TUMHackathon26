"""Offline-Integration aller Bundles: HTTP, PM-Flow, Vorschau, Export, Audit und Neustart.

Schreibt ausschließlich eine temporäre Audit-DB, niemals die Demo-Entscheidungen.
Aufruf: python scripts/verify_stack.py [--output outputs/repo-audit/integration.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


def verify() -> dict:
    os.environ["DEMO_MODUS"] = "true"
    checks, snapshots = [], {}
    with tempfile.TemporaryDirectory(prefix="signal2spec-verify-") as folder:
        os.environ["AUDIT_DB"] = str(Path(folder) / "audit.db")
        os.environ["PROCESSED_DIR"] = str(ROOT / "data" / "processed")
        with TestClient(app) as client:
            def get(path):
                response = client.get(path)
                assert response.status_code == 200, f"{path}: {response.status_code} {response.text[:200]}"
                checks.append(path)
                return response

            get("/health")
            get("/openapi.json")
            scenarios = get("/api/scenarios").json()
            for scenario in scenarios:
                sid = scenario["id"]
                for route in ("overview", "funnel", "signals", "requirements", "product-context", "matrix",
                              "opportunities", "trends", "gaps", "evidence?q=&page=1&size=100"):
                    get(f"/api/scenarios/{sid}/{route}")
                reqs = get(f"/api/scenarios/{sid}/requirements").json()
                assert reqs and [r["rank"] for r in reqs] == list(range(1, len(reqs) + 1))
                state = client.app.state.store.get(sid)
                before = {r.id: r.model_dump(mode="json") for r in state.requirements.values()}
                event_count = len(client.app.state.store.audit.events())
                preview = client.post(f"/api/scenarios/{sid}/whatif", json={"weights": {"reach": 1}})
                assert preview.status_code == 200
                assert {r.id: r.model_dump(mode="json") for r in state.requirements.values()} == before
                assert len(client.app.state.store.audit.events()) == event_count
                for req in reqs:
                    detail = get(f"/api/requirements/{req['id']}/explain").json()
                    assert abs(sum(s["contribution"] for s in detail["waterfall"]) - req["score"]) < 0.11
                    rob = req["robustness"]
                    assert rob and rob["rank_min"] <= req["rank"] <= rob["rank_max"]
                for fmt in ("csv", "json", "md"):
                    get(f"/api/scenarios/{sid}/export?format={fmt}")
                get(f"/api/scenarios/{sid}/memo")
                rid = reqs[0]["id"]
                get(f"/api/requirements/{rid}")
                get(f"/api/requirements/{rid}/counterparts")
                actions = (("approve", {}), ("reject", {}),
                           ("challenge", {"question": "What speaks against it?"}),
                           ("edit", {"changes": {"effort": "S", "acceptance_criterion": "Audit test: 1 step"}}))
                for action, extra in actions:
                    response = client.post(f"/api/requirements/{rid}/decision", json={
                        "action": action, "actor": "pm.audit-test", "rationale": "Repository integration check",
                        **extra})
                    assert response.status_code == 200, response.text[:200]
                    if action == "challenge":
                        answer = response.json()["ai_answer"]
                        cited = answer["supporting_evidence_ids"] + answer["counter_evidence_ids"]
                        assert set(cited) <= set(state.evidence)
                response = client.put(f"/api/scenarios/{sid}/weights", json={
                    "weights": {"reach": 1}, "actor": "pm.audit-test", "rationale": "Repository integration check"})
                assert response.status_code == 200
                snapshots[sid] = {r.id: r.model_dump(mode="json") for r in client.app.state.store.ranked(sid)}
            get("/api/portfolio")
            get("/api/benchmarks")
            get("/api/compare?a=G60-US&b=F70-EU")
            response = client.post("/api/ask", json={"question": "Which requirements matter most for families?"})
            assert response.status_code == 200
            get("/api/audit")
            get("/api/audit/timeline")
            assert get("/api/audit/verify").json()["valid"]
            events_before = len(client.app.state.store.audit.events())
        with TestClient(app) as restarted:
            assert len(restarted.app.state.store.audit.events()) == events_before
            for sid, snapshot in snapshots.items():
                assert {r.id: r.model_dump(mode="json") for r in restarted.app.state.store.ranked(sid)} == snapshot
            assert restarted.get("/api/audit/verify").json()["valid"]
        # Kein echter PM-Zustand wurde verändert; nur die temporäre Datenbank wurde benutzt.
    return {"passed": True, "scenarios": sorted(snapshots), "http_reads": len(checks),
            "pm_actions": len(snapshots) * 5, "restart_replay": True, "offline": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify()
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
