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
