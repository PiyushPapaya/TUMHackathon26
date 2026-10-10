"""Pfad A, A7: Widersprüche zeigen statt wegmitteln (der Brief will "conflicting evidence" ausdrücklich).

Regel: gleiches oder verwandtes Thema (und gleiche Kategorie), eine Seite delight, die andere
complaint/unmet_need, beide mit mindestens MIN_MENTIONS Nennungen. Höchstens MAX_CONFLICTS pro Befund,
damit die Oberfläche nicht überladen ist.

Warum eine feste Liste verwandter Themen: "Touch screen: Lob" gegen "Touch screen: Kritik" ist ein echter
Widerspruch, "Anzeige: Lob" gegen "Touch-Bedienung: Kritik" auch (gleiche Bedienoberfläche). Vorher galt
für verschiedene Themen nur "gleiche Kategorie und ab 30 Nennungen"; das ergab Zufallspaare wie
"Interior comfort: Lob" gegen "Kofferraum-Öffnung: Kritik", die dann in der Konflikt-Arena, im
Anforderungs-Prompt und in der Challenge landeten. Verworfen: nur gleiches Thema (verliert z. B.
"Fahrdynamik gesamt: Lob" gegen "Antrieb: Kritik"), LLM entscheidet (schwankt je Lauf).
"""

from __future__ import annotations

from itertools import combinations

from core.models import Signal, SignalKind

MIN_MENTIONS = 10
MAX_CONFLICTS = 2
NEGATIVE = {SignalKind.COMPLAINT, SignalKind.UNMET_NEED}

# Themen (vfc2 bzw. Quelle-D-Bereich), die dasselbe Erlebnis beschreiben. Ein Test prüft die Namen gegen taxonomy.py.
RELATED_TOPICS: tuple[frozenset[str], ...] = (
    frozenset({  # Fahren
        "Drivetrain", "Drive, driving dynamics and chassis, overall technology", "Handling / Riding",
        "Transmission", "Survey D, driving feel", "Survey D, engine/motor",
    }),
    frozenset({  # Anzeige und Bedienung
        "Touch screen, operation", "Operating concept, operating system", "Instrument cluster", "Head-Up Display",
        "ConnectedDrive and Infotainment, overall technology", "Survey D, infotainment system",
    }),
    frozenset({"Seats", "Interior comfort", "Seating, ventilate / heat", "Seat massage"}),  # Sitzkomfort
    frozenset({  # Klima
        "Vehicle, climatization", "Air conditioning control panel", "Air conditioning, setting", "Blower function",
    }),
    frozenset({"Exterior design", "Exterior", "Survey D, exterior styling"}),
    frozenset({"Interior design", "Interior", "Survey D, interior"}),
    frozenset({  # Assistenz
        "Driver assistance, automated driving, overall technology", "Highway assistant",
        "(Active) cruise control", "Steering and lane guide assist",
    }),
    frozenset({"Electric Range", "Charge high-voltage battery", "Public charging / external providers"}),
)  # fmt: skip


def _topic(signal: Signal) -> str:
    return signal.title.rpartition(": ")[0]  # v1-Titel: "<Thema>: <Art>"


def _related(a: str, b: str) -> bool:
    return a == b or any(a in group and b in group for group in RELATED_TOPICS)


def _opposed(a: Signal, b: Signal) -> bool:
    if a.category != b.category or not _related(_topic(a), _topic(b)):
        return False
    if min(a.mention_count, b.mention_count) < MIN_MENTIONS:
        return False
    return {a.kind == SignalKind.DELIGHT, b.kind == SignalKind.DELIGHT} == {True, False} and (
        a.kind in NEGATIVE or b.kind in NEGATIVE
    )


def link_conflicts(signals: list[Signal]) -> list[Signal]:
    """Trägt `conflicts_with` gegenseitig ein. Titel müssen noch im v1-Format sein (vor der LLM-Stufe aufrufen)."""
    pairs = [(a, b) for a, b in combinations(signals, 2) if _opposed(a, b)]
    pairs.sort(key=lambda p: (
        _topic(p[0]) != _topic(p[1]),                       # gleiches Thema zuerst, dann verwandte
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
