"""Was die KI als Entwurf liefert (Schema für ask_json). Zahlen, Rang und Stufe kommen NICHT von der KI."""

from __future__ import annotations

from pydantic import BaseModel

from core.model_parts import Horizon
from core.models import Category


class RequirementDraft(BaseModel):
    title: str
    description: str
    acceptance_criterion: str
    category: Category
    signal_ids: list[str]
    assumptions: list[str] = []
    uncertainties: list[str] = []
    effort: str = "M"
    forward_looking: bool = False
    horizon: Horizon = "today"
    in_scope: bool = True
    scope_reason: str = ""


class RequirementDrafts(BaseModel):
    drafts: list[RequirementDraft]
