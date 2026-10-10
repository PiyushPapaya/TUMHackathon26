# Notizen Dennis

## Gute Prompts (zum Wiederverwenden)

<!-- Ownership-Sprache: Was + Warum + Was verworfen + Wie prüfen -->

## Notizen


## Entscheidung Sa 10.10., reach als Wurzel (Dennis)

- **Was:** Der Faktor `reach` ist jetzt Wurzel aus (Nennungen / größte Nennungszahl), vorher linear.
- **Warum:** Auf den echten Daten reichen die Nennungen von 7 bis 581 (581 = Lob für den Fahrcharakter). Linear bekam fast jede Anforderung unter 0,3, `reach` war wirkungslos. Doppelt so viele Kunden heißt nicht doppelt so wichtig.
- **Verworfen:** Obergrenze bei 60 Nennungen (viele landen bei 1,0 und werden nicht mehr unterschieden, verschiebt die Rangliste am stärksten); so lassen (Schwachpunkt bei Jury-Fragen zur Formel).
- **Geprüft:** `tests/pfad_c/test_factors.py` (25 von 100 Nennungen = 0,5; 7 von 581 > 0,1; 0 Nennungen = 0). Lauf G60-US: Touchscreen bleibt Platz 1 (47,0), Klimabedienung Platz 2.
- **An Piyush:** bitte in `entscheidungen/LOG.md` und in die Entscheidungstabelle von `docs/ARCHITEKTUR.md` übernehmen.

## Entscheidung Sa 10.10., Evidenzstufe: zweite Quelle hebt um eine Stufe (Dennis)

- **Was:** Basis nur nach Nennungen (15+ = B, sonst C). Bestätigt eine zweite unabhängige Quellenart (mind. 5 Nennungen), steigt die Stufe um eine (B -> A, C -> B). Viele Nennungen aus EINER Quelle ergeben nie A.
- **Warum:** Echte G60-US-Daten: nur 6 von 16 Anforderungen sind durch eine Studie bestätigt. Alte Regel (A = zwei Quellen UND 20 Nennungen) ergab 1 x A, 12 x B, 3 x C; Spracherkennung mit 8 Nennungen plus Studie (16 % unzufrieden) stand gleichauf mit einer Vermutung.
- **Verworfen:** A schon ab 10 Nennungen (Schwelle schwer zu begründen); so lassen (angreifbar: "warum nur ein A?").
- **Wirkung:** 3 x A, 13 x B. HVAC-Bedienung (15 Nennungen, Studienlücke 0,60) liegt mit 47,2 knapp vor dem Touchscreen (47,0), also praktisch gleichauf.
- **Geprüft:** `tests/pfad_c/test_evidence_level.py` (Grenzfälle 4/5/14/15 Nennungen, Web, eine Quelle).
- **An Piyush:** in die Entscheidungstabelle von `docs/ARCHITEKTUR.md` eintragen.

## Entscheidung Sa 10.10., Widersprüche und Abdeckung (Dennis, mit Claude)

- **Was:** (1) Zitiert eine Anforderung Befunde, die sich widersprechen (`conflicts_with`), trägt der Code automatisch "Conflicting evidence: A vs. B" unter Unsicherheiten ein. (2) Der Prompt verlangt, jede Beschwerde und jeden Wunsch in mindestens einer Anforderung zu behandeln.
- **Warum:** Aditya erkennt Konflikte nur grob (gleiche Kategorie, 22 von 45 Befunden betroffen). Der Prompt-Satz "nie verschmelzen" war dadurch nicht einzuhalten, die KI legte nachher sogar MEHR widersprechende Befunde zusammen (5 -> 7). Außerdem blieben nach der Änderung 10 von 30 Beschwerden ohne Anforderung (u. a. Start-Stopp, Spracherkennung).
- **Verworfen:** Nur per Prompt trennen lassen (unwirksam); Konflikte im Code zusammenführen oder trennen (die KI soll formulieren, der Code macht sichtbar).
- **Geprüft:** `tests/pfad_c/test_derive.py` (Widerspruch wird Unsicherheit, kein Duplikat, keine Zusatzzeile ohne Widerspruch), echter Lauf G60-US: 16 Anforderungen, 0 von 30 Beschwerden/Wünschen unbehandelt, 5 von 5 Anforderungen mit Widerspruch zeigen den Hinweis.
- **Offen:** Die Konflikt-Erkennung von Pfad A ist grob (z. B. "Innenraum komfortabel" gegen "Heckklappe funktioniert nicht"). Aditya kann sie verfeinern.

## C8 Qualität der Anforderungstexte: Vorher/Nachher (Dennis, mit Claude, Sa 10.10.)

Geprüft wie ein BMW-PM: kundenorientiert, messbar, realistisch. Verbessert wurde der Prompt (nicht die Ausgabe von Hand), danach neu laufen lassen.

| Messung | Erster Lauf (Beispiel-Befunde) | G60-US (echt, jetzt) | F70-EU (echt, jetzt) |
|---|---|---|---|
| Anforderungen | 8 | 16 | 14 |
| Kriterium ohne Zahl/Testbedingung | 0 | 0 | 0 |
| Platzhalter ("±X km") | 1 | 0 | 0 |
| Erfundene Anforderung über den Befund hinaus | 1 | 0 gefunden | 0 gefunden |
| Out-of-scope-Test (3 Fälle) | 2 von 3 | 3 von 3 | - |
| Beschwerden/Wünsche ohne Anforderung | - | 0 von 30 | 1 von 32 |
| Widersprüche sichtbar (Hinweis unter Unsicherheiten) | - | 5 von 5 | 5 von 5 |
| Stufen A / B / C | 2/5/1 (alt) | 4 / 10 / 2 | 3 / 9 / 2 |
| Befunde mehrfach zitiert | 1 | 1 | 7 |

- **Übertragbarkeit belegt:** F70-EU lief mit derselben Pipeline, nur `config/scenarios/F70-EU.json` (1.433 Kommentare + 37 Studienwerte im Mittelwert-Format, EU = 73,7 % des 2030er-Volumens). Beispielsatz: "Heating/ventilation/air conditioning: mean 7.3 of 10".
- **Bekannte Grenze:** Bei F70 zitieren 7 Befunde mehrere Anforderungen (Nennungen 1,37-fach aufgebläht, vor allem Lob-Themen im Mittelfeld). Nachgerechnet mit geteilten Nennungen: keine Stufe ändert sich, die Spitze bleibt. Darum Formel unverändert, als Grenze dokumentiert. Verworfen: Nennungen anteilig teilen (Mehraufwand ohne sichtbare Wirkung).
- **Offen für Aditya/Piyush:** grobe Konflikt-Erkennung nach Kategorie; Webbelege fehlen lokal.
