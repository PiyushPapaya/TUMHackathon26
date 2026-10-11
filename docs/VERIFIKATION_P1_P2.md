# Browserprüfung, stabile IDs und Abnahmekriterien

## Browserprüfung

`scripts/verify_browser.cjs` prüft am laufenden Frontend alle sechs Szenarien:
Modellwechsel, Belege, Challenge, Bearbeiten, Entscheidungen mit Begründung,
Gewichte, CSV-Download, Memo-Tab, Vorschau ohne Mutation, Audit, mobile Ansichten
und die Wiederherstellung nach einem echten Backend-Neustart.

Backend mit separater Datenbank und `DEMO_MODUS=true` starten; das Skript schreibt PM-Entscheidungen.
Frontend mit `NEXT_PUBLIC_API_URL` auf dieses Backend bauen/starten. Beim Test müssen
`BROWSER_BASE_URL`, `BROWSER_API_URL` und `BROWSER_OUTPUT` auf diese Instanzen zeigen.
Dann `node scripts/verify_browser.cjs` ausführen, das Backend mit derselben Datenbank
und demselben Datenverzeichnis neu starten und `node scripts/verify_browser.cjs --replay` ausführen.
`BROWSER_PLAYWRIGHT_MODULE` und `BROWSER_CHROMIUM_PATH` erlauben vorhandene Installationen.
Die JSON-Berichte enthalten Checks, Laufzeitfehler, HTTP-Fehler und Zeitstempel;
Screenshots, Downloads und der Zustand vor dem Neustart liegen im Ausgabeverzeichnis.
Build und API-Tests ergänzen diese Prüfung.

Ausgeführt am 11.10.2026: Produktionsbuild erfolgreich, kompletter Browser-Flow und
Replay nach Prozessneustart erfolgreich, keine JavaScript-/Konsolen-/HTTP-Fehler.
Lokale Nachweise: `outputs/repo-audit/browser-p1p2-final/report.json` und
`outputs/repo-audit/browser-p1p2-final/replay-report.json`. Der Lauf verwendete den
Offline-Demomodus mit separatem Audit; er belegt keine Live-LLM-Antwortqualität.
Die migrierte Kopie aller sechs Szenarien bestand außerdem 180 HTTP-Leseprüfungen,
30 PM-Aktionen und Replay in `outputs/repo-audit/semantic-ids-final/integration.json`.

## Identität und Migration

Neue interne Signal-IDs enthalten den SHA-256-Ausschnitt eines versionierten Gruppenschlüssels
aus Ursprung (Feedback/Studie), normalisiertem Thema und Befundart; das Szenario ist der Namensraum.
Rang, Nennungen, Zitate und LLM-Formulierungen beeinflussen den Schlüssel nicht.
NHTSA nutzt die Kategorie, Web-Wettbewerbsbefunde Kategorie/Wettbewerber/internen Gruppenschlüssel,
Web-Trends ihre Recherchefrage. Eine andere Gruppe oder ein anderer Recherchehorizont darf eine andere ID erhalten.
Unveränderte IDs erlauben keine automatische Übernahme von Entscheidungen bei veränderten Quelldaten:
der Bundle-Fingerabdruck bleibt eine zusätzliche Replay-Schranke.

```powershell
python scripts/migrate_signal_ids.py --source-dir data/processed --output-dir outputs/semantic-ids
# Nur für einen Prüfpfad mit nachgewiesenem, unverändertem Quellen-Fingerabdruck:
python scripts/migrate_signal_ids.py --source-dir data/processed --output-dir outputs/semantic-ids-with-audit --audit-db data/audit.db
```

Das Werkzeug verändert weder Originaldaten noch Originaldatenbank. Es rekonstruiert interne Gruppen
aus den vollständigen ursprünglichen `evidence.json`-Dateien. Fehlende/mehrdeutige Gruppen und
Kollisionen führen zum Abbruch. Es ersetzt Signal- und Anforderungsreferenzen einschließlich
Kontext-Schlüsseln und Pipeline-Stufen und schreibt ein Zuordnungsmanifest.
Historische externe Gruppen, deren exakte Recherchefrage nicht gespeichert wurde, werden ausdrücklich
in `retained_legacy_external_ids` ausgewiesen und behalten ihre IDs; sie werden nicht anhand von
LLM-Titeln erraten. Ein neuer Recherchelauf verwendet die neuen semantischen IDs.

Eine geprüfte Audit-Kopie erhält ausschließlich angehängte `IDENTITY_MIGRATED`-Ereignisse.
Alte Ereignisse und Hashes bleiben erhalten, Replay und Anforderungshistorie lösen die ID-Zuordnung auf.
Erst nach Prüfung den Backend-Prozess mit `PROCESSED_DIR=<Ausgabe>/processed` und
`AUDIT_DB=<Ausgabe>/audit.db` neu starten. Das alte Paar bleibt als Rückfallstand erhalten.
Ohne Audit-Übernahme eine neue, separate Datenbank verwenden.

Legacy-Audits ohne Fingerabdruck zeigen eine Warnung im Log und im Szenario. Ihre ursprüngliche
Quelldatenidentität ist nicht beweisbar; das Werkzeug verweigert ihre Übernahme als verifizierte Migration.
Auch nach einer Migration bleibt Replay bei weiteren Inhaltsänderungen gesperrt.

## Chancenkarte und Kriterien

Die Chancenkarte benennt die x-Achse als Proxy, zeigt Formel, angenommene Schwellen und
0–1-Indizes. Beide Achsen verwenden Zufriedenheitsdaten. Bei Mittelwertdaten ist auch die
Unzufriedenheit ein transformierter Index, kein erhobener Prozentsatz. Eine unabhängige
Wichtigkeitsbefragung ist für fachliche Bestätigung erforderlich.

Der Benchmark `measurable` zählt weiterhin Kriterien mit Ziffern, bezeichnet dies aber als
Syntax-Heuristik ohne Soll oder fachlichen Testbarkeitsnachweis. Der Prompt und die Oberfläche
fordern Ergebnis, Verfahren, Grenzwert, Stichprobe und bei relativen Zielen eine Baseline.
G60-EU enthält konkrete Aufgaben und Prüfprotokolle für alle zehn Kriterien; relative G60-EU-
und F70-EU-Kriterien definieren Referenzmodell, identische Bedingungen und gepaarte Stichproben.
Schwellen/Stichproben sind vorgeschlagene Annahmen. Noch nicht erhobene Baselines stehen als
Unsicherheiten in den Anforderungen. PM-Prüfung und tatsächliche Kundenvalidierung bleiben erforderlich.

Die geänderten Abnahmekriterien sind Inhaltsänderungen, keine ID-Migration. Bereits fingerprintete
Audits zu älteren Bundles müssen mit ihren Originaldaten archiviert bleiben. Für die neuen Kriterien
einen neuen Prüfpfad starten; die ID-Migration erlaubt keinen Fingerabdruckwechsel für Inhalt.
