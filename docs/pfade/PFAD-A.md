# Pfad A · Aditya · Interne Evidenz + Eval-Zahl

**Ziel:** Aus den BMW-Dateien saubere, zitierbare **Belege** machen, daraus **Befunde** („Kunden vermissen X“), die auf echte
Beleg-IDs zeigen, und am Ende **die eine Zahl**, die beweist, dass man unserer KI trauen kann.
**Du schreibst nur in:** `src/backend/evidence_internal/`, `tests/pfad_a/`, `tests/eval/`.
**Du lieferst:** `data/processed/<szenario>/evidence.json`, `context.json`, `signals.json` (über `pipeline.py`) und `tests/eval/REPORT.md`.
**Verträge (Kopf der Dateien, Signatur nie ändern):** `load_all_evidence(cfg, raw_dir)`, `load_context(cfg, raw_dir)`, `extract_signals(scenario, evidence)`.
Innen bist du frei: Du darfst weitere Dateien in deinem Ordner anlegen (z. B. `feedback.py`, `study.py`, `taxonomy.py`).
Ablauf jedes Tickets: [`ROADMAP.md`](../ROADMAP.md) §4.

## Datenfakten (am 10.10. mit den echten Dateien geprüft, nicht neu suchen)

- **Feedback** `G60_feedback_hackathon.xlsx`, Blatt `Feedback_Explorer`, 5.005 Zeilen, 12 Spalten:
  `ID, Source, Brand, Sales Description, Country, Derivate (e-code), Engine Type, Feedback Type, Customer Feedback, Vfc level2 3 Name, Vfc level2 Name, Vfc level3 Name`.
- 1 Zeile = (Kommentar × Label). **G60 US: 4.365 Zeilen, 3.610 eindeutige IDs** → 3.610 Belege.
- `Source`-Werte heißen `"Source A"` … `"Source D"` (A Online-Bewertung, B Händlernotiz, C Umfrage-Freitext, D „liebe ich am meisten“).
- `Feedback Type`: Likes 1.951 · Difficult to Use 1.306 · **leer 731** · Wants 582 · Defect 435.
- `Vfc level2 Name`: `no_class_found` 525×, danach Drivetrain, Handling / Riding, Exterior design, Seats, Electric Range, Touch screen, operation, …
- **Studie** `F70_G60_G68_G70_customer_studies.xlsx`, Blätter `CN_EU_2025` (76×6) und `US_2025` (929×4), beide **ohne Kopfzeile** lesen (`header=None`).
  - `US_2025`: **Blöcke à 9 Zeilen**: Attributname · `Sample total` · 7 Stufen `I Hate It, A Failure, Unsatisfactory, Satisfactory, Excellent, Delightful, I Love It` (Anteile 0-1).
    Modellnamen stehen nur in Zeile 0, Spalten 2-3: `"BMW 5 Series G60"`, `"BMW 7 Series G70 "` (**Leerzeichen am Ende → `strip()`**).
    **103 Attribute** (nicht ~100); **2 Blöcke haben eine zusätzliche leere Zeile** nach `Sample total` (10 statt 9 Zeilen) → nach Label lesen, nicht nach festem Abstand.
    Ergebnis A2: G60-US 103 Belege, G70-US 103, F70-EU 37.
  - `CN_EU_2025`: Zeile 1 = Land (`China` in Spalte 1, `EU` in Spalte 3; **nach rechts auffüllen**), Zeile 2 = Modell, danach Paare (Attributzeile, `Mean`-Zeile, Skala ~1-10).
    F70 EU = Spalte 3.
- **Absatz** `sales_volumes.xlsx`, Blätter `F70`, `G60_G68`, `G70`; Kopf: `market, market_code, volume_2024, volume_2025, volume_2030`.
  G60_G68: US 2030 = 80.000 von 316.000 → `share_of_total_2030 ≈ 0,253`.

## Absprache mit Dennis (Pfad C braucht diese Felder, bitte genau so)

