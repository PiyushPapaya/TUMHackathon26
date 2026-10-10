"""A7: Konflikte. Nur erfundene Mini-Befunde (Themennamen wie in der BMW-Taxonomie, Texte leer)."""

from core.models import Category, Signal, SignalKind, SourceType
from evidence_internal.conflicts import MAX_CONFLICTS, MIN_MENTIONS, RELATED_TOPICS, link_conflicts

TOUCH = "Touch screen, operation"
CLUSTER = "Instrument cluster"  # verwandt mit TOUCH (Anzeige und Bedienung)
NAVIGATION = "Navigation"  # gleiche Kategorie wie TOUCH, aber nicht verwandt


def _sig(n, topic, kind, mentions, category=Category.INFOTAINMENT_DIGITAL):
    return Signal(id=f"SIG-T-{n:03d}", kind=kind, category=category, title=f"{topic}: {kind.value}", summary="",
                  evidence_ids=[], mention_count=mentions, source_types=[SourceType.FEEDBACK])  # fmt: skip


def _links(signals):
    return {s.id: s.conflicts_with for s in link_conflicts(signals)}


def test_lob_und_kritik_gleiches_thema_werden_gegenseitig_verknuepft():
    links = _links([_sig(1, TOUCH, SignalKind.DELIGHT, 40), _sig(2, TOUCH, SignalKind.COMPLAINT, MIN_MENTIONS)])
    assert links == {"SIG-T-001": ["SIG-T-002"], "SIG-T-002": ["SIG-T-001"]}


def test_verwandte_themen_sind_ein_konflikt():
    # Ticket-Beispiel: Anzeige gelobt, Touch-Bedienung kritisiert
    links = _links([_sig(1, CLUSTER, SignalKind.DELIGHT, 40), _sig(2, TOUCH, SignalKind.COMPLAINT, MIN_MENTIONS)])
    assert links["SIG-T-001"] == ["SIG-T-002"]


def test_fremde_themen_derselben_kategorie_sind_kein_konflikt():
    # Früher reichten 30 Nennungen; das erzeugte Zufallspaare wie "Komfort: Lob" gegen "Kofferraum: Kritik".
    links = _links([_sig(1, NAVIGATION, SignalKind.DELIGHT, 500), _sig(2, TOUCH, SignalKind.COMPLAINT, 500)])
    assert all(v == [] for v in links.values())


def test_unter_schwelle_oder_andere_kategorie_oder_gleiche_seite_kein_konflikt():
    signals = [
        _sig(1, TOUCH, SignalKind.DELIGHT, 30),
        _sig(2, TOUCH, SignalKind.COMPLAINT, MIN_MENTIONS - 1),            # zu klein
        _sig(3, TOUCH, SignalKind.COMPLAINT, 50, Category.EXTERIOR),       # andere Kategorie
        _sig(4, CLUSTER, SignalKind.DELIGHT, 40),                          # gleiche Seite
    ]  # fmt: skip
    assert all(v == [] for v in _links(signals).values())


def test_hoechstens_zwei_konflikte_und_gleiches_thema_zuerst():
    signals = [
        _sig(1, TOUCH, SignalKind.DELIGHT, 15),
        _sig(2, TOUCH, SignalKind.COMPLAINT, 11),   # gleiches Thema: muss gewinnen, obwohl kleiner
        _sig(3, "Operating concept, operating system", SignalKind.COMPLAINT, 90),
        _sig(4, "ConnectedDrive and Infotainment, overall technology", SignalKind.UNMET_NEED, 80),
        _sig(5, CLUSTER, SignalKind.COMPLAINT, 70),
    ]
    links = _links(signals)
    assert links["SIG-T-001"][0] == "SIG-T-002"
    assert all(len(v) <= MAX_CONFLICTS for v in links.values())
    for a, others in links.items():  # immer gegenseitig
        assert all(a in links[b] for b in others)


def test_verwandte_themen_stehen_in_der_taxonomie():
    # Tippfehler in der Liste würden still nie greifen; Quelle-D-Bereiche heißen "Survey D, ...".
    from evidence_internal.taxonomy import SURVEY_D_AREAS, VFC2_TO_CATEGORY

    known = set(VFC2_TO_CATEGORY) | {f"Survey D, {label}" for _, label, _ in SURVEY_D_AREAS}
    assert all(topic in known for group in RELATED_TOPICS for topic in group)
