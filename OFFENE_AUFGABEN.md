# Offene Aufgaben

## Offene Punkte nach Priorität

> ✅ **Stand So 11.10., 08:35: Alle P2-Punkte sind fertig.** Dennis' Auftrag (die letzten drei P2: Audit-Ursprung,
> Reviewer-Budget, Betriebsmodell) ist abgeschlossen und gepusht (`69c084d`, `16fda4e`, `cd2b3f2`, `1cb9a65`).
> Von P1 sind noch zwei Punkte offen: dünne Szenarien und vollständige Neuerzeugung.

Die folgenden Punkte sind offen und aus dem [technischen Abgleich](docs/REPO_CHECK.md#offene-punkte-nach-priorität) übernommen. Die älteren Detailaufgaben darunter enthalten frühere Arbeitsstände; sie sind zusammen mit dem aktuellen Abgleich zu lesen.

| Priorität | Punkt | Konsequenz / konkreter Abschluss |
|---|---|---|
| P1 | ~~Menschliche Evaluation fehlt~~ **erledigt** | 50 von 50 G60-US-Paaren gelabelt, Befund-Treue **88 %** (`tests/eval/REPORT.md`). Zwei Durchläufe: KI-Vorschlag, von Aditya geprüft und bestätigt; KI-Vorlabel von Lasse (`26c00ce`), von Lasse alle 50 Zeilen geprüft und bestätigt, ebenfalls 88 %. Nächster Schritt, falls Zeit: blindes Zweitlabel durch einen Menschen. |
| P1 | Dünne Szenarien und unvollständiger Zukunftshorizont | Piyush/Dennis recherchieren belastbare marktbezogene Wettbewerber-/Trendquellen und erzeugen neue Anforderungen; bis dahin F70-EU/G60-US als Hauptdemo, andere als Datenlücken-/Kaltstartbeweis einordnen. |
| P1 | Vollständige Neuerzeugung nicht bestätigt | Alle sechs Szenarien mit aktuellem Code/Prompts in einen getrennten Ausgabeordner erzeugen, Cache-Fails und Quellen prüfen, Bundle-/API-/Eval-Prüfung wiederholen. Alte PM-Verläufe behalten; für neue Bundles separate Audit-DB verwenden. |
| ~~P1~~ ✅ | Vollständiger Browser-Flow fehlt | **Erledigt 11.10. (`8bb2826`):** `scripts/verify_browser.cjs` hat alle sechs Szenarien inkl. Replay nach Neustart ohne Fehler durchlaufen (Offline-Demomodus, Details `docs/VERIFIKATION_P1_P2.md`). Ursprüngliche Aufgabe: Auf freigegebenem laufendem Frontend Modellwechsel, Belege, Challenge, Edit, Gewichte, Exporte und Neustart prüfen. Start des separaten Frontend-Testservers wurde automatisch abgelehnt, ohne spezifische Begründung. Build/API-Tests ersetzen diesen Schritt nicht. |
| ~~P2~~ ✅ | Stabile Identität bei neuen Quellen | **Erledigt 11.10. (`8bb2826`):** `core/identity.py` + `scripts/migrate_signal_ids.py`, Test `tests/test_identity_migration.py`. Ursprüngliche Aufgabe: Signal-IDs künftig aus semantischen Gruppenschlüsseln ableiten und bestehende IDs kontrolliert migrieren. Legacy-Audit ohne Fingerabdruck kann bisherige Quelldatenidentität nicht belegen und meldet eine Warnung. |
| ~~P2~~ ✅ | Chancenkarte und Akzeptanzkriterien | **Erledigt 11.10. (`8bb2826`):** Proxy-Achse erklärt, G60-EU-Kriterien mit Prüfprotokollen; echte Kundenvalidierung bleibt Sache des PM. Ursprüngliche Aufgabe: Proxy-Wichtigkeit ehrlich erklären. G60-EU hat nur 60 % Kriterien mit Ziffer; relative Kriterien benötigen definierte Baseline/Stichprobe. Die Ziffern-Heuristik beweist generell keine fachlich sinnvolle Messbarkeit. |
| ~~P2~~ ✅ | Vollständigkeit des Audit-Ursprungs | **Erledigt 11.10. (`16fda4e`) für neue Läufe:** `pipeline.py` schreibt `provenance` (Modell, Hash der Prompt-Dateien, Git-Commit, `core/provenance.py`) ins Bundle; der Store übernimmt sie in `PIPELINE_LOADED` und `SIGNALS_EXTRACTED`. Grenze: Modell = Stand bei der Bündelung. Die heutigen sechs Bundles sind älter und zeigen weiter ehrlich „not recorded in snapshot“; nachträglich wird nichts geraten. Prüfen: `tests/test_pipeline.py`. |
| ~~P2~~ ✅ | Reviewer-Budget | **Erledigt 11.10. (`cd2b3f2`, R1-R3 in `7a7f5ef`).** Messung `python scripts/ehl_budget.py` auf HEAD nach R1-R3: Budget voll, `src/` **59,3 %** (vor R0: 21,8 %), Doku 14,2 % (README mit Key-Code-Abschnitt), 124 Dateien ungelesen; Backend 25 Dateien (~37k Zeichen), Frontend ~80k, Tests ~53k. **Demo-Datenstrategie geprüft:** `git archive HEAD` entpackt und gestartet: lädt nur das Beispiel-Bundle G60-US (5 Anforderungen), Audit-Kette gültig. Die echte Demo läuft aus dem Git-Klon (alle 6 Szenarien in `data/processed/`). |
| ~~P2~~ ✅ | Betriebsmodell | **Erledigt 11.10. (`69c084d`):** Ein API-Prozess pro Audit-DB wird jetzt erzwungen (`core/single_process.py`, OS-Sperre auf `<audit.db>.lock`, Linux/Mac/Windows). Ein zweiter Prozess bricht beim Start mit klarer Meldung ab, statt still veraltete RAM-Stände zu zeigen. Live geprüft mit zwei uvicorn-Prozessen. Mehrere Worker bleiben bewusst nicht unterstützt (nächster Schritt: gemeinsamer Store statt RAM). Prüfen: `tests/pfad_b/test_single_process.py`. |

## Weitere offene Teamaufgaben – in dieser Reihenfolge

Alle fünf Aufgaben sind offen. Die Reihenfolge ist die gewünschte Arbeitsreihenfolge des Teams; die technischen Prioritäten oben bleiben bestehen.

| Reihenfolge | Aufgabe | Konkreter Abschluss | Status |
|---|---|---|---|
| 1 | Alle lesen die Projektzusammenfassung und verstehen das Projekt sehr gut | Das gesamte Team liest [START_HIER.md](START_HIER.md) und [docs/01_projekt.md](docs/01_projekt.md). Jede Person kann Problem, Zielgruppe, Datenfluss, Nutzen, menschliche Entscheidungen und aktuelle Grenzen in eigenen Worten erklären; Verständnisfragen sind gemeinsam geklärt. | offen |
| 2 | Pitch-Slides sehr gut gestalten | Eine klare Story mit Problem, Lösung, Demo, belegbaren Ergebnissen und Grenzen ausarbeiten. Die Slides visuell hochwertig und konsistent gestalten; Aussagen mit dem tatsächlichen Projektstand abgleichen. Grundlage: [Pitch](docs/pitch/PITCH.md). | offen |
| 3 | Gesamte Codebase aufräumen | Dateien und Ordner verständlicher organisieren, Benennung und Lesbarkeit verbessern sowie hilfreiche Kommentare zu Zweck und Entscheidungen ergänzen. Referenzen, Imports und Dokumentation anpassen; bestehende Funktionalität durch passende Checks absichern. | offen |
| 4 | Repository visuell und inhaltlich verbessern | README, Beschreibungen und Navigation überarbeiten; passende Bilder, Screenshots und Diagramme ergänzen. Einstieg, Projektidee, Architektur und Demo sollen für neue Leser schnell verständlich sein. | **README erledigt (So 09:15):** echter Cockpit-Screenshot (`visuals/app/cockpit.png`), Datenfluss-Bild, Quickstart in 3 Befehlen, toter Link in `START_HIER.md` repariert. Offen: Rollen-Diagramm KI vs. Mensch. |
| 5 | Pitches üben | Den vollständigen Pitch einschließlich Demo mehrfach gemeinsam proben, Zeit messen, Übergänge und Rollen abstimmen sowie Juryfragen und einen Demo-Ausfall üben. Feedback in Vortrag und Slides einarbeiten. | offen |

### Agenten-Auftrag zu T1–T5 (Stand So 08:52)

Zeitrahmen (`docs/ZEITPLAN.md`): Feature-Freeze war 08:00 · **10:00 Pitch-Probe** · **10:30 Code-Freeze** ·
11:30 abgegeben (Deadline 12:00). Antworten an das Team immer auf Deutsch und einfach. Nach jedem fertigen Schritt:
Status in der Tabelle oben auf `erledigt` + Commit-Hash, dann Skill `sync`.

**T1 · Projekt verstehen** (Mensch lernt, Agent hilft, ca. 20 min pro Person)
- Lesen, in dieser Reihenfolge: `START_HIER.md` → `docs/01_projekt.md` → `PROJEKT_ERKLAERT.html` (im Browser öffnen)
  → `docs/ARCHITEKTUR.md` (nur Datenfluss + Entscheidungen) → `docs/pitch/JURY-FAQ.md`.
- Agent fragt die Person danach ab, eine Frage nach der anderen, und korrigiert falsche Antworten mit `datei:zeile`:
  Welches Problem hat der BMW-PM? · Was passiert von Excel bis Anforderung (Belege → Befunde → Anforderungen)? ·
  Woher kommt der Score (6 Faktoren, Python statt LLM)? · Was heißt Evidenzstufe A–D? · Was darf der PM
  (approve/reject/edit/challenge, Gewichte) und wo steht das im Prüfpfad? · Was ist ein Konflikt (Lob gegen Kritik,
  Segment-Konflikt)? · Was ist der Ausblick 2030 und warum ist er eine Annahme? · Welche Zahlen sind belegt
  (`tests/eval/REPORT.md`: Grounding 100 %, Befund-Treue 88 %)? · Welche Grenzen sagen wir offen (dünne Szenarien)?
- **Fertig, wenn** jede Person (Piyush, Aditya, Dennis, Lasse) alle Fragen ohne Nachlesen beantwortet. Offene
  Verständnisfragen als Zeile in `docs/pitch/JURY-FAQ.md` ergänzen.

**T2 · Pitch-Slides sehr gut gestalten** (bis 10:00 Probe)
- Grundlage: `docs/pitch/PITCH.md` (Ablauf 3:00 + 3:00 Fragen), `docs/pitch/RECHERCHE.md` (Gewinner-Muster, Zahlen,
  Demo-Konflikt Rang 5 Reichweite 38 gegen 28), BMW-Brief `docs/CHALLENGE.md`.
- Aufbau: 4 Vortragsfolien (Problem mit Zitat + Zahl · Lösung in einem Satz · Demo · Ergebnis-Zahlen + eine Grenze)
  plus Anhang, der **ohne Sprecher** verständlich ist (Workflow KI vs. Mensch, Score-Formel, Architektur, Eval,
  Grenzen, Prüfpfad, Skalierung über 6 Szenarien).
- Brief-Wörter müssen sichtbar vorkommen: *trustworthy sources, transparent reasoning, thoughtful prioritization,
  uncertainty and conflicting evidence, PM firmly in control, scale across vehicle lines and markets*.
- Erstellen über das Artifact-Werkzeug (`action: "quickstart"`, `intent: "slides"`); BMW-Logo und BMW-Branding
  **nicht** nachbauen. Bilder aus `visuals/` und Screenshots der laufenden App (`scripts/make_visuals.py`).
- Jede Zahl auf einer Folie mit Quelle prüfen (Code, `tests/eval/REPORT.md` oder `data/processed/*.json`), keine
  gemessene Zeitersparnis behaupten. Export als PDF nach `outputs/`.
- **Fertig, wenn** das Deck vorliegt, jede Zahl belegt ist und Piyush es freigegeben hat.

**T3 · Codebase aufräumen** (Achtung: Code-Freeze 10:30, danach nur Fixes aus `docs/ABGABE.md`)
- Nur **verhaltensneutrale** Änderungen: Kommentare mit WARUM, klarere Namen in privaten Funktionen, tote Dateien
  ins `archiv/` (nie löschen), Docstrings. **Keine** Umzüge von Modulen, keine Signatur-Änderungen an
  Pfad-Schnittstellen, nichts an Score, Rängen, Prompts oder `data/processed/`. R4 (Dateien teilen) bleibt verworfen.
- Vorgehen: Skill `simplify` bzw. Subagent `code-simplifier` je Ordner, Ownership beachten (CLAUDE.md-Tabelle):
  `src/backend/core|api` Piyush, `evidence_internal` Aditya, `requirements_engine` Dennis, `src/frontend` Lasse.
  Kandidaten zuerst suchen: Dateien > 200 Zeilen, ungenutzte Exporte (`entire graph` / `brain_dead_code`),
  Kommentare auf Deutsch/Englisch gemischt in derselben Datei, `TODO`/`FIXME`.
- Nach **jedem** Ordner: `ruff check src/backend tests` · `python -m pytest -q` · `cd src/frontend && npm run lint &&
  npm run build` · `python scripts/ehl_budget.py` (src-Anteil darf nicht sinken). Rot → Änderung zurücknehmen.
- **Fertig, wenn** bis 10:15 alles grün gepusht ist. Was nicht fertig ist, bleibt liegen (Umfang kürzen, nicht Zeit).

**T4 · Repository visuell verbessern** (Doku darf auch nach 10:30, solange kein Code berührt wird)
- `README.md`: oben ein Satz Nutzen + ein Screenshot des Cockpits, dann Quickstart (3 Befehle), Architektur-Bild,
  Abschnitt „Key code“ bleibt (R1). Bilder nach `visuals/` (Skripte `scripts/make_diagrams.py`,
  `scripts/make_visuals.py`), im README relativ verlinken, mit Alt-Text.
- Diagramme: Datenfluss Excel → Belege → Befunde → Anforderungen → PM-Entscheidung → Prüfpfad; Rollen KI vs. Mensch.
- `docs/README.md` als Inhaltsverzeichnis prüfen, tote Links reparieren (`grep -o "](.*\.md)"` gegen vorhandene Dateien).
- Achtung Budget der Jury-KI: große Bilder/Dokus nicht in `src/`; neue Doku-Ordner in `.gitattributes` als
  `export-ignore` nur nach Rückfrage bei Piyush (geteilte Datei). Danach `python scripts/ehl_budget.py`.
- **Fertig, wenn** ein Fremder im README in 60 Sekunden versteht, was Signal2Spec tut, und es starten kann.

**T5 · Pitch üben** (10:00 Probe, danach bis 11:15 wiederholen)
- Skill `pitch-prep`: Probe mit Stoppuhr (Ziel 2:50, hart 3:00), danach Jury-Fragen-Drill aus `docs/pitch/JURY-FAQ.md`
  mit klarer Zuständigkeit pro Person. Skill `demo-check` vor jeder Probe (läuft die App bei Fremden, Demo-Modus an).
- Demo-Ablauf (3 Momente): Warum (Wasserfall + Zitat) · Hinterfragen + Freigeben · Gewichte ändern + Prüfpfad.
  Konflikt-Moment: G60-US Rang 5 Reichweite. Demo-Ausfall üben: Backup-Video abspielen ohne Pause.
- Nach jeder Probe: zu lange Stellen kürzen in `docs/pitch/PITCH.md`, Änderungen in die Slides (T2) übernehmen.
- **Fertig, wenn** 3 Proben hintereinander unter 3:00 liefen und jede Person ihre Jury-Fragen sicher beantwortet.

---

Aktueller technischer Abgleich: [docs/REPO_CHECK.md](docs/REPO_CHECK.md). A1 ist im Backend und den
sechs Snapshots ergänzt und getestet; die vollständige Browserprüfung bleibt offen. A2 ist auf
direkten Nutzerauftrag implementiert (regelbasierter Ausblick außerhalb des Scores).
A3 ist erledigt (G60-US 88 %; KI-Vorschlag, von Aditya geprüft; reines KI-Label von Lasse ebenfalls 88 %).

> Stand: So 11.10.2026, 07:10. Angelegt nach dem Abgleich mit dem BMW-Brief (`docs/CHALLENGE.md`).
> Status: **Entscheidung offen.** Das Team (Piyush) entscheidet später. Ein Agent arbeitet eine Aufgabe nur ab,
> wenn sie hier auf `freigegeben` steht. Nach dem Abarbeiten: Status auf `erledigt` setzen, Commit-Hash eintragen.

Regeln für jeden Agenten: Test zuerst, kein LLM-Aufruf nötig, Ränge und Scores dürfen sich **nicht** ändern,
danach `ruff check src/backend tests`, `python -m pytest -q`, `cd src/frontend && npm run lint && npm run build`.
Ab So 10:30 (Code-Freeze) nur noch Fixes aus `docs/ABGABE.md`.

---

## A1 · Segment-Konflikte fertigstellen (Markt/Antrieb/Quelle)

**Status:** erledigt 11.10. Backend und sechs Snapshots ergänzt; Detailseite zeigt „Where customer groups disagree“ (`7cffbca`).

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

**Status:** erledigt auf direkten Nutzerauftrag. Ausblick in API, Detailseite und Trendradar integriert;
Verifikation: [docs/VERIFIKATION_A2.md](docs/VERIFIKATION_A2.md). Commit über `git log -- src/backend/core/outlook.py`.

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

**Status:** erledigt (So 08:30): 44 von 50 = 88 %. Claude schlug vor, Aditya prüfte und bestätigte. Lasses Durchlauf (`26c00ce`, KI-Vorlabel, von Lasse alle 50 Zeilen geprüft) kam ebenfalls auf 88 %. Offen als nächster Schritt: blindes Zweitlabel durch einen Menschen.

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
- A1 Segment-Konflikte auf der Detailseite · `7cffbca`
- A3 Befund-Treue G60-US 88 %, zwei von Menschen geprüfte KI-Vorlabel (Aditya, Lasse) · `26c00ce`
- Browser-Flow aller sechs Szenarien, stabile Signal-IDs, Prüfprotokolle für Kriterien · `8bb2826`
- R1-R3 README-Key-Code, export-ignore, Daten-Doku · `7a7f5ef`
- P2 Betriebsmodell: nur ein API-Prozess pro `audit.db` (Dateisperre) · `69c084d`
- P2 Audit-Ursprung: Modell, Prompt-Hash und Commit im Bundle und Prüfpfad · `16fda4e`
- P2 Reviewer-Budget gemessen, Abgabe-Archiv gestartet und geprüft · `cd2b3f2`

---

## R · Jury-KI-Review: Kern-Code sichtbar machen (Selbstreview So 07:30)

> Status: **FERTIG (R0-R3 erledigt 11.10.)** (`4eea655`, `7a7f5ef`), R4 verworfen. Simulierte EHL-Note heute **6,3/10**, mit R1-R4 ca. **7,5**.
> Warum: Die Review liest nur 200.000 Zeichen, kleinste Dateien zuerst. Scoring, Audit-Hash-Kette,
> `llm.py` und Routen sieht sie nie, sie muss dem README glauben. Prüfen: `python scripts/ehl_budget.py`.

| ID | Aufgabe | Datei | Zeit | Status |
|---|---|---|---|---|
| R0 | `data/cache/`, `data/external_cache/`, `data/processed/` als `export-ignore` (fraßen ~60-80 % des Budgets). Gemessen: `src/` 21,8 % → 62 %, ungelesene Dateien 332 → 140 | `.gitattributes` | 5 min | erledigt (`4eea655`) |
| R1 | README-Abschnitt „Key code“: 4-5 Original-Snippets mit `datei:zeile` (Score-Formel `scoring.py`, Hash-Kette `audit.py`, ID-Filter `derive.py:73`, Demo-Cache `llm.py`). Größte Wirkung, weil das README immer ganz gelesen wird. | `README.md` | 20 min | erledigt (`7a7f5ef`) |
| R2 | Weitere große Daten ausschließen: `data/demo_cache/`, `src/shared/beispiele/`, große Fixtures in `tests/pfad_c/`; 2-3 kleine Tests sichtbar lassen | `.gitattributes` | 5 min | erledigt (`7a7f5ef`) |
| R3 | README widerspricht Repo: „Cache nicht im Git“ stimmt nicht; dazu 1 Satz, dass wir die BMW-Daten im Repo nutzen dürfen (sonst Datenschutz-Kritik) | `README.md`, `data/README.md` | 10 min | erledigt (`7a7f5ef`) |
| R4 | Nach 08:00 **nicht** mehr: `pipeline.py`/`store.py` unter 200 Zeilen teilen, Root-`package.json` für Next.js-Erkennung | — | — | verworfen (Risiko > Gewinn) |

Umsetzung: R1 = Abschnitt „Key code“ in `README.md` (5 Snippets mit `datei:zeile`). R2 = `.gitattributes` (`data/demo_cache/`, `src/shared/beispiele/views/`, `tests/pfad_c/scope_cases.py`, `SCOPE_REPORT.md`); `bundle_G60-US.json` bleibt absichtlich sichtbar, weil es das Fallback-Beispiel der App ist. R3 = Datenschutz-Satz in `README.md`, `data/README.md` (Cache liegt doch im Git, per `export-ignore` nicht im Zipball), `docs/CHALLENGE.md`.
