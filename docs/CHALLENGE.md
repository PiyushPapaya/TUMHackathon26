# Challenge: BMW Group · AI for Product Decision Making

> Gewählt: Sa 10.10.2026. Quelle: `BMW_Hackathon_Briefing_Short.pdf` (S. 1-2) und Aufgabentext auf ehl.gg.
> Zitate wörtlich, weil der KI-Reviewer Challenge-Alignment am Brief-Text misst.

## Kernsätze (wörtlich)

> "Build an AI-powered application that helps product managers derive, justify, and prioritize customer requirements for a successor vehicle. Ground your proposals in customer feedback, BMW product and sales data, and relevant web research—while keeping the product manager firmly in control of every decision." (S. 1)

> "Make clear where your conclusions are based on available evidence and where they rely on forward-looking assumptions." (S. 1)

> "Think three to five years ahead and identify the customer needs and expectations that should shape the next generation of the vehicle." (S. 1)

> "We value trustworthy sources, transparent reasoning, thoughtful prioritization, and a clear understanding of uncertainty and conflicting evidence." (S. 2)

> "Focus on customer value rather than engineering specifications, regulatory requirements, or detailed business-case calculations." (S. 2)

## Fähigkeiten laut Aufgabe → wo bei uns

| Gefordert (wörtlich) | Unsere Umsetzung | Code |
|---|---|---|
| "Ingest the provided data and enrich it with structured knowledge from the web" | Pfad A Einlesen, Pfad B Websuche mit URL + Vertrauen | `evidence_internal/`, `evidence_external/` |
| "Extract signals such as recurring complaints, unmet needs, competitor advantages and market trends, each linked to its sources" | `Signal.kind` = genau diese 4 (+ delight), `evidence_ids` Pflicht | `core/models.py` |
| "Derive requirements … clear, actionable, customer-facing and realistic" | LLM-Entwurf mit messbarem Kriterium + Scope-Wächter | `requirements_engine/derive.py` |
| "Prioritize them with a logic you define and can explain" | gewichtete Formel, Wasserfall, live änderbar | `requirements_engine/scoring.py` |
| "Involve the PM to approve, reject, edit or challenge" | 4 Aktionen, Begründung Pflicht, KI-Antwort bei Challenge | `api/routes.py`, `core/store.py` |
| "Record everything in an audit trail" | append-only, Hash-Kette, Verify-Endpoint | `core/audit.py` |

## Pflicht-Deliverables

1. Konzept + Prototyp → App + `docs/ARCHITEKTUR.md`
2. Strukturierte Anforderungsliste (ID, Beschreibung, Befunde/Quellen, Score, Begründung, Evidenzstufe, Annahmen/Unsicherheiten, Status) → `GET /api/scenarios/{id}/export` (CSV)
3. End-to-End-Workflow mit KI-autonom vs. Mensch-Pflicht → `docs/PLAN.md` §4 + Trichter-Seite
4. Nachvollziehbarer Prüfpfad (wer/was, wann, Begründung, Vorher/Nachher) → `/api/audit`, `/api/audit/verify`

## Scope

**In:** Ausstattung, Komfort, Platz, Bedienung, Infotainment/Digital, Design/Qualitätsanmutung, Fahrerlebnis, Reichweite/Laden aus Kundensicht, Varianten/Pakete.
**Out:** Regulatorik/Homologation, Technik/Engineering-Specs, Preis/Business-Case (Aufwand nur grob als Faktor).

## Daten (lokal in `data/raw/`, nicht im Git)

| Datei | Inhalt | Größe |
|---|---|---|
| `F70/G60/G70_feedback_hackathon.xlsx` | Kundenfeedback, Quellen A-D, BMW-Taxonomie (VFC), Feedback-Typ | 4.076 / 5.005 / 4.690 Zeilen |
| `F70_G60_G68_G70_customer_studies.xlsx` | CN/EU: Mittelwerte je Attribut; US: 7-stufige Verteilung, ~100 Attribute (G60, G70) | 2 Blätter |
| `sales_volumes.xlsx` | Volumen EU/CN/US/RoW 2024, 2025, 2030 je Modell | 3 Blätter |
| `F70/G60/G70_OptionList.PDF` | DE-Preisliste: Serie/Sonderausstattung, Pakete, technische Werte | 23-28 Seiten |

Marktabdeckung Feedback (Kommentare): F70 EU 1.433 · G60 US 3.610 · G70 US 3.792. Darum Demo **G60-US**, Übertragbarkeit mit **F70-EU**.

## Offene Fragen an BMW

Siehe `docs/pfade/LEAD.md` (Antworten hier eintragen).
