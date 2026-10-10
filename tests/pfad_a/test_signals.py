"""A5: Belege -> Befunde (v1, ohne LLM). Nur erfundene Mini-Daten, keine BMW-Texte."""

from core.models import Category, Evidence, Scenario, Signal, SignalKind, SourceType
from evidence_internal.signals import MAX_QUOTES, MAX_SIGNALS, MAX_STUDY_ONLY, MIN_MENTIONS, extract_signals
from evidence_internal.taxonomy import VFC2_TO_CATEGORY

SCENARIO = Scenario(
    id="G60-US", derivative="G60", model_name="Test", market="US", countries=["US"], competitors=[]
)
LONG = "This is a sufficiently long synthetic comment that stays inside the typical quote length range."


def _fb(n, *, labels, polarity=-1, source="A", scope="in", text=LONG):
    vfc2 = " | ".join(dict.fromkeys(label.rsplit("/", 1)[0] for label in labels.split(" | ")))
    return Evidence(
        id=f"EV-G60-US-FB-{n}", source_type=SourceType.FEEDBACK, source_name="Feedback", derivative="G60",
        market="US", text=text, polarity=polarity,
        meta={"vfc2": vfc2, "labels": labels, "source": source, "scope": scope, "feedback_type": ""},
    )  # fmt: skip


def _many(count, *, start=1, **kwargs):
    return [_fb(start + i, **kwargs) for i in range(count)]


def _study(n, attribute, *, polarity=-1, neg="0.16"):
    return Evidence(
        id=f"EV-G60-US-ST-{n:02d}", source_type=SourceType.STUDY, source_name="US-Studie 2025",
        derivative="G60", market="US", text=f"{attribute}: 16 % dissatisfied", polarity=polarity,
        meta={"attribute": attribute, "neg_share": neg, "top2": "0.30"},
    )  # fmt: skip


def _by_title(signals: list[Signal]) -> dict[str, Signal]:
    return {s.title: s for s in signals}


def test_gruppe_ab_fuenf_nennungen_wird_befund_darunter_faellt_weg():
    five = _many(MIN_MENTIONS, labels="Navigation/Difficult to Use")
    four = _many(MIN_MENTIONS - 1, start=100, labels="Braking/Defect")
    signals = _by_title(extract_signals(SCENARIO, five + four))

    assert list(signals) == ["Navigation: complaint"]
    sig = signals["Navigation: complaint"]
    assert sig.kind == SignalKind.COMPLAINT
    assert sig.category == Category.INFOTAINMENT_DIGITAL
    assert sig.mention_count == 5
    assert sig.source_types == [SourceType.FEEDBACK]


def test_art_aus_feedback_typ_und_bei_leerem_typ_aus_der_polaritaet():
    evidence = (
        _many(5, labels="Seats/Likes", polarity=1)
        + _many(5, start=10, labels="Seats/Wants", polarity=-1)
        + _many(5, start=20, labels="Braking/Defect", polarity=-1)
        + _many(5, start=30, labels="Navigation/", polarity=1)  # BMW-Typ leer, Polarität +1
        + _many(5, start=40, labels="Steering/", polarity=0)  # leer und neutral: kein Befund
    )
    kinds = {s.title: s.kind for s in extract_signals(SCENARIO, evidence)}

    assert kinds["Seats: delight"] == SignalKind.DELIGHT
    assert kinds["Seats: unmet_need"] == SignalKind.UNMET_NEED
    assert kinds["Braking: complaint"] == SignalKind.COMPLAINT
    assert kinds["Navigation: delight"] == SignalKind.DELIGHT
    assert not any(t.startswith("Steering") for t in kinds)


def test_themenname_mit_schrägstrich_wird_richtig_aus_den_labels_gelesen():
    evidence = _many(5, labels="Handling / Riding/Likes", polarity=1)
    [sig] = extract_signals(SCENARIO, evidence)
    assert sig.title == "Handling / Riding: delight"
    assert sig.category == Category.DRIVING_EXPERIENCE


def test_ein_beleg_mit_zwei_themen_zaehlt_in_beiden_gruppen():
    both = _many(5, labels="Seats/Likes | Navigation/Difficult to Use", polarity=0)
    titles = {s.title: s.mention_count for s in extract_signals(SCENARIO, both)}
    assert titles == {"Seats: delight": 5, "Navigation: complaint": 5}


