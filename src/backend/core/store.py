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
import logging
import os
import threading
from copy import copy
from pathlib import Path

from pydantic import ValidationError

from core.audit import AuditLog
from core.identity import bundle_fingerprint, recorded_fingerprint
from core.models import Actor, ActorType, Evidence, Requirement, Scenario, Signal, SourceType, Status
from core.outlook import outlook
from core.replay import replay
from requirements_engine import scoring
from requirements_engine.robustness import compute_robustness

ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = ROOT / "data" / "processed"
EXAMPLES_DIR = ROOT / "src" / "shared" / "beispiele"
SYSTEM = Actor(type=ActorType.SYSTEM, name="pipeline")


class ScenarioState:
    def __init__(self, bundle: dict, feedback_evidence: list[Evidence] | None = None):
        self.scenario = Scenario(**bundle["scenario"])
        # Warnungen sind reiner Anzeigetext: aus config/ nachladen, damit eine Textkorrektur
        # (z. B. Übersetzung) keinen teuren Pipeline-Lauf braucht. Zahlen bleiben im Bundle.
        config = ROOT / "config" / "scenarios" / f"{self.scenario.id}.json"
        if config.exists():
            warnings = json.loads(config.read_text(encoding="utf-8")).get("warnings")
            if isinstance(warnings, list):
                self.scenario.warnings = warnings
        self.funnel: dict = bundle.get("funnel", {})
        self.evidence = {e["id"]: Evidence(**e) for e in bundle["evidence"]}
        self.signals = {s["id"]: Signal(**s) for s in bundle["signals"]}
        self.requirements = {r["id"]: Requirement(**r) for r in bundle["requirements"]}
        self.discarded: list[dict] = bundle.get("discarded", [])  # Beispiel-Bundles haben das Feld nicht
        self.weights = scoring.normalize_weights(bundle.get("weights", {}))
        # Welle 2: Kontext (Absatz, unbekannte Themen) und Chancen-Karte, fertig aus der Pipeline
        self.context: dict = bundle.get("context", {})
        self.opportunities: list[dict] = bundle.get("opportunities", [])
        # Herkunft (Modell, Prompt-Stand, Commit); fehlt bei Bundles von vor dem 11.10. -> None, nie geraten.
        self.provenance: dict | None = bundle.get("provenance")
        # WARUM: Bundles enthalten Zitat-Stichproben; der Szenario-Nenner braucht alle Kommentare.
        outlook_evidence = {e.id: e for e in feedback_evidence or [] if e.source_type == SourceType.FEEDBACK
                            and e.derivative == self.scenario.derivative and e.market == self.scenario.market}
        outlook_evidence.update(self.evidence)
        web_signals = [s for s in self.signals.values() if SourceType.WEB in s.source_types]
        for req in self.requirements.values():
            linked = [self.signals[i] for i in req.signal_ids if i in self.signals]
            req.outlook = outlook(req, linked, outlook_evidence, web_signals, self.scenario.successor_horizon)
            req.outlook["baseline_source"] = "scenario_feedback" if feedback_evidence is not None else "bundle_sample"
            if feedback_evidence is None:
                req.outlook["sentence"] += " Scenario average uses only feedback available in this bundle."


