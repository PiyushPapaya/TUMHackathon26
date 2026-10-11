# Pitch: 3:00 Vortrag inklusive Demo + 3:00 Fragen (strikt)

> Rahmen: Lead. Jeder Pfad liefert 1 Folie + seinen Demo-Abschnitt. Probe So 10:00 (Skill `pitch-prep`).
> Warum dieser Ablauf: [RECHERCHE.md](RECHERCHE.md) (frühere EHL-Gewinner, Web-Regeln, unsere Zahlen).

## Kernbotschaft (auswendig)

**"Wir sagen nicht nur, WAS der nächste 5er braucht, sondern WIE SICHER wir uns sind und WARUM, und der PM behält jede Entscheidung."**

## Ablauf NEU (3:00 Vortrag + 3:00 Fragen), ~390 Wörter

| Zeit | Wer | Inhalt | Folie |
|---|---|---|---|
| 0:00-0:20 | Piyush | Aufhänger: ein echtes Kundenzitat. „Für den 5er in den USA sind das 3.811 solcher Belege. Heute liest sie ein PM von Hand.“ | 1 |
| 0:20-0:35 | Piyush | Lösung in einem Satz + Trichter **3.811 Belege → 55 Befunde → 19 Anforderungen** | 2 |
| 0:35-2:15 | Lasse klickt, Piyush spricht | **Demo, 3 Momente:** ① Platz 1 öffnen: Wasserfall, Originalzitat, Stufe A. ② Hinterfragen: KI antwortet mit Belegen und Gegenbelegen → PM bearbeitet und gibt mit Begründung frei. ③ Gewicht ändern: Liste sortiert sich neu, Eintrag im Prüfpfad. | Demo |
| 2:15-2:45 | Aditya | Vertrauen: Stufen A-D, 100 % der zitierten Beleg-IDs existieren wörtlich in der Excel, eine ehrliche Grenze | 3 |
| 2:45-3:00 | Piyush | „Neues Modell oder Markt = eine JSON-Datei.“ Kernsatz. | 4 |
| 3:00-6:00 | alle | Fragen: Dennis Priorisierung/Score, Aditya Daten/Evaluation, Lasse Oberfläche, Piyush Architektur. Reservefolien A1-A6. | Anhang |

**Deck:** 4 Vortragsfolien + Anhang ohne Sprecher verständlich (A1 Workflow KI vs. Mensch, A2 Formel, A3 Architektur, A4 F70-EU, A5 Grenzen, A6 Prüfpfad). Das PDF wird hochgeladen; die Jury liest es auch ohne uns.

## Ablauf ALT (4:00 Pitch + 2:00 Fragen, ersetzt)

| Zeit | Wer | Inhalt |
|---|---|---|
| 0:00-0:30 | Piyush | Problem: BMW-Folie "1 Billion findings → 1,000 requirements → One car". Heute manuell, schwer nachvollziehbar. |
| 0:30-0:50 | Piyush | Lösung in 1 Satz + Trichter für den G60 USA: "3.610 Stimmen → N Befunde → M Anforderungen". |
| 0:50-2:50 | Lasse klickt, Piyush spricht | **Live-Demo** (Klickpfad unten) |
| 2:50-3:20 | Aditya | Vertrauen: die eine Zahl (Grounding-Rate, Befund-Treue), Webquellen mit Vertrauensstufe |
| 3:20-3:40 | Aditya (Lasse schaltet um) | Übertragbar: Szenario F70-EU umschalten, gleiche Pipeline, eine Config-Datei |
| 3:40-4:00 | Piyush (Dennis: Fragen zur Priorisierung) | Workflow KI vs. Mensch (eine Folie), Abschluss-Satz |

## Demo-Klickpfad (geprobt, mit `DEMO_MODUS=true`)

1. Trichter-Seite → Anforderungsliste G60-US (Rang, Score, Evidenzstufe, Konflikt-Badge).
2. Klick auf Platz 1 "Physische Bedienelemente": Wasserfall → Befunde → Originalzitate + Studienwert + Webquelle.
3. Konflikt-Badge: "Display wird gelobt" → zeigt, dass wir Widersprüche nicht wegmitteln.
4. **Hinterfragen:** "Ist das nur eine Gewohnheitsfrage älterer Kunden?" → KI antwortet mit Belegen + Gegenbelegen.
5. **Bearbeiten** des Akzeptanzkriteriums → **Freigeben** mit Begründung.
6. Regler "Zukunft" hoch ("Nachfolger kommt 2030") → **Apply**: Zeilen gleiten animiert auf neue Plätze, ▲/▼ zeigen die Rangänderung, Toast „WEIGHTS_CHANGED recorded“ (bester Demo-Moment). Einstieg vorher über die Startseite `/` (Scroll-Story) und „Open cockpit“.
7. Prüfpfad: alle Schritte mit wer/wann/warum, Badge "Kette gültig ✓". Export CSV.

