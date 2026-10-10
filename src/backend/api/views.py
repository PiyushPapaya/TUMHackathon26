"""Endpunkte für fertige Ansichten (Owner: Lead). Vertrag für Menschen: src/shared/API.md.

Dünn wie routes.py: Eingaben prüfen, Zustand holen, eine reine Funktion aus core/ aufrufen.
Keine dieser Routen schreibt etwas; nur PUT /weights und POST /decision (routes.py) ändern Zustand.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from core import insights, portfolio, views
from core.store import Store

router = APIRouter(prefix="/api")

EVENT_SENTENCE = {
    "PIPELINE_LOADED": "Pipeline-Ergebnis geladen", "REQUIREMENT_PROPOSED": "KI schlägt Anforderung vor",
    "REQUIREMENT_DISCARDED": "KI verwirft Entwurf (außerhalb des Scopes)", "PM_APPROVE": "PM gibt frei",
    "PM_REJECT": "PM lehnt ab", "PM_EDIT": "PM bearbeitet", "PM_CHALLENGE": "PM stellt Gegenfrage",
    "AI_RESPONDED": "KI antwortet mit Belegen", "WEIGHTS_CHANGED": "PM ändert Gewichte",
    "AI_LENS_SUGGESTED": "KI schlägt Linse (Gewichte + Filter) vor",
}


class WhatIfIn(BaseModel):
    weights: dict[str, float]


def _store(request: Request) -> Store:
    return request.app.state.store


def _state(request: Request, scenario_id: str):
    try:
        return _store(request).get(scenario_id)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err.args[0])) from err


@router.get("/scenarios")
def list_scenarios(request: Request) -> list[dict]:
    """Szenario-Wähler: Szenario + Datenabdeckung + Badge (reich / dünn / Kaltstart) + Kopfzahlen."""
    return [views.scenario_card(s) for s in _store(request).states.values()]


@router.get("/scenarios/{scenario_id}/overview")
def overview(scenario_id: str, request: Request) -> dict:
    return views.overview(_state(request, scenario_id))


@router.get("/requirements/{req_id}/explain")
def explain(req_id: str, request: Request) -> dict:
    store = _store(request)
    try:
        state, req = store.find_requirement(req_id)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err.args[0])) from err
    return views.explain(state, req, store.audit.events(requirement_id=req_id))


@router.post("/scenarios/{scenario_id}/whatif")
def whatif(scenario_id: str, body: WhatIfIn, request: Request) -> list[dict]:
    """Live-Vorschau für den Gewichte-Regler. Speichert nichts und schreibt kein Audit."""
    try:
        return views.whatif(_state(request, scenario_id), body.weights)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


@router.get("/portfolio")
def portfolio_matrix(request: Request) -> dict:
    return portfolio.portfolio(_store(request).states)


@router.get("/compare")
def compare(request: Request, a: str = Query(examples=["G60-US"]), b: str = Query(examples=["G60-EU"])) -> dict:
    return portfolio.compare(_state(request, a), _state(request, b))


@router.get("/scenarios/{scenario_id}/opportunities")
def opportunities(scenario_id: str, request: Request) -> dict:
    return insights.opportunities(_state(request, scenario_id))


@router.get("/scenarios/{scenario_id}/trends")
def trends(scenario_id: str, request: Request) -> dict:
    return insights.trends(_state(request, scenario_id))


@router.get("/scenarios/{scenario_id}/gaps")
def gaps(scenario_id: str, request: Request) -> dict:
    return insights.gaps(_state(request, scenario_id))


@router.get("/scenarios/{scenario_id}/evidence")
def evidence(scenario_id: str, request: Request, signal: str | None = None, segment: str | None = None,
             q: str | None = None, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)) -> dict:
    return insights.evidence_page(_state(request, scenario_id), signal, segment, q, page, size)


@router.get("/audit/timeline")
def audit_timeline(request: Request, scenario_id: str | None = None, requirement_id: str | None = None) -> list[dict]:
    """Prüfpfad als lesbare Zeitleiste: ein Satz pro Ereignis, wer (KI/Mensch/System), warum."""
    return [{"seq": e.seq, "ts": e.ts, "actor": e.actor, "requirement_id": e.requirement_id,
             "event_type": e.event_type, "sentence": EVENT_SENTENCE.get(e.event_type, e.event_type),
             "rationale": e.rationale}
            for e in _store(request).audit.events(scenario_id, requirement_id)]