class Store:
    def __init__(self, audit: AuditLog):
        self.audit = audit
        self.states: dict[str, ScenarioState] = {}
        self._lock = threading.RLock()

    # ─── Laden ──────────────────────────────────────────────────────────────
    def load_all(self) -> None:
        """Echte Pipeline-Ergebnisse haben Vorrang; Beispiele nur für Szenarien ohne Ergebnis."""
        verification = self.audit.verify()
        if not verification["valid"]:
            raise RuntimeError(f"Audit chain is invalid at event {verification['broken_at_seq']}; replay refused.")
        processed_dir = Path(os.getenv("PROCESSED_DIR", PROCESSED_DIR))
        sources = {p.stem.removeprefix("bundle_"): p for p in sorted(EXAMPLES_DIR.glob("bundle_*.json"))}
        sources |= {p.stem: p for p in sorted(processed_dir.glob("*.json"))}
        for path in sources.values():
            bundle = json.loads(path.read_text(encoding="utf-8"))
            fingerprint = bundle_fingerprint(bundle)
            feedback_path = path.parent / bundle["scenario"]["id"] / "evidence.json"
            feedback_evidence = ([Evidence(**e) for e in json.loads(feedback_path.read_text(encoding="utf-8"))
                                  if e["source_type"] == "feedback"] if feedback_path.exists() else None)
            state = ScenarioState(bundle, feedback_evidence)
            self.states[state.scenario.id] = state
            history = self.audit.events(scenario_id=state.scenario.id)
            if history:
                recorded = recorded_fingerprint(history)
                if recorded and recorded != fingerprint:
                    raise RuntimeError(f"{state.scenario.id}: bundle changed since the recorded decisions; "
                                       "replay refused. Review the new bundle with a separate AUDIT_DB.")
                if not recorded:
                    state.scenario.warnings.append(
                        "Legacy audit has no bundle fingerprint: source identity cannot be verified.")
                    logging.getLogger(__name__).warning(
                        "%s: legacy audit has no bundle fingerprint; source identity cannot be verified",
                        state.scenario.id)
                result = replay(state, history)  # PM-Entscheidungen überleben den Neustart (L19)
                if result["skipped"]:
                    logging.getLogger(__name__).warning(
                        "%s: %s audit events reference requirements missing from the current bundle",
                        state.scenario.id, result["skipped"])
            self._rescore(state)  # Score immer aus der Formel (mit evtl. wiederhergestellten Gewichten)
            if not history:
                self._log_initial_proposals(state, path.name, fingerprint)

    def _log_initial_proposals(self, state: ScenarioState, source: str, fingerprint: str) -> None:
        """Erste Einträge im Prüfpfad: woher die Vorschläge stammen."""
        sid = state.scenario.id
        self.audit.append("PIPELINE_LOADED", sid, SYSTEM, f"Ergebnisse geladen aus {source}",
                          {"funnel": state.funnel, "bundle_sha256": fingerprint,
                           "provenance": state.provenance})
        self.audit.append("EVIDENCE_INGESTED", sid, SYSTEM, f"Einleseergebnis aus {source} registriert",
                          {"count": state.funnel.get("evidence", len(state.evidence)),
                           "data_coverage": state.scenario.data_coverage.model_dump(), "source": source})
        self.audit.append("SIGNALS_EXTRACTED", sid, SYSTEM, f"Befundergebnis aus {source} registriert",
                          {"count": len(state.signals), "source": source,
                           "model": (state.provenance or {}).get("llm_model", "not recorded in snapshot")})
        for req in sorted(state.requirements.values(), key=lambda r: r.rank):
            self.audit.append(
                "REQUIREMENT_PROPOSED", sid, Actor(type=ActorType.AI, name="pipeline"),
                req.rationale, {"score": req.score, "evidence_level": req.evidence_level.value,
                                "signal_ids": req.signal_ids}, requirement_id=req.id,
            )
        for item in state.discarded:  # Begründung = Scope-Grund der KI; ohne requirement_id, es gibt keine Anforderung
            self.audit.append(
                "REQUIREMENT_DISCARDED", sid, Actor(type=ActorType.AI, name="scope-waechter"),
                item.get("reason") or "Außerhalb des Scopes",
                {"title": item["title"], "signal_ids": item["signal_ids"]},
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
        self._validate_pm(actor, rationale)
        with self._lock:
            return self._decide(req_id, action, actor, rationale, changes)

    @staticmethod
    def _validate_pm(actor: Actor, rationale: str) -> None:
        if actor.type != ActorType.HUMAN or not actor.name.strip() or not rationale.strip():
            raise ValueError("PM-Aktionen brauchen einen Menschen, einen Namen und eine Begründung.")

    @staticmethod
    def _candidate(state: ScenarioState) -> ScenarioState:
        candidate = copy(state)
        candidate.requirements = {i: r.model_copy(deep=True) for i, r in state.requirements.items()}
        candidate.weights = dict(state.weights)
        return candidate

    def _decide(self, req_id, action, actor, rationale, changes) -> Requirement:
        state, req = self.find_requirement(req_id)
        state = self._candidate(state)
        req = state.requirements[req_id]
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
            # model_validate statt model_copy: prüft die neuen Werte (z. B. effort nur S/M/L),
            # sonst landet ein ungültiger Zustand im Store und im Prüfpfad.
            try:
                req = Requirement.model_validate({**before, **changes, "version": req.version + 1})
            except ValidationError as err:
                raise ValueError(f"Ungültige Änderung: {err.errors()[0]['msg']}") from err
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
        self.states[state.scenario.id] = state
        return state.requirements[req_id]

    def set_weights(
        self, scenario_id: str, weights: dict[str, float], actor: Actor, rationale: str
    ) -> list[Requirement]:
        self._validate_pm(actor, rationale)
        with self._lock:
            return self._set_weights(scenario_id, weights, actor, rationale)

    def _set_weights(self, scenario_id, weights, actor, rationale) -> list[Requirement]:
        state = self._candidate(self.get(scenario_id))
        before = {r.id: (r.rank, r.score) for r in state.requirements.values()}
        old_weights = state.weights
        state.weights = scoring.normalize_weights(weights)
        self._rescore(state)
        changes = {r.id: {"before": before[r.id], "after": (r.rank, r.score)} for r in state.requirements.values()
                   if before[r.id] != (r.rank, r.score)}
        self.audit.append("WEIGHTS_CHANGED", scenario_id, actor, rationale,
                          {"weights": {"before": old_weights, "after": state.weights}, "rank_changes": changes})
        self.states[scenario_id] = state
        return self.ranked(scenario_id)

    def _rescore(self, state: ScenarioState) -> None:
        """Neu rechnen mit den gespeicherten Faktorwerten, dann neu ranken."""
        for req in state.requirements.values():
            values = {k: f.value for k, f in req.score_breakdown.items()}
            values["effort_inverse"] = scoring.effort_factor(req.effort)
            texts = {k: f.explanation for k, f in req.score_breakdown.items()}
            texts["effort_inverse"] = f"effort estimate {req.effort}"
            req.score, req.score_breakdown = scoring.score(values, texts, req.evidence_level, state.weights)
        for rank, req in enumerate(sorted(state.requirements.values(), key=lambda r: -r.score), start=1):
            req.rank = rank
        robustness = compute_robustness(list(state.requirements.values()), weights=state.weights)
        for req in state.requirements.values():
            req.robustness = robustness[req.id]

    def ranked(self, scenario_id: str) -> list[Requirement]:
        return sorted(self.get(scenario_id).requirements.values(), key=lambda r: r.rank)
