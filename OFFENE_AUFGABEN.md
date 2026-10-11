# Offene Aufgaben

## R · Jury-KI-Review: Kern-Code sichtbar machen (Selbstreview So 07:30)

> Status: **Entscheidung offen** (Piyush). Simulierte EHL-Note heute **6,3/10**, mit R1-R4 ca. **7,5**.
> Warum: Die Review liest nur 200.000 Zeichen, kleinste Dateien zuerst. Scoring, Audit-Hash-Kette,
> `llm.py` und Routen sieht sie nie, sie muss dem README glauben. Prüfen: `python scripts/ehl_budget.py`.

| ID | Aufgabe | Datei | Zeit | Status |
|---|---|---|---|---|
| R0 | `data/cache/`, `data/external_cache/`, `data/processed/` als `export-ignore` (fraßen ~60-80 % des Budgets). Gemessen: `src/` 21,8 % → 62 %, ungelesene Dateien 332 → 140 | `.gitattributes` | 5 min | erledigt (`4eea655`) |
| R1 | README-Abschnitt „Key code“: 4-5 Original-Snippets mit `datei:zeile` (Score-Formel `scoring.py`, Hash-Kette `audit.py`, ID-Filter `derive.py:73`, Demo-Cache `llm.py`). Größte Wirkung, weil das README immer ganz gelesen wird. | `README.md` | 20 min | offen |
| R2 | Weitere große Daten ausschließen: `data/demo_cache/`, `src/shared/beispiele/`, große Fixtures in `tests/pfad_c/`; 2-3 kleine Tests sichtbar lassen | `.gitattributes` | 5 min | offen |
| R3 | README widerspricht Repo: „Cache nicht im Git“ stimmt nicht; dazu 1 Satz, dass wir die BMW-Daten im Repo nutzen dürfen (sonst Datenschutz-Kritik) | `README.md`, `data/README.md` | 10 min | offen |
| R4 | Nach 08:00 **nicht** mehr: `pipeline.py`/`store.py` unter 200 Zeilen teilen, Root-`package.json` für Next.js-Erkennung | — | — | verworfen (Risiko > Gewinn) |

---

Aktueller technischer Abgleich: [docs/REPO_CHECK.md](docs/REPO_CHECK.md). A1 ist im Backend und den
sechs Snapshots ergänzt und getestet; die vollständige Browserprüfung bleibt offen. A2 bleibt eine
Produktentscheidung. A3 benötigt weiterhin menschliche Labels (G60-US: 0 von 50).

> Stand: So 11.10.2026, 07:10. Angelegt nach dem Abgleich mit dem BMW-Brief (`docs/CHALLENGE.md`).
> Status: **Entscheidung offen.** Das Team (Piyush) entscheidet später. Ein Agent arbeitet eine Aufgabe nur ab,
> wenn sie hier auf `freigegeben` steht. Nach dem Abarbeiten: Status auf `erledigt` setzen, Commit-Hash eintragen.

Regeln für jeden Agenten: Test zuerst, kein LLM-Aufruf nötig, Ränge und Scores dürfen sich **nicht** ändern,
danach `ruff check src/backend tests`, `python -m pytest -q`, `cd src/frontend && npm run lint && npm run build`.
Ab So 10:30 (Code-Freeze) nur noch Fixes aus `docs/ABGABE.md`.

---

## A1 · Segment-Konflikte fertigstellen (Markt/Antrieb/Quelle)

**Status:** offen, wird vermutlich schon von einer anderen Session gebaut (Stand 07:00, noch nicht committet).

**Warum:** Der Brief verlangt ausdrücklich *„a clear understanding of uncertainty and conflicting evidence“*.
Heute zeigen wir nur Lob gegen Kritik (`Signal.conflicts_with`). `Requirement.segment_conflicts` ist in allen
`data/processed/*/requirements.json` **leer**, z. B. „BEV-Fahrer kritisieren, ICE-Fahrer loben“ gibt es nicht.

