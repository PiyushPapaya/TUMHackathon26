# Pitch: 6 Minuten inklusive Fragen (strikt)

> Rahmen: Lead. Jeder Pfad liefert 1 Folie + seinen Demo-Abschnitt. Probe So 10:00 (Skill `pitch-prep`).

## Kernbotschaft (auswendig)

**"Wir sagen nicht nur, WAS der nächste 5er braucht, sondern WIE SICHER wir uns sind und WARUM, und der PM behält jede Entscheidung."**

## Ablauf (4:00 Pitch + 2:00 Fragen)

| Zeit | Wer | Inhalt |
|---|---|---|
| 0:00-0:30 | Lead | Problem: BMW-Folie "1 Billion findings → 1,000 requirements → One car". Heute manuell, schwer nachvollziehbar. |
| 0:30-0:50 | Lead | Lösung in 1 Satz + Trichter für den G60 USA: "3.610 Stimmen → N Befunde → M Anforderungen". |
| 0:50-2:50 | D klickt, Lead spricht | **Live-Demo** (Klickpfad unten) |
| 2:50-3:20 | B | Vertrauen: die eine Zahl (Grounding-Rate, Genauigkeit vs. Baseline), Webquellen mit Vertrauensstufe |
| 3:20-3:40 | A | Übertragbar: Szenario F70-EU umschalten, gleiche Pipeline, eine Config-Datei |
| 3:40-4:00 | Lead | Workflow KI vs. Mensch (eine Folie), Abschluss-Satz |

## Demo-Klickpfad (geprobt, mit `DEMO_MODUS=true`)

1. Trichter-Seite → Anforderungsliste G60-US (Rang, Score, Evidenzstufe, Konflikt-Badge).
2. Klick auf Platz 1 "Physische Bedienelemente": Wasserfall → Befunde → Originalzitate + Studienwert + Webquelle.
3. Konflikt-Badge: "Display wird gelobt" → zeigt, dass wir Widersprüche nicht wegmitteln.
4. **Hinterfragen:** "Ist das nur eine Gewohnheitsfrage älterer Kunden?" → KI antwortet mit Belegen + Gegenbelegen.
5. **Bearbeiten** des Akzeptanzkriteriums → **Freigeben** mit Begründung.
6. Regler "Zukunft" hoch ("Nachfolger kommt 2030") → Liste rankt neu.
7. Prüfpfad: alle Schritte mit wer/wann/warum, Badge "Kette gültig ✓". Export CSV.

## Jury-Fragen (jede Person kann jede beantworten)

| Frage | Antwort in 2 Sätzen |
|---|---|
| Woher weiß ich, dass die KI keine Zitate erfindet? | Jede Aussage zeigt auf Beleg-IDs aus der Eingabe, ein Test prüft das automatisch. Die Grounding-Rate steht in `tests/eval/REPORT.md`. |
| Warum rechnet nicht das LLM die Priorität? | Weil der PM jeden Punkt nachvollziehen und ändern können muss. Die Formel ist sichtbar, die Gewichte sind live einstellbar und protokolliert. |
| Was ist der Unterschied zwischen Evidenzstufe und Score? | Die Stufe sagt, wie sicher wir sind (Regel A-D). Der Score sagt, wie wichtig es ist, und schwach belegte Punkte werden abgewertet, aber nicht versteckt. |
| Wie kommt ein neues Modell oder ein neuer Markt dazu? | Eine JSON-Datei in `config/scenarios/` mit Dateien, Ländern und Wettbewerbern, dann die Pipeline starten. |
| Was, wenn sich Belege widersprechen? | Wir zeigen beide Befunde verknüpft und markieren den Konflikt. Die Abwägung trifft der PM. |
| Kann man den Prüfpfad fälschen? | Jeder Eintrag enthält den Hash des vorherigen. Wer etwas ändert, bricht die Kette, und `verify` zeigt die Stelle. |
| Was ist out of scope? | Regulatorik, Engineering-Specs und Preise. Der Scope-Wächter verwirft solche Vorschläge mit Begründung im Prüfpfad. |

## Backup

Backup-Video (2 min) der Demo-Strecke, aufgenommen So 08:30, lokal + Drive. Bei Netzausfall: `DEMO_MODUS=true`.
