# Signal2Spec Welle 2: Schnell-Umsetzungsplan

> **So benutzt du diesen Plan:** Such deinen Namen. Arbeite die Karten **von oben nach unten** ab. Pro Karte kopierst du den Prompt in deine Claude-Session, Claude schreibt zuerst den Test und dann den Code, du führst den Fertig-Befehl aus und rufst danach `sync` auf. Eine Karte dauert 20–45 Minuten. Hängst du 45 Minuten an einer Karte: Karte überspringen und Piyush Bescheid geben.
>
> **Kartennamen beginnen mit `W-`** (Welle 2), damit sie nicht mit den alten Tickets A0–A11, C0–C11, L0–L16 in `docs/pfade/` verwechselt werden.
>
> **Ziel bis So 07:30:** 6 Szenarien, Backend liefert alles fertig gerechnet → Frontend zeigt nur an. Danach nur noch Pitch.

---

## 0. In 60 Sekunden

- **Problem:** Unser Produkt läuft, aber die Jury sieht keine **Annahmen** (0× Stufe D), keine **Unsicherheit**, flache **Konflikte**, nur **3 Szenarien** ohne Vergleich, und der Pitch nennt eine falsche #1.
- **Lösung:** 6 Szenarien (neu: G60-EU, G70-EU, G68-CN als „Kaltstart ohne Kommentare“), Segmente (BEV/ICE, Land), Robustheit der Reihenfolge, Zukunftswetten mit Stufe D, zweite Kundenquelle NHTSA, Portfolio-Vergleich, und fertige View-Endpunkte für das Frontend.
- **Siegformel:** Für jedes Wort im BMW-Brief zeigen wir einen sichtbaren Beweis (Tabelle in Anhang B).

---

## 1. Startreihenfolge (wer wartet auf wen)

```
Piyush  W-P0 Verträge (bis 21:45) ──┬──► L-Karten
Aditya  W-A1 (braucht W-P0 nicht) ────┼──► ab W-A2 mit W-P0-Feldern
Dennis  W-C1 (braucht W-P0 nicht) ────┘──► ab W-C2 mit W-P0-Feldern
Lasse   baut ab 21:45 gegen src/shared/API.md + Beispiel-JSONs
```
Wer auf W-P0 wartet, macht zuerst seine Karte 1, die W-P0 nicht braucht.

**Vor jeder Karte:** `git pull --no-rebase origin main` · **Nach jeder Karte:** Fertig-Befehl → `ruff check src/backend tests` → `python -m pytest -q` → Skill `sync`.

---

## 2. Piyush (Lead + Pfad B)

### W-P0 · Verträge + Configs · 21:00–21:45 · **blockiert alle, zuerst**
Dateien: `src/backend/core/models.py`, `src/shared/API.md`, `src/shared/beispiele/bundle_G60-US.json`, `config/scenarios/*.json`, `config/datasets.json`
```
Ticket W-P0. Erweitere den Vertrag nur ADDITIV mit Defaults, damit alte Bundles, Tests und das Frontend nicht brechen.
1) core/models.py:
   Signal.segments: dict[str, dict[str,int]] = {}   (Schlüssel engine, country, source, feedback_type)
   Signal.study_link: dict | None = None
   Requirement.horizon: Literal["today","next_gen"] = "today"
   (Requirement.assumptions und .uncertainties gibt es schon, nicht neu anlegen)
   Requirement.robustness: dict | None = None        ({rank_min, rank_max, top3_share})
   Requirement.segment_conflicts: list[dict] = []
   Requirement.business: dict = {}                   ({volume_2030, growth_pct, market_share})
   Requirement.badges: list[str] = []
   Scenario.data_coverage: dict = {}; Scenario.warnings: list[str] = []
2) Neue Configs G60-EU, G70-EU, G68-CN nach Muster config/scenarios/F70-EU.json.
   Studienspalten aus Blatt CN_EU_2025: "EU G60", "EU G70", "China G68" (exakte Spaltennamen im Excel prüfen).
   Sales: G60_G68/EU, G70/EU, G60_G68/CN. G68-CN: feedback_file=null, option_list_file=null.
   CN-Wettbewerber: NIO ET7, Li Auto L9, BYD Han, Mercedes E-Klasse L.
3) F70-EU: countries nur auf Länder kürzen, die es im Excel gibt (GB, SE, FR, DK, FI).
4) config/datasets.json: heutige Sheet- und Spaltennamen als Profil (Feedback_Explorer, Spalten, sales-Spalten).
5) Beispiel-Bundle um die neuen Felder mit realistischen Beispielwerten ergänzen; API.md um alle Endpunkte aus Abschnitt 6 dieses Plans (Signatur + Beispiel-JSON).
Warum: Alle Pfade und das Frontend brauchen den Vertrag zuerst. Verworfen: Felder als Pflicht (bricht alte Bundles).
Prüfen: pytest grün, pipeline läuft für G60-US mit DEMO_MODUS=true.
```
Fertig: `python -m pytest -q` grün · `python src/backend/pipeline.py --scenario G60-US --stage bundle` läuft · Lasse hat `API.md` bekommen.

