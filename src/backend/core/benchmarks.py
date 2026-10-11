"""Benchmarks Teil 1: Wie gut sind die KI-Vorschläge? Eine Zahl je Prüffrage, je Szenario (Owner: Lead).

Warum diese Messungen und keine anderen: Ein BMW-PM fragt vor jeder Freigabe dasselbe.
  1. Stimmt die Quelle?            -> grounding (jede zitierte ID existiert)
  2. Enthält das Kriterium Zahlen? -> measurable (Syntax-Heuristik, kein fachlicher Nachweis)
  3. Wie stark ist der Beleg?      -> strong_evidence (Stufe A/B) und triangulated (intern + extern)
  4. Kippt das Ranking bei kleinen Änderungen? -> rank_stability (Simulation, siehe unten)
  5. Was hat die KI verworfen?     -> scope_guard (Entwürfe außerhalb des Scopes, sichtbar statt still)
Verworfen: Modell-Benchmarks wie MMLU oder Token-Kosten. Sie sagen nichts darüber, ob DIESE Anforderung stimmt.

Alles rechnet Python aus dem geladenen Zustand, ohne LLM: gleiche Daten ergeben immer dieselbe Zahl.
"""

from __future__ import annotations

import random
import re

from core.models import EvidenceLevel, SourceType
from requirements_engine import scoring

SIMULATION_RUNS = 200
JITTER = 0.2  # jedes Gewicht zufällig ±20 %: so unsicher ist ein PM realistisch bei "wie wichtig ist Reichweite?"
TOP_N = 5
SEED = 42  # fester Seed: die Seite zeigt bei jedem Laden dieselbe Zahl

INTERNAL = {SourceType.FEEDBACK, SourceType.STUDY, SourceType.SALES, SourceType.OPTION_LIST}
EXTERNAL = {SourceType.WEB, SourceType.EXTERNAL_STAT, SourceType.FEEDBACK_EXTERNAL}


def _share(hits: int, total: int) -> float:
    return round(100 * hits / total, 1) if total else 0.0


def _metric(key: str, label: str, value: float, target: float | None, explain: str) -> dict:
    """target None = Orientierung ohne Soll (z. B. Abdeckung hängt an der Datenlage, nicht an der KI)."""
    return {"key": key, "label": label, "value": value, "unit": "%", "target": target,
            "ok": None if target is None else value >= target, "explain": explain}


def grounding(state) -> tuple[int, int]:
    """(gefundene, zitierte) IDs über beide Ketten: Anforderung -> Befund und Befund -> Beleg."""
    cited = [i for r in state.requirements.values() for i in r.signal_ids]
    found = sum(1 for i in cited if i in state.signals)
    for sig in state.signals.values():
        cited += sig.evidence_ids
        found += sum(1 for i in sig.evidence_ids if i in state.evidence)
    return found, len(cited)


def _scores(state, weights: dict[str, float]) -> dict[str, float]:
    out = {}
    for req in state.requirements.values():
        values = {k: f.value for k, f in req.score_breakdown.items()}
        values["effort_inverse"] = scoring.effort_factor(req.effort)
        out[req.id] = scoring.score(values, {}, req.evidence_level, weights)[0]
    return out


def _top(scores: dict[str, float], n: int) -> list[str]:
    return [rid for rid, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def rank_stability(state) -> tuple[float, float]:
    """Simulation: 200 Läufe mit verwackelten Gewichten. Ergebnis: (Top-5-Überlappung %, Platz 1 bleibt %).

    Warum: Ein Ranking, das bei ±20 % Gewicht komplett umfällt, ist Zufall und keine Empfehlung.
    """
    if not state.requirements:
        return 0.0, 0.0
    rng = random.Random(SEED)
    base = _top(_scores(state, state.weights), TOP_N)
    overlap = same_first = 0.0
    for _ in range(SIMULATION_RUNS):
        jittered = {k: w * rng.uniform(1 - JITTER, 1 + JITTER) for k, w in state.weights.items()}
        top = _top(_scores(state, jittered), TOP_N)
        overlap += len(set(top) & set(base)) / len(base)
        same_first += top[0] == base[0]
    return _share(overlap, SIMULATION_RUNS), _share(same_first, SIMULATION_RUNS)


def quality(state) -> dict:
    reqs = list(state.requirements.values())
    found, cited = grounding(state)
    measurable = sum(1 for r in reqs if re.search(r"\d", r.acceptance_criterion))
    strong = sum(1 for r in reqs if r.evidence_level in (EvidenceLevel.A, EvidenceLevel.B))
    internal = [s for s in state.signals.values() if INTERNAL & set(s.source_types)]
    confirmed = sum(1 for s in internal if EXTERNAL & set(s.source_types))
    overlap, first = rank_stability(state)
    evidence = state.funnel.get("evidence", len(state.evidence))
    return {
        "scenario_id": state.scenario.id, "model_name": state.scenario.model_name, "market": state.scenario.market,
        "funnel": {"evidence": evidence, "signals": len(state.signals), "requirements": len(reqs),
                   "discarded": len(state.discarded)},
        "metrics": [
            _metric("grounding", "Sources exist", _share(found, cited), 100,
                    f"{found} of {cited} cited IDs exist (requirement → finding → evidence)."),
            _metric("measurable", "Criteria containing a number (heuristic)", _share(measurable, len(reqs)), None,
                    f"{measurable} of {len(reqs)} acceptance criteria contain a number. "
                    "This syntax check does not prove meaningful measurability. Review the outcome, "
                    "test procedure, threshold, sample and baseline for relative targets."),
            _metric("rank_stability", "Top 5 stays stable", overlap, 80,
                    f"{SIMULATION_RUNS} simulated runs, every weight ±{JITTER:.0%}: "
                    f"average overlap with today's top {TOP_N}."),
            _metric("first_stays_first", "#1 stays #1", first, None,
                    f"Share of the {SIMULATION_RUNS} runs in which the top proposal keeps rank 1."),
            _metric("strong_evidence", "Strong or moderate evidence (A/B)", _share(strong, len(reqs)), None,
                    f"{strong} of {len(reqs)} proposals. Low values are honest: thin data stays visible as C/D."),
            _metric("triangulated", "Confirmed outside BMW data", _share(confirmed, len(internal)), None,
                    f"{confirmed} of {len(internal)} internal findings also have web or authority evidence."),
        ],
    }


def quality_all(states: dict) -> list[dict]:
    return [quality(states[sid]) for sid in sorted(states)]
