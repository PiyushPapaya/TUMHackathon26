"""Successor relevance is an explicit assumption, never a score factor."""

from core.models import Requirement, Signal, SignalKind, SourceType


def outlook(req: Requirement, linked_signals: list[Signal], evidence_by_id: dict,
            web_signals: list[Signal], successor_year: str) -> dict:
    # WARUM: Nur Kundenfeedback bildet den Nenner; EPA, Web und Studien sind keine Kommentare.
    feedback = {i: e for i, e in evidence_by_id.items() if e.source_type == SourceType.FEEDBACK}
    linked_ids = {i for s in linked_signals for i in s.evidence_ids}
    critical = [e for i, e in feedback.items() if i in linked_ids and e.polarity == -1]
    total, count = len(feedback), len(critical)
    bev_total = sum(e.meta.get("engine") in ("BEV", "BEVE") for e in feedback.values())
    ice_total = sum(e.meta.get("engine") == "ICE" for e in feedback.values())
    bev_count = sum(e.meta.get("engine") in ("BEV", "BEVE") for e in critical)
    ice_count = sum(e.meta.get("engine") == "ICE" for e in critical)
    bev_average, ice_average = (bev_total / total, ice_total / total) if total else (0, 0)
    bev_critical, ice_critical = (bev_count / count, ice_count / count) if count else (0, 0)
    result = {"direction": "stays", "rule": "no_shift", "successor_year": successor_year,
              "assumption": True, "sentence": "No trend or segment shift found; expected to stay as relevant as today.",
              "critical_count": count, "scenario_feedback_count": total,
              "bev_critical_share": bev_critical, "bev_scenario_share": bev_average,
              "ice_critical_share": ice_critical, "ice_scenario_share": ice_average,
              "evidence_ids": [], "signal_ids": []}
    # WARUM: Kategorie-Verknüpfung erweitert den Ausblick, ohne Score-Zitate oder Ränge zu ändern.
    trends = sorted((s for s in web_signals if s.kind == SignalKind.TREND and s.category == req.category),
                    key=lambda s: s.id)
    if trends:
        ids = sorted({i for s in trends for i in s.evidence_ids if i in evidence_by_id
                      and evidence_by_id[i].source_type == SourceType.WEB})
        sources = ", ".join(sorted({evidence_by_id[i].source_name for i in ids})) or "web trend finding"
        result.update(direction="grows", rule="category_trend", evidence_ids=ids,
                      signal_ids=[s.id for s in trends],
                      sentence=f"A trend in {req.category.replace('_', ' ')} ({sources}) makes this more "
                               f"important by {successor_year}. Assumption.")
    # WARUM: Unter zehn kritischen Kommentaren wäre ein Segmentwechsel zu leicht Zufall.
    elif count >= 10 and bev_total > 0 and 2 * bev_count * total >= 3 * bev_total * count:
        result.update(direction="grows", rule="bev_shift", evidence_ids=sorted(e.id for e in critical),
                      sentence=f"{bev_critical:.1%} of critical comments come from BEV drivers "
                               f"(scenario average {bev_average:.1%}). The successor will be more electric, "
                               "so this grows. Assumption.")
    elif count >= 10 and ice_critical >= 0.9 and ice_average < 0.9:
        result.update(direction="fades", rule="ice_shift", evidence_ids=sorted(e.id for e in critical),
                      sentence="Criticism comes almost only from combustion drivers; it shrinks as the "
                               "line electrifies. Assumption.")
    return result
