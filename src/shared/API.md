# API contract

Local base URL: `http://localhost:8000`. Interactive docs with every field: **`/docs`**.
Data model in code: `src/backend/core/models.py` and `core/model_parts.py`. A full example bundle:
`beispiele/bundle_G60-US.json` (synthetic quotes).

**Rule: the frontend computes nothing.** Every number, label and sentence comes ready from the backend.
**A real example response for every endpoint** is in `beispiele/views/<name>.json`
(generated with `python scripts/make_view_examples.py`, so it always matches the code).

> Some enum values are internal German keys (`Chance`, `reich`, `einzeln`, `Lücke: nicht angeboten` ...).
> They are stable identifiers. The cockpit translates them for display in
> `src/frontend/src/components/insights/labels.ts`. They are listed below with their meaning.

## Read: views (pre-computed)

| Method + path | View | Example |
|---|---|---|
| `GET /health` | Status: `version`, `demo_mode`, `scenarios` | `views/health.json` |
| `GET /api/scenarios` | Scenario picker: scenario + `data_coverage`, `badge` (`reich` = rich / `dünn` = thin / `Kaltstart` = cold start), `headline_numbers`, `warnings` | `views/scenarios.json` |
| `GET /api/scenarios/{id}/overview` | Start page: `funnel`, `top3`, `level_distribution` (A-D), `warnings`, `source_mix`, `generated_at` | `views/overview.json` |
| `GET /api/requirements/{req_id}/explain` | Detail page: `waterfall` (factor, weight, contribution, sentence; last step = evidence discount), `quotes` (top 5 with country / drivetrain / source), `segments`, `conflicts`, `assumptions`, `offer_check`, `web_sources` (by trust), `study`, `robustness` + `robustness_sentence`, `business`, `history` | `views/explain.json` |
| `POST /api/scenarios/{id}/whatif` | Live preview for weight sliders, **saves nothing**: `[{id, title, old_rank, new_rank, rank_change, old_score, new_score}]` | `views/whatif.json` |
| `GET /api/portfolio` | Matrix category × scenario: `rows[].cells[scenario]` (rank, level), `rows[].class` (`plattformweit` = platform-wide / `modellspezifisch` = model-specific / `marktspezifisch` = market-specific / `einzeln` = single / `gemischt` = mixed / `nicht oben` = not near the top), `rule` | `views/portfolio.json` |
| `GET /api/benchmarks` | `quality[]` per scenario: `funnel`, `metrics[]` (`key`, `value` in %, `target`, `ok`, `explain`); `market[]` US only: `range[]` (EPA km, kWh/100 km, rank), `range_gap_km`, `complaints[]` (NHTSA), `limits` | none |
| `GET /api/compare?a=G60-US&b=G60-EU` | Market comparison: same category side by side, `rank_diff`, dissatisfaction, `sentence` | `views/compare.json` |
| `GET /api/scenarios/{id}/opportunities` | Opportunity map: `points[]` with `importance`, `dissatisfaction`, `quadrant` (`Chance` = opportunity / `Stärke halten` = keep strength / `Beobachten` = watch / `Nebensache` = minor), `thresholds` | `views/opportunities.json` |
| `GET /api/scenarios/{id}/trends` | Trend radar: `rings` (today, successor year), `items[]` (`kind`: `trend` or `bet`) | `views/trends.json` |
| `GET /api/scenarios/{id}/gaps` | "What we do not know": `weak_requirements` (C/D with `why`, `next_study`), `missing_sources`, `share_weak` | `views/gaps.json` |
| `GET /api/scenarios/{id}/evidence?signal=&segment=engine:BEV&q=&page=1&size=20` | Evidence browser, filtered and paged: `{total, page, size, items}` | `views/evidence.json` |
| `GET /api/audit/timeline?scenario_id=&requirement_id=` | Audit trail as sentences: `sentence`, `actor`, `rationale` | `views/audit_timeline.json` |
| `GET /api/scenarios/{id}/matrix` | Matrix today/future × evidence: `items[req_id]` with `horizon`, `evidence_level`, `quadrant` (`Sicher & dringend` = safe and urgent / `Belegte Zukunftswette` = evidenced future bet / `Schwach belegt, heute` = weak, today / `Annahme – beobachten` = assumption, watch), `offer_gap` + `offer_gap_label` (`Lücke: nicht angeboten` = gap, not offered / `nur optional` = optional only / `Serie` = standard) | `views/matrix.json` |
| `GET /api/requirements/{req_id}/counterparts` | Same requirement in other scenarios: per scenario `match` (`id`, `rank`, `score`) or `null` + `sentence`. Rule: same category and title Jaccard ≥ 0.3 | `views/counterparts.json` |
| `GET /api/scenarios/{id}/memo` | Decision memo as **Markdown** (text/plain): approved requirements (otherwise top 5 as draft), score, level, evidence, assumptions, line "audit trail valid, N events" | none |

