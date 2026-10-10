"""A6: LLM formuliert nur. Fake für ask_json, nur erfundene Mini-Daten."""

import pytest

from core.models import Evidence, Scenario, SignalKind, SourceType
from evidence_internal import signals_llm
from evidence_internal.signals import extract_signals
from evidence_internal.signals_llm import SignalDraft

SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="Test", market="US", countries=["US"], competitors=[])
TEXT = "The navigation screen is hard to use while driving and I miss a simple way to zoom."


def _fb(n, labels="Navigation/Difficult to Use"):
    return Evidence(
        id=f"EV-G60-US-FB-{n}", source_type=SourceType.FEEDBACK, source_name="Feedback", derivative="G60",
        market="US", text=f"{TEXT} #{n}", polarity=-1,
        meta={"vfc2": "Navigation", "labels": labels, "source": "A", "scope": "in", "feedback_type": ""},
    )  # fmt: skip


@pytest.fixture
def evidence():
    return [_fb(n) for n in range(1, 9)]


def _fake(draft):
    def ask(system, user, schema, **kwargs):
        return draft
    return ask


def test_unbekannte_id_wird_entfernt(monkeypatch, evidence):
    draft = SignalDraft(title="Navigation is hard to use", summary="Drivers struggle with the map screen.",
                        representative_ids=["EV-G60-US-FB-2", "EV-ERFUNDEN-99", "EV-G60-US-FB-3"])  # fmt: skip
    monkeypatch.setattr(signals_llm, "ask_json", _fake(draft))
    [sig] = extract_signals(SCENARIO, evidence)
    assert sig.evidence_ids == ["EV-G60-US-FB-2", "EV-G60-US-FB-3"]
    assert sig.title == "Navigation is hard to use"
    assert sig.kind == SignalKind.COMPLAINT and sig.mention_count == 8  # Gruppe und Zahl bleiben aus v1


def test_fehler_faellt_auf_v1_zurueck(evidence, capsys):  # conftest: ask_json wirft
    [sig] = extract_signals(SCENARIO, evidence)
    assert "blieben bei v1" in capsys.readouterr().err
    assert sig.title == "Navigation: complaint"
    assert extract_signals(SCENARIO, evidence) == extract_signals(SCENARIO, evidence, use_llm=False)


def test_zahlen_im_text_werden_abgelehnt(monkeypatch, evidence):
    draft = SignalDraft(title="Top 10 map problems", summary="95 percent of drivers complain.",
                        representative_ids=["EV-G60-US-FB-1"])  # fmt: skip
    monkeypatch.setattr(signals_llm, "ask_json", _fake(draft))
    [sig] = extract_signals(SCENARIO, evidence)
    assert sig.title == "Navigation: complaint"
    assert "95" not in sig.summary


def test_nur_erfundene_ids_behalten_v1_zitate(monkeypatch, evidence):
    draft = SignalDraft(title="Map is confusing", summary="Hard to read.", representative_ids=["EV-X-1"])
    monkeypatch.setattr(signals_llm, "ask_json", _fake(draft))
    [sig] = extract_signals(SCENARIO, evidence)
    plain = extract_signals(SCENARIO, evidence, use_llm=False)[0]
    assert sig.evidence_ids == plain.evidence_ids
    assert all(i in {e.id for e in evidence} for i in sig.evidence_ids)
