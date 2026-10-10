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

from core.llm import ask_json
from core.models import (
    Evidence,
    OfferCheck,
    Requirement,
    Scenario,
    Signal,
    SignalKind,
)
from requirements_engine import evidence_level, scoring
from requirements_engine.blocks import merge_overlapping, separate_bets, split_into_blocks
from requirements_engine.business import business_context
from requirements_engine.derive_checks import (
    badges_for,
    conflict_notes,
    make_ids_unique,
    next_gen_problem,
    not_covered,
    stable_key,
)
from requirements_engine.drafts import RequirementDraft, RequirementDrafts
from requirements_engine.factors import compute_factors, rationale_from
from requirements_engine.offer_check import check, load_offer_for
from requirements_engine.prompts import SYSTEM_PROMPT
from requirements_engine.robustness import compute_robustness


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
    kept: list[tuple[RequirementDraft, list[Signal]]] = []
    discarded: list[dict] = []
    for block_name, block in split_into_blocks(signals):  # ein KI-Aufruf pro Themenblock (W-C5)
        known = {s.id: s for s in block}
        answer = ask_json(SYSTEM_PROMPT, f"Scenario: {scenario.model_name} ({scenario.market})\n"
                          f"Topic block: {block_name}\nSignals:\n{_compact(block)}", RequirementDrafts)
        for draft in answer.drafts:
            # Halluzinationsschutz: nur IDs aus DIESEM Block, denn nur die hat die KI gesehen.
            ids = [i for i in dict.fromkeys(draft.signal_ids) if i in known]
            if not ids:
                continue
            if not draft.in_scope:
                discarded.append({"title": draft.title, "reason": draft.scope_reason, "signal_ids": ids})
                continue
            linked = [known[i] for i in ids]
            problem = next_gen_problem(draft.assumptions, linked) if draft.horizon == "next_gen" else None
            if problem:
                discarded.append({"title": draft.title, "reason": problem, "signal_ids": ids})
                continue
            kept.append((draft, linked))
    kept = separate_bets(merge_overlapping(kept))
    discarded += not_covered(signals, kept, discarded)
    # reach braucht die größte Nennungszahl ALLER Anforderungen, darum erst jetzt bauen.
    max_mentions = max((sum(s.mention_count for s in linked) for _, linked in kept), default=0)
    by_id = {e.id: e for e in evidence}
    requirements = [_build(scenario, d, linked, by_id, max_mentions, context) for d, linked in kept]
    make_ids_unique(requirements)
    offer, offer_note = load_offer_for(context)
    for req in requirements:  # "Gibt es das schon?": pro Anforderung ein KI-Abgleich gegen die Optionsliste
        req.offer_check = check(req.title, offer) if offer else OfferCheck(status="unknown", note=offer_note)
    requirements.sort(key=lambda r: -r.score)  # stabil: gleiche Punkte behalten KI-Reihenfolge
    for rank, req in enumerate(requirements, start=1):
        req.rank = rank
    robustness = compute_robustness(requirements)  # erst nach dem Rang: die Spanne muss den echten Rang enthalten
    for req in requirements:
        req.robustness = robustness[req.id]
    return requirements, discarded


def _build(
    scenario: Scenario, draft: RequirementDraft, linked: list[Signal],
    by_id: dict[str, Evidence], max_mentions: int, context: dict,
) -> Requirement:
    mentions = sum(s.mention_count for s in linked)
    sources = {t for s in linked for t in s.source_types}
    # Direkte Kundennennungen: ohne Trend- und Wettbewerbsbefunde (die stammen aus dem Web).
    customer = sum(s.mention_count for s in linked if s.kind not in (SignalKind.TREND, SignalKind.COMPETITOR_ADVANTAGE))
    level, level_reason = evidence_level.classify(
        mentions, sources, draft.forward_looking, next_gen=draft.horizon == "next_gen", customer_mentions=customer)
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
        offer_check=OfferCheck(status="unknown", note="Option list not checked yet."),
        effort=effort, horizon=draft.horizon, badges=badges_for(draft.horizon, level.value),
        business=business_context(context.get("sales", {})),
    )


def derive_requirements(
    scenario: Scenario, signals: list[Signal], evidence: list[Evidence], context: dict
) -> list[Requirement]:
    return derive_all(scenario, signals, evidence, context)[0]