### W-P0b · Erste Abgabe · 21:45–22:00
Skill `abgabe` mit dem heutigen Stand. Danach gilt: nach jedem großen Schritt „Update Submission“.

### W-L1 · LLM robust · 22:00–22:30
Datei: `src/backend/core/llm.py`, `tests/test_llm.py`
```
Ticket W-L1. Mach ask_json() robust: Timeout (60 s), 2 Retries mit kurzer Pause, klare Fehlermeldung wenn output_parsed None ist, Cache atomar schreiben (tmp-Datei + os.replace).
WICHTIG: Den Cache-Schlüssel NICHT ändern, sonst ist data/demo_cache wertlos.
Warum: Nachtlauf über 6 Szenarien darf nicht an einem Netz-Wackler sterben. Verworfen: neues Paket (tenacity), unnötig.
Tests: Retry nach einer Exception klappt; None → RuntimeError mit Text; Cache-Datei ist nach Schreibfehler nicht halb geschrieben.
```
Fertig: `python -m pytest tests/test_llm.py -q`

### W-L2 · Pipeline „all“ + Fehler pro Schritt · 22:30–23:15
Dateien: `src/backend/pipeline.py`, `src/backend/evidence_external/claims.py`, `tests/test_pipeline.py`
```
Ticket W-L2. pipeline.py: --scenario all läuft alle Configs aus config/scenarios/ nacheinander; ein Fehler in einem Szenario stoppt nicht die anderen; am Ende Tabelle: Szenario | Belege | Signale | Anforderungen | Fehler.
claims.py: try/except pro Frage, fehlgeschlagene Frage = Warnung, Rest läuft weiter.
Warum: Ein kaputter Web-Aufruf hat bisher die ganze Stufe abgebrochen. Prüfen: Test mit gemocktem ask_json, das bei Frage 2 wirft.
```
Fertig: `python -m pytest tests/test_pipeline.py tests/pfad_b -q`

### W-L3 · Entscheidungen überleben Neustart · 23:15–23:45
Dateien: `src/backend/core/store.py`, `tests/test_api.py`
```
Ticket W-L3. Store.load_all(): nach dem Laden der Bundles die Audit-Events REQUIREMENT_DECIDED und WEIGHTS_CHANGED pro Szenario in Reihenfolge erneut anwenden (ohne neue Events zu schreiben). Unbekannte requirement_id: überspringen + Warnung.
Warum: Heute verliert der PM nach einem Server-Neustart alle Entscheidungen, mitten in der Demo tödlich.
Test: decide() → neuer Store mit derselben audit.db → Status und Gewichte sind wieder da.
```
Fertig: `python -m pytest tests/test_api.py -q`

