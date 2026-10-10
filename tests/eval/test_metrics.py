"""Rechenfunktionen der Eval mit erfundenen Daten."""

from eval_metrics import coverage, fidelity, grounding_rate, numbers_share, sample_pairs, verbatim_rate


def test_grounding_und_wortlaut():
    assert grounding_rate(["A", "B", "X"], {"A", "B"}) == 2 / 3
    assert grounding_rate([], {"A"}) is None  # nichts gemessen heißt nicht 100 %
    assert verbatim_rate([" Hello ", "Changed"], {"Hello"}) == 0.5


def test_abdeckung_zaehlt_jeden_kommentar_einmal():
    groups = {"S1": ["a", "b"], "S2": ["b", "c"], "S3": ["zzz"]}  # zzz ist kein Kommentar der Menge
    assert coverage(groups, {"a", "b", "c", "d"}) == 0.75


def test_zahl_im_kriterium():
    assert numbers_share(["Bedienung in max. 2 Schritten", "deutlich besser"]) == 0.5
    assert numbers_share([]) is None


def test_treue_ignoriert_leere_zeilen_und_gross_klein():
    assert fidelity(["j", "J", "n", "", " "]) == 2 / 3
    assert fidelity(["", ""]) is None


def test_stichprobe_ist_mit_seed_42_stabil_und_ohne_duplikate():
    pairs = [(f"S{i % 5}", f"E{i}") for i in range(200)]
    first = sample_pairs(pairs, n=50)
    assert first == sample_pairs(list(reversed(pairs)), n=50)  # Reihenfolge der Eingabe egal
    assert len(first) == len(set(first)) == 50
