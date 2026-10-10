"""Der Prompt ist Teil unserer Qualitätssicherung (Ticket C8): Die Regeln dürfen nicht still verschwinden.

Wir prüfen nicht, was die KI antwortet (das ist nicht reproduzierbar), sondern dass die Regeln gegen
die drei bekannten Schwächen im Prompt stehen. Die Wirkung belegt ein echter Lauf (siehe Commit).
"""

from requirements_engine.derive import SYSTEM_PROMPT


def test_prompt_verbietet_doppelte_anforderungen():
    assert "ONE requirement per distinct customer need" in SYSTEM_PROMPT


def test_prompt_verbietet_erfindungen_ueber_den_befund_hinaus():
    assert "directly supported" in SYSTEM_PROMPT


def test_prompt_verlangt_verwerfen_von_bauteil_wuenschen():
    assert "engineering specification" in SYSTEM_PROMPT and "in_scope=false" in SYSTEM_PROMPT


def test_prompt_verbietet_platzhalter_in_kriterien():
    assert "placeholders" in SYSTEM_PROMPT


def test_prompt_verlangt_beide_seiten_bei_widerspruechlichen_befunden():
    # Echter Fund: "nie verschmelzen" war nicht einzuhalten (22 von 45 Befunden haben einen Konflikt, die
    # Erkennung ist kategorieweise). Der Code trägt den Widerspruch selbst ein; die KI soll beide Seiten nennen.
    assert "conflicts_with" in SYSTEM_PROMPT and "both sides" in SYSTEM_PROMPT


def test_widersprueche_werden_der_ki_mitgegeben():
    import json

    from core.models import Category, Signal, SignalKind, SourceType
    from requirements_engine.derive import _compact

    sig = Signal(id="SIG-1", kind=SignalKind.DELIGHT, category=Category.INFOTAINMENT_DIGITAL, title="t",
                 summary="s", evidence_ids=["E"], mention_count=5, source_types=[SourceType.FEEDBACK],
                 conflicts_with=["SIG-2"])
    assert json.loads(_compact([sig]))[0]["conflicts_with"] == ["SIG-2"]


def test_prompt_verlangt_abdeckung_aller_beschwerden():
    # Echter Fund: Nach einer Prompt-Änderung blieben 10 von 30 Beschwerden/Wünschen ohne Anforderung
    # (u. a. Start-Stopp, Spracherkennung). Jede Beschwerde muss in einer Anforderung vorkommen.
    assert "Cover EVERY complaint and unmet_need" in SYSTEM_PROMPT


def test_prompt_haelt_die_zielzahl_aus_dem_ticket():
    # W-C5: pro Block 3-7 Anforderungen (heute) plus höchstens 2 Wetten; Summe über 3 Blöcke 15-25.
    assert "3-7 requirements with horizon" in SYSTEM_PROMPT and "up to 2 bets" in SYSTEM_PROMPT


def test_prompt_trennt_paketinhalt_von_paketpreis_und_verbietet_rechtswoerter():
    # Echter Fund (W-C12, 8 Läufe): Preiswünsche in der Kategorie "Varianten/Pakete" wurden in 2 von 8 Läufen zu einer
    # Anforderung "MSRP < $50,000" verschmolzen, CCC und GDPR rutschten durch. Der Code-Wächter fängt den Rest.
    assert "What a package CONTAINS is in scope, what it COSTS is not" in SYSTEM_PROMPT
    assert "WITHOUT any legal or certification wording" in SYSTEM_PROMPT
