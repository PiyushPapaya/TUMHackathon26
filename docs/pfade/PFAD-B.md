# Pfad B · Externe Evidenz + Qualitätsbeweis

**Ziel 1:** Wettbewerb und Trends aus dem Web holen. Jede Aussage hat URL, Abrufdatum und Vertrauensstufe.
**Ziel 2:** Die **"eine Zahl"** für den Pitch messen, die zeigt, dass man unserer KI trauen kann.
**Du schreibst in:** `src/backend/evidence_external/`, `tests/pfad_b/`, `tests/eval/`.
**Du lieferst:** `web_evidence.json`, `web_signals.json`, `tests/eval/REPORT.md` (Zahl + Methode).
**Schnittstelle:** `research(scenario, signals) -> (list[Evidence], list[Signal])` (Kopf von `web_research.py`).

## Schritte

| # | Zeitbox | Aufgabe | Fertig, wenn … |
|---|---|---|---|
| 1 | 30 min | Websuche ausprobieren: `core.llm.ask_json(..., tools=[{"type": "web_search"}])` mit Schema `Claims` (text, url, publisher, published, stance) | 1 Frage liefert ≥ 3 Claims mit echter URL |
| 2 | 45 min | Fragen-Generator: aus Top-10-Befunden (Beispiel `signals.json`) + `scenario.competitors` → Wettbewerbsfragen; dazu 5 feste Trendfragen 2028-2031 (Laden, Software/Apps, Bedienung, Innenraum, Assistenz) | 15 Fragen für G60-US |
| 3 | 30 min | `trust.py`: Vertrauen per Regel (Hersteller-Seite, Testmagazin, Studie/Institut = high; Fachpresse = medium; Forum/unbekannt = low) | Test mit 6 URLs |
| 4 | 45 min | `research()` v1: Claims → `Evidence(source_type="web")`, Wettbewerbsvorteile → `Signal(kind="competitor_advantage")`, Trends → `Signal(kind="trend")` | **Sa 18:00**: 5+ Webbelege mit URL in `web_evidence.json` |
| 5 | 60 min | Triangulation: Webbeleg stützt/widerspricht internem Befund (`stance`) → Liste `{signal_id, evidence_id, stance}` in `web_signals.json`-Meta; Lead/C nutzen das für die Evidenzstufe | 3 interne Befunde bekommen Webbestätigung (**Sa 22:00**) |
| 6 | 60 min | **Eval-Set:** 60 G60-US-Kommentare zufällig ziehen (Seed 42), von Hand labeln: Thema + "gehört zu Befund X?" (in `data/`, nicht im Git!) | Labels fertig (**So 01:00**) |
| 7 | 60 min | **Eval-Skript** `tests/eval/run_eval.py`: (a) **Grounding-Rate**: Anteil zitierter IDs/Zitate, die wörtlich in den Quelldaten existieren (Ziel 100 %); (b) **Zuordnungs-Genauigkeit** Befund vs. Hand-Label; (c) Baseline: nur BMW-Taxonomie ohne LLM | `REPORT.md` mit Zahl, Baseline, Methode (**So 05:00**) |
| 8 | Nacht | Gleiches für F70-EU (andere Wettbewerber in `config/scenarios/F70-EU.json`) | Webbelege für 2. Szenario |

## Regeln

- **Kein Webbeleg ohne URL.** Kein Trend ohne Kennzeichnung als Annahme (Evidenzstufe D, wenn intern nichts dazu da ist).
- Alles läuft über `core/llm.py` (Cache!). Nach dem ersten Lauf geht die Demo offline.
- Preise/Business-Case sind out of scope: Fragen dazu nicht stellen.

## Start-Prompt für Claude

> "Ich baue Pfad B. Wir nutzen die OpenAI-Websuche über `core.llm.ask_json` statt eigenem Scraping,
> weil sie Quellen-URLs mitliefert und in 24 h kein Scraper robust wird. Verworfen: Scraping von
> Testmagazinen (Paywalls, fragil). Bitte baue in `src/backend/evidence_external/web_research.py`
> ein Pydantic-Schema `Claims` und eine Funktion, die für eine Frage Claims mit URL liefert. Test:
> Claims ohne URL werden verworfen. Prüfen mit `python -m pytest tests/pfad_b -q`."

## Deine Pitch-Folie + Demo-Abschnitt

- Folie "Kann man der KI trauen?": Grounding-Rate (z. B. "100 % der Zitate existieren wörtlich"),
  Genauigkeit vs. Baseline, Webquellen nur mit Vertrauensstufe.
- Demo (30 s): Webbeleg mit Link und Vertrauensstufe auf der Detailseite; Trend als "Annahme" markiert.
