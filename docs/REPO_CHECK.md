# Repository-Prüfung gegen den BMW-Brief

Stand: 11.10.2026. Geprüft wurde der lokale Arbeitsstand einschließlich bereits vorhandener, noch
nicht committeter Änderungen. UI-Gestaltung und die Entscheidung über zusätzliche UI-Funktionen
waren ausdrücklich ausgenommen. Dieser Bericht ersetzt keine fachliche Freigabe durch BMW.

## Ergebnis

Der Kernstack funktioniert in den geprüften Abläufen: sechs Szenarien laden, Quellen anzeigen,
Anforderungen erklären, Gewichte ausprobieren/übernehmen, Anforderungen freigeben/ablehnen/
bearbeiten/hinterfragen, exportieren und nach einem Neustart denselben PM-Zustand wiederherstellen.
Mehrere Fehler bei Randfällen wurden behoben und durch Regressionstests abgesichert.

**Nicht alle Planpunkte sind fertig.** Insbesondere fehlen die menschliche Befund-Evaluation,
ausreichende Web-/Zukunftsevidenz in mehreren Szenarien und ein vollständiger neuer Pipeline-Lauf
mit den aktuellen Prompts. Ein erfolgreicher Build beweist außerdem keinen vollständigen Browser-Flow.
Die Prüfung rechtfertigt weder „bugfrei“ noch eine Garantie für Wettbewerbsfähigkeit.

## Prüfgrundlage

- `BMW_Hackathon_Briefing_Short-1.pdf` aus dem Downloads-Ordner: beide gescannten Seiten gerendert
  und gelesen. Schwerpunkt: Kundenbedürfnisse eines Nachfolgers in 3–5 Jahren, interne und externe
  Evidenz, begründete Anforderungen/Prioritäten, klare Annahmen/Unsicherheiten/Widersprüche,
  menschliche Kontrolle und Anpassbarkeit an Modelle/Märkte.
- `README.md`, `PLAN.md`, `docs/ROADMAP.md`, Zeitplan, Architektur, Challenge, Abgabe,
  `docs/UPGRADE_WELLE2.md`, UX-/Briefing-Abgleich und die technischen Ablauf-/Rollenpläne.
- Arbeitsbücher für Pfad A/B/C/D/Lead sowie Team-/Mission-/Workshop-Einstiege und
  `OFFENE_AUFGABEN.md`. Historische Haken wurden gegen aktuellen Code und Daten geprüft.
- Aktuelle Configs, Rohdatenformate, sechs verarbeitete Szenarien, Backend, API-Verträge,
  Frontend-Anbindung, Cache-/Audit-Verhalten und Tests.

## Tatsächliche Szenario-Abdeckung

„Feedback“ zählt alle eingelesenen Kommentare; die Evaluation verwendet zusätzlich den
gefilterten Kunden-Scope. Web-/externe Zahlen sind Belege, keine unabhängigen Quellenanzahlen.

| Szenario | Feedback | Studie | Web | Extern | Anforderungen | Zukunft / Stufe D | Anforderungen mit Segmentkonflikt |
|---|---:|---:|---:|---:|---:|---:|---:|
| F70-EU | 1433 | 37 | 100 | 0 | 20 | 4 / 4 | 1 |
| G60-US | 3610 | 103 | 98 | 56 | 19 | 1 / 1 | 7 |
| G70-US | 3792 | 103 | 90 | 32 | 15 | 0 / 0 | 2 |
| G60-EU | 111 | 37 | 0 | 0 | 10 | 0 / 0 | 0 |
| G68-CN | 0 | 37 | 0 | 0 | 3 | 0 / 0 | 0 |
| G70-EU | 19 | 37 | 0 | 0 | 2 | 0 / 0 | 0 |

Alle sechs Szenarien haben Absatzkontext. Optionslisten werden für fünf Szenarien eingelesen;
G68-CN hat keine. Ein Kaltstart läuft technisch, ist fachlich aber deutlich schwächer als G60-US/F70-EU.
Bei G70-EU erreicht kein Feedback-Thema die Mindestgröße; die Anforderungen beruhen auf Studien.
Die Anforderungsliste wurde nicht mit unbelegten Einträgen auf eine Zielzahl aufgefüllt.

## Abgleich mit Roadmap und Aufgaben

