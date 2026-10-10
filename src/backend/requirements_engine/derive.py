"""Pfad C: Befunde -> Anforderungen (KI schlägt vor) -> Score (Formel) -> Rang.

Vertrag (nicht ändern ohne Lead):
    derive_requirements(scenario, signals, evidence, context) -> list[Requirement]

Arbeitsteilung KI vs. Code (das zeigen wir der Jury):
- KI (core.llm.ask_json): Befunde zu Anforderungen bündeln, kundenorientiert formulieren,
  messbares Akzeptanzkriterium, Annahmen, Unsicherheiten, grober Aufwand S/M/L,
  Scope-Prüfung (Regulatorik/Technik/Preis -> verwerfen mit Grund).
- Code: Faktorwerte (customer_pain, reach, satisfaction_gap, competitive_pressure,
  future_relevance) aus Zählungen berechnen, Evidenzstufe (evidence_level.classify),
  Score (scoring.score), Rang, OfferCheck gegen context["offer"].

Regeln für den Prompt:
- Nur signal_ids aus der Eingabe; jede Anforderung >= 1 Befund (Test prüft das).
- "customer-facing": beschreibt, was der Kunde erlebt, keine Bauteile.
- Akzeptanzkriterium mit Zahl (wie BMW-Folie: "Range: 600 or 700 mi?").
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from core.llm import ask_json
from core.models import (
    Category,
    Evidence,
    OfferCheck,
    Requirement,
    Scenario,
    Signal,
)
from requirements_engine import evidence_level, scoring
from requirements_engine.derive_checks import conflict_notes, make_ids_unique, not_covered, stable_key
from requirements_engine.factors import compute_factors, rationale_from
from requirements_engine.offer_check import check, load_offer
from requirements_engine.robustness import compute_robustness

SYSTEM_PROMPT = """You are a product analyst for BMW. You turn customer findings (signals) into
requirements for the successor vehicle, 3-5 years ahead. Write ALL text in English.
Rules for every requirement:
- Customer-facing: describe what the customer experiences, never components
  (good: "Adjust volume without looking at the screen"; bad: "rotary encoder part X").
- Measurable: the acceptance_criterion contains a concrete number or test condition
  (like "range of 600 or 700 miles?", "cooler for how many bottles?"). Never leave placeholders
  such as "X" or "±X km": pick a reasonable target and name it in `assumptions`.
- Realistic for the successor in 3-5 years. Put forward-looking guesses into `assumptions`
  and set forward_looking=true if the requirement rests mainly on a trend.
- A delight (strength) becomes a keep-requirement ("Keep ride comfort at least at today's level").
- ONE requirement per distinct customer need. Never split one need into several near-identical
  requirements (e.g. do not write three variants of "physical controls" from one signal).
  If two requirements would cite the same signal, merge them into one.
- Signals that list each other in `conflicts_with` contradict each other (e.g. a praised display vs.
  distracting touch controls). Never average a conflict away: if one requirement cites both sides, it
  must address both sides explicitly (e.g. keep the strength while fixing the weakness).
- Every requirement must be directly supported by the signals it cites. Do not invent extra
  capabilities the signals never mention (e.g. an offline fallback from a charging complaint);
  put such ideas into `assumptions` or `uncertainties` instead.
- Out of scope: regulation/homologation, engineering specification, price or business case.
  A wish for a specific component, part or technical value (resolution, voltage, kW) is an
  engineering specification: output it as its own draft with in_scope=false and a scope_reason.
  If a real customer outcome stands behind it, add a separate customer-facing requirement for that.
  Do not hide discarded drafts, we log them.
- Use ONLY signal_ids from the input. Every requirement cites at least one signal.
- Cover EVERY complaint and unmet_need signal in at least one requirement (merge related ones, but
  never drop a topic silently). Delights only need a keep-requirement when they are strong.
