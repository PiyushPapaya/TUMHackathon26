# Lead (Piyush) · Rückgrat, Integration, Pitch, Abgabe

**Ziel:** Alle vier Pfade sind nie blockiert. Um 18:00 / 22:00 / 08:00 läuft auf `main` ein Stand, der die Demo trägt.
**Du schreibst in:** `src/backend/core/`, `api/`, `main.py`, `pipeline.py`, `src/shared/`, `config/`, Root-Dateien, `docs/`.

## Schon fertig (Sa 15:00, Branch `piyush/neustart`)

- Datenmodell `core/models.py`, Prüfpfad mit Hash-Kette `core/audit.py`, Store mit PM-Aktionen `core/store.py`
- API (`api/routes.py`): Szenarien, Trichter, Befunde, Anforderungen, Detail, Entscheidung, Gewichte, Prüfpfad, Verify, CSV-Export
- Pipeline-Gerüst mit Stufendateien + Beispiel-Fallback, 3 Szenario-Configs, Startversion von Scoring/Evidenzstufe/Challenge
- 23 Tests grün, ruff grün

## Deine Takte

| Zeit | Aufgabe |
|---|---|
| 14:45 | Kick-off (15 min): Idee in 3 Sätzen, Pfade verteilen, Setup-Check reihum |
| jede volle Stunde | **Merge-Fenster**: grüne PRs mergen, danach `pipeline.py --scenario G60-US` mit dem, was da ist |
| 16:00 | Kontakt BMW-Mentor: 3 Fragen (unten), Antworten in `docs/CHALLENGE.md` |
| **18:00** | Durchstich: Pipeline mit echten Belegen → Bundle → UI zeigt echte Liste |
| 19:00 | Stand-up beim Dinner (je 1 min: fertig / blockiert / nächster Schritt), Kürzungsliste prüfen |
| **22:00** | MVP auf `main`, **erste Abgabe ehl.gg**, Skill `selbstreview` |
| Nacht | Integration F70-EU, Deck-Rohfassung aus den 4 Pfad-Folien |
| So 08:00 | Feature-Freeze, `demo-check`, Deck final, Backup-Video |
| So 10:00 | Pitch-Probe (Skill `pitch-prep`) · 10:30 Code-Freeze · 11:30 abgegeben (Skill `abgabe`) |

## Integrationsaufgaben (Backlog, nach Priorität)

1. Bundle-Stufe: verworfene Out-of-scope-Anforderungen von Pfad C als `REQUIREMENT_DISCARDED` in den Prüfpfad.
2. Audit-Ereignisse für Pipeline-Schritte (`EVIDENCE_INGESTED`, `SIGNALS_EXTRACTED` mit Modell + Anzahl).
3. Endpoint `GET /api/requirements/{id}/history?at=<seq>` für "Zeitreise" im Prüfpfad (Stretch).
4. `DEMO_MODUS` end-to-end prüfen (Netz aus, Demo läuft).
5. README: Zahl von Pfad B, Mermaid-Diagramm aktuell, Alignment-Map.
6. Deploy: Backend lokal + Frontend lokal reicht für den Pitch (BMW-Daten nicht in die Cloud). Optional Vercel mit Beispiel-Bundle.

## Fragen an BMW (Mentor/Deep Dive)

1. Welche Rolle hat der PM heute bei der Freigabe: Einzelperson oder Gremium? (Beeinflusst den Freigabe-Workflow.)
2. Gibt es interne Begriffe für Evidenzstufen oder Must/Should/Could, die wir übernehmen sollten?
3. Was bedeuten die Quellen A-D im Feedback genau, und ist eine davon vertrauenswürdiger?

## Pitch-Deck (du baust den Rahmen, Pfade liefern je 1 Folie)

1. Problem (BMW-Folie "1 Billion findings → One car", in unseren Worten) · 2. Lösung in 1 Satz + Trichter ·
3. Live-Demo · 4. Pfad A Belege · 5. Pfad C Priorität · 6. Pfad B Vertrauen/Zahl · 7. Übertragbar (Config) · 8. Workflow KI vs. Mensch · 9. Ask/Nächste Schritte