### W-L4 · View-Endpunkte fürs Frontend · 23:45–01:30
Dateien (neu): `src/backend/core/views.py`, `src/backend/core/portfolio.py`, `src/backend/api/views.py`; `main.py` Router einhängen
```
Ticket W-L4. Baue die View-Endpunkte aus Abschnitt 6 dieses Plans: overview, requirements/{id}/explain, whatif, portfolio, compare, evidence (Filter + Seiten), gaps, export?format=json|md. Logik in core/, Routen in api/views.py (routes.py bleibt < 200 Zeilen).
Regel: Das Frontend rechnet nichts. Jede Zahl, jeder Satz, jede Diagramm-Reihe kommt fertig.
whatif nutzt requirements_engine.whatif (Dennis, W-C4) und speichert NICHTS.
Portfolio: Kategorie × Szenario mit Rang + Stufe; Klasse plattformweit (Top 10 in ≥3 Szenarien) / marktspezifisch / modellspezifisch.
Warum: BMW fragt nach Skalierung über Baureihen und Märkte; das Frontend soll nur anzeigen. Verworfen: Logik im Frontend (doppelt, ungetestet).
Tests: pro Endpunkt 1 Test gegen Beispiel-Bundle; whatif ändert audit nicht.
```
Fertig: `python -m pytest tests/test_views.py -q`

### W-L5 · Web-Fragen aus Config · 01:30–02:00
Datei: `src/backend/evidence_external/questions.py` (L67, L76)
```
Ticket W-L5. Trendfenster aus successor_horizon der Config statt fest "2028-2031"/"2025/2026". Bei Szenarien ohne Feedback (G68-CN) bis zu 8 Trendfragen statt 5.
Test: Horizont 2031 steht im Fragetext; G68-CN-Config ergibt 8 Trendfragen.
```

### W-L6 · NHTSA als zweite Kundenquelle · 02:00–03:00
Datei (neu): `src/backend/evidence_external/nhtsa.py`, `tests/pfad_b/test_nhtsa.py`
```
Ticket W-L6. Lies US-Kundenbeschwerden aus https://api.nhtsa.gov/complaints/complaintsByVehicle?make=BMW&model=<Modell>&modelYear=<Jahr> (kostenlos, kein Key, Behördendaten).
Modelle/Jahre in der Config (z. B. G60: "530I","I5" 2024–2025; G70: "740I","I7" 2023–2025; Modellnamen vorher im API-Browser prüfen).
Antwort cachen in data/external_cache/nhtsa_<model>_<jahr>.json (für Demo committen). Jede Beschwerde = Evidence mit SourceType feedback (Herkunft "NHTSA"), Text wörtlich, Komponente als Thema.
Nur US-Szenarien. Nur httpx/requests, wenn schon in requirements.txt, sonst urllib aus der Standardbibliothek.
Warum: Zweite, unabhängige Kundenquelle → Evidenzstufen werden ehrlich begründbar. Verworfen: Reddit (Key, Lizenz unklar).
Test: gespeicherte Beispielantwort → richtige Anzahl Evidence, keine Netzanfrage im Test.
```
Fertig: `python -m pytest tests/pfad_b/test_nhtsa.py -q`

### W-L7 · Nachtlauf · 04:00–06:00 (im Hintergrund, Aditya schaut drauf)
```
python src/backend/pipeline.py --scenario all --stage all
```
Danach: `python scripts/check_bundles.py` (W-L8) · alle genutzten Cache-Dateien nach `data/demo_cache/` kopieren · committen · Skill `demo-check` auf frischem Clone mit `DEMO_MODUS=true`.

### W-L8 · Bundle-Prüfer · 03:00–03:30
Datei (neu): `scripts/check_bundles.py`
```
Ticket W-L8. Prüft data/processed/*.json und meldet rot/grün:
G60-US ≥15 Anforderungen; insgesamt ≥1× Stufe D; jede D hat assumptions; jede Anforderung hat robustness; G68-CN hat data_coverage.feedback==0 und >0 Anforderungen; alle zitierten IDs existieren; IDs stabil gegenüber letztem Lauf (falls vorhanden).
```

