# API-Vertrag (Owner: Lead)

Basis-URL lokal: `http://localhost:8000`. Interaktive Doku mit allen Feldern: **`/docs`**.
Datenmodell im Code: `src/backend/core/models.py` + `core/model_parts.py`. Vollständiges Beispiel-Bundle:
`beispiele/bundle_G60-US.json` (synthetische Zitate).

**Grundsatz Welle 2: Das Frontend rechnet nichts.** Jede Zahl, jedes Label, jeder Satz kommt fertig
aus dem Backend. **Echte Beispielantwort für jeden Endpunkt:** `beispiele/views/<name>.json`
(erzeugt mit `python scripts/make_view_examples.py`, also immer passend zum Code).

## Lesen: Ansichten (fertig gerechnet)

| Methode + Pfad | Ansicht | Beispiel |
|---|---|---|
| `GET /health` | Status: `version`, `demo_mode`, `scenarios` | `views/health.json` |
| `GET /api/scenarios` | Szenario-Wähler: Szenario + `data_coverage`, `badge` (`reich`/`dünn`/`Kaltstart`), `headline_numbers`, `warnings` | `views/scenarios.json` |
| `GET /api/scenarios/{id}/overview` | Startseite: `funnel`, `top3`, `level_distribution` (A–D), `warnings`, `source_mix`, `generated_at` | `views/overview.json` |
| `GET /api/requirements/{req_id}/explain` | Detailseite: `waterfall` (Faktor, Gewicht, Beitrag, Satz; letzter Schritt = Abschlag der Evidenzstufe), `quotes` (Top 5 mit Land/Antrieb/Quelle), `segments`, `conflicts`, `assumptions`, `offer_check`, `web_sources` (nach Vertrauen), `study`, `robustness` + `robustness_sentence`, `business`, `history` | `views/explain.json` |
| `POST /api/scenarios/{id}/whatif` | Gewichte-Regler Live-Vorschau, **speichert nichts**: `[{id, title, old_rank, new_rank, rank_change, old_score, new_score}]` | `views/whatif.json` |
| `GET /api/portfolio` | Matrix Kategorie × Szenario: `rows[].cells[szenario]` (Rang, Stufe), `rows[].class` (`plattformweit`/`modellspezifisch`/`marktspezifisch`/`einzeln`/`gemischt`/`nicht oben`), `rule` | `views/portfolio.json` |
| `GET /api/compare?a=G60-US&b=G60-EU` | Markt-Vergleich: gleiche Kategorie nebeneinander, `rank_diff`, Unzufriedenheit, `sentence` | `views/compare.json` |
| `GET /api/scenarios/{id}/opportunities` | Chancen-Karte: `points[]` mit `importance`, `dissatisfaction`, `quadrant` (`Chance`/`Stärke halten`/`Beobachten`/`Nebensache`), `thresholds` | `views/opportunities.json` |
| `GET /api/scenarios/{id}/trends` | Trendradar: `rings` (heute, Nachfolger-Jahr), `items[]` (`kind`: `trend` oder `bet`) | `views/trends.json` |
| `GET /api/scenarios/{id}/gaps` | „Was wir nicht wissen“: `weak_requirements` (C/D mit `why`, `next_study`), `missing_sources`, `share_weak` | `views/gaps.json` |
| `GET /api/scenarios/{id}/evidence?signal=&segment=engine:BEV&q=&page=1&size=20` | Beleg-Browser, gefiltert und seitenweise: `{total, page, size, items}` | `views/evidence.json` |
| `GET /api/audit/timeline?scenario_id=&requirement_id=` | Prüfpfad als Sätze: `sentence`, `actor`, `rationale` | `views/audit_timeline.json` |

