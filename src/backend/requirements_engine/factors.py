"""Faktoren der Priorisierung, berechnet im Code (Owner: Pfad C, Ticket C3).

Warum im Code und nicht im LLM: Gleiche Eingabe muss gleiche Zahl ergeben, und der PM sieht im
Wasserfall zu jedem Wert einen Satz, woher er kommt. Alle Werte liegen zwischen 0 und 1.
Fehlen Daten (keine Studie, kein Vertrauenswert), zählt der Faktor 0 und der Satz sagt es offen.
"""

from __future__ import annotations

import math
from collections import Counter

from core.models import Evidence, ScoreFactor, Signal, SignalKind
from requirements_engine import scoring

# Schwere je Art des Befunds: Beschwerden stören am meisten, Trends sind nur Annahmen.
SEVERITY = {
    SignalKind.COMPLAINT: 1.0, SignalKind.UNMET_NEED: 0.7, SignalKind.COMPETITOR_ADVANTAGE: 0.5,
    SignalKind.DELIGHT: 0.4, SignalKind.TREND: 0.3,
}
KIND_LABEL = {
    SignalKind.COMPLAINT: "complaints", SignalKind.UNMET_NEED: "unmet needs",
    SignalKind.COMPETITOR_ADVANTAGE: "competitor advantages", SignalKind.DELIGHT: "strengths",
    SignalKind.TREND: "trends",
}
TRUST_VALUE = {"high": 1.0, "medium": 0.6}
US_FULL_GAP = 0.25  # 25 % Unzufriedene in der US-Studie zählen als volle Lücke (Startwert, C7 prüft)


def _number(text: str | None) -> float | None:
    try:
        return float(text) if text not in (None, "") else None
    except ValueError:
        return None


def _customer_pain(signals: list[Signal], by_id: dict[str, Evidence]) -> tuple[float, str]:
    total = sum(s.mention_count for s in signals)
    if total == 0:
        return 0.0, "no mentions"
    value = sum(SEVERITY[s.kind] * s.mention_count for s in signals) / total
    weight_by_kind: Counter = Counter()
    for s in signals:
        weight_by_kind[s.kind] += s.mention_count
    top_kind = weight_by_kind.most_common(1)[0][0]
    types = Counter(by_id[i].meta.get("feedback_type", "") for s in signals for i in s.evidence_ids if i in by_id)
    names = [name for name, _ in types.most_common(2) if name]
    detail = f" ({' / '.join(names)})" if names else ""
    return value, f"Mostly {KIND_LABEL[top_kind]}{detail}, {total} mentions"


def _reach(mentions: int, max_mentions: int, context: dict) -> tuple[float, str]:
    # Wurzel statt linear (Entscheidung Sa 10.10.): Auf den echten Daten reichen die Nennungen von 7 bis 581,
    # linear bekäme fast jede Anforderung unter 0,3 und reach wäre wirkungslos. Doppelt so viele Kunden
    # heißt nicht doppelt so wichtig.
    value = math.sqrt(min(mentions / max_mentions, 1.0)) if max_mentions else 0.0
    sales = context.get("sales", {})
    share = sales.get("share_of_total_2030")
    market = f"; {sales.get('market', '?')} = {share * 100:.0f} % of 2030 volume" if share is not None else ""
    return value, f"{mentions} of at most {max_mentions} mentions (square root scale){market}"


def _satisfaction_gap(signals: list[Signal], by_id: dict[str, Evidence]) -> tuple[float, str]:
    best, best_text = 0.0, "no study data"
    for s in signals:
        for i in s.evidence_ids:
            meta = by_id[i].meta if i in by_id else {}
            neg, mean = _number(meta.get("neg_share")), _number(meta.get("mean"))
            if neg is not None:  # US-Studie: Anteil Unzufriedener (0-1, auch als Prozent lesbar)
                neg = neg / 100 if neg > 1 else neg
                value, text = neg / US_FULL_GAP, f"{meta.get('attribute', 'study')}: {neg * 100:.0f} % unsatisfied"
            elif mean is not None:  # CN/EU-Studie: Mittelwert 1-10, Ziel 9
                value, text = (9 - mean) / 3, f"{meta.get('attribute', 'study')}: mean {mean:g} of 10"
            else:
                continue
            if best_text == "no study data" or value > best:
                best, best_text = value, text
    return min(max(best, 0.0), 1.0), best_text


def _competitive_pressure(signals: list[Signal], by_id: dict[str, Evidence]) -> tuple[float, str]:
    best, trust_name = 0.0, ""
    for s in signals:
        if s.kind != SignalKind.COMPETITOR_ADVANTAGE:
            continue
        for i in s.evidence_ids:
            trust = by_id[i].meta.get("trust", "") if i in by_id else ""
            if TRUST_VALUE.get(trust, 0.0) > best:
                best, trust_name = TRUST_VALUE[trust], trust
    if not best:
        return 0.0, "no trusted web source shows a competitor advantage"
    return best, f"competitor advantage backed by a {trust_name}-trust web source"


def _future_relevance(signals: list[Signal], forward_looking: bool) -> tuple[float, str]:
    if any(s.kind == SignalKind.TREND for s in signals):
        return 1.0, "linked to a 3-5 year trend (assumption)"
    if forward_looking:
        return 0.5, "rests partly on a forward-looking assumption"
    return 0.1, "no trend behind it"


def compute_factors(
    signals: list[Signal], by_id: dict[str, Evidence], max_mentions: int,
    forward_looking: bool, effort: str, context: dict,
) -> tuple[dict[str, float], dict[str, str]]:
    """Liefert (Faktorwerte 0-1, Erklärsatz je Faktor) für eine Anforderung."""
    mentions = sum(s.mention_count for s in signals)
    parts = {
        "customer_pain": _customer_pain(signals, by_id),
        "reach": _reach(mentions, max_mentions, context),
        "satisfaction_gap": _satisfaction_gap(signals, by_id),
        "competitive_pressure": _competitive_pressure(signals, by_id),
        "future_relevance": _future_relevance(signals, forward_looking),
        "effort_inverse": (scoring.effort_factor(effort), f"effort estimate {effort}"),
    }
    return {k: min(max(v, 0.0), 1.0) for k, (v, _) in parts.items()}, {k: t for k, (_, t) in parts.items()}


def rationale_from(breakdown: dict[str, ScoreFactor]) -> str:
    """Ein Satz aus den zwei größten Beiträgen: so liest der PM sofort, warum der Platz stimmt."""
    top = sorted(breakdown.items(), key=lambda kv: -kv[1].contribution)[:2]
    named = [f"{name.replace('_', ' ')} ({f.contribution:g} points)" for name, f in top]
    return "Ranked mainly because of " + " and ".join(named) + "."