### W-L9 · Doku · 06:00–07:30
`docs/ARCHITEKTUR.md` (neue Komponenten, `/studio` raus) · `data/README.md` (Rohdaten SIND committet, warum) · README „Neues Auto in 2 Schritten“ · Tickets in `docs/pfade/*.md` + `docs/ROADMAP.md` · diesen Plan als `docs/UPGRADE_WELLE2.md`.

**Kann (nur wenn Zeit):** W-L10 fueleconomy.gov-Connector (`https://www.fueleconomy.gov/ws/rest/...`, kein Key) · W-L11 `POST /ask` (Antwort nur mit Beleg-IDs, Demo nur Cache) · W-L12 `scripts/new_scenario.py` (G70-CN in 5 Minuten als Pitch-Beweis).

---

## 3. Aditya (Pfad A: `src/backend/evidence_internal/`, `tests/pfad_a/`, `tests/eval/`)

### W-A1 · Datensatz-Profil · 21:00–21:45 · braucht W-P0 nicht
```
Ticket W-A1. Ersetze harte Namen durch ein Profil-Dict mit den heutigen Werten als Default: feedback.py SHEET (L21) + Spaltennamen, context.py SALES_FILE (L19), study.py Sheet-Präfixe (L33, L145-149). Wenn config/datasets.json existiert, Werte daraus lesen.
Warum: Ein neuer BMW-Datensatz mit anderen Spalten braucht dann nur einen Profil-Eintrag, keinen Code. Verworfen: automatische Spaltenerkennung (fehleranfällig).
Test: synthetische Mini-Excel mit umbenannten Spalten + passendem Profil wird korrekt gelesen.
```
Fertig: `python -m pytest tests/pfad_a -q`

### W-A2 · Ohne Feedback laufen + alle Studienspalten · 22:00–23:00
```
Ticket W-A2. load_all_evidence() und extract_signals() laufen, wenn feedback_file null ist (G68-CN): dann nur Studien-Signale, keine Exception.
study.py liest aus CN_EU_2025 auch "China G68", "China G70", "EU G60", "EU G70" (Spalte aus Config).
Warum: Kaltstart-Szenario G68-CN ist unser Wow-Moment: "Ohne Kundenstimmen sagen wir das, statt zu raten."
Test: Mini-Szenario ohne Feedback → >0 Signale aus Studie.
```

### W-A3 · Segmente pro Signal · 23:00–00:00
```
Ticket W-A3. Neue Datei segments.py (signals.py hat schon 195 Zeilen): pro Signal Zählung nach Engine Type (ICE/BEVE/PHEV), Country, Source (A-D), Feedback Type → Signal.segments. In extract_signals() einhängen.
Warum: G60 hat 1.763 BEV-Kommentare, G70 1.347 – heute ungenutzt. BEV-Bedürfnisse = Zukunftssignal.
Test: Mini-Daten mit 3 BEV + 2 ICE → segments["engine"] == {"BEVE":3,"ICE":2}.
```

### W-A4 · Unbekannte Themen sichtbar · 00:00–00:30
```
Ticket W-A4. taxonomy.py: Themen, die nicht in der Karte stehen, zählen; Warnung auf stderr und context.json["unmapped_topics"] = {thema: anzahl}.
Warum: Ein neuer Datensatz verliert sonst lautlos Kommentare.
Test: unbekanntes Thema erscheint mit Anzahl.
```

### W-A5 · Sales sauber · 00:30–01:15
```
Ticket W-A5. context.py: Wachstum 2024→2025→2030 in %, Anteil des Szenario-Markts am Modell 2030. Formelzelle (F70 CN "=-D3-C10") nicht als 0 lesen: Wert ausrechnen oder "n/a" + Warnung.
Test: Mini-Excel mit Formelzelle → nie 0.
```