| Bereich / Planpunkte | Befund |
|---|---|
| Lead W-P0, W-L2/L4/L5/L8 | Sechs Configs, additive Verträge, Szenario-Fehlerisolierung, View-API und Bundle-Prüfung vorhanden. CSV/JSON/Markdown-Export funktioniert. |
| Lead W-L1 | Timeout/Retry und atomarer LLM-Cache vorhanden; paralleles Schreiben unter Windows repariert. Ein echter strukturierter LLM-Aufruf erfolgreich. |
| Lead W-L3 | Replay für Entscheidungen, Bearbeitungen und Gewichte im Neustarttest bestätigt. Neue Audit-Datenbanken binden Replay an den Bundle-Fingerabdruck. |
| Lead W-L6/L10, Pfad B | NHTSA-/Verbrauchs-Connectoren und Benchmarks vorhanden, lokale US-Caches genutzt. Fehlende Vergleichsdaten werden nicht als null Beschwerden ausgegeben. Kein neuer vollständiger Live-Abruf geprüft. |
| Lead W-L7 | Snapshot-Demo offline bestätigt. Vollständige Offline-Neuerzeugung mit aktuellen Prompts scheitert an fehlenden Cache-Einträgen. Nachtlauf-Ziel bleibt offen. |
| Pfad A W-A1–A5 | Datensatzprofil, Kaltstart, Segmente aus allen Gruppenmitgliedern, unbekannte Themen und fehlende Absatzwerte verarbeitet/abgesichert. |
| Pfad A W-A6 | Chancenkarte vorhanden. „Importance“ ist ein aus Zufriedenheit abgeleiteter Proxy, keine separat gemessene Wichtigkeit; API kennzeichnet diese Grenze. |
| Pfad A W-A7, Pfad C W-C9; offene Aufgabe A1 | Segmentkonflikte berechnet, in Bundles übernommen, mit Gegenbelegen an Explain/Challenge geliefert. G60-US hat sieben Anforderungen mit Segmentkonflikten. Browserdarstellung nicht abschließend geprüft. |
| Pfad A W-A8, Pfad C W-C8; offene Aufgabe A3 | Automatische Evaluation funktioniert; menschliche Treue-Bewertung fehlt: 0 von 50 G60-US-Paaren gelabelt. |
| Pfad C W-C1 | Anforderungs-IDs bei umgeordneten Entwürfen stabil, auch today/next_gen-Kollisionen repariert. Vorgelagerte Signal-IDs bleiben teilweise positionsabhängig: keine allgemeine Stabilitätsgarantie bei neuen Quelldaten. |
| Pfad C W-C2/W-C4 | Robustheit für alle Anforderungen ergänzt; berücksichtigt aktuelle Gewichte und bearbeiteten Aufwand. What-if verändert weder Zustand noch Audit. |
| Pfad C W-C3; offene Aufgabe A2 | Zukunftswetten vorhanden, aber nur F70-EU und G60-US; kein flächendeckender 2030-Ausblick umgesetzt. Zusätzlicher regelbasierter Ausblick bleibt Produktentscheidung. |
| Pfad C W-C5 | Ziel 15–25 Anforderungen erreicht bei F70-EU/G60-US/G70-US; nicht bei G60-EU/G68-CN/G70-EU. |
| Pfad C W-C6/W-C7/W-C11/W-C12 | Absatz-/Business-Kontext, fehlende Optionsliste, Scope-Filter und Markdown-Lastenheft vorhanden und geprüft. Fehlende Werte bleiben unbekannt. |
| Pfad D | Frontend-Build und vorhandene JavaScript-Tests erfolgreich. Gestaltung unverändert; vollständiger aktueller Klickablauf nicht ausgeführt. |
| Abgabe/Pitch | Technische Demo-Grundlage vorhanden. Deck, Video, externe Abgabe und menschliche Freigaben nicht durch diese Prüfung als erledigt bestätigt. |

## Behobene Fehler und Randfälle

- Nur Leerzeichen als PM-Begründung/Name wurden angenommen. Eingaben werden vor der Prüfung
  getrimmt; ungültige Entscheidungen verändern keinen Zustand.
- Eine fehlgeschlagene Audit-Schreibung konnte bereits den PM-Zustand ändern. Änderungen werden
  jetzt erst nach erfolgreichem Audit-Eintrag veröffentlicht; Disk-full-Regression vorhanden.
- Gleichzeitige Audit-Schreiber konnten dieselbe Vorgänger-Hash-Zeile benutzen. Die Datenbank
  sperrt jetzt die Schreibtransaktion vor dem Lesen; vier unabhängige Verbindungen/40 Events geprüft.
- Manipulierte Audit-Payloads werden als ungültig erkannt; eine beschädigte Kette wird beim Start
  nicht wiederhergestellt. Neue Verläufe speichern einen Bundle-Fingerabdruck und verweigern
  Replay auf geänderten Snapshots statt alte Entscheidungen auf neue Inhalte anzuwenden.
- Challenge/Explain bekamen nicht alle gegensätzlichen Befunde und Segmentbelege. Diese werden
  jetzt gezielt mitgegeben; widersprechende Web-Belege bleiben beim Bündeln erhalten.
- Mehrere Aussagen derselben URL wurden fälschlich zusammengelegt; jetzt bleiben unterschiedliche
  Aussagen/Haltungen getrennt und ihre Signal-Verknüpfungen erhalten.
