# Browser- und Pipeline-Nachprüfung

Stand: 11.10.2026. Die Nachprüfung ergänzt [REPO_CHECK.md](REPO_CHECK.md) und
[VERIFIKATION_P1_P2.md](VERIFIKATION_P1_P2.md). Ausgeführt mit lokalem Playwright/Chromium,
einem Next.js-Produktionsbuild und separaten FastAPI-Testinstanzen/Audit-Datenbanken.

## Ergebnis

Der vollständige Browser-Ablauf und die vollständige Pipeline-Neuerzeugung wurden ausgeführt.
Die frühere Ablehnung des Frontend-Testserverstarts ist für diese Prüfung erledigt.
Der Playwright-Connector war nicht erreichbar; lokal installiertes Playwright funktionierte.

Zwei reproduzierte Fehler wurden korrigiert:

- CSV-Export lieferte Klartext statt eines Downloads. Er liefert jetzt `text/csv` und einen
  `Content-Disposition`-Download-Header; HTTP-Regression und echter Browser-Download geprüft.
- Eine Bearbeitung ohne geänderte Felder konnte abgesendet werden und endete mit HTTP 422.
  Der Dialog verlangt jetzt mindestens eine Änderung und zeigt einen passenden Hinweis.

## Ausgeführte Prüfungen

- Vollständige PM-Abläufe in allen sechs Szenarien: Modell-/Marktfilter, Szenariowechsel,
  Ranglistenanzahl gegen API, Suche/leere Treffer/Reset, Belege aufklappen, Score-Vorschau ohne
  Zustandsänderung, Freigabe/Ablehnung/Challenge/Bearbeitung mit Begründung und Gewichte übernehmen.
- Echte Challenge-Antworten bleiben sichtbar; zitierte Beleglinks öffnen die zugehörigen Belege.
  CSV-Dateien werden über den UI-Link heruntergeladen, Memos öffnen über ihren UI-Link einen Tab.
- Priorisierungslinse: Vorschlag wird protokolliert; erst „Apply“ verändert die Rangliste.
- Audit-Integrität, Aktionsfilter und Suche; Belegsuche und Paginierung;
  Startseite, Übersicht, Portfolio, Benchmarks, Guide und alle Insights-Tabs.
- Modelle, Cockpit, Detail, Audit, Portfolio und Belegbrowser bei 1440, 768 und 390 Pixeln:
  kein horizontaler Dokumentüberlauf; mobiles Menü bedienbar. Screenshots gespeichert.
- Keine JavaScript-Laufzeitfehler, Konsolenfehler oder fehlgeschlagenen HTTP-Antworten im
  erfolgreichen vollständigen Browser-Lauf.
- Echter Backend-Neustart: exakter Vergleich aller Anforderungen einschließlich PM-Status,
  Bearbeitungen, Versionen, Gewichten, Scores und Reihenfolge; Kriterien erneut im Browser geprüft.
- Produktionsbuild mit TypeScript-Prüfung, Frontend-Lint und 15 JavaScript-Tests erfolgreich.
- Python-Gesamtsuite einschließlich `scripts/tests`: abschließend **469 bestanden,
  3 übersprungen**. Die übersprungenen Tests sind nicht als bestanden gewertet.
- API-Integration der neuen Bundles: 198 HTTP-Leseprüfungen, 30 PM-Aktionen, drei Exportformate,
  What-if ohne Mutation, Audit-Integrität und exakter Neustart-Replay.

Der vorhandene zusätzliche UX-Test bestand ebenfalls; sein Challenge-Regressionsteil verwendet
eine simulierte Antwort. Der vollständige Test in `scripts/verify_browser.cjs` verwendet echte API-Antworten.

## Vollständige Pipeline

Alle Stufen wurden ausgeführt: evidence → signals → web → external → requirements → bundle.
Der erste Neulauf und eine zweite Neuerzeugung mit den erweiterten Kriterien-Prompts liegen separat
unter `outputs/repo-audit/pipeline-current/` und `outputs/repo-audit/pipeline-final/`.
Während der Prüfung entstanden parallel weitere Änderungen. Der zweite Lauf verwendet deshalb
einen gesicherten Backend-/Config-Stand mit SHA-256-Manifest unter
`outputs/repo-audit/frozen-current/source-manifest.json`; spätere Änderungen sind davon unterscheidbar.
Die Quellen und lokalen LLM-/Behörden-Caches wurden verwendet; dies ist kein erzwungener Lauf ohne Cache.
Die API prüft die neuen Bundles anschließend mit dem aktuellen Backend.

