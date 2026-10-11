"""Belege und Gegenbelege einer Anforderung, inklusive widersprechender Befunde."""

from core.models import Requirement


def challenge_context(state, req: Requirement) -> tuple[list, list]:
    linked = [state.signals[s] for s in req.signal_ids if s in state.signals]
    signal_ids = list(dict.fromkeys([s.id for s in linked] + [i for s in linked for i in s.conflicts_with]))
    signals = [state.signals[i] for i in signal_ids if i in state.signals]
    evidence_ids = {i for s in signals for i in s.evidence_ids}
    counter = state.context.get("counter_evidence", {})
    evidence_ids.update(i for s in linked for i in counter.get(s.id, []))
    evidence_ids.update(i for conflict in req.segment_conflicts for i in conflict.evidence_ids)
    return signals, [state.evidence[i] for i in sorted(evidence_ids) if i in state.evidence]
