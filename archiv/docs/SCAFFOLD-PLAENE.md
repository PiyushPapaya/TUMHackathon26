# Scaffold-Pläne für die 9 Ideen-Hypothesen

> Bauplan pro Idee aus [SPONSOREN.md](SPONSOREN.md). **Kein Code vor dem Event.** Wird vom Skill `challenge-intake` genutzt.
> Gemeinsamer Rahmen für alle: `src/backend/main.py` (FastAPI, `/health`), `src/backend/llm.py` (OpenAI-Aufruf + Cache), `src/backend/<logik>.py`, `src/frontend/src/app/page.tsx`, `src/shared/API.md` + `beispiele/`, `tests/test_eval.py`, `demo/beispiele/`, `demo/cache/`.
> OpenAI-Baustein-Kürzel: **RS** = Responses API + Structured Outputs (Pydantic-Schema), **EMB** = Embeddings, **VIS** = Bild/PDF als Eingabe.

## BMW

| | B1 Erklärbares Routing | B2 Qualitäts-Agent Produktion | B3 Werkstatt-Diagnose |
|---|---|---|---|
| Backend-Dateien | `graph.py` (Abschnitte + Scores), `route.py` (Dijkstra mit Gewichten), `erklaerung.py` | `cluster.py`, `ursachen.py` | `symptome.py`, `regeln.py` |
| Endpunkte | `POST /route {start, ziel, profil}` → `{abschnitte[], fun_score, rote_flaggen_km, begruendung[]}` | `POST /analyse {berichte[]}` → `{cluster[{ursache, anteil, belege[]}]}` | `POST /diagnose {beschwerde, fehlercodes[]}` → `{diagnosen[{name, sicherheit, teile[]}]}` |
| Datenmodell | `Abschnitt{id, laenge, kurven, belag, fun, flaggen[]}` | `Bericht{id, text, datum}` → `Cluster{id, ursache, berichte[]}` | `Symptom{text, code}` → `Diagnose{name, regel_id}` |
| OpenAI | RS nur für die Begründung in Worten; Score rechnet Python | EMB fürs Clustering, RS für die Cluster-Zusammenfassung | RS für die Symptom-Extraktion |
| Die Zahl | −X % Rote-Flaggen-km bei +Y % Fun vs. schnellste Route (N Fahrten) | Top-3-Trefferquote der Ursache (N gelabelte Fälle) | richtige Diagnose in X/N Testfällen |
| Demo in 5 Klicks | Start wählen → Ziel → „Route“ → Abschnitt antippen → Begründung | Datei hochladen → „Analysieren“ → Top-Cluster → Belege → Export | Beschwerde einfügen → Codes → „Diagnose“ → Teile → Erklärung |

## Atira

| | A1 Anfrage → Angebot | A2 Lastenheft-Prüfer | A3 Konfigurator |
|---|---|---|---|
| Backend-Dateien | `extrahieren.py`, `katalog.py` (Abgleich), `angebot.py` | `anforderungen.py`, `pruefen.py` | `constraints.py` (Regeln), `solver.py`, `uebersetzen.py` |
| Endpunkte | `POST /anfrage (PDF)` → `{anforderungen[], treffer[], offene_punkte[], angebot_entwurf}` | `POST /pruefung {lastenheft, datenblatt}` → `{ergebnisse[{anforderung, status, zitat, seite}]}` | `POST /konfiguration {wunsch}` → `{gueltig, konfiguration, verletzt[], alternativen[]}` |
| Datenmodell | `Anforderung{id, text, wert, einheit, muss}` → `Treffer{produkt, erfuellt, grund}` | `Ergebnis{status: erfuellt/nicht/unklar, zitat}` | `Regel{wenn, dann}`, `Konfiguration{optionen{}}` |
| OpenAI | RS + VIS (PDF), EMB für den Katalog-Abgleich | RS mit Pflichtfeld `zitat`; Python prüft, ob das Zitat im Original steht | RS: Wunsch → Constraints-JSON; Gültigkeit prüft der Solver |
| Die Zahl | Extraktions-F1 auf N gelabelten Anforderungen; Minuten pro Anfrage | X % korrekt klassifiziert, 100 % mit echter Belegstelle | 0 ungültige Konfigurationen in N Wünschen (LLM allein: X %) |
| Demo in 5 Klicks | PDF hochladen → Anforderungen → Treffer → offene Punkte → Angebot | 2 Dateien → „Prüfen“ → rote Zeile → Zitat → Export | Wunsch tippen → „Konfigurieren“ → Verstoß → Alternative → Übernehmen |

## tacto

| | T1 Angebotsvergleich | T2 Should-Cost | T3 Verhandlungs-Copilot |
|---|---|---|---|
| Backend-Dateien | `angebote.py` (Extraktion), `normalisieren.py` (Gesamtkosten), `ranking.py` | `teil.py`, `kostenmodell.py`, `indizes.py` | `kontext.py`, `leitfaden.py` |
| Endpunkte | `POST /vergleich (PDFs)` → `{angebote[{lieferant, gesamtkosten, posten[]}], empfehlung, begruendung}` | `POST /should-cost {teil}` → `{aufschluesselung{material, maschine, arbeit, marge}, abweichung_zum_angebot}` | `POST /leitfaden {lieferant, angebot}` → `{zielpreis, argumente[], fragen[]}` |
| Datenmodell | `Angebot{lieferant, staffel[{menge, preis}], incoterm, zahlungsziel}` | `Teil{material, gewicht, prozess, stueckzahl}` | `Argument{text, beleg}` |
| OpenAI | RS + VIS für PDFs; Rechnen in Python (deterministisch) | RS: Beschreibung → `Teil`; Kosten rechnet Python aus Indizes | RS mit Belegen |
| Die Zahl | Feld-Genauigkeit X % (N Angebote); 2 h → 3 min | MAPE X % gegen echte Preise (N Teile) | schwer messbar → nur wählen, wenn tacto Testdaten gibt |
| Demo in 5 Klicks | 3 PDFs hochladen → „Vergleichen“ → Matrix → Empfehlung → Detail Staffel | Teil eingeben → „Schätzen“ → Aufschlüsselung → Angebot daneben → Abweichung | Lieferant wählen → „Vorbereiten“ → Zielpreis → Argumente → Export |

## Gemeinsam für jede Idee

- **Vertrag zuerst:** Endpunkt-Zeilen oben 1:1 nach `src/shared/API.md`, Beispiel-Responses nach `src/shared/beispiele/`.
- **Demo-Modus:** `DEMO_MODUS=true` → `llm.py` liefert Antworten aus `demo/cache/` (siehe `demo/README.md`).
- **Evaluation:** `tests/test_eval.py` vergleicht gegen `tests/data/*.json` und gibt Zahl + Baseline aus.