| `GET /api/scenarios/{id}/matrix` | Matrix Heute/Zukunft × Evidenz: `items[req_id]` mit `horizon`, `evidence_level`, `quadrant` (`Sicher & dringend`/`Belegte Zukunftswette`/`Schwach belegt, heute`/`Annahme – beobachten`), `offer_gap` + `offer_gap_label` (`Lücke: nicht angeboten`/`nur optional`/`Serie`) | `views/matrix.json` |
| `GET /api/requirements/{req_id}/counterparts` | Markt-Vergleich je Anforderung: pro anderem Szenario `match` (`id`, `rank`, `score`) oder `null` + `sentence` (`"F70-EU: Platz 4, Score 71"` / `"kein Gegenstück"`); Regel: gleiche Kategorie + Titel-Jaccard ≥ 0,3 | `views/counterparts.json` |
| `GET /api/scenarios/{id}/memo` | Entscheidungs-Memo als **Markdown** (text/plain): freigegebene Anforderungen (sonst Top 5 als Entwurf), Score, Stufe, Belege, Annahmen, Zeile „Prüfpfad gültig, N Ereignisse“ | – |

## Prompt-Linse: `POST /api/scenarios/{id}/lens`

```json
{"question": "Familien in den USA, Fokus Laden und Platz", "actor": "pm.mueller"}
```

Antwort: `{question, interpretation, source ("ai"|"rules"), weights, filters: {categories, only_gaps}, note, top: [{requirement, lens_score, lens_rank, reasons: [{factor, contribution, sentence}]}]}` (Beispiel `views/lens.json`).
Die KI liefert nur Gewichte + Filter, nie IDs; Python rechnet die Top 5 auf Kopien, **der Store bleibt unverändert**.
Schreibt `AI_LENS_SUGGESTED` in den Prüfpfad. „Gewichte übernehmen“ = `PUT /weights` mit `weights` aus der Antwort und dem Prompt-Text als `rationale`.
Fehler: `404` unbekanntes Szenario · `422` leere Frage.

## Lesen: Rohdaten (wie bisher)

| Methode + Pfad | Antwort |
|---|---|
| `GET /api/scenarios/{id}/funnel` | `{"evidence": 3610, "signals": 8, "requirements": 5, "approved": 0}` |
| `GET /api/scenarios/{id}/signals` | `[Signal]` |
| `GET /api/scenarios/{id}/requirements` | `[Requirement]` sortiert nach `rank` |
| `GET /api/requirements/{req_id}` | `{"requirement", "signals", "evidence", "history"}` |
| `GET /api/audit?scenario_id=&requirement_id=` | `[AuditEvent]` chronologisch |
| `GET /api/audit/verify` | `{"valid": true, "broken_at_seq": null, "checked": 12}` |
| `GET /api/scenarios/{id}/export?format=csv\|json` | CSV (`;`) oder JSON-Liste der Anforderungen (Markdown-Lastenheft folgt mit C21) |

## Schreiben (jede Aktion erzeugt ein Audit-Ereignis, Begründung ist Pflicht)

### `POST /api/requirements/{req_id}/decision`

```json
{"action": "approve", "actor": "pm.mueller", "rationale": "Belege aus Feedback und Studie überzeugen"}
{"action": "reject", "actor": "pm.mueller", "rationale": "Zu wenige Nennungen, später erneut prüfen"}
{"action": "edit", "actor": "pm.mueller", "rationale": "Kriterium geschärft",
 "changes": {"acceptance_criterion": "Lautstärke und Temperatur blind in 1 Handgriff", "effort": "S"}}
{"action": "challenge", "actor": "pm.mueller", "rationale": "Gegenprobe",
 "question": "Ist das nur Gewohnheit älterer Kunden?"}
```

Bearbeitbar: `title, description, acceptance_criterion, effort, assumptions, uncertainties`.
Antwort: `{"requirement": Requirement, "ai_answer": null | {"answer", "supporting_evidence_ids", "counter_evidence_ids", "suggested_change"}}`.
Fehler: `404` unbekannte ID · `422` leere Begründung, falsche Felder.

### `PUT /api/scenarios/{id}/weights` (Regler „Übernehmen“)

