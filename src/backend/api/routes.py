"""HTTP-Endpunkte (Owner: Lead). Vertrag für Menschen: src/shared/API.md.

Die Routen sind bewusst dünn: Sie prüfen Eingaben und rufen Store bzw. Engine auf.
Die Logik liegt in core/ und requirements_engine/, damit sie ohne HTTP testbar ist.
"""

from __future__ import annotations

import csv
import io
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from core.models import Actor, ActorType, AuditEvent, Requirement, Scenario, Signal
from core.store import Store
from requirements_engine.challenge import answer_challenge

router = APIRouter(prefix="/api")


class DecisionIn(BaseModel):
    action: Literal["approve", "reject", "edit", "challenge"]
    actor: str = Field(examples=["pm.mueller"])
    rationale: str = Field(min_length=3)  # Pflicht: jede Entscheidung braucht ein Warum
    changes: dict | None = None           # nur bei "edit"
    question: str | None = None           # nur bei "challenge"


class DecisionOut(BaseModel):
    requirement: Requirement
    ai_answer: dict | None = None


class WeightsIn(BaseModel):
    weights: dict[str, float]
    actor: str
    rationale: str = Field(min_length=3)


def _store(request: Request) -> Store:
    return request.app.state.store


def _not_found(err: KeyError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(err.args[0]))


@router.get("/scenarios", response_model=list[Scenario])
def list_scenarios(request: Request):
    return [s.scenario for s in _store(request).states.values()]


@router.get("/scenarios/{scenario_id}/funnel")
def funnel(scenario_id: str, request: Request) -> dict:
    """Zahlen für den Trichter; Freigaben werden live gezählt, nicht aus der Datei gelesen."""
    try:
        state = _store(request).get(scenario_id)
    except KeyError as err:
        raise _not_found(err) from err
    approved = sum(r.status.value == "approved" for r in state.requirements.values())
    return {**state.funnel, "requirements": len(state.requirements), "approved": approved}


@router.get("/scenarios/{scenario_id}/signals", response_model=list[Signal])
def signals(scenario_id: str, request: Request):
    try:
        return list(_store(request).get(scenario_id).signals.values())
    except KeyError as err:
        raise _not_found(err) from err


@router.get("/scenarios/{scenario_id}/requirements", response_model=list[Requirement])
def requirements(scenario_id: str, request: Request):
    try:
        return _store(request).ranked(scenario_id)
    except KeyError as err:
        raise _not_found(err) from err


@router.get("/requirements/{req_id}")
def requirement_detail(req_id: str, request: Request) -> dict:
    """Alles für die Detailseite: Anforderung + Befunde + Belege + Verlauf."""
    store = _store(request)
    try:
        state, req = store.find_requirement(req_id)
    except KeyError as err:
        raise _not_found(err) from err
    sigs = [state.signals[s] for s in req.signal_ids if s in state.signals]
    ev_ids = {e for s in sigs for e in s.evidence_ids}
    return {
        "requirement": req,
        "signals": sigs,
        "evidence": [state.evidence[e] for e in sorted(ev_ids) if e in state.evidence],
        "history": store.audit.events(requirement_id=req_id),
    }


@router.post("/requirements/{req_id}/decision", response_model=DecisionOut)
def decide(req_id: str, body: DecisionIn, request: Request):
    store = _store(request)
    pm = Actor(type=ActorType.HUMAN, name=body.actor)
    try:
        req = store.decide(req_id, body.action, pm, body.rationale, body.changes)
    except KeyError as err:
        raise _not_found(err) from err
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    ai_answer = None
    if body.action == "challenge":
        state, _ = store.find_requirement(req_id)
        sigs = [state.signals[s] for s in req.signal_ids if s in state.signals]
        evidence = [state.evidence[e] for s in sigs for e in s.evidence_ids if e in state.evidence]
        ai_answer = answer_challenge(req, body.question or body.rationale, sigs, evidence)
        store.audit.append("AI_RESPONDED", state.scenario.id, Actor(type=ActorType.AI, name="challenge-engine"),
                           "Antwort auf PM-Challenge mit Belegen und Gegenbelegen", ai_answer, requirement_id=req_id)
    return DecisionOut(requirement=req, ai_answer=ai_answer)


@router.put("/scenarios/{scenario_id}/weights", response_model=list[Requirement])
def set_weights(scenario_id: str, body: WeightsIn, request: Request):
    try:
        return _store(request).set_weights(scenario_id, body.weights, Actor(type=ActorType.HUMAN, name=body.actor),
                                           body.rationale)
    except KeyError as err:
        raise _not_found(err) from err
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


@router.get("/audit", response_model=list[AuditEvent])
def audit(request: Request, scenario_id: str | None = None, requirement_id: str | None = None):
    return _store(request).audit.events(scenario_id, requirement_id)


@router.get("/audit/verify")
def audit_verify(request: Request) -> dict:
    return _store(request).audit.verify()


def _csv_safe(value: object) -> str:
    """Schutz vor Formel-Injection: Excel führt Zellen mit = + - @ als Formel aus.
    Texte stammen teils aus LLM/Webquellen, daher mit ' entschärfen."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@router.get("/scenarios/{scenario_id}/export", response_class=PlainTextResponse)
def export_csv(scenario_id: str, request: Request):
    """Die geforderte "strukturierte Anforderungsliste" als CSV (Excel-tauglich)."""
    try:
        reqs = _store(request).ranked(scenario_id)
    except KeyError as err:
        raise _not_found(err) from err
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["id", "rank", "title", "description", "acceptance_criterion", "signals", "score",
                     "rationale", "evidence_level", "assumptions", "uncertainties", "status"])
    for r in reqs:
        row = [r.id, r.rank, r.title, r.description, r.acceptance_criterion, ",".join(r.signal_ids),
               r.score, r.rationale, r.evidence_level.value, " | ".join(r.assumptions),
               " | ".join(r.uncertainties), r.status.value]
        writer.writerow([_csv_safe(v) for v in row])
    return buf.getvalue()
