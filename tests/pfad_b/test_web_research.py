"""B3: research() mit Fake-ask_claims. Kein Netz, kein Key."""

import json
from pathlib import Path

from core.models import Scenario, Signal, SignalKind, SourceType
from evidence_external import web_research
from evidence_external.claims import Claim

ROOT = Path(__file__).resolve().parents[2]
BEISPIEL = ROOT / "src" / "shared" / "beispiele" / "stufen" / "signals.json"
G60 = ROOT / "config" / "scenarios" / "G60-US.json"

HIGH_URL = "https://www.caranddriver.com/reviews/audi-a6-e-tron"
MEDIUM_URL = "https://electrek.co/2026/01/ev-news"
LOW_URL = "https://www.reddit.com/r/cars/comments/abc"


def _g60():
    scenario = Scenario(**json.loads(G60.read_text(encoding="utf-8")))
    signals = [Signal(**s) for s in json.loads(BEISPIEL.read_text(encoding="utf-8"))]
    return scenario, signals


def _claim(url, text="Aussage", stance="supports"):
    return Claim(text=text, url=url, publisher="Pub", published="2026", stance=stance, about="Audi A6 e-tron")


def _fake(by_url_prefix):
    """Fake für ask_claims: Wettbewerbsfragen bekommen die erste Liste, Trendfragen die zweite."""
    def fake(question):
        return by_url_prefix["trend" if "2028" in question else "competitor"]
    return fake


def test_jeder_webbeleg_hat_url_id_und_trust(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", _fake({
        "competitor": [_claim(HIGH_URL)], "trend": [_claim(MEDIUM_URL)]}))

    evidence, _ = web_research.research(scenario, signals)

    assert evidence
    assert all(e.source_type == SourceType.WEB and e.url.startswith("http") for e in evidence)
    assert all(e.retrieved_at is not None for e in evidence)
    assert {e.meta["trust"] for e in evidence} == {"high", "medium"}
    assert [e.id for e in evidence] == [f"EV-G60-US-WEB-{n:02d}" for n in range(1, len(evidence) + 1)]


def test_doppelte_urls_werden_zusammengefuehrt(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", _fake({
        "competitor": [_claim(HIGH_URL)], "trend": [_claim(HIGH_URL + "/")]}))

    evidence, web_signals = web_research.research(scenario, signals)

    assert len(evidence) == 1  # 13 Fragen, aber nur eine Quelle
    assert all(s.evidence_ids == [evidence[0].id] for s in web_signals)  # jeder Befund zitiert sie trotzdem


def test_wettbewerb_wird_competitor_advantage_trend_wird_trend(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", _fake({
        "competitor": [_claim(HIGH_URL)], "trend": [_claim(MEDIUM_URL)]}))

    _, web_signals = web_research.research(scenario, signals)

    kinds = [s.kind for s in web_signals]
    assert kinds.count(SignalKind.COMPETITOR_ADVANTAGE) == 8
    assert kinds.count(SignalKind.TREND) == 5
    assert [s.id for s in web_signals] == [f"SIG-G60-US-WEB-{n:02d}" for n in range(1, 14)]
    assert all(s.source_types == [SourceType.WEB] for s in web_signals)


def test_low_trust_kommt_in_keinen_befund(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", _fake({
        "competitor": [_claim(LOW_URL)], "trend": [_claim(MEDIUM_URL)]}))

    evidence, web_signals = web_research.research(scenario, signals)

    low = [e for e in evidence if e.meta["trust"] == "low"]
    assert low  # bleibt als Beleg sichtbar (Transparenz) ...
    assert not any(e.id in s.evidence_ids for s in web_signals for e in low)  # ... aber ohne Befund
    assert all(s.kind == SignalKind.TREND for s in web_signals)  # Wettbewerbsfragen ohne belastbaren Claim: kein Befund


def test_meta_verweist_auf_ausloesenden_befund(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", _fake({
        "competitor": [_claim(HIGH_URL, stance="contradicts")], "trend": []}))

    evidence, _ = web_research.research(scenario, signals)

    internal_ids = {s.id for s in signals}
    assert evidence[0].meta["supports_signal_id"] in internal_ids
    assert evidence[0].meta["stance"] == "contradicts"
    assert {"publisher", "published", "trust"} <= set(evidence[0].meta)


def test_ohne_claims_keine_ergebnisse(monkeypatch):
    scenario, signals = _g60()
    monkeypatch.setattr(web_research, "ask_claims", lambda question: [])

    assert web_research.research(scenario, signals) == ([], [])