- Feedback-Beleg `meta`: `vfc2`, `vfc3`, `feedback_type` (bei mehreren: `" | "`-getrennt), `labels` (`"vfc2/Typ | vfc2/Typ"`), `engine`, `source` (A-D), `scope` (`in`/`out`).
- Polarität: leerer Feedback-Typ = 0, **außer Quelle D** = +1 (Frage „Was liebst du am meisten?“, BMW lässt den Typ leer). Dann steht `meta["polarity_basis"] = "source_d_praise"`. Quelle A/C ohne Typ bleiben 0 (mischen Lob und Beschwerden).
- Studien-Beleg `meta`: `attribute`, `neg_share` (US: Hate+Failure+Unsatisfactory, als `"0.14"`), `top2` (Delightful+Love), `mean` (CN/EU).
- Beleg-IDs: Feedback `EV-<szenario>-FB-<BMW-ID>`, Studie `EV-<szenario>-ST-<nn>`. Befund-IDs: `SIG-<szenario>-<nnn>`.

## Tickets

### [x] A0 · Setup (15 min, ab 15:15)
- `Ich bin Aditya, starte meine Sitzung.` → Skill prüft venv, `.env` (eigener OpenAI-Key), Entire, Tests.
- BMW-Dateien per USB von Piyush nach `data/raw/` kopieren (nie committen, `data/` ist gitignored).
- **Fertig, wenn:** `python -m pytest -q` grün, `entire status` = Enabled, `ls data/raw` zeigt 9 Dateien.

### [x] A1 · Feedback einlesen (45 min, bis 16:15)
**Prompt:**
> Ich baue Pfad A, Ticket A1. Wir lesen das Feedback mit pandas statt mit einem LLM, weil das reproduzierbar ist und jede Zeile eine stabile ID braucht.
> Lege `src/backend/evidence_internal/feedback.py` an mit `feedback_to_evidence(df, cfg) -> list[Evidence]` (rein, testbar ohne Datei) und
> `load_feedback(cfg, raw_dir)` (liest `cfg["data"]["feedback_file"]`, Blatt `Feedback_Explorer`). Regeln: nur `Country` in `cfg["countries"]`;
> gleiche `ID` → **ein** Beleg, alle Labels in `meta` (Felder siehe Abschnitt „Absprache mit Dennis“ in `docs/pfade/PFAD-A.md`);
> Polarität: Likes +1, Defect/Difficult to Use/Wants -1, leer 0, bei mehreren Labels Vorzeichen der Summe; `meta["scope"]="out"`, wenn **alle** Labels `Defect` sind und Quelle B (Werkstattfall, keine Kundenanforderung).
> Text unverändert übernehmen (nur `strip()`), weil die Eval später prüft, dass jedes Zitat wörtlich existiert.
> Verworfen: ein Beleg pro Zeile, weil Kommentare sonst mehrfach zählen. `load_all_evidence` in `loaders.py` ruft vorerst nur `load_feedback` auf.
> Erst Test `tests/pfad_a/test_feedback.py` mit synthetischem Mini-DataFrame (3 Zeilen gleiche ID → 1 Beleg mit 3 Labels; fremdes Land fliegt raus; leerer Typ → Polarität 0), dann Code.
> Danach lokal: wie viele Belege ergibt G60-US? Erwartet 3.610.
- **Fertig, wenn:** Test grün · G60-US ergibt **3.610** Belege · jede ID beginnt mit `EV-G60-US-FB-` · keine echten BMW-Texte in `tests/`.
- **Subagent:** „Ein Subagent schreibt den Test aus diesen Regeln, während du `feedback.py` baust.“
- **Wenn es hakt:** Zahl ≠ 3.610 → prüfen, ob `Country` Leerzeichen hat (`str.strip()`), ob IDs als Zahl/Text gemischt sind (`astype(str)`).

