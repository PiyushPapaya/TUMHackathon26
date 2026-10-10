# Pfad C · Dennis · Anforderungen + Priorisierung (+ BMW-Mentor)

**Ziel:** Aus Befunden klare, kundenorientierte, **messbare** Anforderungen machen und sie mit einer **erklärbaren Formel** priorisieren.
Dazu Evidenzstufe, Annahmen, Unsicherheiten, „Gibt es das schon?“-Check und die KI-Antwort, wenn der PM nachhakt.
**Du schreibst nur in:** `src/backend/requirements_engine/`, `tests/pfad_c/`.
**Du lieferst:** `requirements.json` (Liste von `Requirement`, siehe `core/models.py`).
**Verträge (nie ändern):** `derive_requirements(scenario, signals, evidence, context)`, `load_offer(pdf_path)`, `check(requirement_title, offer)`,
`answer_challenge(req, question, signals, evidence)`. Innen frei (neue Dateien wie `factors.py`, `prompts.py` erlaubt).
**Schon da (Startversion vom Lead, darfst du verbessern):** `scoring.py`, `evidence_level.py`, `challenge.py`.
Ablauf jedes Tickets: [`ROADMAP.md`](../ROADMAP.md) §4.

## Was Aditya dir liefert (Felder, auf die du dich verlassen kannst)

- Feedback-Beleg `meta`: `feedback_type`, `vfc2`, `source`, `scope`. Studien-Beleg `meta`: `attribute`, `neg_share`, `top2` (US) oder `mean` (CN/EU).
- Webbeleg (Piyush) `meta`: `trust` (high/medium/low), `publisher`, `stance`.
- `context`: `{"sales": {"market", "volume_2030", "share_of_total_2030"}, "option_list_path"}`.
- Bis die echten Dateien da sind: `src/shared/beispiele/stufen/*.json` (die Pipeline nimmt sie automatisch).

## Regeln für jede Anforderung (gehören in den Prompt)

