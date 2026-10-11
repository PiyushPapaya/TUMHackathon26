"""W-C12: Zweite Verteidigungslinie für den Scope. Der Prompt allein hielt nicht (Messung mit 8 Läufen, scope_eval.py).

Basis nur mit Prompt: 195 von 224 Out-of-scope-Wünschen erkannt (87 %). In 2 von 8 Läufen fasste die KI 8 Preiswünsche
zu "More affordable pricing ... MSRP < $50,000" zusammen, Zertifizierung (CCC) und GDPR rutschten in 5 von 8 durch.
Der Code prüft deshalb Titel und Akzeptanzkriterium auf eindeutige Preis- und Zulassungswörter und verwirft solche
Anforderungen mit Grund in den Prüfpfad. Nur eindeutige Wörter, keine Zahlen mit Einheiten (Kriterien nennen "7.5 W").
"""

import pytest

from core.models import Category, Scenario, Signal, SignalKind, SourceType
from requirements_engine import derive
from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all
from requirements_engine.scope_guard import guard_reason


@pytest.mark.parametrize("text", [
    "Entry model MSRP below $50,000 and a cheaper lease",
    "More affordable and transparent pricing for option packages",
    "Offer 0 percent financing",
    "Heated seats as a subscription at 15 USD per month",
    "Guarantee a residual value of 60 percent",
    "Reduce dealer margin on extras",
    "Lower the price of the comfort package by 30 %",
])
def test_preiswoerter_werden_erkannt(text):
    assert "price" in guard_reason(text, "").lower()


@pytest.mark.parametrize("text", [
    "Infotainment must pass CCC certification before delivery",
    "Driver profile meets GDPR data-subject rights",
    "Obtain type approval for Level 3 driving",
    "Cybersecurity per UN R155",
    "Headlights follow ECE R112 beam pattern rules",
    "FMVSS 208 airbag homologation",
    "Comply with CARB emission limits",
])
def test_zulassungswoerter_werden_erkannt(text):
    assert "regulat" in guard_reason("", text).lower()


@pytest.mark.parametrize(("title", "criterion"), [
    ("Wireless charging that reliably charges common phones", "Charges at >=7.5 W for 95 % of phone+case pairs"),
    ("Range: 600 or 700 miles?", "Real-world range of at least 600 miles in a mixed test cycle"),
    ("Heated steering wheel is part of the cold weather package", "Package contains the heated wheel and seats"),
    ("Charge port light shows the charging state", "State is visible from 5 m in daylight in customer trials"),
    ("Voice control understands common commands", "90 % of 100 commands executed correctly"),
    ("Climate controls without looking", "Operable in under 3 seconds in 90 % of trials"),
    ("Keep the sense of quality at today's level", "Customer rating of at least 8 of 10 in clinics"),
    ("Release the tailgate without a key", "Opens within 2 seconds, certain in 95 % of attempts"),  # release/certain
])
def test_normale_kundenwuensche_bleiben_unberuehrt(title, criterion):
    assert guard_reason(title, criterion) is None


SCENARIO = Scenario(id="G60-US", derivative="G60", model_name="5", market="US", countries=["US"], competitors=[])
SIGNALS = [Signal(id=f"S{n}", kind=SignalKind.UNMET_NEED, category=Category.VARIANTS_PACKAGES, title="t", summary="s",
                  evidence_ids=["E"], mention_count=20, source_types=[SourceType.FEEDBACK]) for n in (1, 2)]


def _draft(title, criterion, ids):
    return RequirementDraft(title=title, description="d", acceptance_criterion=criterion,
                            category=Category.VARIANTS_PACKAGES, signal_ids=ids)


def test_derive_all_verwirft_preis_anforderung_mit_grund_und_befunden(monkeypatch):
    drafts = [_draft("More affordable pricing", "Entry model MSRP < $50,000", ["S1"]),
              _draft("Clear package contents", "Configurator lists contents of each package", ["S2"])]
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=drafts))
    reqs, discarded = derive_all(SCENARIO, SIGNALS, [], {})
    assert [r.title for r in reqs] == ["Clear package contents"]
    assert len(discarded) == 1 and discarded[0]["signal_ids"] == ["S1"]
    assert discarded[0]["reason"].startswith("Scope guard:") and "price" in discarded[0]["reason"].lower()


def test_wetten_mit_zulassungswort_im_titel_werden_verworfen(monkeypatch):
    # Echter Fund (W-C3): Die Level-3-Wette hieß "certified ... in approved jurisdictions", obwohl der Prompt es verbot.
    trend = Signal(id="T1", kind=SignalKind.TREND, category=Category.VARIANTS_PACKAGES, title="t", summary="s",
                   evidence_ids=["E"], mention_count=2, source_types=[SourceType.WEB])
    bet = _draft("Certified hands-free highway driving", "Hands-free for 30 minutes", ["T1"])
    bet = bet.model_copy(update={"horizon": "next_gen", "assumptions": ["Law allows it"]})
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=[bet]))
    reqs, discarded = derive_all(SCENARIO, [*SIGNALS, trend], [], {})
    assert reqs == [] and any(d["reason"].startswith("Scope guard:") for d in discarded)
