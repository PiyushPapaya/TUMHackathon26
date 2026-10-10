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
