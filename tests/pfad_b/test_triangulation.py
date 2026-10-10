"""B4: Triangulation Web <-> intern. Reine Funktion, kein Netz."""

from core.models import Category, Evidence, Signal, SignalKind, SourceType
from evidence_external.triangulation import triangulate


def _intern(sig_id):
    return Signal(id=sig_id, kind=SignalKind.COMPLAINT, category=Category.INTERIOR, title="t", summary="s",
                  evidence_ids=["EV-1"], mention_count=20, source_types=[SourceType.FEEDBACK])


def _web(ev_id, signal_id, stance="supports", trust="high"):
    meta = {"trust": trust, "stance": stance}
    if signal_id:
        meta["supports_signal_id"] = signal_id
    return Evidence(id=ev_id, source_type=SourceType.WEB, source_name="Pub", derivative="G60", market="US",
                    text="x", url="https://example.com/" + ev_id, meta=meta)


def test_stuetzender_webbeleg_haengt_id_und_web_an():
    signals = [_intern("SIG-1"), _intern("SIG-2")]
    web = [_web("W1", "SIG-1"), _web("W2", "SIG-1", trust="medium"), _web("W3", "SIG-2")]

    result, counter = triangulate(signals, web)

    assert result[0].evidence_ids == ["EV-1", "W1", "W2"]
    assert result[1].evidence_ids == ["EV-1", "W3"]
    assert all(SourceType.WEB in s.source_types for s in result)
    assert SourceType.FEEDBACK in result[0].source_types  # bisherige Quellenart bleibt
    assert counter == {}


def test_widerspruch_wird_nicht_angehaengt_aber_als_gegenbeleg_gemeldet():
    signals = [_intern("SIG-1")]
    web = [_web("W1", "SIG-1", stance="contradicts")]

    result, counter = triangulate(signals, web)

    assert result[0].evidence_ids == ["EV-1"]
    assert SourceType.WEB not in result[0].source_types
    assert counter == {"SIG-1": ["W1"]}


def test_low_trust_neutral_und_ohne_befund_zaehlen_nicht():
    signals = [_intern("SIG-1")]
    web = [_web("W1", "SIG-1", trust="low"), _web("W2", "SIG-1", stance="neutral"), _web("W3", None)]

    result, _ = triangulate(signals, web)

    assert result[0].evidence_ids == ["EV-1"]
    assert SourceType.WEB not in result[0].source_types


def test_eingabe_bleibt_unveraendert_und_zweiter_lauf_doppelt_nicht():
    signals = [_intern("SIG-1")]
    web = [_web("W1", "SIG-1")]

    once, _ = triangulate(signals, web)
    twice, _ = triangulate(once, web)

    assert signals[0].evidence_ids == ["EV-1"]  # Original nicht verändert
    assert twice[0].evidence_ids == ["EV-1", "W1"]
    assert twice[0].source_types.count(SourceType.WEB) == 1
