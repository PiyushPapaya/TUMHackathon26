# API-Vertrag (Owner: Lead)

Basis-URL lokal: `http://localhost:8000`. Interaktive Doku mit allen Feldern: **`/docs`**.
Datenmodell im Code: `src/backend/core/models.py`. Vollständiges Beispiel: `beispiele/bundle_G60-US.json`
(synthetische Zitate). Änderungen nur per PR vom Lead.

## Lesen

| Methode + Pfad | Antwort |
|---|---|
| `GET /health` | `{"status": "ok"}` |
| `GET /api/scenarios` | `[Scenario]`, z. B. `{"id": "G60-US", "model_name": "BMW 5er Limousine (G60)", "market": "US", "competitors": [...]}` |
| `GET /api/scenarios/{id}/funnel` | `{"evidence": 3610, "signals": 8, "requirements": 5, "approved": 0}` |
| `GET /api/scenarios/{id}/signals` | `[Signal]` |
| `GET /api/scenarios/{id}/requirements` | `[Requirement]` sortiert nach `rank` |
| `GET /api/requirements/{req_id}` | `{"requirement": Requirement, "signals": [Signal], "evidence": [Evidence], "history": [AuditEvent]}` |
| `GET /api/audit?scenario_id=&requirement_id=` | `[AuditEvent]` chronologisch |
| `GET /api/audit/verify` | `{"valid": true, "broken_at_seq": null, "checked": 12}` |
| `GET /api/scenarios/{id}/export` | CSV (Trennzeichen `;`), eine Zeile pro Anforderung |

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
Antwort: `{"requirement": Requirement, "ai_answer": null | {"answer": "...", "supporting_evidence_ids": [...], "counter_evidence_ids": [...], "suggested_change": null}}`
Fehler: `404` unbekannte ID · `422` leere Begründung, falsche Felder.

### `PUT /api/scenarios/{id}/weights`

```json
{"weights": {"future_relevance": 0.3, "customer_pain": 0.2}, "actor": "pm.mueller",
 "rationale": "Nachfolger kommt 2030, Zukunft zählt mehr"}
```

Faktoren: `customer_pain, reach, satisfaction_gap, competitive_pressure, future_relevance, effort_inverse`.
Fehlende Faktoren behalten ihren Standardwert; alles wird auf Summe 1 normiert. Antwort: neu gerankte `[Requirement]`.

## Wichtige Felder

**Requirement:** `id` (`REQ-G60-US-001`), `title`, `description`, `acceptance_criterion`, `category`,
`signal_ids`, `score` (0-100), `rank`, `score_breakdown` (`{faktor: {value, weight, contribution, explanation}}`),
`rationale`, `evidence_level` (`A|B|C|D`), `assumptions`, `uncertainties`,
`offer_check` (`{status: not_offered|optional|standard|unknown, note, option_code}`), `effort` (`S|M|L`),
`status` (`proposed|challenged|approved|rejected`), `version`.

**Signal:** `id`, `kind` (`complaint|unmet_need|delight|competitor_advantage|trend`), `category`, `title`,
`summary`, `evidence_ids`, `mention_count`, `source_types`, `conflicts_with`.

**Evidence:** `id`, `source_type` (`feedback|study|sales|option_list|web`), `source_name`, `text`, `url`,
`retrieved_at`, `polarity` (-1/0/1), `meta`.

**AuditEvent:** `seq`, `ts`, `event_type`, `scenario_id`, `requirement_id`, `actor` (`{type: ai|human|system, name}`),
`rationale`, `payload` (bei Änderungen `{feld: {before, after}}`), `prev_hash`, `hash`.