- effort is a rough guess: S, M or L. Aim for 10-15 in-scope requirements; above 15 the PM loses
  the overview, so merge related needs instead of adding more."""


class RequirementDraft(BaseModel):
    """Was die KI vorschlägt. Zahlen, Rang und Stufe kommen NICHT von der KI, sondern aus Code."""

    title: str
    description: str
    acceptance_criterion: str
    category: Category
    signal_ids: list[str]
    assumptions: list[str] = []
    uncertainties: list[str] = []
    effort: str = "M"
    forward_looking: bool = False
    in_scope: bool = True
    scope_reason: str = ""


class RequirementDrafts(BaseModel):
    drafts: list[RequirementDraft]


def _compact(signals: list[Signal]) -> str:
    """Nur das, was die KI zum Bündeln braucht: weniger Text = billiger und genauer."""
    rows = [
        {"id": s.id, "kind": s.kind.value, "category": s.category.value, "title": s.title,
         "summary": s.summary, "mention_count": s.mention_count,
         "source_types": [t.value for t in s.source_types], "conflicts_with": s.conflicts_with}
        for s in signals
    ]
    return json.dumps(rows, ensure_ascii=False)


def derive_all(
    scenario: Scenario, signals: list[Signal], evidence: list[Evidence], context: dict
) -> tuple[list[Requirement], list[dict]]:
    """Liefert (Anforderungen nach Rang, verworfene Out-of-scope-Entwürfe mit Grund)."""
    if not signals:  # nichts zu bündeln: die KI nicht fragen (kostet Geld und könnte Themen erfinden)
        return [], []
    known = {s.id: s for s in signals}
    answer = ask_json(SYSTEM_PROMPT, f"Scenario: {scenario.model_name} ({scenario.market})\n"
                      f"Signals:\n{_compact(signals)}", RequirementDrafts)
    kept: list[tuple[RequirementDraft, list[Signal]]] = []
    discarded: list[dict] = []
    for draft in answer.drafts:
        # Halluzinationsschutz: nur IDs, die es in der Eingabe wirklich gibt.
        ids = [i for i in dict.fromkeys(draft.signal_ids) if i in known]
        if not ids:
            continue
        if not draft.in_scope:
            discarded.append({"title": draft.title, "reason": draft.scope_reason, "signal_ids": ids})
            continue
        kept.append((draft, [known[i] for i in ids]))
    discarded += not_covered(signals, kept, discarded)
    # reach braucht die größte Nennungszahl ALLER Anforderungen, darum erst jetzt bauen.
    max_mentions = max((sum(s.mention_count for s in linked) for _, linked in kept), default=0)
    by_id = {e.id: e for e in evidence}
    requirements = [_build(scenario, d, linked, by_id, max_mentions, context) for d, linked in kept]
    make_ids_unique(requirements)
    offer = _load_offer(context)
    if offer:  # "Gibt es das schon?": pro Anforderung ein KI-Abgleich gegen die Optionsliste
        for req in requirements:
            req.offer_check = check(req.title, offer)
    requirements.sort(key=lambda r: -r.score)  # stabil: gleiche Punkte behalten KI-Reihenfolge
    for rank, req in enumerate(requirements, start=1):
        req.rank = rank
    robustness = compute_robustness(requirements)  # erst nach dem Rang: die Spanne muss den echten Rang enthalten
    for req in requirements:
        req.robustness = robustness[req.id]
    return requirements, discarded


def _load_offer(context: dict) -> list[dict]:
    """Optionsliste lesen; fehlt oder kaputt, läuft die Pipeline ohne Abgleich weiter (Status unknown)."""
    path = context.get("option_list_path")
    if not path or not Path(path).exists():
        return []
    try:
        return load_offer(Path(path))
    except Exception:
        return []


def _build(
    scenario: Scenario, draft: RequirementDraft, linked: list[Signal],
    by_id: dict[str, Evidence], max_mentions: int, context: dict,
) -> Requirement:
    mentions = sum(s.mention_count for s in linked)
    sources = {t for s in linked for t in s.source_types}
    level, level_reason = evidence_level.classify(mentions, sources, draft.forward_looking)
    effort = draft.effort if draft.effort in ("S", "M", "L") else "M"
    factors, explanations = compute_factors(linked, by_id, max_mentions, draft.forward_looking, effort, context)
    points, breakdown = scoring.score(factors, explanations, level)
    key = stable_key([s.id for s in linked])
    return Requirement(
        id=f"REQ-{scenario.id}-{key}", stable_key=key, title=draft.title, description=draft.description,
        acceptance_criterion=draft.acceptance_criterion, category=draft.category,
        signal_ids=[s.id for s in linked], score=points, rank=0, score_breakdown=breakdown,
        rationale=f"{rationale_from(breakdown)} Evidence level {level.value}: {level_reason}",
        evidence_level=level, assumptions=draft.assumptions,
        uncertainties=[*conflict_notes(linked), *draft.uncertainties],
        offer_check=OfferCheck(status="unknown", note="Option list not checked yet (C5)."),
        effort=effort,
    )


def derive_requirements(
    scenario: Scenario, signals: list[Signal], evidence: list[Evidence], context: dict
) -> list[Requirement]:
    return derive_all(scenario, signals, evidence, context)[0]