def test_out_of_scope_und_unbekannte_themen_werden_ignoriert():
    evidence = (
        _many(6, labels="Braking/Defect", scope="out")
        + _many(6, start=10, labels="no_class_found/Likes", polarity=1)
        + _many(6, start=20, labels="Some Unmapped Theme/Likes", polarity=1)
    )
    assert extract_signals(SCENARIO, evidence) == []


def test_zitate_sind_begrenzt_stammen_aus_der_eingabe_und_bevorzugen_normale_laenge():
    short = [_fb(n, labels="Seats/Likes", polarity=1, text="ok") for n in range(1, 11)]  # zu kurz zum Zitieren
    good = _many(12, start=100, labels="Seats/Likes", polarity=1)
    [sig] = extract_signals(SCENARIO, short + good)

    assert sig.mention_count == 22  # volle Gruppengröße, nicht nur die Zitate
    assert len(sig.evidence_ids) == MAX_QUOTES
    assert set(sig.evidence_ids) <= {e.id for e in short + good}
    assert all(i in {e.id for e in good} for i in sig.evidence_ids)
    assert sig.mention_count >= len(sig.evidence_ids)


def test_quelle_d_ohne_thema_wird_ueber_den_bereich_im_satz_zugeordnet():
    text = "Smooth and quiet. That is the one thing I love most about the driving feel of my vehicle."
    evidence = [
        _fb(n, labels="/", polarity=1, source="D", text=text).model_copy(update={"meta": {
            "vfc2": "", "labels": "/", "source": "D", "scope": "in", "feedback_type": ""}})
        for n in range(1, 6)
    ]  # fmt: skip
    [sig] = extract_signals(SCENARIO, evidence)

    assert sig.kind == SignalKind.DELIGHT
    assert sig.category == Category.DRIVING_EXPERIENCE
    assert sig.title == "Survey D, driving feel: delight"


def test_studie_wird_an_passenden_feedback_befund_gehaengt():
    evidence = [*_many(6, labels="Navigation/Difficult to Use"), _study(7, "Navigation system")]
    [sig] = extract_signals(SCENARIO, evidence)

    assert set(sig.source_types) == {SourceType.FEEDBACK, SourceType.STUDY}
    assert "EV-G60-US-ST-07" in sig.evidence_ids
    assert sig.mention_count == 6  # Studie ändert die Kommentarzahl nicht


def test_studie_ohne_feedback_befund_wird_eigener_complaint():
    [sig] = extract_signals(SCENARIO, [_study(3, "Navigation system")])

    assert sig.kind == SignalKind.COMPLAINT
    assert sig.source_types == [SourceType.STUDY]
    assert sig.evidence_ids == ["EV-G60-US-ST-03"]
    assert sig.category == Category.INFOTAINMENT_DIGITAL


def test_studie_ohne_problem_und_ausserhalb_des_scopes_wird_nicht_zum_befund():
    evidence = [
        _study(1, "Navigation system", polarity=0, neg="0.05"),
        _study(2, "Overall value for money"),  # Preis liegt laut Brief nicht im Umfang
    ]
    assert extract_signals(SCENARIO, evidence) == []


def test_ids_sind_fortlaufend_nach_nennungen_absteigend_und_zitieren_nur_vorhandene_belege():
    evidence = _many(5, labels="Seats/Likes", polarity=1) + _many(9, start=50, labels="Braking/Defect")
    signals = extract_signals(SCENARIO, evidence)

    assert [s.id for s in signals] == ["SIG-G60-US-001", "SIG-G60-US-002"]
    assert [s.mention_count for s in signals] == [9, 5]
    known = {e.id for e in evidence}
    assert all(set(s.evidence_ids) <= known for s in signals)
    assert all(s.summary and s.title for s in signals)


def test_lauf_ist_reproduzierbar():
    evidence = _many(7, labels="Seats/Likes", polarity=1) + _many(6, start=20, labels="Braking/Defect")
    first = [s.model_dump() for s in extract_signals(SCENARIO, evidence)]
    second = [s.model_dump() for s in extract_signals(SCENARIO, list(reversed(evidence)))]
    assert first == second