### [x] A2 · Studie einlesen (45 min, bis 17:00)
**Prompt:**
> Ticket A2. Lege `src/backend/evidence_internal/study.py` an mit `parse_us_study(df, model_column)` und `parse_cn_eu_study(df, market, model_column)`
> (beide rein, testbar) und `load_study(cfg, raw_dir)`. Format steht exakt im Abschnitt „Datenfakten“ von `docs/pfade/PFAD-A.md`
> (US: Blöcke à 9 Zeilen, Spaltennamen mit Leerzeichen am Ende; CN/EU: Land-Zeile nach rechts auffüllen, Attribut + Mean-Zeile).
> Pro Attribut ein `Evidence(source_type="study")`, Text als Satz, z. B. „Rear interior roominess: 14 % dissatisfied, 61 % top-2 (US study 2025)“,
> Meta `attribute`, `neg_share`, `top2` bzw. `mean`. Polarität US: -1 wenn neg_share ≥ 0,10, +1 wenn top2 ≥ 0,60, sonst 0; CN/EU: -1 wenn Mean < 7,5, +1 wenn ≥ 9,0.
> Warum Kennzahl als Satz: Die UI zeigt Belege einheitlich, und der PM soll die Zahl ohne Excel verstehen.
> `load_all_evidence` = Feedback + Studie. Tests mit Mini-DataFrames für beide Formate (inkl. Spaltenname mit Leerzeichen).
- **Fertig, wenn:** Tests grün · G60-US hat ~100 Studienbelege · F70-EU liest Spalte 3 von `CN_EU_2025` · `pipeline.py --scenario G60-US --stage evidence` läuft.
- **Subagent:** zwei Subagents parallel, je einer pro Studienformat (verschiedene Funktionen, gleiche Datei → nacheinander einfügen lassen).
- **Wenn es hakt (nach 30 min):** CN/EU weglassen (nur US), F70-EU kommt in A8 dran.

### [x] A3 · Absatz-Kontext (20 min, bis 17:20)
**Prompt:**
> Ticket A3. Implementiere `load_context` in `context.py` nach Vertrag: Blatt `cfg["data"]["sales_sheet"]`, Zeile mit `market_code == cfg["data"]["sales_market_code"]`.
> `share_of_total_2030` = Volumen 2030 des Markts / Summe aller Märkte 2030. Test mit Mini-DataFrame.
- **Fertig, wenn:** G60-US → `share_of_total_2030 ≈ 0.253`, `volume_2030 = 80000`.

### [x] A4 · Push + M1 (10 min, 17:20-17:30)
- `sync`, dann Piyush im Chat: „A1-A3 auf main, bitte Stufe evidence laufen lassen.“
- Du selbst: `python src/backend/pipeline.py --scenario G60-US --stage evidence` → `data/processed/G60-US/evidence.json` + `context.json`.

### [x] A5 · Befunde v1 ohne LLM (60 min, bis 18:30, **M2 Durchstich**)
**Prompt:**
> Ticket A5. Implementiere `extract_signals` in `signals.py`, **v1 ohne LLM**, weil die Taxonomie von BMW schon gute Gruppen liefert und das erklärbar ist.
> 1) Lege `taxonomy.py` an: Mapping `vfc2 → Category` für alle `Vfc level2 Name`-Werte (gib mir zuerst lokal die Liste der eindeutigen Werte aus allen drei Feedback-Dateien;
>    nicht zuordenbare → `None` = ignorieren; `no_class_found` → ignorieren in v1).
> 2) Gruppen = (vfc2, Feedback-Typ) aus `meta["labels"]` (ein Beleg kann in mehreren Gruppen sein); nur `scope=in`; nur Gruppen mit ≥ 5 Nennungen.
> 3) Art: Likes → delight, Defect/Difficult to Use → complaint, Wants → unmet_need; leerer Typ → nach Polarität.
> 4) `evidence_ids` = bis zu 8 typische Belege (Länge 60-300 Zeichen bevorzugt), `mention_count` = volle Gruppengröße, Titel v1 = „<vfc2>: <Art>“.
> 5) Studie: Attribute mit neg_share ≥ 0,10 an den passenden Feedback-Befund hängen (kleines Mapping Attribut → vfc2 in `taxonomy.py`), dann `source_types` = feedback + study.
>    Ohne passenden Befund: eigener complaint-Befund aus der Studie.
> 6) IDs `SIG-<szenario>-<nnn>` nach Nennungen absteigend.
> Tests: jede zitierte `evidence_id` existiert; `mention_count >= len(evidence_ids)`; Kategorie gültig; Gruppe < 5 fällt weg.
- **Fertig, wenn:** G60-US ergibt **20-45 Befunde** · ≥ 3 Befunde haben feedback **und** study · `pipeline.py --scenario G60-US --stage signals` läuft · `sync`, Piyush Bescheid geben.
- **Subagent:** einer baut `taxonomy.py` (Mapping), du baust die Gruppierung.
- **Ergebnis A5 (echte Daten):** je Szenario 45 Befunde (Obergrenze, größte zuerst, Untergrenze 5 Nennungen). G60-US: 6 mit Feedback + Studie, 10 Wünsche, 0 unbekannte IDs.
  Entscheidungen: Obergrenze 45 statt Schwelle (bei ≥5 wären es 162); Gruppen mit 2 Quellenarten bleiben immer; reine Studien-Befunde max. 8; 10 Plätze für Wünsche;
  Quelle D über den Bereich im Satz zugeordnet; „Body equipment“ bewusst ungemappt (Sammelbegriff).