### W-A6 · Chancen-Karte (Studie) · 03:30–04:30
```
Ticket W-A6. Neue Datei opportunities.py: aus US_2025 pro Attribut Wichtigkeit und Unzufriedenheit → Quadranten "Chance" (wichtig + unzufrieden), "halten", "überdimensioniert", "egal", mit fertigem Satz pro Punkt. Rein rechnerisch.
Test: 4 Mini-Attribute landen in 4 Quadranten.
```

### W-A7 · Segment-Konflikte · 04:30–05:30 (S)
```
Ticket W-A7. conflicts.py: Thema ist in Segment X überwiegend Kritik und in Y überwiegend Lob, je ≥10 Nennungen (Engine, Country). Zusätzlich: Studie sagt zufrieden, Kommentare sagen unzufrieden. Ergebnis als Konflikt mit Satz.
Test: konstruierter BEV-vs-ICE-Konflikt wird gefunden; unter 10 Nennungen nicht.
```

### W-A8 · Eval fertig (mit Dennis) · 06:00–07:00 · **nie streichen**
50 Stichproben von Hand labeln (je 25) → `python tests/eval/run_eval.py` für alle 6 Szenarien → neuer `tests/eval/REPORT.md` mit Kopfzahl für die Trust-Folie.

**Kann:** W-A9 „Wants“-Kommentare als eigene, stärkere Signal-Art.

---

## 4. Dennis (Pfad C: `src/backend/requirements_engine/`, `tests/pfad_c/`)

### W-C1 · Stabile IDs · 21:00–21:45 · braucht W-P0 nicht
```
Ticket W-C1. derive.py L122: REQ-<sid>-nnn kommt heute aus der LLM-Reihenfolge. Neu: REQ-<sid>-<6 Zeichen sha1 aus sortierten signal_ids>.
Warum: Bei jedem Re-Run würden sonst Audit-Einträge und PM-Entscheidungen auf falsche Anforderungen zeigen. Verworfen: ID aus dem Titel (LLM formuliert jedes Mal anders).
Test: gleiche Drafts in vertauschter Reihenfolge → gleiche IDs.
```
Fertig: `python -m pytest tests/pfad_c -q`

### W-C2 · Robustheit · 22:00–23:00 · **nie streichen**
```
Ticket W-C2. Neue Datei robustness.py: 500 zufällige Gewichtungen (jedes Gewicht ±30 %, normalisiert, random.Random(42)), pro Anforderung rank_min, rank_max, top3_share → Requirement.robustness. Nur Standardbibliothek.
Warum: BMW will "understanding of uncertainty". Satz für den Pitch: "Die #1 bleibt in X % aller plausiblen Gewichtungen vorne."
Test: gleiche Eingabe → gleiches Ergebnis; klar dominante Anforderung hat top3_share 1.0.
```

### W-C3 · Zukunftswetten mit Stufe D · 23:00–00:30 · **nie streichen**
```
Ticket W-C3. derive.py: zusätzlich 2-4 Anforderungen mit horizon="next_gen" aus Trend-Websignalen und Marktwachstum 2030; jede mit assumptions (Pflicht).
evidence_level.classify() (L35): überwiegend Trend-Web + wenige Kundennennungen → D. D ohne assumptions → Draft verwerfen.
Warum: Heute 0× D – die Jury sieht keine Annahmen, obwohl der Brief genau das verlangt.
Test: next_gen-Draft ohne assumptions wird verworfen; mit → Stufe D.
```

### W-C4 · What-if · 00:30–01:00
```
Ticket W-C4. Baut auf scoring.score_without() (C10, schon fertig) auf. Neue Datei whatif.py: reine Funktion whatif(requirements, weights) → neue Reihenfolge + Rangänderung pro Anforderung (+2 / -1). Speichert nichts.
Test: höheres Gewicht auf reach hebt die Anforderung mit größter Reichweite.
```