- Fehlende Pipeline-Stufen konnten synthetische Daten eines anderen Szenarios einschleusen.
  Fehlende Pflichtstufen liefern nun einen Fehler. Vollständig gescheiterte Web-Recherche
  überschreibt keine vorhandenen Web-Stufen; Teilfehler werden im Kontext markiert.
- Segmente beruhten auf ausgewählten Zitaten statt auf der ganzen Gruppe; LLM-Verfeinerung verlor
  additive Metadaten. Beides korrigiert, ebenso Studienverknüpfung und Konflikt-Übernahme.
- Kontext, Chancenkarte, Absatz-/Optionsabdeckung und externe US-Belege fehlten teilweise in
  vorhandenen Snapshots. Offline angereichert; bestehende Texte, IDs und PM-Ausgangsstatus erhalten.
- Robustheitswerte fehlten in vier Szenarien oder bezogen sich nach Gewichtsänderung noch auf die
  Standardgewichte. Werte sind nun vollständig und werden bei Änderungen neu berechnet.
- Sehr große endliche Gewichte konnten beim Normieren überlaufen. Skalierung verhindert dies.
- Parallel geschriebene LLM-Caches scheiterten unter Windows. Eindeutige temporäre Dateien,
  synchronisierter Zugriff und begrenzte Wiederholungen bei Dateisperren abgesichert.
- Entwürfe ohne gültige Signal-Verknüpfung werden begründet verworfen. Fehlende Benchmark-Caches
  erscheinen als fehlend, statt eine scheinbar belegte Null zu erzeugen.
- Evaluation überging externe/Web-IDs und konnte beim Kaltstart scheitern; sie prüft nun alle
  Quellenarten. Bestehende menschliche Labels werden vom Stichproben-Skript nicht überschrieben.
- Vollständiger Git-Historien-Secret-Scan lief in einen Speicherfehler. Streaming ersetzt das
  vollständige Einlesen; Scan über 1010 Dateien plus Historie erfolgreich, ohne gefundenen Schlüssel.
- Während der Prüfung entstand durch einen parallel begonnenen Merge ein neuer Zwischenstand
  mit neun Konfliktdateien. Belegtexte/IDs waren auf beiden Seiten gleich; zusätzliche Metadaten,
  Kontext und externe Belege wurden erhalten. Beide Seiten sind lokal gesichert, Konflikte
  aufgelöst und der zusammengeführte Stand erneut geprüft. Es wurde keine Merge-Abgabe ausgelöst.
- Der isolierte Next-Build-Ordner wurde in ESLint ausgenommen, damit generierte Dateien nicht
  als Quellcode gelintet werden. Das verändert keine UI-Gestaltung oder Produktfunktion.

## Ausgeführte Verifikation

- Saubere isolierte Python-3.12-Umgebung mit `requirements.txt`: Installation und `pip check` erfolgreich.
- Gesamte Python-Suite: **455 bestanden, 3 übersprungen**. Die übersprungenen Tests sind nicht als
  erfolgreich gewertet. Neue Tests reproduzieren konkrete Fehler, darunter Dateisperren,
  Audit-Schreibfehler, konkurrierende Verbindungen, Gegenbelege und veränderte Snapshots.
- `scripts/verify_stack.py`: **6 Szenarien, 180 HTTP-Leseprüfungen, 30 PM-Aktionen**, drei Exportformate,
  Score-Wasserfälle, What-if ohne Seiteneffekt, gültige Audit-Kette und exakter Neustart-Replay.
  Nur temporäre Audit-Datenbank; echte PM-Entscheidungen wurden nicht verändert.
- `scripts/check_bundles.py`: **28 grün, 0 rot** einschließlich Vergleich mit dem inzwischen
  aktualisierten Git-Stand; Backend-/Test-Lint erfolgreich.
- Frontend: Produktionsbuild mit 15 Routen, 15 vorhandene JavaScript-Tests erfolgreich;
  Lint ohne Fehler, eine bestehende Warnung wegen ungenutztem `scenarioId`.
- Live-LLM: ein minimaler strukturierter Aufruf erfolgreich. Das bestätigt Zugang/Schema-Verarbeitung,
  nicht die Qualität einer kompletten Web-Recherche oder Anforderungsgenerierung.
- Evaluation aller sechs Szenarien: Quellen-/Befund-ID-Grounding 100 %. Zitierte Originalkommentare
  wortgleich, soweit Feedback zitiert wird. Menschliche Treue weiterhin **nicht gemessen**.

Protokolle liegen lokal unter `outputs/repo-audit/` (gitignored). Die sechs numerischen Eval-Berichte
liegen in `tests/eval/REPORT-*.md`; der Hauptbericht in `tests/eval/REPORT.md`.

## Offene Punkte nach Priorität