### [ ] A6 · Befunde v2 mit LLM (90 min, 19:30-21:00)
**Prompt:**
> Ticket A6. Wir lassen das LLM nur **formulieren und auswählen**, nicht gruppieren, weil die Gruppen aus v1 nachvollziehbar sind.
> Für die Top-30-Gruppen: `core.llm.ask_json` mit Schema `SignalDraft` (title, summary in Kundensprache auf Englisch, kind, representative_ids 3-5).
> Pro Gruppe max. 40 Belege (ID + Text, auf 300 Zeichen gekürzt). Prompt-Regel: nur IDs aus der Eingabe. **Danach im Code alle unbekannten IDs entfernen**
> (Halluzinationsschutz) und bei Fehler/leerem Ergebnis auf v1 zurückfallen. Verworfen: freies Clustering per LLM (teuer, nicht reproduzierbar).
> Test mit einem Fake für `ask_json` (monkeypatch), der eine erfundene ID zurückgibt → muss rausgefiltert werden.
- **Fertig, wenn:** Test grün · echter Lauf G60-US: Titel lesen sich wie Kundenaussagen · zweiter Lauf ist sofort fertig (Cache) · `sync`.
- **Wenn es hakt:** Kürzung 5 in der ROADMAP (v1-Titel bleiben). Kosten: ~30 Aufrufe, wenige Cent.
- **Stand:** Code + Tests fertig (`signals_llm.py`, `extract_signals(..., use_llm=True)`). **Echter Lauf offen:** `.env` hat keinen `OPENAI_API_KEY`;
  ohne Key bleibt v1 und es erscheint eine Warnung. Danach `pipeline.py --scenario G60-US --stage signals` zweimal laufen lassen (zweiter Lauf = Cache).
  Entscheidungen: Gruppen und `kind` bleiben aus v1 (nicht im Schema); Titel/Zusammenfassung mit Zahlen werden abgelehnt (Zahlen nur aus dem Code); Zitate nur aus der eigenen Gruppe.

### [x] A7 · Konflikte (45 min, bis 22:00, **M3**)
**Prompt:**
> Ticket A7. Widersprüche zeigen statt wegmitteln, weil der Brief „conflicting evidence“ ausdrücklich will.
> Regel in `conflicts.py`: gleiche Kategorie, eine Seite delight, andere complaint/unmet_need, beide ≥ 10 Nennungen → `conflicts_with` gegenseitig.
> Pro Befund höchstens 2 Konflikte (die mit den meisten Nennungen), damit die UI nicht überladen ist. In `extract_signals` am Ende aufrufen. Test mit 4 Mini-Befunden.
- **Fertig, wenn:** im echten G60-US ist z. B. Display/Instrumente gelobt ↔ Touch-Bedienung kritisiert verknüpft · `sync` vor 22:00.
- **Ergebnis A7:** gleiches Thema ab 10 Nennungen (z. B. Seats: Lob 41 ↔ Kritik 36), verschiedene Themen erst ab 30, höchstens 2 je Befund, gleiches Thema zuerst. G60-US: 11 Themenpaare; bei Schwelle 10 für alle hingen 33 von 45 Befunden an einem Konflikt (zu viel Rauschen).