### W-C5 · 15–25 Anforderungen · 01:00–02:00
```
Ticket W-C5. derive_all() (L100): statt einem Prompt über alle ~55 Signale ein Prompt pro Kategorie-Block (z. B. 3 Blöcke); Duplikate zusammenführen, wenn signal_ids zu ≥50 % überlappen.
Ziel G60-US ≥15. Cache wird für neue Prompts neu befüllt (Nachtlauf).
Test: zwei überlappende Drafts → eine Anforderung.
```

### W-C6 · Business-Faktor · 02:00–03:00
```
Ticket W-C6. factors.py: Reach gewichtet mit Volumen 2030 des Markts, future_relevance nutzt Wachstum 2025→2030 aus context.json. Jeder Faktor-Satz nennt seine Zahl. Requirement.business füllen.
Warum: BMW-Folie trennt Customer und Business; heute nur Reach.
Test: Faktor-Text enthält die Zahl; höheres Wachstum → höhere future_relevance.
```

### W-C7 · Keine stillen Fehler + ohne Optionsliste · 03:00–03:30
```
Ticket W-C7. derive.py L141 (_load_offer: except Exception: return []) → konkrete Ausnahme fangen, Warnung ausgeben. Ohne option_list_file (G68-CN): offer_check liefert "keine Optionsliste vorhanden" statt Fehler.
Test: G68-CN-Fall läuft durch, Warnung im Ergebnis.
```

### W-C8 · Eval mit Aditya · 06:00–07:00 (siehe W-A8)

**Soll/Kann danach:** W-C9 Segment-Konflikte an Anforderungen (Stufe −1 mit Satz) · W-C10 Preis aus Optionsliste im Offer-Check · W-C11 Markdown-Lastenheft-Export (User Story, Akzeptanzkriterien, Belege, Annahmen) · W-C12 Scope-Filter mit Test beweisen.

---

## 5. Lasse (Pfad D, nicht Teil dieses Plans)
Ab 21:45 gegen `src/shared/API.md` + Beispiel-JSONs bauen. Das Backend liefert die Ansichten: Szenario-Wähler, Overview, Tabelle, Detail mit Wasserfall, Regler mit Live-Vorschau (`whatif`), Portfolio-Matrix, Chancen-Karte, „Was wir nicht wissen“, Audit, Export. Rechnen muss das Frontend nichts. Ab So 08:00 Backup-Video.

---

## 6. Endpunkte, die das Frontend nur anzeigen muss (Vertrag für W-P0 und W-L4)

| Endpunkt | Liefert fertig |
|---|---|
| `GET /api/scenarios` | + `data_coverage`, Badge „reich/dünn/Kaltstart“ |
| `GET /api/scenarios/{id}/overview` | Funnel, Top 3, Stufen-Verteilung A–D, Quellen-Mix, Warnungen |
| `GET /api/scenarios/{id}/requirements` | + `robustness`, `horizon`, `assumptions`, `segment_conflicts`, `badges` |
| `GET /api/requirements/{id}/explain` | Wasserfall-Schritte mit Satz und Zahl, Top-5-Zitate (Quelle, Land, Antrieb), Segment-Balken, Konflikte, Annahmen, Optionsstatus, Webquellen nach Vertrauen, Rang-Spanne |
| `POST /api/scenarios/{id}/whatif` | neue Reihenfolge + Rang-Pfeile, speichert nichts |
| `PUT /api/scenarios/{id}/weights` | wie heute (mit Audit) |
| `GET /api/portfolio` | Matrix Kategorie × Szenario, Klasse plattformweit/markt/modell |
| `GET /api/compare?a=&b=` | gleiche Themen nebeneinander |
| `GET /api/scenarios/{id}/opportunities` | Chancen-Karte (Quadranten fertig benannt) |
| `GET /api/scenarios/{id}/gaps` | „Was wir nicht wissen“ + empfohlene nächste Studie |
| `GET /api/scenarios/{id}/evidence?signal=&segment=&q=&page=` | Beleg-Browser |
| `GET /api/scenarios/{id}/export?format=csv\|json\|md` | Export inkl. Lastenheft |
| `GET /api/audit`, `/api/audit/verify` | wie heute |