| Szenario | Feedback | Studie | Web-Belege | Externe Belege | Anforderungen | Zukunft / Stufe D |
|---|---:|---:|---:|---:|---:|---:|
| F70-EU | 1433 | 37 | 109 | 0 | 22 | 3 / 3 |
| G60-EU | 111 | 37 | 111 | 0 | 11 | 4 / 4 |
| G60-US | 3610 | 103 | 112 | 56 | 17 | 1 / 1 |
| G68-CN | 0 | 37 | 134 | 0 | 9 | 4 / 4 |
| G70-EU | 19 | 37 | 101 | 0 | 6 | 4 / 4 |
| G70-US | 3792 | 103 | 103 | 32 | 22 | 4 / 4 |

Alle sechs Bundles haben Robustheitswerte und gültige Quellen-/Befundreferenzen.
Automatisches ID-Grounding beträgt jeweils 100 %. Zitierte Feedback-Kommentare stimmen dort,
wo Feedback zitiert wird, mit der Originaldatei überein. Alle neuen Kriterien enthalten eine Zahl;
diese Syntaxprüfung bestätigt keine fachliche Messbarkeit oder sinnvollen Zielwerte.
Der erfolgreiche zweite Lauf meldet keine fehlgeschlagenen Webfragen.

Die sechs parallelen Wiederholungsläufe erreichten zeitweise die lokale Speichergrenze.
Der erfolgreiche Abschluss verwendete zwei Prozesse und einen OpenBLAS-/OMP-Rechenthread.
Fehlgeschlagene Zwischenläufe sind nicht als bestanden gewertet.

## Verbleibende fachliche Arbeit

Die menschliche Befund-Treue ist weiterhin ungemessen. Für jedes neue Szenario liegt eine
frische Stichprobe mit Belegtext und gegebenenfalls Quellen-URL unter
`outputs/repo-audit/pipeline-final/<Szenario>-human-sample.csv` bereit.
Die Spalte `passt (j/n)` ist absichtlich leer; bestehende menschliche Labels wurden erhalten.

G68-CN hat weiterhin kein internes Feedback und keine Optionsliste. G70-EU hat nur 19,
G60-EU nur 111 Feedback-Kommentare. Die neue Recherche ergänzt diese Szenarien, ersetzt
aber keine zusätzliche interne Erhebung. Ihre 9/6/11 Anforderungen liegen unter dem
ursprünglichen Ziel von 15–25. Die fachliche Eignung der Quellen, Schlussfolgerungen,
Zielwerte und Zukunftsannahmen benötigt menschliche Prüfung.

Die neu erzeugten Bundles bleiben in getrennten Ausgabeordnern. Ihre Nutzung als Demo-Stand
erfordert einen eigenen Audit-Verlauf, weil die neuen Inhalte andere Bundle-Fingerabdrücke haben.
Die Testergebnisse sind ein Nachweis für die ausgeführten Abläufe am dokumentierten Prüfstand;
eine allgemeine Bugfreiheit wird daraus nicht abgeleitet.

## Protokolle und Wiederholung

Lokal unter `outputs/repo-audit/` liegen JSON-Berichte, Logs, Downloads und Screenshots:

- `browser-production/report.json` und `replay-report.json`: ursprüngliche sechs Bundles.
- `browser-pipeline-final/`: neue Bundles im aktuellen Produktionsbuild.
- `pipeline-final-results.json`, `pipeline-final-verification.json` und `integration-pipeline-final.json`.
- `pytest-live-final.txt`, `frontend-build-latest.txt`, `frontend-lint-latest.txt`.

Der Browser-Test schreibt Entscheidungen. Backend mit separater `AUDIT_DB`, `DEMO_MODUS=true`
und passendem `CORS_ORIGINS` starten; das Frontend auf dessen API-URL bauen.
`BROWSER_BASE_URL`, `BROWSER_API_URL`, `BROWSER_OUTPUT`, `BROWSER_PLAYWRIGHT_MODULE` und
gegebenenfalls `BROWSER_CHROMIUM_PATH` setzen. Danach:

```powershell
node scripts/verify_browser.cjs
# Backend mit derselben Testdatenbank und denselben Bundles neu starten:
node scripts/verify_browser.cjs --replay
python scripts/verify_stack.py --processed-dir outputs/repo-audit/pipeline-final
```
