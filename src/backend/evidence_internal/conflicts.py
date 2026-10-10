"""Pfad A, A7: Widersprüche zeigen statt wegmitteln (der Brief will "conflicting evidence" ausdrücklich).

Regel: gleiche Kategorie, eine Seite delight, die andere complaint/unmet_need, beide mit mindestens
MIN_MENTIONS Nennungen. Höchstens MAX_CONFLICTS pro Befund, damit die Oberfläche nicht überladen ist.

Warum zuerst gleiches Thema: "Touch screen: Lob" gegen "Touch screen: Kritik" ist ein echter Widerspruch,
"Antrieb: Lob" gegen "Navigation: Kritik" liegt nur zufällig in derselben groben Kategorie. Also kommen
Paare mit gleichem Thema zuerst, danach die mit den meisten Nennungen. Verschiedene Themen zählen nur ab
CROSS_TOPIC_MIN (echte Daten: bei 10 hingen 33 von 45 Befunden an einem Konflikt, bei 30 nur noch 22).
"""

from __future__ import annotations

from itertools import combinations

from core.models import Signal, SignalKind

MIN_MENTIONS = 10
CROSS_TOPIC_MIN = 30  # verschiedene Themen: erst ab 30 Nennungen, sonst hängt fast jeder Befund an einem Zufallspartner
MAX_CONFLICTS = 2
NEGATIVE = {SignalKind.COMPLAINT, SignalKind.UNMET_NEED}


def _topic(signal: Signal) -> str:
    return signal.title.rpartition(": ")[0]  # v1-Titel: "<Thema>: <Art>"


def _opposed(a: Signal, b: Signal) -> bool:
    needed = MIN_MENTIONS if _topic(a) == _topic(b) else CROSS_TOPIC_MIN
    if a.category != b.category or min(a.mention_count, b.mention_count) < needed:
        return False
    return {a.kind == SignalKind.DELIGHT, b.kind == SignalKind.DELIGHT} == {True, False} and (
        a.kind in NEGATIVE or b.kind in NEGATIVE
    )


def link_conflicts(signals: list[Signal]) -> list[Signal]:
    """Trägt `conflicts_with` gegenseitig ein. Titel müssen noch im v1-Format sein (vor der LLM-Stufe aufrufen)."""
    pairs = [(a, b) for a, b in combinations(signals, 2) if _opposed(a, b)]
    pairs.sort(key=lambda p: (
        _topic(p[0]) != _topic(p[1]),                       # gleiches Thema zuerst
        -min(p[0].mention_count, p[1].mention_count),       # dann die stärkere schwächere Seite
        -(p[0].mention_count + p[1].mention_count),
        p[0].id, p[1].id,
    ))  # fmt: skip
    linked: dict[str, list[str]] = {s.id: [] for s in signals}
    for a, b in pairs:  # Gierig, damit die Verknüpfung gegenseitig bleibt und das Limit für beide gilt
        if len(linked[a.id]) < MAX_CONFLICTS and len(linked[b.id]) < MAX_CONFLICTS:
            linked[a.id].append(b.id)
            linked[b.id].append(a.id)
    return [s.model_copy(update={"conflicts_with": linked[s.id]}) for s in signals]
