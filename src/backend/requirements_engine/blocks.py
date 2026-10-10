"""Themenblöcke für die Ableitung (Pfad C, W-C5) und Zusammenführen überlappender Entwürfe.

Warum Blöcke: Ein Aufruf über alle ~55 Befunde ließ die KI Beschwerden vergessen und hielt die Liste kurz. Pro Block
sieht die KI nur ~20 Befunde und deckt sie vollständig ab. Die Zuordnung Kategorie -> Block ist eine feste Tabelle:
erklärbar, reproduzierbar, ohne KI. Verworfen: Clustering per KI (schwankt), ein Aufruf je Kategorie (Blöcke zu klein,
Themen wie Display und Bedienung gehören zusammen).
"""

from __future__ import annotations

from core.models import Category, Signal, SignalKind
from requirements_engine.drafts import RequirementDraft

BLOCKS: list[tuple[str, list[Category]]] = [
    ("Driving, range and assistance",
     [Category.DRIVING_EXPERIENCE, Category.RANGE_CHARGING, Category.DRIVER_ASSISTANCE]),
    ("Digital, controls and packages", [Category.INFOTAINMENT_DIGITAL, Category.VARIANTS_PACKAGES]),
    ("Space, comfort and design",
     [Category.COMFORT_SPACE, Category.INTERIOR, Category.EXTERIOR, Category.QUALITY_PERCEPTION]),
]
# Ab dieser Überlappung der Befund-IDs (bezogen auf den kleineren Entwurf) meinen zwei Entwürfe dasselbe Bedürfnis.
MIN_OVERLAP = 0.5


def split_into_blocks(signals: list[Signal]) -> list[tuple[str, list[Signal]]]:
    """Befunde auf die Blöcke verteilen; leere Blöcke entfallen (kein KI-Aufruf), kein Befund geht verloren."""
    block_of = {category: name for name, categories in BLOCKS for category in categories}
    fallback = BLOCKS[-1][0]  # eine künftige Kategorie landet im letzten Block statt unterzugehen
    grouped: dict[str, list[Signal]] = {name: [] for name, _ in BLOCKS}
    for signal in signals:
        grouped[block_of.get(signal.category, fallback)].append(signal)
    return [(name, group) for name, group in grouped.items() if group]


def _overlap(a: list[Signal], b: list[Signal]) -> float:
    ids_a, ids_b = {s.id for s in a}, {s.id for s in b}
    return len(ids_a & ids_b) / min(len(ids_a), len(ids_b))


def merge_overlapping(
    items: list[tuple[RequirementDraft, list[Signal]]],
) -> list[tuple[RequirementDraft, list[Signal]]]:
    """Entwürfe, die zu mindestens 50 % dieselben Befunde zitieren, werden eine Anforderung.

    Sonst zählen dieselben Kunden mehrfach und der Rang stimmt nicht. Heute-Anforderung und Wette bleiben getrennt:
    Die Wette ist absichtlich eine zweite Aussage zum selben Thema. Der Entwurf mit mehr Befunden liefert den Text.
    """
    merged: list[tuple[RequirementDraft, list[Signal]]] = []
    for draft, linked in items:
        target = next((i for i, (d, other) in enumerate(merged)
                       if d.horizon == draft.horizon and _overlap(linked, other) >= MIN_OVERLAP), None)
        if target is None:
            merged.append((draft, linked))
            continue
        old_draft, old_linked = merged[target]
        main = old_draft if len(old_linked) >= len(linked) else draft
        union = list({s.id: s for s in [*old_linked, *linked]}.values())  # nach ID, Reihenfolge bleibt
        merged[target] = (main.model_copy(update={
            "assumptions": list(dict.fromkeys([*old_draft.assumptions, *draft.assumptions])),
            "uncertainties": list(dict.fromkeys([*old_draft.uncertainties, *draft.uncertainties])),
            "forward_looking": old_draft.forward_looking or draft.forward_looking,
            "signal_ids": [s.id for s in union],
        }), union)
    return merged


def separate_bets(
    items: list[tuple[RequirementDraft, list[Signal]]],
) -> list[tuple[RequirementDraft, list[Signal]]]:
    """Eine Wette darf keine Kundenbefunde zitieren, die schon eine Heute-Anforderung trägt.

    Echter Fund (F70-EU): Eine Wette lieh sich eine Beschwerde mit 96 Nennungen, die auch eine Heute-Anforderung trug,
    und stand mit Stufe A auf Platz 1. Dieselben Kunden zählten doppelt, und die "Annahme" sah aus wie ein Befund.
    Trend- und Wettbewerbsbefunde (Web) bleiben der Wette immer, denn auf ihnen ruht sie. Verworfen: die Wette dann
    streichen (verliert gerade die Zukunftsaussage), oder Nennungen anteilig teilen (keine saubere Zuordnung möglich).
    """
    taken = {s.id for draft, linked in items if draft.horizon == "today" for s in linked}
    web_kinds = (SignalKind.TREND, SignalKind.COMPETITOR_ADVANTAGE)
    result = []
    for draft, linked in items:
        if draft.horizon == "next_gen":
            linked = [s for s in linked if s.kind in web_kinds or s.id not in taken]
            draft = draft.model_copy(update={"signal_ids": [s.id for s in linked]})
        result.append((draft, linked))
    return result