| Priorität | Punkt | Konsequenz / konkreter Abschluss |
|---|---|---|
| P1 | Menschliche Evaluation fehlt | Aditya/Dennis bewerten die 50 vorbereiteten G60-US-Paare in `data/eval/G60-US_sample.csv` mit j/n; danach Evaluation neu ausführen. Keine KI-erfundene Trust-Zahl verwenden. |
| P1 | Dünne Szenarien und unvollständiger Zukunftshorizont | Piyush/Dennis recherchieren belastbare marktbezogene Wettbewerber-/Trendquellen und erzeugen neue Anforderungen; bis dahin F70-EU/G60-US als Hauptdemo, andere als Datenlücken-/Kaltstartbeweis einordnen. |
| P1 | Vollständige Neuerzeugung nicht bestätigt | Alle sechs Szenarien mit aktuellem Code/Prompts in einen getrennten Ausgabeordner erzeugen, Cache-Fails und Quellen prüfen, Bundle-/API-/Eval-Prüfung wiederholen. Alte PM-Verläufe behalten; für neue Bundles separate Audit-DB verwenden. |
| P1 | Vollständiger Browser-Flow fehlt | Auf freigegebenem laufendem Frontend Modellwechsel, Belege, Challenge, Edit, Gewichte, Exporte und Neustart prüfen. Start des separaten Frontend-Testservers wurde automatisch abgelehnt, ohne spezifische Begründung. Build/API-Tests ersetzen diesen Schritt nicht. |
| P2 | Stabile Identität bei neuen Quellen | Signal-IDs künftig aus semantischen Gruppenschlüsseln ableiten und bestehende IDs kontrolliert migrieren. Legacy-Audit ohne Fingerabdruck kann bisherige Quelldatenidentität nicht belegen und meldet eine Warnung. |
| P2 | Chancenkarte und Akzeptanzkriterien | Proxy-Wichtigkeit ehrlich erklären. G60-EU hat nur 60 % Kriterien mit Ziffer; relative Kriterien benötigen definierte Baseline/Stichprobe. Die Ziffern-Heuristik beweist generell keine fachlich sinnvolle Messbarkeit. |
| P2 | Vollständigkeit des Audit-Ursprungs | **Erledigt 11.10. für neue Läufe:** `pipeline.py` schreibt `provenance` (Modell, Hash der Prompt-Dateien, Git-Commit, `core/provenance.py`) ins Bundle; der Store übernimmt sie in `PIPELINE_LOADED` und `SIGNALS_EXTRACTED`. Grenze: Modell = Stand bei der Bündelung. Die heutigen sechs Bundles sind älter und zeigen weiter ehrlich „not recorded in snapshot“; nachträglich wird nichts geraten. Prüfen: `tests/test_pipeline.py`. |
| P2 | Reviewer-Budget | **Bestätigt 11.10. (HEAD, `python scripts/ehl_budget.py`):** Budget 200000/200000, `src/` jetzt **62,0 %** (vorher 21,8 %), Doku 11,9 %, 140 Dateien ungelesen. Gelesen: Frontend ~76k, Tests ~49k, Backend nur ~32k Zeichen (23 von 61 `.py`). **Demo-Datenstrategie geprüft:** `git archive HEAD` entpackt und gestartet: lädt nur das Beispiel-Bundle G60-US (5 Anforderungen), Audit-Kette gültig. Die echte Demo läuft aus dem Git-Klon (alle 6 Szenarien in `data/processed/`). Offen bleibt nur R1/R2 (Lead-Entscheidung). |
| P2 | Betriebsmodell | **Erledigt 11.10.:** Ein API-Prozess pro Audit-DB wird jetzt erzwungen (`core/single_process.py`, OS-Sperre auf `<audit.db>.lock`, Linux/Mac/Windows). Ein zweiter Prozess bricht beim Start mit klarer Meldung ab, statt still veraltete RAM-Stände zu zeigen. Live geprüft mit zwei uvicorn-Prozessen. Mehrere Worker bleiben bewusst nicht unterstützt (nächster Schritt: gemeinsamer Store statt RAM). Prüfen: `tests/pfad_b/test_single_process.py`. |

## Wiederholen

Im Repository-Stamm, mit installierten Abhängigkeiten:

```powershell
python -m pytest tests scripts/tests -q
python -m ruff check src/backend tests scripts/verify_stack.py scripts/refresh_bundles.py
python scripts/check_bundles.py
python scripts/verify_stack.py
python tests/eval/run_eval.py all
python tests/eval/run_eval.py G60-US
python scripts/secret_scan.py --historie
```

`scripts/refresh_bundles.py` ergänzt vorhandene Snapshots ohne LLM-Aufruf; es verweigert die
Aktualisierung bei abweichenden Signalgruppen/Quellen. Es ersetzt keinen neuen Recherchelauf.
