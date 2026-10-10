"""A7: Konflikte. Nur erfundene Mini-Befunde."""

from core.models import Category, Signal, SignalKind, SourceType
from evidence_internal.conflicts import CROSS_TOPIC_MIN, MAX_CONFLICTS, MIN_MENTIONS, link_conflicts


def _sig(n, topic, kind, mentions, category=Category.INFOTAINMENT_DIGITAL):
    return Signal(id=f"SIG-T-{n:03d}", kind=kind, category=category, title=f"{topic}: {kind.value}", summary="",
                  evidence_ids=[], mention_count=mentions, source_types=[SourceType.FEEDBACK])  # fmt: skip


def _links(signals):
    return {s.id: s.conflicts_with for s in link_conflicts(signals)}


def test_lob_und_kritik_gleiche_kategorie_werden_gegenseitig_verknuepft():
    touch = _sig(2, "Touch", SignalKind.COMPLAINT, CROSS_TOPIC_MIN)
    links = _links([_sig(1, "Display", SignalKind.DELIGHT, 40), touch])
    assert links == {"SIG-T-001": ["SIG-T-002"], "SIG-T-002": ["SIG-T-001"]}


def test_verschiedene_themen_brauchen_mehr_nennungen_als_gleiches_thema():
    weak = _sig(2, "Touch", SignalKind.COMPLAINT, CROSS_TOPIC_MIN - 1)
    other = _links([_sig(1, "Display", SignalKind.DELIGHT, 40), weak])
    same = _links([_sig(1, "Touch", SignalKind.DELIGHT, 40), _sig(2, "Touch", SignalKind.COMPLAINT, MIN_MENTIONS)])
    assert other["SIG-T-001"] == [] and same["SIG-T-001"] == ["SIG-T-002"]


def test_unter_schwelle_oder_andere_kategorie_oder_gleiche_seite_kein_konflikt():
    signals = [
        _sig(1, "A", SignalKind.DELIGHT, 30),
        _sig(2, "B", SignalKind.COMPLAINT, MIN_MENTIONS - 1),            # zu klein
        _sig(3, "C", SignalKind.COMPLAINT, 50, Category.EXTERIOR),       # andere Kategorie
        _sig(4, "D", SignalKind.DELIGHT, 40),                            # gleiche Seite
    ]  # fmt: skip
    assert all(v == [] for v in _links(signals).values())


def test_hoechstens_zwei_konflikte_und_gleiches_thema_zuerst():
    signals = [
        _sig(1, "Touch", SignalKind.DELIGHT, 15),
        _sig(2, "Touch", SignalKind.COMPLAINT, 11),   # gleiches Thema: muss gewinnen, obwohl kleiner
        _sig(3, "Menu", SignalKind.COMPLAINT, 90),
        _sig(4, "Voice", SignalKind.COMPLAINT, 80),
        _sig(5, "Sound", SignalKind.COMPLAINT, 70),
    ]
    links = _links(signals)
    assert links["SIG-T-001"][0] == "SIG-T-002"
    assert all(len(v) <= MAX_CONFLICTS for v in links.values())
    for a, others in links.items():  # immer gegenseitig
        assert all(a in links[b] for b in others)
