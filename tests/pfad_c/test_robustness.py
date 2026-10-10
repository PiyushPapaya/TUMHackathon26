"""W-C2: Rang-Robustheit. Wie stabil ist der Rang, wenn jedes Gewicht zufällig um ±30 % schwankt?

Brief: "a clear understanding of uncertainty". Die Gewichte sind Startwerte (Grenze 1 im Spickzettel), also
zeigen wir, ob die Reihenfolge davon abhängt. Pitch-Satz: "Die Nr. 1 bleibt in X % aller plausiblen
Gewichtungen vorne." Nur Standardbibliothek, fester Seed: gleiche Eingabe = gleiche Zahl.
"""

import pytest

from core.models import EvidenceLevel, OfferCheck, Requirement, ScoreFactor
from requirements_engine import scoring
from requirements_engine.robustness import PERTURBATION, RUNS, compute_robustness

NAMES = list(scoring.DEFAULT_WEIGHTS)


def _req(rid: str, values: dict[str, float] | float, level=EvidenceLevel.A) -> Requirement:
    values = {n: values for n in NAMES} if isinstance(values, float) else values
    breakdown = {n: ScoreFactor(value=values.get(n, 0.0), weight=scoring.DEFAULT_WEIGHTS[n], contribution=0,
                                explanation="x") for n in NAMES}
    return Requirement(id=rid, title=rid, description="d", acceptance_criterion="c", category="exterior",
                       signal_ids=["S"], score=0, rank=0, score_breakdown=breakdown, rationale="r",
                       evidence_level=level, assumptions=[], uncertainties=[],
                       offer_check=OfferCheck(status="unknown", note=""))


def test_gleiche_eingabe_gleiches_ergebnis():
    reqs = [_req("A", 0.9), _req("B", 0.5), _req("C", 0.2)]
    assert compute_robustness(reqs) == compute_robustness(reqs)


def test_klar_dominante_anforderung_bleibt_immer_auf_platz_1():
    result = compute_robustness([_req("A", 0.9), _req("B", 0.4), _req("C", 0.3), _req("D", 0.2)])
    assert result["A"].rank_min == result["A"].rank_max == 1 and result["A"].top3_share == 1.0
    assert result["D"].rank_min == result["D"].rank_max == 4 and result["D"].top3_share == 0.0


def test_laufzahl_und_grenzen():
    result = compute_robustness([_req("A", 0.9), _req("B", 0.5)])
    assert result["A"].runs == RUNS == 500 and PERTURBATION == 0.3
    assert all(1 <= r.rank_min <= r.rank_max <= 2 and 0 <= r.top3_share <= 1 for r in result.values())


def test_knappes_rennen_zeigt_eine_spanne():
    # A stark bei reach, B stark bei effort: je nach Gewichtung vorn. Die Spanne muss das zeigen.
    # Vorsprung A: 0,5 x Gewicht(reach) = 0,10. Vorsprung B: 1,0 x Gewicht(effort) = 0,10.
    # Mit den Standardgewichten also Gleichstand: schon kleine Verschiebungen kippen die Reihenfolge.
    a = _req("A", {"customer_pain": 0.8, "reach": 0.9, "effort_inverse": 0.0})
    b = _req("B", {"customer_pain": 0.8, "reach": 0.4, "effort_inverse": 1.0})
    result = compute_robustness([a, b])
    assert (result["A"].rank_min, result["A"].rank_max) == (1, 2)
    assert (result["B"].rank_min, result["B"].rank_max) == (1, 2)


def test_spanne_enthaelt_den_unverschobenen_rang():
    reqs = [_req("A", 0.9), _req("B", 0.5, EvidenceLevel.B), _req("C", 0.5, EvidenceLevel.C)]
    base = sorted(reqs, key=lambda r: -scoring.score({k: f.value for k, f in r.score_breakdown.items()}, {},
                                                      r.evidence_level)[0])
    result = compute_robustness(reqs)
    for rank, req in enumerate(base, start=1):
        assert result[req.id].rank_min <= rank <= result[req.id].rank_max


def test_schwache_evidenz_wird_abgewertet_auch_bei_gleichen_faktoren():
    result = compute_robustness([_req("stark", 0.6, EvidenceLevel.A), _req("schwach", 0.6, EvidenceLevel.D)])
    assert result["stark"].rank_max == 1 and result["schwach"].rank_min == 2


@pytest.mark.parametrize("reqs", [[], [_req("A", 0.5)]])
def test_leere_oder_einzelne_liste_stuerzt_nicht_ab(reqs):
    result = compute_robustness(reqs)
    assert len(result) == len(reqs)
    if reqs:
        assert (result["A"].rank_min, result["A"].rank_max, result["A"].top3_share) == (1, 1, 1.0)


def test_derive_all_fuellt_robustness(monkeypatch):
    from core.models import Category, Scenario, Signal, SignalKind, SourceType
    from requirements_engine import derive
    from requirements_engine.derive import RequirementDraft, RequirementDrafts, derive_all

    scenario = Scenario(id="G60-US", derivative="G60", model_name="5", market="US", countries=["US"], competitors=[])
    signals = [Signal(id=f"SIG-{n}", kind=SignalKind.COMPLAINT, category=Category.EXTERIOR, title="t", summary="s",
                      evidence_ids=["E"], mention_count=10 * n, source_types=[SourceType.FEEDBACK]) for n in (1, 2)]
    drafts = [RequirementDraft(title=f"R{n}", description="d", acceptance_criterion="c", category=Category.EXTERIOR,
                               signal_ids=[f"SIG-{n}"]) for n in (1, 2)]
    monkeypatch.setattr(derive, "ask_json", lambda *a, **k: RequirementDrafts(drafts=drafts))
    reqs, _ = derive_all(scenario, signals, [], {})
    assert all(r.robustness is not None and r.robustness.runs == 500 for r in reqs)