**Was schon existiert (im Arbeitsordner, uncommitted):**
- `src/backend/evidence_internal/conflicts.py` → `segment_conflicts(signals, evidence, groups)`:
  Dimensionen `engine`, `country`, `source`, mindestens 10 Kommentare je Segment (`MIN_MENTIONS`), gegensätzliche
  Mehrheiten, plus `study_vs_feedback` (Studie zufrieden, Feedback kritisch).
- Eingehängt in `src/backend/pipeline.py` (Stufe `signals` schreibt `context.json["segment_conflicts"]`)
  und `src/backend/requirements_engine/derive.py` (übernimmt sie in `Requirement.segment_conflicts`).
- Anzeige gibt es schon: `core/views.py explain()` → `conflicts`, Frontend `RequirementDetailView.tsx`,
  Filter „Conflicting evidence“ in `cockpit/RequirementFilters.tsx`.

**Schritte für den Agenten:**
1. Erst fragen bzw. `git status` + `git log` prüfen: Hat die andere Session das inzwischen committet? Dann nur Schritt 4.
2. Falls nicht: **nicht neu bauen**, sondern die vorhandene Funktion mit Tests absichern
   (`tests/pfad_a/test_conflicts.py`): ein Fall mit Konflikt (BEV 12× negativ, ICE 12× positiv), ein Fall unter
   10 Nennungen (kein Konflikt), ein Fall mit gleicher Mehrheit (kein Konflikt).
3. Daten neu erzeugen **ohne Ränge zu ändern**: prüfen, ob `--stage signals`/`--stage requirements` LLM braucht.
   Wenn ja: Konflikte lieber beim Laden nachrechnen (siehe A2, gleiche Stelle in `core/store.py`), statt die
   Pipeline neu laufen zu lassen.
4. Prüfen: `python -c` über `data/processed/G60-US/requirements.json` → mindestens 1 Anforderung mit
   `segment_conflicts`. Live: `GET /api/requirements/<id>/explain` → `conflicts` enthält `dimension: "engine"`.
5. Text auf Englisch (UI ist Englisch). Satz in `docs/pitch/RECHERCHE.md` §4 ergänzen.

**Fertig, wenn:** G60-US zeigt mindestens einen Antriebs-Konflikt in der Detailseite, Tests grün.

---

## A2 · Ausblick 2030 je Anforderung (3–5 Jahre vorausdenken)

**Status:** offen, Entscheidung „bauen oder in der Fragerunde als nächsten Schritt nennen“ steht aus.

**Warum:** Der Brief sagt *„Think three to five years ahead“*. Bei G60-US betreffen 18 von 19 Anforderungen
`horizon: "today"`. Der Score-Faktor `future_relevance` steht fast überall auf 0,1 („no trend behind it“), weil
`requirements_engine/factors.py::_future_relevance` nur zählt, wenn eine Anforderung einen Web-Trend **direkt**
zitiert. G60-US hat nur 2 Trend-Befunde (`web_signals.json`: `interior`, `driver_assistance`).
**Die Formel nicht ändern** (Pfad C, würde kurz vor dem Pitch die Ränge verschieben).

**Idee (deterministisch, ohne LLM):** neue Datei `src/backend/core/outlook.py`, Funktion
`outlook(req, linked_signals, evidence_by_id, web_signals, successor_year) -> dict`:

| Ausblick | Regel | Begründungssatz (Englisch, als Annahme markiert) |
|---|---|---|
| `grows` | Web-Trend (`kind == "trend"`) in **derselben Kategorie** wie die Anforderung | „A 2028-2031 trend in <category> (web source) makes this more important by <Jahr>. Assumption.“ |
| `grows` | BEV-Anteil der kritischen Kommentare (`polarity == -1`, `meta.engine` in `BEV`/`BEVE`) ≥ 1,5 × BEV-Anteil aller Feedback-Kommentare im Szenario, mind. 10 kritische Kommentare | „<x> % of critical comments come from BEV drivers (scenario average <y> %). The successor will be more electric, so this grows. Assumption.“ |
| `fades` | ICE-Anteil der kritischen Kommentare ≥ 90 % und ICE-Anteil gesamt < 90 % | „Criticism comes almost only from combustion drivers; it shrinks as the line electrifies. Assumption.“ |
| `stays` | sonst | „No trend or segment shift found; expected to stay as relevant as today.“ |

