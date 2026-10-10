"""KI-Antwort, wenn der PM eine Anforderung hinterfragt ("Challenge") (Owner: Pfad C).

Warum: Der Brief will, dass der PM Begründung und Belege "challengen" kann. Die KI
verteidigt die Anforderung nicht blind, sondern nennt Belege UND Gegenbelege
(Devil's Advocate) und schlägt ggf. eine Änderung vor. Der PM entscheidet.

Startversion ohne LLM: fasst vorhandene Belege und Unsicherheiten regelbasiert zusammen.
TODO Pfad C: LLM-Version mit core.llm.ask_json, die nur zitierte Beleg-IDs verwenden darf.
"""

from __future__ import annotations

from core.models import Evidence, Requirement, Signal


def answer_challenge(req: Requirement, question: str, signals: list[Signal], evidence: list[Evidence]) -> dict:
    supporting = [e for e in evidence if e.polarity <= 0][:3]
    contrary = [e for e in evidence if e.polarity > 0][:2]
    lines = [f"Frage des PM: {question}",
             f"Stützende Belege ({len(supporting)}): " + "; ".join(f"{e.id}" for e in supporting)]
    if contrary:
        lines.append("Gegenbelege: " + "; ".join(e.id for e in contrary))
    if req.uncertainties:
        lines.append("Offene Unsicherheit: " + req.uncertainties[0])
    return {
        "answer": "\n".join(lines),
        "supporting_evidence_ids": [e.id for e in supporting],
        "counter_evidence_ids": [e.id for e in contrary],
        "suggested_change": None,
    }