- **Kundensicht:** „Adjust volume without looking at the screen“, nicht „Drehgeber Bauteil X“.
- **Messbar:** Zahl oder Testbedingung, wie auf der BMW-Folie („Range: 600 or 700 mi?“).
- **Realistisch** für den Nachfolger in 3-5 Jahren; Zukunftsannahmen ausdrücklich als `assumptions`.
- Stärken (delight) werden zu **Erhalten-Anforderungen** („Keep ride comfort at least at today's level“).
- **Out of scope** (Regulatorik, Engineering-Spec, Preis/Business-Case) → nicht in die Liste, aber mit Grund in den Prüfpfad.

## Tickets

### [ ] C0 · Setup (15 min, ab 15:15)
- `Ich bin Dennis, starte meine Sitzung.` · eigener OpenAI-Key in `.env` · `data/raw/` per USB.
- **Fertig, wenn:** Tests grün, Entire „Enabled“.

### [ ] C1 · Formel verstehen + BMW-Mentor (25 min, bis 15:55)
- Prompt: „Ticket C1. Erklär mir `scoring.py` und `evidence_level.py` in 5 Sätzen mit einem Rechenbeispiel. Ich muss das der Jury erklären können.“
- **Du als Partner-Kontakt:** die 3 Fragen aus [`LEAD.md`](LEAD.md) („Fragen an BMW“) dem Mentor stellen (vor Ort oder Discord), Antworten in den Team-Chat. Piyush trägt sie in `docs/CHALLENGE.md` ein.
- **Fertig, wenn:** du die Formel ohne Zettel erklären kannst.

### [x] C2 · Anforderungen ableiten v1 (75 min, bis 17:10)
**Prompt:**
> Ich baue Pfad C, Ticket C2. Das LLM formuliert nur die Anforderungen; die Priorität rechnen wir in Python, weil Modelle nicht reproduzierbar rechnen
> und der PM jeden Punkt nachvollziehen muss. Verworfen: LLM vergibt den Score.
> Baue in `derive.py` eine Funktion `derive_all(scenario, signals, evidence, context) -> tuple[list[Requirement], list[dict]]` (zweiter Teil = verworfene Out-of-scope-Entwürfe mit Grund);
> `derive_requirements` gibt nur `derive_all(...)[0]` zurück (Vertrag bleibt). Ein `core.llm.ask_json`-Aufruf mit Schema `RequirementDrafts`
> (Liste von `RequirementDraft`: title, description, acceptance_criterion, category, signal_ids, assumptions, uncertainties, effort S/M/L, forward_looking, in_scope, scope_reason).
> Eingabe: alle Befunde kompakt (id, kind, category, title, summary, mention_count, source_types). Ziel 8-15 Anforderungen. Regeln aus `docs/pfade/PFAD-C.md` („Regeln für jede Anforderung“) in den Prompt.
> Danach im Code: unbekannte `signal_ids` entfernen, Entwürfe ohne gültigen Befund verwerfen, IDs `REQ-<szenario>-<nnn>` in Ausgabereihenfolge.
> Faktoren vorerst alle 0,5, Evidenzstufe über `evidence_level.classify`, Score über `scoring.score`, Rang nach Score.
> Test mit Fake-`ask_json` (monkeypatch): erfundene signal_id fliegt raus; Entwurf mit `in_scope=false` landet im zweiten Rückgabewert.
- **Fertig, wenn:** Test grün · `pipeline.py --scenario G60-US --stage requirements` schreibt 8-15 Anforderungen (anfangs auf Beispiel-Befunden) · `sync`.
- **Subagent:** einer schreibt den Test mit dem Fake, du baust `derive.py`.
- **Wenn es hakt:** Schema-Fehler vom LLM → Felder vereinfachen (Listen als `list[str]`), `effort` als Text und im Code prüfen.

### [x] C3 · Faktoren im Code (45 min, bis 18:00 → **M2 Durchstich 18:30**)
**Prompt:**
> Ticket C3. Lege `factors.py` an: pro Anforderung fünf Werte 0-1 plus je einen Erklärsatz auf Englisch, weil der PM im Wasserfall sehen soll, woher jeder Punkt kommt.
> - `customer_pain`: Schwere nach Art der verknüpften Befunde (complaint 1,0 · unmet_need 0,7 · competitor_advantage 0,5 · delight 0,4 · trend 0,3), gewichtet mit Nennungen. Satz: „Mostly complaints (Defect / Difficult to use), 38 mentions“.
> - `reach`: Nennungen / größte Nennungszahl aller Anforderungen. Satz nennt zusätzlich Markt und `share_of_total_2030` („US = 25 % of 2030 volume“).
> - `satisfaction_gap`: höchstes `neg_share` der verknüpften Studienbelege / 0,25 (max. 1); CN/EU: (9 − mean) / 3. Ohne Studienbeleg 0 und Satz „no study data“.
> - `competitive_pressure`: verknüpfter competitor_advantage-Befund mit Webbeleg `trust=high` → 1,0, `medium` → 0,6, sonst 0.
> - `future_relevance`: verknüpfter trend-Befund → 1,0; `forward_looking` im Entwurf → 0,5; sonst 0,1.
> - `effort_inverse` über `scoring.effort_factor`. `rationale` = Satz aus den zwei größten Beiträgen.
> Tests: je Faktor ein Beispiel mit erwarteter Zahl; alles bleibt zwischen 0 und 1.
- **Fertig, wenn:** echter Lauf auf Adityas `signals.json` (sobald da) liefert plausible Reihenfolge, Top 3 laut vorlesen: ergibt das Sinn? · `sync` · Piyush Bescheid.

### [x] C4 · Scope-Wächter prüfen (30 min, 19:30-20:00)
- Prompt: „Ticket C4. Teste den Scope-Wächter mit 3 Out-of-scope-Befunden (Zulassung/Homologation, Bauteil-Spezifikation, Preis). Sie müssen im zweiten Rückgabewert von `derive_all` landen, mit Grund. Piyush schreibt sie als `REQUIREMENT_DISCARDED` in den Prüfpfad.“
- **Fertig, wenn:** Test grün, Piyush hat `derive_all` in der Pipeline angeschlossen.

### [x] C5 · „Gibt es das schon?“ Optionsliste (60 min, 20:00-21:00)
**Prompt:**
> Ticket C5. Varianten und Pakete sind laut Brief in scope: Wünschen Kunden etwas, das es schon als Option gibt, ist die Antwort oft „ins Paket/Serie“, nicht „neu entwickeln“.
> Zeig mir zuerst lokal 40 Zeilen Text von Seite 5 aus `data/raw/G60_OptionList.PDF` (pymupdf), damit wir das Format sehen. Dann `load_offer`: Code (3 Zeichen), Name, Status
> (■ = standard, □ = optional). `check`: ein `ask_json`-Aufruf mit Anforderungstitel + Liste aller Optionsnamen (PDF ist Deutsch, Titel Englisch, darum LLM statt Wortvergleich),
> Antwort: Status + option_code + kurzer Hinweis; Code muss in der Liste existieren, sonst `unknown`. In `derive_all` für jede Anforderung aufrufen.
> Test für den Parser mit 5 synthetischen Textzeilen.
- **Fertig, wenn:** z. B. berührungslose Heckklappe → `optional` mit Code · `sync`.
- **Wenn es hakt:** Kürzung 3 (Status „unknown“ lassen).

### [x] C6 · Challenge-Antwort mit LLM (60 min, 21:00-22:00, **M3**)
**Prompt:**
> Ticket C6. Die KI soll die Anforderung nicht blind verteidigen, sondern Belege **und** Gegenbelege nennen und ggf. eine Änderung vorschlagen, weil der PM entscheidet.
> `answer_challenge` v2 in `challenge.py`: `ask_json` mit Schema `ChallengeAnswer` (answer, supporting_evidence_ids, counter_evidence_ids, suggested_change oder null),
> Eingabe = Anforderung, Frage, verknüpfte Befunde, bis 30 Belege (ID + Text). Unbekannte IDs im Code entfernen. Bei Fehler oder `DEMO_MODUS`-Cache-Fehlschlag: die bisherige regelbasierte Antwort (nicht wegwerfen).
> Rückgabe-Format (dict mit denselben Schlüsseln) bleibt gleich, weil API und UI es schon nutzen.
> Test: Fake liefert erfundene ID → wird entfernt; Fake wirft Fehler → regelbasierte Antwort kommt.
- **Fertig, wenn:** Tests grün · über `http://localhost:8000/docs` eine Challenge auf Platz 1 schicken → sinnvolle Antwort · `sync` vor 22:00.
- **Für die Demo:** Lasse zeigt 3 Vorschlagsfragen als Buttons („Is this only a US issue?“, „Is this just a habit of older customers?“, „What speaks against it?“). Lass sie vorab einmal laufen, damit sie im Cache sind.

### [x] C7 · Evidenzstufen kalibrieren (45 min, 22:00-23:00)
- Prompt: „Ticket C7. Zeig mir die Verteilung A/B/C/D und die Nennungen pro Anforderung für G60-US. Passe die Schwellen in `evidence_level.py` so an, dass A wirklich stark ist (Richtwert: 2-4× A, mehrere B/C, Trends D). Begründe die Schwellen im Docstring mit den echten Zahlen.“
- **Fertig, wenn:** Verteilung plausibel, Docstring begründet, Tests angepasst, `sync`. **Dann schlafen (Schicht 1, 23:30-03:30).**

### [x] C8 · Qualität der Anforderungstexte (60 min, ab 03:30)
- Prompt: „Ticket C8. Lies alle Anforderungen für G60-US und F70-EU kritisch wie ein BMW-PM: Ist jede kundenorientiert, messbar, realistisch? Verbessere den Prompt (nicht die Ausgabe von Hand), lass neu laufen, vergleiche vorher/nachher in einer Tabelle.“
- **Achtung:** Neuer Prompt = neuer Cache-Eintrag. Danach Piyush bitten, das Bundle neu zu bauen.

### [x] C9 · Randfälle testen (45 min, bis 05:30)
- Prompt: „Ticket C9. Ergänze Tests in `tests/pfad_c/` für Randfälle: keine Befunde, Befund ohne Belege, alle Gewichte 0 außer einem, Anforderung ohne Studienbeleg, LLM liefert leere Liste. Nichts darf abstürzen.“

### [ ] C10 · Was-wäre-wenn erklären (30 min, bis 06:00)
- Lasse baut einen Schalter „Annahmen ignorieren“ (Score ohne `future_relevance`) direkt im Frontend aus `score_breakdown`. Du lieferst ihm die Formel als 2 Sätze und prüfst 2 Beispiele von Hand.

### [ ] C11 · Pitch-Teil (So 08:30-09:30)
- Folie „Priorität, die man erklären kann“: Formel, Wasserfall von Platz 1, Evidenzstufen A-D in einem Satz. 3 Stichpunkte an Piyush.
- Jury-Fragen zu Priorisierung, Evidenzstufe, Scope aus `pitch/PITCH.md` laut üben.