---

## 7. Zeitplan auf einen Blick

| Zeit | Piyush | Aditya | Dennis |
|---|---|---|---|
| 21:00–22:00 | W-P0, W-P0b Abgabe | W-A1 | W-C1 |
| 22:00–00:00 | W-L1, W-L2, W-L3 | W-A2, W-A3 | W-C2, W-C3 |
| 00:00–02:00 | W-L4 | W-A4, W-A5 | W-C3, W-C4, W-C5 |
| 02:00–03:30 | W-L5, W-L6, W-L8 | Schlaf | W-C6, W-C7 |
| 03:30–06:00 | Schlaf (W-L7 läuft ab 04:00) | W-A6, W-A7, überwacht W-L7 | Schlaf |
| 06:00–07:30 | W-L9, Demo-Cache committen | W-A8 Eval | W-C8 Eval |
| **07:30** | **Backend-Freeze, Zahlen einfrieren** | | |
| 07:30–10:00 | Deck, Pitch, FAQ, Probe 10:00 | Trust-Folie | Priorisierungs-Folie |
| **10:30** | **Code-Freeze, Skill `abgabe`** | | |

**Streichen, wenn es wackelt (in dieser Reihenfolge):** Kann-Karten → W-A7 → G70-EU → W-C6 → W-L6.
**Nie streichen:** W-P0, W-C1, W-L3 (Demo-Stabilität) · W-C2, W-C3 (Unsicherheit) · W-A2 + G68-CN (Kaltstart) · W-L4 (Frontend-Endpunkte) · W-L7 (offline-Demo) · W-A8 (Trust-Zahl).

---

## 8. Pitch (ab 07:30, nur Zahlen aus dem Nachtlauf)

| Zeit | Wer | Inhalt |
|---|---|---|
| 0:00 | Piyush | BMW-Folie „1 Mrd. Findings → 1.000 Anforderungen → ein Auto“; 13.771 Kommentare, 3 Baureihen |
| 0:30 | Piyush | Lösung in einem Satz + Funnel G60-US |
| 0:50 | Lasse klickt | echte #1 → Wasserfall → Zitat → BEV-vs-ICE-Konflikt → Challenge → Freigeben → Regler + Robustheit |
| 2:20 | Dennis | Zukunftswette Stufe D mit Annahme · „Was wir nicht wissen“ |
| 2:50 | Aditya | Trust-Zahl + NHTSA als zweite Quelle |
| 3:10 | Dennis | Portfolio 6 Szenarien · G68-CN-Kaltstart · „neues Auto = 1 Config“ |
| 3:40 | Piyush | KI vs. Mensch · Audit „Kette gültig“ · Schlusssatz |

Deck (9 Folien, `outputs/`): Problem · Lösung · Demo · Unsicherheit · Konflikte · Vertrauen · Skalierung · KI vs. Mensch · Team. `docs/pitch/JURY-FAQ.md` neu mit echten Antworten (Regeln statt LLM? Was ohne Kommentare? Neuer Datensatz? Halluzinationen? NHTSA-Grenzen? Robustheit? Wer entscheidet? Rohdaten im Repo? Kosten/Laufzeit? 3 Monate mehr?). Skill `pitch-prep`.

---

## 9. Verifikation (Ende Phase 1 um 02:00 und vor 07:30)
1. `ruff check src/backend tests` + `python -m pytest -q` grün (Ziel >230 Tests).
2. Frischer Clone, `DEMO_MODUS=true`: `python src/backend/pipeline.py --scenario all --stage all` → 6 Bundles, keine Exception.
3. `python scripts/check_bundles.py` → alles grün.
4. `uvicorn` starten: jeder Endpunkt aus Abschnitt 6 antwortet; Entscheidung → Neustart → noch da; `/api/audit/verify` gültig.
5. Requirements-Stufe zweimal → gleiche IDs.
6. `python scripts/secret_scan.py` sauber · Skill `demo-check` · `cd src/frontend && npm run build` läuft weiter · Skill `selbstreview`.

