"""B2: Fragen aus Befunden + Wettbewerbern. Reine Funktion, kein Netz."""

import json
from pathlib import Path

from core.models import Scenario, Signal
from evidence_external.questions import build_questions

ROOT = Path(__file__).resolve().parents[2]
BEISPIEL = ROOT / "src" / "shared" / "beispiele" / "stufen" / "signals.json"
G60 = ROOT / "config" / "scenarios" / "G60-US.json"


def _g60():
    scenario = Scenario(**json.loads(G60.read_text(encoding="utf-8")))
    signals = [Signal(**s) for s in json.loads(BEISPIEL.read_text(encoding="utf-8"))]
    return scenario, signals


def test_g60_us_hat_13_fragen_8_wettbewerb_und_5_trend():
    scenario, signals = _g60()
    questions = build_questions(scenario, signals)

    assert len(questions) == 13
    assert sum(q.kind == "competitor" for q in questions) == 8
    assert sum(q.kind == "trend" for q in questions) == 5


def test_wettbewerbsfragen_nennen_befund_und_wettbewerber_und_keine_dubletten():
    scenario, signals = _g60()
    competitor_qs = [q for q in build_questions(scenario, signals) if q.kind == "competitor"]
    allowed = {s.id for s in signals if s.kind in ("complaint", "unmet_need")}

    assert {q.signal_id for q in competitor_qs} <= allowed  # nur Beschwerden/Bedarfe lösen Fragen aus
    assert all(q.competitor in scenario.competitors for q in competitor_qs)
    assert all(q.competitor in q.text for q in competitor_qs)
    assert len({(q.signal_id, q.competitor) for q in competitor_qs}) == 8
    assert {q.competitor for q in competitor_qs} == set(scenario.competitors)  # jeder Wettbewerber kommt vor


def test_trendfragen_decken_2028_bis_2031_und_markt_ab():
    scenario, signals = _g60()
    trend_qs = [q for q in build_questions(scenario, signals) if q.kind == "trend"]

    assert all("2028" in q.text and "2031" in q.text for q in trend_qs)
    assert all(scenario.market in q.text for q in trend_qs)
    assert all(q.signal_id is None for q in trend_qs)  # Trend ohne internen Befund = Annahme
    assert len({q.category for q in trend_qs}) >= 4


def test_ohne_befunde_bleiben_nur_trendfragen():
    scenario, _ = _g60()
    questions = build_questions(scenario, [])

    assert len(questions) == 5
    assert all(q.kind == "trend" for q in questions)