## Prompt lens: `POST /api/scenarios/{id}/lens`

```json
{"question": "Families in the US, focus on charging and space", "actor": "pm.demo"}
```

Response: `{question, interpretation, source ("ai"|"rules"), weights, filters: {categories, only_gaps}, note, top: [{requirement, lens_score, lens_rank, reasons: [{factor, contribution, sentence}]}]}` (example `views/lens.json`).
The AI only returns weights and filters, never IDs. Python computes the top 5 on copies; **the store is not changed**.
Writes `AI_LENS_SUGGESTED` to the audit trail. "Apply weights" = `PUT /weights` with the `weights` from the response
and the question as `rationale`. Errors: `404` unknown scenario, `422` empty question.

## Assistant: `POST /api/ask`

```json
{"question": "What matters most for families?", "actor": "pm.demo"}
```

Response: `{question, source ("ai"|"rules"), interpretation, answer, top: [{scenario_id, requirement_id, title, rank, score, lens_score, evidence_level, signal_ids, evidence_ids, reasons}]}` (example `views/ask.json`).
Interprets the question **once** (lens, one LLM call) and applies it to **all** scenarios (top 2 each, at most 6).
Only IDs from the store, nothing is saved (no audit entry, because nothing is proposed). Errors: `422` empty question.

## Read: raw data

| Method + path | Response |
|---|---|
| `GET /api/scenarios/{id}/funnel` | `{"evidence": 3610, "signals": 58, "requirements": 19, "approved": 0}` |
| `GET /api/scenarios/{id}/signals` | `[Signal]` |
| `GET /api/scenarios/{id}/requirements` | `[Requirement]` sorted by `rank` |
| `GET /api/requirements/{req_id}` | `{"requirement", "signals", "evidence", "history"}` |
| `GET /api/scenarios/{id}/product-context` | Reference from the option list: `source`, `reference_market` (Germany), `currency` (EUR), `min_eur`, `max_eur`, `pages`, `engines`, `note`. Gross list prices incl. 19 % VAT, without delivery. Missing prices stay `null`. Not a US/CN price and not a cost estimate for the successor. Changes neither scores nor the audit trail |
| `GET /api/audit?scenario_id=&requirement_id=` | `[AuditEvent]` in order |
| `GET /api/audit/verify` | `{"valid": true, "broken_at_seq": null, "checked": 12}` |
| `GET /api/scenarios/{id}/export?format=csv\|json\|md` | CSV (`;`), JSON list, or a Markdown spec with criteria, evidence, assumptions and uncertainties |

## Write (every action creates an audit event, a reason is required)

### `POST /api/requirements/{req_id}/decision`

```json
{"action": "approve", "actor": "pm.demo", "rationale": "Feedback and study agree"}
{"action": "reject", "actor": "pm.demo", "rationale": "Too few mentions, revisit next year"}
{"action": "edit", "actor": "pm.demo", "rationale": "Sharpened the criterion",
 "changes": {"acceptance_criterion": "Volume and temperature blind in one move", "effort": "S"}}
{"action": "challenge", "actor": "pm.demo", "rationale": "Double check",
 "question": "Is this just a habit of older customers?"}
```

