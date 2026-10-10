"""Endpunkte für Prompt-Linse, Matrix, Markt-Gegenstück und Memo (Owner: Lead). Vertrag: src/shared/API.md.

Eigene Datei, weil routes.py und views.py sonst über 200 Zeilen wachsen. Dünn: prüfen, Zustand holen,
reine Funktion aus core/ aufrufen. Nur die Linse schreibt etwas, und zwar nur in den Prüfpfad
(AI_LENS_SUGGESTED); Gewichte ändert erst der PM über PUT /weights.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from core import lens, req_insights
from core.models import Actor, ActorType
from core.store import Store

router = APIRouter(prefix="/api")


class LensIn(BaseModel):
    question: str = Field(min_length=1, max_length=500, examples=["Familien in den USA, Fokus Laden und Platz"])
    actor: str = Field(min_length=1, examples=["pm.mueller"])


def _store(request: Request) -> Store:
    return request.app.state.store


def _state(request: Request, scenario_id: str):
    try:
        return _store(request).get(scenario_id)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err.args[0])) from err


@router.post("/scenarios/{scenario_id}/lens")
def run_lens(scenario_id: str, body: LensIn, request: Request) -> dict:
    """PM-Frage -> Gewichte + Filter (KI oder Regeln) -> Top 5, in Python gerechnet. Store bleibt unverändert."""
    state = _state(request, scenario_id)
    result = lens.run_lens(state, body.question.strip())
    model = "lens-rules" if result["source"] == "rules" else "lens-llm"
    _store(request).audit.append(
        "AI_LENS_SUGGESTED", scenario_id, Actor(type=ActorType.AI, name=model),
        result["interpretation"] or "Linse ohne Deutung",
        {"question": result["question"], "asked_by": body.actor, "weights": result["weights"],
         "filters": result["filters"], "top_ids": [t["requirement"]["id"] for t in result["top"]]},
    )
    return result


@router.get("/scenarios/{scenario_id}/matrix")
def matrix(scenario_id: str, request: Request) -> dict:
    """Heute/Zukunft × Evidenzstufe und Ausstattungs-Lücke je Anforderung."""
    return req_insights.matrix(_state(request, scenario_id))


@router.get("/requirements/{req_id}/counterparts")
def counterparts(req_id: str, request: Request) -> list[dict]:
    """Gegenstück derselben Anforderung in allen anderen Szenarien (Rang, Score) oder "kein Gegenstück"."""
    store = _store(request)
    try:
        state, req = store.find_requirement(req_id)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err.args[0])) from err
    return req_insights.counterparts(state, req, store.states)


@router.get("/scenarios/{scenario_id}/memo", response_class=PlainTextResponse)
def memo(scenario_id: str, request: Request) -> str:
    """Entscheidungs-Memo als Markdown: freigegebene Anforderungen (sonst Top 5) + Prüfpfad-Status."""
    state = _state(request, scenario_id)
    return req_insights.memo(state, _store(request).audit.verify())
