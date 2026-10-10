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

from core.models import Evidence, Scenario, Signal


def research(scenario: Scenario, signals: list[Signal]) -> tuple[list[Evidence], list[Signal]]:
    raise NotImplementedError("Pfad B: research noch nicht gebaut (siehe docs/pfade/PFAD-B.md)")
