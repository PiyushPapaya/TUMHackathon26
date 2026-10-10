"""PM-Entscheidungen aus dem Prüfpfad neu abspielen (Owner: Lead, Ticket L19).

Warum: Der Prüfpfad (audit.db) ist die einzige Wahrheit über PM-Aktionen. Ohne Replay wären
Freigaben, Bearbeitungen und Gewichte nach jedem Server-Neustart weg (Demo-Risiko), obwohl
sie im Prüfpfad stehen. Wir spielen deshalb dieselben Ereignisse in derselben Reihenfolge ab.
Ereignisse zu Anforderungen, die es im neuen Bundle nicht mehr gibt, werden übersprungen
(und gezählt), statt den Start abzubrechen.
"""

from __future__ import annotations

from core.models import Requirement, Status

STATUS_BY_EVENT = {"PM_APPROVE": Status.APPROVED, "PM_REJECT": Status.REJECTED, "PM_CHALLENGE": Status.CHALLENGED}
EDITABLE = {"title", "description", "acceptance_criterion", "effort", "assumptions", "uncertainties", "version"}


def replay(state, events: list) -> dict:
    """Wendet PM-Ereignisse auf den frisch geladenen Zustand an. Liefert Zählung für das Log."""
    applied, skipped = 0, 0
    for event in events:
        if event.event_type == "WEIGHTS_CHANGED":
            state.weights = event.payload.get("weights", {}).get("after", state.weights)
            applied += 1
            continue
        if event.event_type not in STATUS_BY_EVENT and event.event_type != "PM_EDIT":
            continue  # KI-/System-Ereignisse ändern keinen Zustand
        req = state.requirements.get(event.requirement_id or "")
        if req is None:
            skipped += 1
            continue
        if event.event_type == "PM_EDIT":
            after = {k: v["after"] for k, v in event.payload.items() if k in EDITABLE and isinstance(v, dict)}
            req = Requirement.model_validate({**req.model_dump(mode="json"), **after})
            state.requirements[req.id] = req
        else:
            req.status = STATUS_BY_EVENT[event.event_type]
        applied += 1
    return {"applied": applied, "skipped": skipped}
