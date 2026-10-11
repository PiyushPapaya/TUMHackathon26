# A2: regelbasierter Nachfolger-Ausblick

Geprüft am 11.10.2026. Jede Anforderung erhält einen englischen Ausblick
`grows/stays/fades`, mit Nachfolgerjahr und sichtbarer Kennzeichnung als Annahme.
Detailansicht und Trendradar zeigen denselben vom Backend berechneten Wert.

Die Tests wurden zuerst angelegt und scheiterten zunächst am fehlenden Modul.
Abgedeckt sind Kategorie-Trends, beide Segmentregeln, Regelvorrang, Mindestzahl zehn,
die exakte 1,5-fache BEV-Grenze, reine ICE-Szenarien, fehlende/doppelte Belege,
externe Kommentare, vollständiger Feedback-Nenner sowie API und Radar.

## Ergebnisse mit den vorhandenen sechs Demo-Bundles

Vor der Implementierung wurden per `GET /api/scenarios/{id}/requirements` IDs,
Ränge, Scores und sämtliche Score-Faktoren gesichert. Der Vergleich nach der
Implementierung ist für alle sechs Szenarien exakt identisch.

| Szenario | Feedback-Nenner | grows | stays | fades | zusätzliche Outlook-Radareinträge |
|---|---:|---:|---:|---:|---:|
| G60-US | 3.610 | 3 | 15 | 1 | 3 |
| F70-EU | 1.433 | 9 | 11 | 0 | 9 |
| G60-EU | 111 | 0 | 10 | 0 | 0 |
| G68-CN | 0 | 0 | 3 | 0 | 0 |
| G70-EU | 19 | 0 | 2 | 0 | 0 |
| G70-US | 3.792 | 12 | 3 | 0 | 12 |

G60-US Rang 5 (`REQ-G60-US-bf2d7c`, Reichweite/Laden) ist `grows`:
12 von 13 eindeutigen kritischen Feedback-Zitaten kommen von BEV/BEVE-Fahrern
(92,3 %), gegenüber 1.271 von 3.610 Kommentaren im Szenario (35,2 %).
Die Annahme einer stärkeren Elektrifizierung ist ausdrücklich im Satz gekennzeichnet.
Der Zähler verwendet zitierte Kommentare; er ist keine Vollzählung aller Kommentare
der ursprünglichen Befundgruppen.

## Ausgeführte Prüfungen

- `python -m ruff check src/backend tests`: erfolgreich.
- `python -m pytest -q`: 472 Tests erfolgreich.
- `npm run lint` und `npm run build` in `src/frontend`: erfolgreich.
  ESLint meldet den vorhandenen ungenutzten Parameter `scenarioId` (Warnung, kein Fehler).
- Nach Übernahme der aktuellen A1-/A3-Commits: dieselben 472 Backend-Tests und
  sechs `segmentConflicts`-Frontendtests erfolgreich; Produktionsbuild erneut geprüft.
- Playwright mit Produktionsfrontend und separater Audit-DB: Detailausblick und
  exakte Zahl der Outlook-Radareinträge in allen sechs Szenarien bestätigt.
- G60-US Rang 5 auf Desktop (1440 × 1000) und Mobil (390 × 844): Satz und
  Annahme sichtbar; mobil kein horizontaler Überlauf; keine JavaScript-Seitenfehler.

Lokale Nachweise liegen unter `outputs/repo-audit/outlook/`: `before.json`,
`report.json`, `browser-report.json` und Screenshots. Der Browserlauf leitete
API-Anfragen an den isolierten Testserver um; bestehende Demo-Entscheidungen
wurden nicht verändert.

Ohne benachbarte vollständige `evidence.json` wird der Feedback-Nenner aus der
Bundle-Stichprobe berechnet und als `baseline_source: bundle_sample` einschließlich
englischem Hinweis im Satz ausgewiesen. Es werden keine fehlenden Trends erfunden.
Scoring-Formel und bestehende Bundles wurden nicht geändert.
