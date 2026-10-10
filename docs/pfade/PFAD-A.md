# Pfad A · Interne Evidenz (BMW-Daten → Belege → Befunde)

**Ziel:** Aus den BMW-Dateien saubere, zitierbare Belege machen und daraus Befunde
("Kunden vermissen X", "Y wird gelobt"), die jeweils auf echte Beleg-IDs zeigen.
**Du schreibst in:** `src/backend/evidence_internal/`, `tests/pfad_a/`.
**Du lieferst:** `data/processed/<szenario>/evidence.json`, `context.json`, `signals.json`.
**Schnittstellen:** Kopf von `loaders.py`, `context.py`, `signals.py` (Signaturen nicht ändern).

## Datenfakten (schon geprüft, spart dir Zeit)

- Feedback-Excel = 1 Zeile pro **(Kommentar × Label)**. G60: 5.005 Zeilen, 4.000 Kommentare; US = 3.610.
- `Feedback Type`: Likes / Difficult to Use / Defect / Wants / leer. `Vfc level2 Name` = Thema (z. B. "Electric Range").
- Quellen A-D: A Online-Bewertung, B Händlernotiz, C Umfrage-Freitext, D "das liebe ich am meisten".
- US-Studie (`US_2025`): Blöcke à 8 Zeilen: Attributname, Sample total, 7 Stufen von "I Hate It" bis "I Love It" (Anteile).
- CN/EU-Studie (`CN_EU_2025`): Attribut, darunter "Mean" (~1-10), Spalten = Modell × Land.
- `sales_volumes.xlsx`: Blatt pro Modell, Zeilen EU/CN/US/RoW, Spalten 2024/2025/2030.

## Schritte

| # | Zeitbox | Aufgabe | Fertig, wenn … |
|---|---|---|---|
| 1 | 45 min | `load_feedback` in `loaders.py`: Länder filtern, Duplikat-IDs zu einem Beleg zusammenführen, Labels in `meta`, Polarität | Test: 3 Zeilen gleicher ID → 1 Beleg mit 3 Labels; G60-US ergibt 3.610 Belege |
| 2 | 45 min | `load_study`: US-Blöcke + CN/EU-Mean → je Attribut ein Beleg mit Satz und Kennzahl (Negativanteil, Top-2-Box) | Test mit Mini-DataFrame; "Rear interior roominess" taucht auf |
| 3 | 20 min | `load_context` (Absatz) | `share_of_total_2030` für G60-US ≈ 0,25 |
| 4 | — | **Commit + PR** → Lead lässt Stufe `evidence` laufen (**Sa 17:00**) | `evidence.json` real |
| 5 | 60 min | `extract_signals` v1 **ohne LLM**: Gruppen nach `vfc2 × Feedback Type`, Anzahl, Polarität, 3-5 Beispiel-IDs, Kategorie per Mapping-Tabelle | 20-40 Befunde für G60-US (**Sa 18:00**) |
| 6 | 90 min | v2 **mit LLM** (`core.llm.ask_json`): pro Gruppe Titel/Zusammenfassung/Art; "no_class_found" zuordnen; Studienwerte anhängen | Test: jede `evidence_id` existiert; ≥ 1 Befund mit 2 Quellenarten |
| 7 | 45 min | Konflikte: gleiches Thema, gegensätzliche Polarität → `conflicts_with` | Display-Lob ↔ Touch-Kritik wird erkannt (**Sa 22:00**) |
| 8 | Nacht | Szenario **F70-EU** und **G70-US** durchlaufen lassen, Kategorien-Mapping ergänzen | 3 Szenarien laufen |
| 9 | Nacht | Stretch: "Trickle-down": Befunde aus dem 7er (G70), die beim 5er noch fehlen | Liste in `signals.json` mit `meta.source_derivative` |

## Tests (Beispiele)

- Synthetisches Mini-Excel als DataFrame in `tests/pfad_a/` (keine echten BMW-Daten in Tests!).
- Jeder Befund: `mention_count >= len(evidence_ids)`, alle IDs existieren, Kategorie gültig.
- Out-of-scope (reine Defekte/Werkstatt) wird markiert, nicht still gelöscht.

## Start-Prompt für Claude (anpassen, Ownership-Sprache!)

> "Ich baue Pfad A. Wir lesen das G60-Feedback mit pandas statt mit einem LLM ein, weil das
> reproduzierbar ist und jede Zeile eine stabile ID braucht. Bitte implementiere `load_feedback` in
> `src/backend/evidence_internal/loaders.py` nach dem Vertrag im Dateikopf: Länder aus `cfg["countries"]`,
> gleiche ID → ein Beleg, Labels in meta. Verworfen: eine Zeile pro Label, weil sonst Kommentare
> mehrfach zählen. Schreib zuerst den Test mit einem Mini-DataFrame, dann den Code. Prüfen mit
> `python -m pytest tests/pfad_a -q`."

## Deine Pitch-Folie + Demo-Abschnitt

- Folie "Von 3.610 Stimmen zu 30 Befunden": Trichter + 1 Beispiel (Befund → 3 Zitate).
- Demo (30 s): Auf der Detailseite einen Befund aufklappen und die Originalzitate zeigen.
