"""Lastenheft-Export aus dem aktuellen, vom PM bearbeiteten Zustand."""


def requirements_markdown(state) -> str:
    lines = [f"# Requirements: {state.scenario.model_name} ({state.scenario.market})", "",
             f"Successor horizon: {state.scenario.successor_horizon}", ""]
    for req in sorted(state.requirements.values(), key=lambda r: r.rank):
        evidence_ids = sorted({i for sid in req.signal_ids if sid in state.signals
                               for i in state.signals[sid].evidence_ids})
        lines += [f"## {req.rank}. {req.title}", "", f"ID: {req.id} | Status: {req.status.value} | "
                  f"Score: {req.score} | Evidence level: {req.evidence_level.value}", "",
                  req.description, "", f"Acceptance criterion: {req.acceptance_criterion}", "",
                  f"Priority rationale: {req.rationale}", "", "Evidence:", ""]
        for eid in evidence_ids:
            ev = state.evidence.get(eid)
            if ev:
                source = f" ({ev.url})" if ev.url else ""
                lines.append(f"- {eid}: {ev.source_name}{source} — {ev.text}")
        lines += ["", "Assumptions:", "", *[f"- {x}" for x in req.assumptions or ["None recorded."]],
                  "", "Uncertainties:", "", *[f"- {x}" for x in req.uncertainties or ["None recorded."]], "",
                  f"Current offer: {req.offer_check.status}. {req.offer_check.note}", ""]
    return "\n".join(lines)
