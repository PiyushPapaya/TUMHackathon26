"""Zustand pro Szenario + alle PM-Aktionen (Owner: Lead).

Warum ein zentraler Store: Jede Änderung an einer Anforderung (PM-Entscheidung,
Gewichte, Bearbeitung) läuft durch GENAU diese Klasse und erzeugt ein Audit-Ereignis.
So kann keine Änderung am Prüfpfad vorbeigehen.

Datenquelle: data/processed/<szenario>.json (von pipeline.py erzeugt). Fehlt sie,
nehmen wir src/shared/beispiele/bundle_<szenario>.json, damit Frontend und Tests
ohne OpenAI-Key und ohne BMW-Rohdaten laufen.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from core.audit import AuditLog
from core.models import Actor, ActorType, Evidence, Requirement, Scenario, Signal, Status
from requirements_engine import scoring

ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = ROOT / "data" / "processed"
EXAMPLES_DIR = ROOT / "src" / "shared" / "beispiele"
SYSTEM = Actor(type=ActorType.SYSTEM, name="pipeline")


class ScenarioState:
    def __init__(self, bundle: dict):
        self.scenario = Scenario(**bundle["scenario"])
        self.funnel: dict = bundle.get("funnel", {})
        self.evidence = {e["id"]: Evidence(**e) for e in bundle["evidence"]}
        self.signals = {s["id"]: Signal(**s) for s in bundle["signals"]}
        self.requirements = {r["id"]: Requirement(**r) for r in bundle["requirements"]}
        self.weights = scoring.normalize_weights(bundle.get("weights", {}))


class Store:
    def __init__(self, audit: AuditLog):
        self.audit = audit
        self.states: dict[str, ScenarioState] = {}

    # ─── Laden ──────────────────────────────────────────────────────────────
    def load_all(self) -> None:
        """Echte Pipeline-Ergebnisse haben Vorrang; Beispiele nur für Szenarien ohne Ergebnis."""
        processed_dir = Path(os.getenv("PROCESSED_DIR", PROCESSED_DIR))
        sources = {p.stem.removeprefix("bundle_"): p for p in sorted(EXAMPLES_DIR.glob("bundle_*.json"))}
        sources |= {p.stem: p for p in sorted(processed_dir.glob("*.json"))}
        for path in sources.values():
            state = ScenarioState(json.loads(path.read_text(encoding="utf-8")))
            self._rescore(state)  # Score immer aus der Formel, nie aus der Datei übernehmen
            self.states[state.scenario.id] = state
            if not self.audit.events(scenario_id=state.scenario.id):
                self._log_initial_proposals(state, path.name)

    def _log_initial_proposals(self, state: ScenarioState, source: str) -> None:
        """Erste Einträge im Prüfpfad: woher die Vorschläge stammen."""
        sid = state.scenario.id
        self.audit.append("PIPELINE_LOADED", sid, SYSTEM, f"Ergebnisse geladen aus {source}", {"funnel": state.funnel})
        for req in sorted(state.requirements.values(), key=lambda r: r.rank):
            self.audit.append(
                "REQUIREMENT_PROPOSED", sid, Actor(type=ActorType.AI, name="pipeline"),
                req.rationale, {"score": req.score, "evidence_level": req.evidence_level.value,
                                "signal_ids": req.signal_ids}, requirement_id=req.id,
            )

    def get(self, scenario_id: str) -> ScenarioState:
        if scenario_id not in self.states:
            raise KeyError(f"Unbekanntes Szenario: {scenario_id}")
        return self.states[scenario_id]

    def find_requirement(self, req_id: str) -> tuple[ScenarioState, Requirement]:
        for state in self.states.values():
            if req_id in state.requirements:
                return state, state.requirements[req_id]
        raise KeyError(f"Unbekannte Anforderung: {req_id}")

    # ─── PM-Aktionen (jede erzeugt ein Audit-Ereignis) ─────────────────────
    def decide(
        self, req_id: str, action: str, actor: Actor, rationale: str, changes: dict | None = None
    ) -> Requirement:
        state, req = self.find_requirement(req_id)
        before = req.model_dump(mode="json")
        if action == "approve":
            req.status = Status.APPROVED
        elif action == "reject":
            req.status = Status.REJECTED
        elif action == "edit":
            allowed = {"title", "description", "acceptance_criterion", "effort", "assumptions", "uncertainties"}
            bad = set(changes or {}) - allowed
            if bad or not changes:
                raise ValueError(f"Bearbeitbar sind nur: {sorted(allowed)}")
            req = req.model_copy(update=changes)
            req.version += 1
            state.requirements[req_id] = req
            if "effort" in changes:
                self._rescore(state)
        elif action == "challenge":
            req.status = Status.CHALLENGED
        else:
            raise ValueError(f"Unbekannte Aktion: {action}")
        after = req.model_dump(mode="json")
        diff = {k: {"before": before[k], "after": after[k]} for k in after if before.get(k) != after[k]}
        self.audit.append(f"PM_{action.upper()}", state.scenario.id, actor, rationale, diff, requirement_id=req_id)
        return state.requirements[req_id]

    def set_weights(
        self, scenario_id: str, weights: dict[str, float], actor: Actor, rationale: str
    ) -> list[Requirement]:
        state = self.get(scenario_id)
        before = {r.id: (r.rank, r.score) for r in state.requirements.values()}
        old_weights = state.weights
        state.weights = scoring.normalize_weights(weights)
        self._rescore(state)
        changes = {r.id: {"before": before[r.id], "after": (r.rank, r.score)} for r in state.requirements.values()
                   if before[r.id] != (r.rank, r.score)}
        self.audit.append("WEIGHTS_CHANGED", scenario_id, actor, rationale,
                          {"weights": {"before": old_weights, "after": state.weights}, "rank_changes": changes})
        return self.ranked(scenario_id)

    def _rescore(self, state: ScenarioState) -> None:
        """Neu rechnen mit den gespeicherten Faktorwerten, dann neu ranken."""
        for req in state.requirements.values():
            values = {k: f.value for k, f in req.score_breakdown.items()}
            values["effort_inverse"] = scoring.effort_factor(req.effort)
            texts = {k: f.explanation for k, f in req.score_breakdown.items()}
            req.score, req.score_breakdown = scoring.score(values, texts, req.evidence_level, state.weights)
        for rank, req in enumerate(sorted(state.requirements.values(), key=lambda r: -r.score), start=1):
            req.rank = rank

    def ranked(self, scenario_id: str) -> list[Requirement]:
        return sorted(self.get(scenario_id).requirements.values(), key=lambda r: r.rank)
