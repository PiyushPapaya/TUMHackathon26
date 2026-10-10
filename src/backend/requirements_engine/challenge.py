"""KI-Antwort, wenn der PM eine Anforderung hinterfragt ("Challenge") (Owner: Pfad C, Ticket C6).

Warum: Der Brief will, dass der PM Begründung und Belege "challengen" kann. Die KI verteidigt die
Anforderung nicht blind, sondern nennt Belege UND Gegenbelege (Devil's Advocate) und schlägt ggf. eine
Änderung vor. Der PM entscheidet.

Sicherheit (gleiche Regeln wie überall):
- Die KI sieht höchstens 30 Belege und darf nur deren IDs nennen; unbekannte IDs entfernt der Code.
- Ein Beleg ist nie zugleich Beleg und Gegenbeleg.
- Fällt die KI aus (kein Netz, Demo-Cache-Fehlschlag), kommt die regelbasierte Antwort. Das Format
  (answer, supporting_evidence_ids, counter_evidence_ids, suggested_change) bleibt gleich, weil API
  und Oberfläche es schon nutzen.
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from core.llm import ask_json
from core.models import Evidence, Requirement, Signal

MAX_EVIDENCE = 30
SYSTEM_PROMPT = """You are a critical reviewer for a BMW product manager (PM). The PM challenges a
requirement. Do NOT defend it blindly: be a fair devil's advocate. Write in English, at most 120 words.
- Start with a one-word verdict ("Yes.", "No.", "Partly." or "Unclear.") that matches what follows, then
  answer using only the evidence given. If the evidence cannot answer the question, say "Unclear." and why.
- supporting_evidence_ids: evidence that customers NEED this requirement. Complaints about today's car
  and dissatisfied study scores SUPPORT it, even if they show the target is hard to reach.
- counter_evidence_ids: evidence that the need is smaller, already solved or limited: praise for today's
  solution, satisfied study scores, other markets or customer groups, competitors without it, opposing views.
  Never list a complaint as counter-evidence. Use ONLY ids from the input.
- Never invent facts, numbers or quotes. Refer to counts only if they appear in the input.
- suggested_change: a concrete change to the requirement or its criterion if the challenge is justified,
  otherwise null."""


class ChallengeAnswer(BaseModel):
    answer: str
    supporting_evidence_ids: list[str] = []
    counter_evidence_ids: list[str] = []
    suggested_change: str | None = None


def _select(evidence: list[Evidence]) -> list[Evidence]:
    """Höchstens 30 Belege, abwechselnd aus allen Polaritäten, damit Gegenstimmen nicht untergehen."""
    groups = [[e for e in evidence if e.polarity == p] for p in (-1, 0, 1)]
    chosen: list[Evidence] = []
    while len(chosen) < MAX_EVIDENCE and any(groups):
        for group in groups:
            if group and len(chosen) < MAX_EVIDENCE:
                chosen.append(group.pop(0))
    return chosen


def _rule_based(req: Requirement, question: str, evidence: list[Evidence]) -> dict:
    supporting = [e for e in evidence if e.polarity <= 0][:3]
    contrary = [e for e in evidence if e.polarity > 0][:2]
    lines = [f"PM question: {question}",
             f"Supporting evidence ({len(supporting)}): " + "; ".join(e.id for e in supporting)]
    if contrary:
        lines.append("Counter-evidence: " + "; ".join(e.id for e in contrary))
    if req.uncertainties:
        lines.append("Open uncertainty: " + req.uncertainties[0])
    return {"answer": "\n".join(lines), "supporting_evidence_ids": [e.id for e in supporting],
            "counter_evidence_ids": [e.id for e in contrary], "suggested_change": None}


def answer_challenge(req: Requirement, question: str, signals: list[Signal], evidence: list[Evidence]) -> dict:
    fallback = _rule_based(req, question, evidence)
    chosen = _select(list(evidence))
    if not chosen:
        return fallback
    payload = {
        "requirement": {"title": req.title, "description": req.description,
                        "acceptance_criterion": req.acceptance_criterion, "assumptions": req.assumptions,
                        "uncertainties": req.uncertainties},
        "question": question,
        "signals": [{"id": s.id, "kind": s.kind.value, "title": s.title, "summary": s.summary,
                     "mention_count": s.mention_count, "conflicts_with": s.conflicts_with} for s in signals],
        "evidence": [{"id": e.id, "source": e.source_type.value, "market": e.market, "polarity": e.polarity,
                      "text": e.text[:300]} for e in chosen],
    }
    try:
        answer = ask_json(SYSTEM_PROMPT, json.dumps(payload, ensure_ascii=False), ChallengeAnswer)
    except Exception:  # kein Netz, Demo-Cache-Fehlschlag, Schemafehler: die API darf nie ausfallen
        return fallback
    known = {e.id for e in chosen}
    supporting = [i for i in dict.fromkeys(answer.supporting_evidence_ids) if i in known]
    counter = [i for i in dict.fromkeys(answer.counter_evidence_ids) if i in known and i not in supporting]
    if not answer.answer.strip():
        return fallback
    return {"answer": answer.answer.strip(), "supporting_evidence_ids": supporting,
            "counter_evidence_ids": counter, "suggested_change": answer.suggested_change}