---

## Anhang A: Was wir gefunden haben (Begründung für die Karten)

| Schwäche | Beleg | Karte |
|---|---|---|
| 0× Stufe D, Annahmen unsichtbar | G60-US nach C8: 4×A, 10×B, 2×C, 0×D | W-C3 |
| Keine Unsicherheit in der Reihenfolge | Score = eine Zahl | W-C2 |
| Konflikte nur Lob vs. Kritik | `conflicts.py` | W-A7 |
| Nur 3 Szenarien, kein Vergleich | `config/scenarios/` | W-P0, W-L4 |
| G60-US hat nach C8 16 Anforderungen, F70-EU/G70-US noch weniger; Ziel 15–25 überall | Bundles, Commit 48561b6 | W-C5 |
| Zukunftshorizont hart codiert | `questions.py` L67, L76 | W-L5 |
| Business nur über Reach | `factors.py` | W-C6 |
| Entscheidungen weg nach Neustart | `store.py` L47 | W-L3 |
| IDs ändern sich bei Re-Run | `derive.py` L122 | W-C1 |
| Ein Web-Fehler stoppt alles | `claims.py` L42 | W-L2 |
| Fehler still verschluckt | `derive.py` L141 | W-C7 |
| `llm.py` ohne Timeout/Retry | `core/llm.py` | W-L1 |
| Unbekannte Themen fallen still raus | `taxonomy.py` | W-A4 |
| Antriebsart ungenutzt (1.763 + 1.347 BEV) | Feedback-Excel | W-A3 |
| China/EU-Studienspalten ungenutzt | `CN_EU_2025` | W-A2 |
| F70-CN Sales ist Formelzelle | `sales_volumes.xlsx` | W-A5 |
| F70-EU nennt Länder ohne Daten | Config | W-P0 |
| Trust-Zahl fehlt (0/50 gelabelt) | `tests/eval/REPORT.md` | W-A8 |
| G60-US-Bundle veraltet (vor den alten Tickets C7/A7) | Zeitstempel 19:12 | W-L7 |
| Pitch-#1 falsch (echt: öffentliches Laden) | Bundle G60-US | Abschnitt 8 |
| Doku veraltet (`/studio`, „gitignored“) | ARCHITEKTUR, data/README | W-L9 |

## Anhang B: Siegformel (jedes BMW-Wort → sichtbarer Beweis)

| BMW will | Wir zeigen |
|---|---|
| trustworthy sources | wörtliche Zitate mit Excel-ID, Vertrauensstufen, NHTSA, Eval-Zahl |
| transparent reasoning | Wasserfall: Faktor × Gewicht, jeder Satz mit Zahl |
| thoughtful prioritization | Kunde + Business (Volumen 2030, Wachstum), What-if |
| uncertainty | Stufe A–D, D nur mit Annahme, Rang-Spanne, „Was wir nicht wissen“ |
| conflicting evidence | BEV vs. ICE, Markt vs. Markt, Studie vs. Kommentare, Web widerspricht |
| PM in control | Freigeben/Ablehnen/Bearbeiten/Challenge, Gewichte, Audit-Kette, bleibt nach Neustart |
| 3–5 Jahre | Zukunftswetten, Wachstum bis 2030, Trendfragen nach Horizont |
| scale across lines/markets | 6 Szenarien, Portfolio, Kaltstart G68-CN, „neues Auto = 1 Config“ |

**Bewusst nicht:** Technik-Specs, Regulierung, Business-Case-Rechnung (schließt BMW aus); keine Anforderung nur aus Web; kein LLM-Score.