Editable: `title, description, acceptance_criterion, effort, assumptions, uncertainties`.
Response: `{"requirement": Requirement, "ai_answer": null | {"answer", "supporting_evidence_ids", "counter_evidence_ids", "suggested_change"}}`.
Errors: `404` unknown ID, `422` empty reason or wrong fields.

### `PUT /api/scenarios/{id}/weights` (the "Apply" button)

```json
{"weights": {"future_relevance": 0.3, "customer_pain": 0.2}, "actor": "pm.demo",
 "rationale": "Successor launches 2030, the future counts more"}
```

Factors: `customer_pain, reach, satisfaction_gap, competitive_pressure, future_relevance, effort_inverse`.
Missing factors keep their default; everything is normalized to sum 1. Response: re-ranked `[Requirement]`.
`POST /whatif` takes the same `weights` object (without `actor` / `rationale`) and saves nothing.

## Key fields

**Requirement:** `id`, `title`, `description`, `acceptance_criterion`, `category`, `signal_ids`, `score` (0-100), `rank`,
`score_breakdown` (`{factor: {value, weight, contribution, explanation}}`), `rationale`, `evidence_level` (`A|B|C|D`),
`assumptions`, `uncertainties`, `offer_check`, `effort` (`S|M|L`), `status`, `version`,
`horizon` (`today|next_gen`), `robustness` (`{rank_min, rank_max, top3_share, runs}` or null),
`segment_conflicts` (`[{dimension, segment_a, segment_b, statement, a_count, b_count, evidence_ids}]`),
`business` (`{volume_2025, volume_2030, growth_pct, market_share, note}` or null; null values = "not available"),
`stable_key`, `badges` (short labels such as `robust`, conflict, future bet, assumption).

**Outlook** (default `null`): `Requirement.outlook` is computed by rules on load and also returned in
`GET /api/requirements/{id}/explain`. Fields: `direction` (`grows|stays|fades`), `successor_year`,
`rule` (`category_trend|bev_shift|ice_shift|no_shift`), `assumption: true`, `sentence`,
`critical_count`, `scenario_feedback_count`, BEV/ICE shares (0-1), `evidence_ids`, `signal_ids`,
`baseline_source` (`scenario_feedback|bundle_sample`).
Rule order: a web trend in the same category → `grows`; otherwise at least ten unique negative feedback quotes and a
BEV share ≥ 1.5 × the scenario share → `grows`; otherwise at least ten such quotes, ICE share ≥ 90 % and scenario ICE share
< 90 % → `fades`; otherwise `stays`. The outlook never changes `horizon`, `future_relevance`, score or rank.

**Signal (finding):** `id`, `kind`, `category`, `title`, `summary`, `evidence_ids`, `mention_count`, `source_types`, `conflicts_with`,
`segments` (`{"engine": {"BEV": 42, "ICE": 18}, "country": {...}, "source": {...}, "feedback_type": {...}}`),
`study_link` (`{attribute, importance, dissatisfaction}` or null).

**Scenario:** `id`, `derivative`, `model_name`, `market`, `countries`, `competitors`, `successor_horizon`,
`data_coverage` (`{feedback, study, sales, options, web, external, badge}`), `warnings`.

**Evidence:** `id`, `source_type` (`feedback|study|sales|option_list|web|external_stat|feedback_external`), `source_name`,
`text`, `url`, `retrieved_at`, `polarity` (-1/0/1), `meta` (keys include `engine`, `country`, `source_letter`, `feedback_type`, `trust`, `publisher`).

**AuditEvent:** `seq`, `ts`, `event_type`, `scenario_id`, `requirement_id`, `actor` (`{type: ai|human|system, name}`),
`rationale`, `payload`, `prev_hash`, `hash`.
