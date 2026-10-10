"""Pfad A: Belege -> Befunde (Signals). v1 ohne LLM, jeder Befund zitiert echte Beleg-IDs.

Vertrag (nicht ändern ohne Lead):
    extract_signals(scenario: Scenario, evidence: list[Evidence]) -> list[Signal]

Warum v1 ohne LLM: Die BMW-Taxonomie liefert schon gute Gruppen. Das ist reproduzierbar, kostet nichts
und lässt sich im Pitch erklären ("Gruppe = Thema x Art der Aussage, mindestens 5 Kommentare").

Ablauf:
1. Je Feedback-Beleg (nur scope=in) und je Label (Thema, Typ) eine Gruppe (Thema, Art).
2. Gruppen unter MIN_MENTIONS fallen weg, Themen ohne Kategorie ebenfalls (siehe taxonomy.py).
3. Studienwerte mit Problem hängen am passenden Feedback-Befund oder werden ein eigener Befund.
4. IDs SIG-<szenario>-<nnn> nach Nennungen absteigend.
5. v2 (signals_llm.py): Das LLM formuliert Titel/Zusammenfassung und wählt Zitate; die Gruppen bleiben.
6. conflicts.py (A7): Lob und Kritik in derselben Kategorie werden gegenseitig verknüpft.
"""

from __future__ import annotations

from collections import defaultdict

from core.models import Category, Evidence, Scenario, Signal, SignalKind, SourceType
from evidence_internal.conflicts import link_conflicts
from evidence_internal.signals_llm import MAX_COMMENTS, refine_signals
from evidence_internal.study_topics import study_category, study_vfc2
from evidence_internal.taxonomy import category_for_vfc2, survey_area

MIN_MENTIONS = 5  # kleinere Gruppen sind Zufall, nicht "wiederkehrend"
MAX_SIGNALS = 45  # ein PM prüft keine 160 Punkte; die größten Gruppen zuerst (Ticket A5: 20-45 Befunde)
MAX_STUDY_ONLY = 8  # Kontingent für Befunde, die nur aus der Studie stammen (die schlimmsten zuerst)
MAX_UNMET_NEEDS = 10  # reservierte Plätze: Wünsche zerfallen in kleine Gruppen und kämen sonst nie unter die Top 45
MAX_QUOTES = 8  # so viele Belege zeigt ein Befund direkt; mention_count bleibt die volle Gruppengröße
QUOTE_LENGTH = (60, 300)  # sehr kurze oder sehr lange Kommentare taugen schlecht als Zitat
PRAISE_SOURCE = "D"

TYPE_TO_KIND = {
    "Likes": SignalKind.DELIGHT,
    "Defect": SignalKind.COMPLAINT,
    "Difficult to Use": SignalKind.COMPLAINT,
    "Wants": SignalKind.UNMET_NEED,
}

Group = tuple[str, SignalKind]  # (Themenname, Art)


def _labels(ev: Evidence) -> list[tuple[str, str]]:
    """'Handling / Riding/Likes | Seats/' -> [('Handling / Riding', 'Likes'), ('Seats', '')].

    rsplit, weil Themennamen selbst einen Schrägstrich enthalten können, Typen aber nie."""
    pairs = []
    for part in ev.meta.get("labels", "").split(" | "):
        topic, sep, feedback_type = part.rpartition("/")
        if sep:
            pairs.append((topic.strip(), feedback_type.strip()))
    return pairs


def _kind(feedback_type: str, ev: Evidence) -> SignalKind | None:
    """Art aus dem BMW-Typ; bei leerem Typ aus der Polarität (Quelle D ist schon +1)."""
    if feedback_type in TYPE_TO_KIND:
        return TYPE_TO_KIND[feedback_type]
    if ev.polarity > 0:
        return SignalKind.DELIGHT
    if ev.polarity < 0:
        return SignalKind.COMPLAINT
    return None


def _group_feedback(evidence: list[Evidence]) -> tuple[dict[Group, set[str]], dict[str, Category]]:
    members: dict[Group, set[str]] = defaultdict(set)  # Set: ein Beleg zählt je Gruppe nur einmal
    category_of: dict[str, Category] = {}
    for ev in evidence:
        if ev.source_type != SourceType.FEEDBACK or ev.meta.get("scope", "in") != "in":
            continue
        for topic, feedback_type in _labels(ev):
            kind = _kind(feedback_type, ev)
            name, category = topic, category_for_vfc2(topic)
            if not topic and ev.meta.get("source") == PRAISE_SOURCE and (area := survey_area(ev.text)):
                name, category = area  # Quelle D: Bereich steckt im Satz
            if kind is None or category is None:
                continue
            members[(name, kind)].add(ev.id)
            category_of[name] = category
    return members, category_of


def _quotes(ids: set[str], by_id: dict[str, Evidence], limit: int = MAX_QUOTES) -> list[str]:
    """Bis zu `limit` typische Belege: Länge im Zitatbereich zuerst, dann stabil nach ID."""
    low, high = QUOTE_LENGTH

    def rank(i: str) -> tuple[int, str]:
        return (0 if low <= len(by_id[i].text) <= high else 1, i)

    return sorted(ids, key=rank)[:limit]


def _summary(name: str, kind: SignalKind, comments: int, study_texts: list[str]) -> str:
    study = f"Study: {'; '.join(study_texts)}." if study_texts else ""
    if not comments:  # reiner Studien-Befund: es gibt keine Kommentare, die wir zählen könnten
        return study
    text = f"{comments} customer comments about '{name}' ({kind.value.replace('_', ' ')})."
    return f"{text} {study}".strip()