### [ ] A8 · Zweites Szenario F70-EU (+ G70-US) (60 min, Nacht ab 23:00)
- **Prompt:** „Ticket A8. Lass die Pipeline für `F70-EU` und `G70-US` laufen. Prüfe Länderliste in `config/scenarios/F70-EU.json` gegen die echten `Country`-Werte
  der F70-Datei und melde Piyush Änderungen (Config gehört dem Lead). Ergänze fehlende vfc2-Werte in `taxonomy.py`.“
- **Fertig, wenn:** beide Szenarien liefern Befunde; Piyush hat die Bundles gebaut; im UI-Umschalter sichtbar.
- **Stand A8:** G70-US und F70-EU liefern je 45 Befunde (0 unbekannte IDs). Länderliste F70-EU gegen die echte Datei geprüft: in `F70_feedback_hackathon.xlsx` kommen
  GB (2.790 von 4.076 Zeilen), SE, FR, DK, FI vor; NO, ES, DE, IT, NL, LV fehlen (harmlos). JP (1.026), AU, KR, ZA sind absichtlich nicht im EU-Szenario.
  **Hinweis an Piyush:** F70-EU ist praktisch ein UK-Szenario. Taxonomie deckt 73-81 % der Kommentare mit Thema ab; der Rest sind seltene Themen (je < 20 Nennungen), nichts ergänzt.

### [ ] A9 · Eval-Stichprobe von Hand labeln (60 min, Nacht ~00:00)
**Prompt:**
> Ticket A9. Wir messen, ob unsere Befunde stimmen, weil die Jury fragen wird „Warum soll ich der KI trauen?“.
> Erzeuge `data/eval/G60-US_sample.csv` (nicht im Git!): 50 zufällige Paare (Befund, zitierter Beleg), Seed 42, Spalten `signal_id, signal_title, evidence_id, text, passt (j/n)`.
> Ich fülle `passt` in Excel aus.
- **Du selbst:** 50 Zeilen lesen, `j`/`n` eintragen (~30 min). Ehrlich labeln, auch wenn es weh tut.
- **Stand A9:** `python tests/eval/make_sample.py G60-US` hat `data/eval/G60-US_sample.csv` erzeugt (50 Paare, 33 Befunde, Seed 42). **Offen: das Labeln der Spalte `passt (j/n)` (nur ein Mensch).** Danach `python tests/eval/run_eval.py G60-US`.

### [ ] A10 · Eval-Skript + REPORT (60 min, bis 03:00)
**Prompt:**
> Ticket A10. Baue `tests/eval/run_eval.py` (läuft lokal mit Daten, in der CI überspringen, wenn `data/` fehlt):
> (a) **Grounding-Rate**: Anteil aller in Befunden und Anforderungen zitierten IDs, die in `evidence.json` existieren, und Anteil Feedback-Texte, die **wörtlich** in der Excel stehen (Ziel 100 %);
> (b) **Befund-Treue**: Anteil `j` in `data/eval/G60-US_sample.csv`;
> (c) **Abdeckung**: Anteil der US-Kommentare, die in mindestens einem Befund landen; (d) Anteil Anforderungen mit Zahl im Akzeptanzkriterium.
> Schreibe `tests/eval/REPORT.md` nur mit Zahlen, Methode und Grenzen, **ohne BMW-Zitate** (Repo ist öffentlich). Kleiner pytest für die Rechenfunktionen mit Fake-Daten.
- **Stand A10:** `tests/eval/run_eval.py` + `eval_metrics.py` + Tests fertig. G60-US: Grounding 100 %, Wortlaut 100 %, Abdeckung 41,8 %. Offen: Befund-Treue (wartet auf A9-Labels) und Anforderungs-Zahlen (wartet auf `requirements.json` von Pfad C).
- **Fertig, wenn:** `REPORT.md` hat 4 Zahlen + Methode · Piyush hat die Zahl für Deck und README · `sync` vor dem Schlafen (03:30).

### [ ] A11 · Pitch-Teil (So 08:30-09:30)
- Folie „Kann man der KI trauen?“: Grounding-Rate, Befund-Treue, Trichter 3.610 → N → M. Inhalt als 3 Stichpunkte an Piyush.
- Demo-Teil (20 s): Szenario auf F70-EU umschalten. 2 Jury-Antworten aus `pitch/PITCH.md` laut üben.
