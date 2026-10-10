"""Entscheidungshilfen je Anforderung: Matrix, Markt-Gegenstück, Memo (Owner: Lead).

Warum: Der Brief will "evidence vs. assumptions" trennen und "3-5 years ahead" denken.
- Matrix: x = Horizont (heute / Nachfolger, kommt schon aus der Pipeline: Requirement.horizon),
  y = Evidenzstufe. Vier Felder mit festen Regeln statt Bauchgefühl.
- Gegenstück: gleiche Kategorie + ähnliche Titelwörter (Jaccard) im anderen Szenario.
  Verworfen: Embeddings (zusätzliche Abhängigkeit, nicht nachrechenbar für den PM).
- Memo: Markdown, komplett in Python gebaut (kein LLM), damit jede Zahl aus dem Store stammt.
Alles reine Funktionen: lesen den Zustand, ändern nichts.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from core.models import EvidenceLevel, Requirement
from core.views import LEVEL_LABEL

STRONG = (EvidenceLevel.A, EvidenceLevel.B)
QUADRANTS = {
    ("today", True): "Sicher & dringend", ("next_gen", True): "Belegte Zukunftswette",
    ("today", False): "Schwach belegt, heute", ("next_gen", False): "Annahme – beobachten",
}
OFFER_LABEL = {"not_offered": "Lücke: nicht angeboten", "optional": "nur optional", "standard": "Serie",
               "unknown": "Angebot unbekannt"}
MATCH_FROM = 0.3  # Jaccard der Titelwörter ab 0,3 = gleiches Thema
MEMO_FALLBACK_N = 5


def quadrant(horizon: str, level: EvidenceLevel) -> str:
    return QUADRANTS[(horizon, level in STRONG)]


def matrix(state) -> dict:
    """Je Anforderung Feld der Matrix + Ausstattungs-Lücke, damit das Frontend nur anzeigt."""
    items = {r.id: {"horizon": r.horizon, "evidence_level": r.evidence_level,
                    "quadrant": quadrant(r.horizon, r.evidence_level),
                    "offer_gap": r.offer_check.status, "offer_gap_label": OFFER_LABEL.get(r.offer_check.status,
                                                                                         r.offer_check.status)}
             for r in state.requirements.values()}
    return {"scenario_id": state.scenario.id, "successor_horizon": state.scenario.successor_horizon,
            "quadrants": list(QUADRANTS.values()), "items": items,
            "rule": "Zukunft = Horizont next_gen (Pipeline); belegt = Evidenzstufe A oder B."}


def _words(title: str) -> set[str]:
    return {w for w in re.findall(r"\w+", title.lower()) if len(w) > 2}


def jaccard(a: str, b: str) -> float:
    wa, wb = _words(a), _words(b)
    return len(wa & wb) / len(wa | wb) if wa | wb else 0.0


def counterparts(state, req: Requirement, others: dict) -> list[dict]:
    """Für jedes andere Szenario: ähnlichste Anforderung gleicher Kategorie oder "kein Gegenstück"."""
    rows = []
    for sid, other in sorted(others.items()):
        if sid == state.scenario.id:
            continue
        same_cat = [r for r in other.requirements.values() if r.category == req.category]
        best = max(same_cat, key=lambda r: jaccard(req.title, r.title), default=None)
        sim = round(jaccard(req.title, best.title), 2) if best else 0.0
        if best is None or sim < MATCH_FROM:
            rows.append({"scenario_id": sid, "match": None, "similarity": sim, "sentence": "kein Gegenstück"})
            continue
        rows.append({"scenario_id": sid, "similarity": sim,
                     "match": {"id": best.id, "title": best.title, "rank": best.rank, "score": best.score,
                               "evidence_level": best.evidence_level},
                     "sentence": f"{sid}: Platz {best.rank}, Score {round(best.score)}"})
    return rows


def _evidence_count(state, req: Requirement) -> int:
    return len({e for s in req.signal_ids if s in state.signals for e in state.signals[s].evidence_ids})


def memo(state, verify: dict) -> str:
    """Entscheidungs-Memo für das Gremium. Ohne Freigabe: Top 5, klar als Entwurf markiert."""
    ranked = sorted(state.requirements.values(), key=lambda r: r.rank)
    approved = [r for r in ranked if r.status.value == "approved"]
    chosen = approved or ranked[:MEMO_FALLBACK_N]
    sc = state.scenario
    lines = [f"# Entscheidungs-Memo {sc.model_name} {sc.market} ({sc.id})",
             f"Stand: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC · Nachfolger-Horizont {sc.successor_horizon}",
             "",
             f"**{len(approved)} vom PM freigegebene Anforderungen.**" if approved
             else f"**Entwurf: noch nichts freigegeben, hier die Top {len(chosen)} nach Score.**", ""]
    for r in chosen:
        lvl = r.evidence_level.value
        lines += [f"## {r.rank}. {r.title} ({r.id})",
                  f"- Score {r.score} · Evidenzstufe {lvl} ({LEVEL_LABEL[lvl]}) · "
                  f"{_evidence_count(state, r)} Belege · Angebot heute: {OFFER_LABEL.get(r.offer_check.status, '?')}",
                  f"- Abnahmekriterium: {r.acceptance_criterion}",
                  f"- Begründung: {r.rationale}"]
        lines += [f"- Annahme: {a}" for a in r.assumptions] or ["- Annahmen: keine"]
        lines.append("")
    status = "gültig" if verify.get("valid") else f"VERLETZT bei Ereignis {verify.get('broken_at_seq')}"
    lines.append(f"---\nPrüfpfad {status}, {verify.get('checked', 0)} Ereignisse (Hash-Kette, /api/audit/verify).")
    return "\n".join(lines) + "\n"