def _assemble(drafts: list[dict], study: list[Evidence]) -> list[dict]:
    """Studienwerte an Feedback-Befunde hängen oder als eigenen Befund ergänzen."""
    out = [{**d, "study": []} for d in drafts]
    complaints = {d["name"]: d for d in out if d["kind"] == SignalKind.COMPLAINT}
    for ev in study:
        attribute = ev.meta.get("attribute", "")
        category = study_category(attribute)
        if category is None:
            continue  # außerhalb des Umfangs (Preis, Marke ...) oder nicht zuordenbar
        target = complaints.get(study_vfc2(attribute) or "")
        if target:
            target["study"].append(ev.id)
        else:  # kein passender Feedback-Befund: die Studie steht für sich
            out.append({
                "name": attribute, "kind": SignalKind.COMPLAINT, "category": category, "mentions": 0,
                "quotes": [], "study": [ev.id], "title": f"{attribute}: {SignalKind.COMPLAINT.value}",
                "severity": _severity(ev),
            })  # fmt: skip
    return out


def _severity(ev: Evidence) -> float:
    """Wie schlimm ein Studienwert ist (0-1): Anteil Unzufriedener (US) bzw. Abstand zur Skalenobergrenze (CN/EU)."""
    meta = ev.meta
    if "neg_share" in meta:
        return float(meta["neg_share"])
    return (10 - float(meta.get("mean", 10))) / 10


def _select(drafts: list[dict]) -> list[dict]:
    """Obergrenze MAX_SIGNALS. Reihenfolge der Priorität:
    1. Feedback + Studie (zwei Quellenarten = stärkste Evidenz, bleibt immer drin)
    2. reine Studien-Befunde, höchstens MAX_STUDY_ONLY, die schlimmsten zuerst
    3. Wünsche (unmet_need), höchstens MAX_UNMET_NEEDS: für einen Nachfolger der wertvollste Befundtyp
    4. übrige Feedback-Gruppen nach Nennungen, bis die Liste voll ist"""
    both = [d for d in drafts if d["mentions"] and d["study"]]
    study_only = sorted((d for d in drafts if not d["mentions"]), key=lambda d: -d["severity"])[:MAX_STUDY_ONLY]
    feedback_only = [d for d in drafts if d["mentions"] and not d["study"]]  # schon nach Nennungen sortiert
    needs = [d for d in feedback_only if d["kind"] == SignalKind.UNMET_NEED][:MAX_UNMET_NEEDS]
    rest = [d for d in feedback_only if d not in needs]
    chosen = [*both, *study_only]
    chosen += needs[: max(0, MAX_SIGNALS - len(chosen))]
    chosen += rest[: max(0, MAX_SIGNALS - len(chosen))]
    return chosen[:MAX_SIGNALS]


def _build(scenario: Scenario, evidence: list[Evidence]) -> tuple[list[Signal], list[dict]]:
    """v1: Befunde plus die Entwürfe dahinter (mit allen Mitgliedern je Gruppe)."""
    by_id = {e.id: e for e in evidence}
    members, category_of = _group_feedback(evidence)
    feedback = [
        {"name": name, "kind": kind, "category": category_of[name], "mentions": len(ids),
         "quotes": _quotes(ids, by_id), "title": f"{name}: {kind.value}", "severity": 0.0,
         "members": _quotes(ids, by_id, MAX_COMMENTS), "ids": sorted(ids)}
        for (name, kind), ids in members.items()
        if len(ids) >= MIN_MENTIONS
    ]  # fmt: skip
    feedback.sort(key=lambda d: (-d["mentions"], d["title"]))
    study = sorted((e for e in evidence if e.source_type == SourceType.STUDY and e.polarity < 0), key=lambda e: e.id)

    drafts = sorted(_select(_assemble(feedback, study)), key=lambda d: (-d["mentions"], d["title"]))
    signals: list[Signal] = []
    for number, d in enumerate(drafts, start=1):
        study_ids = d["study"][:3]
        # Zitate + Studien dürfen die Nennungen nicht übersteigen (Vertrag: mention_count >= len(evidence_ids))
        quotes = d["quotes"][: max(0, min(MAX_QUOTES, d["mentions"] - len(study_ids)))] if d["mentions"] else []
        source_types = [*([SourceType.FEEDBACK] if d["mentions"] else []), *([SourceType.STUDY] if study_ids else [])]
        signals.append(Signal(
            id=f"SIG-{scenario.id}-{number:03d}",
            kind=d["kind"], category=d["category"], title=d["title"],
            summary=_summary(d["name"], d["kind"], d["mentions"], [by_id[i].text for i in study_ids]),
            evidence_ids=[*quotes, *study_ids],
            mention_count=max(d["mentions"], len(study_ids)),
            source_types=source_types,
        ))  # fmt: skip
    return signals, drafts


def signal_groups(scenario: Scenario, evidence: list[Evidence]) -> dict[str, list[str]]:
    """Befund-ID -> alle Kommentare der Gruppe (nicht nur die Zitate). Für die Abdeckung in tests/eval."""
    signals, drafts = _build(scenario, evidence)
    return {s.id: d.get("ids", []) for s, d in zip(signals, drafts, strict=True)}


def extract_signals(scenario: Scenario, evidence: list[Evidence], use_llm: bool = True) -> list[Signal]:
    """v1 (Regeln) und danach v2 (LLM formuliert). use_llm=False = reines v1; bei LLM-Fehler bleibt v1 ebenfalls."""
    signals, drafts = _build(scenario, evidence)
    signals = link_conflicts(signals)  # vor der LLM-Stufe: nutzt die v1-Titel (Thema: Art)
    if use_llm:
        signals = refine_signals(signals, [d.get("members", []) for d in drafts], evidence)
    return signals
