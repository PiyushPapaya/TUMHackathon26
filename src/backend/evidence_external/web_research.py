"""Pfad B: Webrecherche -> externe Belege + Befunde (Wettbewerb, Trends). KI autonom mit Quellen.

Vertrag (nicht ändern ohne Lead):
    research(scenario: Scenario, signals: list[Signal]) -> tuple[list[Evidence], list[Signal]]

Warum: Der Brief verlangt "enrich it with structured knowledge from the web" und
"trustworthy sources". Jede Webaussage braucht URL + Abrufdatum + Vertrauensstufe,
sonst darf sie nicht in einen Befund.

Ansatz:
1. Fragen generieren aus den Top-Befunden von Pfad A, z. B.
   "Bietet Mercedes E-Class 2026 physische Klimatasten?" und 3-5 Trendfragen für 2028-2031.
2. core.llm.ask_json(..., tools=[{"type": "web_search"}]) mit Schema
   {claims: [{text, url, publisher, published, supports_signal_id, stance}]}.
3. Quellen-Vertrauen regelbasiert (trust.py): Hersteller/Testmagazin/Studie > Forum > unbekannt.
   meta["trust"] = "high|medium|low". Nur high/medium in Befunde übernehmen.
4. Triangulation: Webbeleg bestätigt/widerspricht internem Befund -> Befund erhält
   zusätzliche evidence_ids und source_type "web" (hebt evtl. die Evidenzstufe).
5. Trend-Befunde (kind=trend) ohne interne Belege sind ANNAHMEN -> Evidenzstufe D.
Ergebnisse cachen (core.llm macht das), damit die Demo offline läuft.
"""

from __future__ import annotations

from datetime import UTC, datetime

from core.models import Evidence, Scenario, Signal, SignalKind, SourceType
from evidence_external.claims import Claim, ask_claims
from evidence_external.questions import Question, build_questions
from evidence_external.trust import trust_for_url

SUMMARY_CLAIMS = 3  # so viele Aussagen fasst der Befund zusammen; mehr wäre für den PM zu lang


def _url_key(url: str) -> str:
    """Gleiche Quelle trotz anderer Schreibweise (Slash am Ende, Großschreibung des Hosts, #Anker)."""
    return url.strip().split("#")[0].rstrip("/").lower()


def _evidence(scenario: Scenario, number: int, claim: Claim, question: Question, now: datetime) -> Evidence:
    meta = {
        "trust": trust_for_url(claim.url), "publisher": claim.publisher, "published": claim.published,
        "stance": claim.stance, "about": claim.about, "question_kind": question.kind,
    }
    if question.signal_id:  # nur Wettbewerbsfragen kennen ihren auslösenden internen Befund
        meta["supports_signal_id"] = question.signal_id
    return Evidence(
        id=f"EV-{scenario.id}-WEB-{number:02d}", source_type=SourceType.WEB, source_name=claim.publisher,
        derivative=scenario.derivative, market=scenario.market, text=claim.text,
        url=claim.url, retrieved_at=now, meta=meta,
    )


def _signal(scenario: Scenario, number: int, question: Question, usable: list[Evidence],
            internal_titles: dict[str, str]) -> Signal:
    if question.kind == "competitor":
        kind = SignalKind.COMPETITOR_ADVANTAGE
        title = f"{question.competitor}: {internal_titles.get(question.signal_id, question.category.value)}"
    else:
        kind = SignalKind.TREND
        title = f"Trend 2028-2031: {question.category.value}"
    return Signal(
        id=f"SIG-{scenario.id}-WEB-{number:02d}", kind=kind, category=question.category, title=title,
        summary=" ".join(e.text for e in usable[:SUMMARY_CLAIMS]),
        evidence_ids=[e.id for e in usable], mention_count=len(usable), source_types=[SourceType.WEB],
    )


def research(scenario: Scenario, signals: list[Signal]) -> tuple[list[Evidence], list[Signal]]:
    now = datetime.now(UTC)
    internal_titles = {s.id: s.title for s in signals}
    by_url: dict[str, Evidence] = {}  # eine Quelle = ein Beleg, auch wenn mehrere Fragen sie liefern
    web_signals: list[Signal] = []

    for question in build_questions(scenario, signals):
        usable: list[Evidence] = []  # Belege dieser Frage mit Vertrauen high/medium
        for claim in ask_claims(question.text):
            key = _url_key(claim.url)
            if key not in by_url:
                by_url[key] = _evidence(scenario, len(by_url) + 1, claim, question, now)
            evidence = by_url[key]
            if evidence.meta["trust"] in ("high", "medium") and evidence not in usable:
                usable.append(evidence)
        if usable:  # Befund nur mit mindestens einem belastbaren Beleg
            web_signals.append(_signal(scenario, len(web_signals) + 1, question, usable, internal_titles))
    return list(by_url.values()), web_signals