## Jury-Fragen (jede Person kann jede beantworten)

| Frage | Antwort in 2 Sätzen |
|---|---|
| Woher weiß ich, dass die KI keine Zitate erfindet? | Jede Aussage zeigt auf Beleg-IDs aus der Eingabe, ein Test prüft das automatisch. Die Grounding-Rate steht in `tests/eval/REPORT.md`. |
| Warum rechnet nicht das LLM die Priorität? | Weil der PM jeden Punkt nachvollziehen und ändern können muss. Die Formel ist sichtbar, die Gewichte sind live einstellbar und protokolliert. |
| Was ist der Unterschied zwischen Evidenzstufe und Score? | Die Stufe sagt, wie sicher wir sind (Regel A-D). Der Score sagt, wie wichtig es ist, und schwach belegte Punkte werden abgewertet, aber nicht versteckt. |
| Wie kommt ein neues Modell oder ein neuer Markt dazu? | Eine JSON-Datei in `config/scenarios/` mit Dateien, Ländern und Wettbewerbern, dann die Pipeline starten. |
| Wie belastbar sind die Reichweiten-Vergleiche? | Es sind amtliche EPA-Prüfstandswerte (fueleconomy.gov), also vergleichbar zwischen Herstellern, aber kein Alltagsverbrauch, und sie gelten für die in der Config gewählte Radgröße. Nur US-Szenarien, Elektroautos ohne EPA-Reichweite (Audi A6 e-tron) fehlen bewusst. |
| Was, wenn sich Belege widersprechen? | Wir zeigen beide Befunde verknüpft und markieren den Konflikt. Die Abwägung trifft der PM. |
| Kann man den Prüfpfad fälschen? | Jeder Eintrag enthält den Hash des vorherigen. Wer etwas ändert, bricht die Kette, und `verify` zeigt die Stelle. |
| Die Prompt-Zeile ist doch eine Blackbox? | Nein: Die KI übersetzt die Frage nur in Gewichte und Filter, die wir offen anzeigen, und nennt keine einzige Anforderung. Die Top 5 rechnet dieselbe Formel wie immer, und übernommen wird erst, wenn der PM klickt, mit Eintrag im Prüfpfad. |
| Was ist out of scope? | Regulatorik, technische Detailauslegung und detaillierte Wirtschaftlichkeitsrechnungen. Gelieferte Listenpreise zeigen wir als DE-Referenzkontext, nicht als Nachfolger-Kalkulation. |

## Backup

## Aktualisierter Demo-Fokus (11.10.2026)

1. `/models`: G60 und United States waehlen. Die Zahl der Belege direkt aus
   dem laufenden Szenario zeigen, keine Rohdatei-Gesamtzahl als US-Zahl nennen.
2. Cockpit: eine kundenbezogene Anforderung oeffnen. Der Chart ist sofort
   sichtbar. Kundenproblem und Erfolgskriterium erklaeren, dann den Originalbeleg.
3. Einen Widerspruch oder eine Unsicherheit zeigen; Gegenfrage stellen.
   Die KI-Antwort bleibt nach dem Speichern im Entscheidungspanel sichtbar.
4. PM bearbeitet/freigibt mit Begruendung. Audit-Link oeffnen, neuestes
   Ereignis, Person und Vorher/Nachher zeigen. CSV exportieren.
5. F70-EU oeffnen: gleiche Pipeline, anderer Markt. Begrenzte Datenabdeckung
   anderer Szenarien ehrlich benennen.

Die Preise sind aus gelieferten DE-Listen abgelesener Kontext. Aufwand ist
eine grobe Schaetzung. Beides nicht als optimierten Business Case verkaufen.
Evidenzstufe A/B bedeutet stark/moderat belegt, nicht absolut bewiesen.
Die Hash-Kette ist manipulationsnachweisend gegen die bestehende Kette;
ein externer Anker fuer Schutz gegen vollstaendiges Neuschreiben fehlt.
Eine evaluierte Grounding-Rate nur nennen, wenn der konkrete Report samt
Testumfang vorliegt. Der Discord-Abgleich steht noch aus.

Vollstaendige Grenzen und Dateiabgleich:
[UX-UND-BRIEFING-ABGLEICH.md](../UX-UND-BRIEFING-ABGLEICH.md).

## Backup-Datei

Backup-Video (2 min) der Demo-Strecke, aufgenommen So 08:30, lokal + Drive. Bei Netzausfall: `DEMO_MODUS=true`.