```json
{"weights": {"future_relevance": 0.3, "customer_pain": 0.2}, "actor": "pm.mueller",
 "rationale": "Nachfolger kommt 2030, Zukunft zählt mehr"}
```

Faktoren: `customer_pain, reach, satisfaction_gap, competitive_pressure, future_relevance, effort_inverse`.
Fehlende Faktoren behalten ihren Standardwert; alles wird auf Summe 1 normiert. Antwort: neu gerankte `[Requirement]`.
`POST /whatif` nimmt dasselbe `weights`-Objekt (ohne `actor`/`rationale`) und speichert nichts.

## Wichtige Felder

**Requirement:** `id`, `title`, `description`, `acceptance_criterion`, `category`, `signal_ids`, `score` (0-100), `rank`,
`score_breakdown` (`{faktor: {value, weight, contribution, explanation}}`), `rationale`, `evidence_level` (`A|B|C|D`),
`assumptions`, `uncertainties`, `offer_check`, `effort` (`S|M|L`), `status`, `version`.
**Neu (Welle 2, alle mit Default):** `horizon` (`today|next_gen`), `robustness` (`{rank_min, rank_max, top3_share, runs}` oder null),
`segment_conflicts` (`[{dimension, segment_a, segment_b, statement, a_count, b_count, evidence_ids}]`),
`business` (`{volume_2025, volume_2030, growth_pct, market_share, note}` oder null; null-Werte = „nicht verfügbar“),
`stable_key`, `badges` (fertige Kurzlabels, z. B. `robust`, `Konflikt`, `Zukunftswette`, `Annahme`).

**Signal:** `id`, `kind`, `category`, `title`, `summary`, `evidence_ids`, `mention_count`, `source_types`, `conflicts_with`.
**Neu:** `segments` (`{"engine": {"BEV": 42, "ICE": 18}, "country": {...}, "source": {...}, "feedback_type": {...}}`),
`study_link` (`{attribute, importance, dissatisfaction}` oder null).

**Scenario:** `id`, `derivative`, `model_name`, `market`, `countries`, `competitors`, `successor_horizon`.
**Neu:** `data_coverage` (`{feedback, study, sales, options, web, external, badge}`), `warnings`.

**Evidence:** `id`, `source_type` (`feedback|study|sales|option_list|web|external_stat|feedback_external`), `source_name`,
`text`, `url`, `retrieved_at`, `polarity` (-1/0/1), `meta` (Schlüssel u. a. `engine`, `country`, `source_letter`, `feedback_type`, `trust`, `publisher`).

**AuditEvent:** `seq`, `ts`, `event_type`, `scenario_id`, `requirement_id`, `actor` (`{type: ai|human|system, name}`),
`rationale`, `payload`, `prev_hash`, `hash`.

## Wer füllt welches neue Feld (Pipeline)

| Feld | Pfad · Ticket | Wo |
|---|---|---|
| `Evidence.meta.engine/country/source_letter/feedback_type` | A · A14 | `evidence.json` |
| `Signal.segments`, `Signal.study_link` | A · A14, A17 | `signals.json` |
| `context.json["unmapped_topics"]` (`{thema: anzahl}`) | A · A15 | wird zu `bundle.context` |
| `context.json["sales"]` mit `volume_2024/2025/2030`, `growth_pct`, `share_of_total_2030` (nie still 0, sonst `null`) | A · A16 | wird zu `bundle.context` |
| `context.json["opportunities"]` (`[{attribute, category, importance, dissatisfaction, evidence_id}]`) | A · A17 | wird zu `bundle.opportunities` |
| `Requirement.stable_key`, `horizon`, `assumptions` (Pflicht bei D), `robustness`, `business`, `segment_conflicts`, `badges` | C · C12-C19 | `requirements.json` |
| `Scenario.data_coverage`, `funnel.generated_at` | Lead | `pipeline.py bundle_stage` |