Zahlen aus den Daten (Stand 07:00): G60-US Feedback ICE 2017 · BEVE 1271 · PHEV 322; G70-US ICE 2435 · BEVE 1075
· PHEV 282; F70-EU nur ICE (dort greift nur die Trend-Regel). Das Jahr kommt aus `scenario.successor_horizon`.

**Schritte für den Agenten:**
1. Test zuerst: `tests/pfad_b/test_outlook.py` mit je einem Fall pro Zeile der Tabelle + „unter 10 Kommentaren → stays“.
2. `core/outlook.py` schreiben (< 80 Zeilen, Kommentare mit WARUM).
3. Einhängen **erst, wenn A1 committet ist** (sonst Konflikt mit der parallelen Session in denselben Dateien):
   - `core/models.py`: `Requirement.outlook: dict | None = None` (oder kleines Modell in `model_parts.py`).
   - `core/store.py ScenarioState.__init__`: nach dem Laden `req.outlook = outlook(...)` für jede Anforderung.
   - `core/views.py explain()`: Feld `outlook` mitgeben.
   - `core/insights.py` (Trendradar `/trends`): Anforderungen mit `grows` als `kind: "outlook"` in den Ring
     `successor_horizon` legen, damit das Radar nicht fast leer ist.
   - Frontend (Pfad D, mit Lasse absprechen): `src/frontend/src/lib/api.ts` Typ erweitern, in
     `RequirementDetailView.tsx` eine Zeile „Outlook <Jahr>: grows/stays/fades“ + Satz, als Annahme gekennzeichnet.
   - `src/shared/API.md` + `docs/ARCHITEKTUR.md` (Entscheidung: „Ausblick regelbasiert statt im Score, weil sich
     sonst Ränge verschieben; verworfen: LLM-Schätzung, weil nicht nachprüfbar“).
4. Prüfen: G60-US hat mindestens eine Anforderung mit `grows`, Rang 5 Reichweite (BEV-lastig) sollte `grows` sein.
   Ränge vorher/nachher identisch (`GET /api/scenarios/G60-US/requirements` vergleichen).

**Fertig, wenn:** Detailseite zeigt den Ausblick, Trendradar hat Einträge, Tests grün, Ränge unverändert.

**Falls gestrichen:** Satz für die Fragerunde in `docs/pitch/PITCH.md`: „Heute stützen wir uns vor allem auf
heutiges Feedback; die Trend-Verknüpfung über die Kategorie ist unser nächster Schritt. F70-EU zeigt schon 4
Nachfolger-Anforderungen.“

---

## A3 · Befund-Treue von Hand labeln

**Status:** offen, braucht einen **Menschen** (z. B. Aditya), ca. 15 Minuten.

**Warum:** Einzige fehlende Kernzahl im Eval (`tests/eval/REPORT.md`: Befund-Treue n/a, 0 von 50 gelabelt).
Bewusst nicht per KI, sonst prüft die KI sich selbst.

**Schritte:** `python tests/eval/make_sample.py G60-US` (erzeugt `data/eval/G60-US_sample.csv`, falls noch nicht da),
letzte Spalte `passt` mit `j`/`n` füllen, dann `python tests/eval/run_eval.py G60-US`. Die CSV bleibt lokal
(BMW-Zitate), nur `REPORT.md` wird committet. Zahl in `docs/pitch/RECHERCHE.md` §4 eintragen.

---

## Erledigt

- Eval-Grounding zählt Web-Befunde mit (vorher fälschlich 89,8 %, jetzt 100 %) · `7525ee6`
- Konflikt-„!“ im Cockpit nur, wenn beide Seiten zitiert sind (gleiche Regel wie Detailseite) · `7525ee6`
- Demo-Konflikt gefunden: G60-US Rang 5 Reichweite, 38 gegen 28 Nennungen · `docs/pitch/RECHERCHE.md`
