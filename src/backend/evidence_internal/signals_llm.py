"""Pfad A, v2: Das LLM formuliert und wählt aus, es gruppiert nicht.

Warum so: Die Gruppen aus v1 (Thema x Art) sind nachvollziehbar und reproduzierbar. Das LLM macht daraus
nur einen Titel und eine Zusammenfassung in Kundensprache und sucht die typischsten Zitate heraus.
Freies Clustering per LLM wurde verworfen (teuer, nicht reproduzierbar, im Pitch schwer zu erklären).

Sicherheitsnetz (Ticket A6): Jede Antwort wird im Code geprüft. Unbekannte IDs fliegen raus, Zahlen im
Text werden abgelehnt (Zahlen kommen aus dem Code, nie aus dem Modell). Bei jedem Fehler bleibt v1.
"""

from __future__ import annotations

import re
import sys

from pydantic import BaseModel

from core.llm import ask_json
from core.models import Evidence, Signal, SourceType

TOP_GROUPS = 30  # ~30 Aufrufe, wenige Cent; kleinere Befunde behalten den v1-Titel
MAX_COMMENTS = 40  # pro Gruppe, damit der Prompt klein und der Cache stabil bleibt
COMMENT_CHARS = 300
MAX_REPRESENTATIVE = 5

SYSTEM = (
    "You help a BMW product manager read customer feedback. You get ONE group of customer comments about "
    "the same topic and the same kind of statement (complaint, unmet need or delight). Write: "
    "title = short headline in the customers' own words (max 10 words, no numbers); "
    "summary = 1-2 sentences in plain customer language, English, no numbers, no invented facts; "
    "representative_ids = 3 to 5 ids of the comments that illustrate the group best. "
    "Use ONLY ids that appear in the input. Do not mention any model, price or feature the comments do not mention."
)


class SignalDraft(BaseModel):
    title: str
    summary: str
    representative_ids: list[str]


def _prompt(signal: Signal, comments: list[Evidence]) -> str:
    lines = [f"[{c.id}] {c.text[:COMMENT_CHARS]}" for c in comments]
    head = f"Topic: {signal.title}\nKind: {signal.kind.value}\nComments ({len(lines)} of {signal.mention_count}):\n"
    return head + "\n".join(lines)


def _clean(text: str) -> str | None:
    """Text ohne Zahlen. Sonst None: Zahlen im Befund müssen aus dem Code stammen."""
    text = " ".join(text.split())
    return text if text and not re.search(r"\d", text) else None


def _refine_one(signal: Signal, member_ids: list[str], by_id: dict[str, Evidence]) -> Signal:
    comments = [by_id[i] for i in member_ids[:MAX_COMMENTS] if i in by_id]
    if not comments:
        return signal  # reiner Studien-Befund: nichts zu formulieren
    study_ids = [i for i in signal.evidence_ids if i in by_id and by_id[i].source_type == SourceType.STUDY]
    try:
        draft = ask_json(SYSTEM, _prompt(signal, comments), SignalDraft)
    except Exception:  # noqa: BLE001 - kein Netz, kein Key, Demo-Modus ohne Cache, kaputte Antwort: v1 bleibt
        return signal
    allowed = {c.id for c in comments}
    picked = list(dict.fromkeys(i for i in draft.representative_ids if i in allowed))  # Halluzinationsschutz
    # Zitate + Studien dürfen die Nennungen nicht übersteigen (Vertrag: mention_count >= len(evidence_ids))
    room = max(0, min(MAX_REPRESENTATIVE, signal.mention_count - len(study_ids)))
    # Ohne gültige Auswahl bleiben die v1-Zitate unverändert (bis zu 8), sonst höchstens MAX_REPRESENTATIVE
    picked = picked[:room] or [i for i in signal.evidence_ids if i not in study_ids]
    study_part = signal.summary[signal.summary.find("Study:"):] if "Study:" in signal.summary else ""
    summary = _clean(draft.summary)
    return signal.model_copy(update={
        "title": _clean(draft.title) or signal.title,
        "summary": f"{summary} {study_part}".strip() if summary else signal.summary,
        "evidence_ids": [*picked, *study_ids],
    })  # fmt: skip


def refine_signals(signals: list[Signal], members: list[list[str]], evidence: list[Evidence]) -> list[Signal]:
    """members[i] = Belege der Gruppe von signals[i] (typische zuerst). Nur die größten Gruppen gehen ans LLM."""
    by_id = {e.id: e for e in evidence}
    ranked = sorted(range(len(signals)), key=lambda i: -signals[i].mention_count)[:TOP_GROUPS]
    out = list(signals)
    failed = 0
    for i in ranked:
        out[i] = _refine_one(signals[i], members[i], by_id)
        failed += bool(members[i]) and out[i] is signals[i]  # unverändert trotz Gruppe = Fallback auf v1
    if failed:  # sichtbar machen, sonst hält man v1-Titel für ein LLM-Ergebnis (z. B. OPENAI_API_KEY fehlt)
        msg = f"  ! LLM-Formulierung: {failed} von {len(ranked)} Befunden blieben bei v1 (Key/Netz prüfen)"
        print(msg, file=sys.stderr)
    return out