def test_obergrenze_haelt_die_liste_pruefbar_und_behaelt_die_groessten():
    names = list(VFC2_TO_CATEGORY)[: MAX_SIGNALS + 10]
    evidence = []
    for rank, name in enumerate(names):  # Gruppe i hat 5 + i Nennungen, die letzten sind die größten
        evidence += _many(5 + rank, start=1000 * (rank + 1), labels=f"{name}/Defect")
    signals = extract_signals(SCENARIO, evidence)

    assert len(signals) == MAX_SIGNALS
    assert signals[0].mention_count == 5 + len(names) - 1
    assert min(s.mention_count for s in signals) == 5 + 10  # die 10 kleinsten fielen weg


def test_angehaengte_studien_ueberschreiten_nie_die_nennungen():
    evidence = _many(MIN_MENTIONS, labels="Seats/Difficult to Use") + [
        _study(1, "Comfort of front seat"),
        _study(2, "Overall comfort of the seats"),
        _study(3, "Comfort of 2nd row seat"),
    ]  # fmt: skip
    [sig] = extract_signals(SCENARIO, evidence)

    assert sig.mention_count == MIN_MENTIONS
    assert len(sig.evidence_ids) <= sig.mention_count
    assert set(sig.source_types) == {SourceType.FEEDBACK, SourceType.STUDY}


def test_studienattribut_der_cn_eu_studie_haengt_am_feedback_befund():
    evidence = [*_many(6, labels="Space / spatial impression/Difficult to Use"), _study(5, "Rear interior roominess")]
    [sig] = extract_signals(SCENARIO, evidence)
    assert set(sig.source_types) == {SourceType.FEEDBACK, SourceType.STUDY}


def test_gruppe_mit_zwei_quellenarten_bleibt_trotz_obergrenze_drin():
    names = [n for n in VFC2_TO_CATEGORY if n != "Navigation"][: MAX_SIGNALS + 5]
    evidence = []
    for rank, name in enumerate(names):  # 50 große Gruppen füllen die Liste
        evidence += _many(50, start=1000 * (rank + 1), labels=f"{name}/Defect")
    evidence += _many(MIN_MENTIONS, start=900_000, labels="Navigation/Difficult to Use")  # klein, aber mit Studie
    evidence.append(_study(1, "Navigation system"))

    signals = extract_signals(SCENARIO, evidence)

    assert len(signals) == MAX_SIGNALS
    nav = {s.title: s for s in signals}["Navigation: complaint"]
    assert set(nav.source_types) == {SourceType.FEEDBACK, SourceType.STUDY}


def test_reine_studien_befunde_haben_ein_festes_kontingent_die_schlimmsten_zuerst():
    attributes = [
        "Overall exterior styling", "Appearance of tires/ wheels", "Headlight/ taillight design",
        "Overall interior styling/ aesthetics", "Interior lighting", "Instrument panel (IP)", "Cupholders",
        "Interior storage", "Overall comfort of the seats", "Interior roominess", "Cargo capacity/usefulness",
        "Heater performance",
    ]  # fmt: skip
    # Je höher die Nummer, desto größer der Unzufriedenen-Anteil
    evidence = [_study(n + 1, a, neg=f"{0.10 + n / 100:.2f}") for n, a in enumerate(attributes)]
    signals = extract_signals(SCENARIO, evidence)

    assert len(signals) == MAX_STUDY_ONLY
    worst = {a for a in attributes[-MAX_STUDY_ONLY:]}
    assert {s.title.removesuffix(": complaint") for s in signals} == worst


def test_wuensche_bekommen_reservierte_plaetze_auch_wenn_sie_klein_sind():
    # Wünsche zerfallen in viele kleine Gruppen; ohne Reservierung kämen sie nie in die Top 45.
    big = list(VFC2_TO_CATEGORY)[: MAX_SIGNALS + 5]
    evidence = []
    for rank, name in enumerate(big):
        evidence += _many(60, start=1000 * (rank + 1), labels=f"{name}/Likes", polarity=1)
    wants = ["Navigation", "Radio function", "Seat massage"]
    for rank, name in enumerate(wants):
        evidence += _many(MIN_MENTIONS, start=900_000 + 100 * rank, labels=f"{name}/Wants")
    signals = extract_signals(SCENARIO, evidence)

    needs = {s.title for s in signals if s.kind == SignalKind.UNMET_NEED}
    assert needs == {f"{name}: unmet_need" for name in wants}
    assert len(signals) == MAX_SIGNALS
