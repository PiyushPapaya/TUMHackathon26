# Masterplan: Signal2Spec (BMW · AI for Product Decision Making)

> Ein Dokument für alle. Lesezeit 10 Minuten. Details pro Pfad: `docs/pfade/`.
> Zeitplan Stunde für Stunde: `docs/ZEITPLAN.md`. Brief wörtlich: `docs/CHALLENGE.md`.

## 1. Die Idee in drei Sätzen

**Signal2Spec** macht aus tausenden Kundenstimmen, Studienwerten, Absatzzahlen und Webquellen
eine priorisierte Liste von Kundenanforderungen für den Nachfolger eines BMW-Modells.
Jede Anforderung zeigt **wie gut sie belegt ist (Evidenzstufe A-D)**, **welche Annahmen sie trägt**
und **wo Belege sich widersprechen**, bis hinunter zum einzelnen Zitat.
Der Produktmanager entscheidet (freigeben, ablehnen, bearbeiten, hinterfragen), und jede
Änderung landet in einem **fälschungssicheren Prüfpfad**.

**Demo-Fall:** BMW 5er (G60) in den USA (3.610 Kommentare, US-Studie mit ~100 Attributen,
BEV + PHEV + Verbrenner). **Zweiter Fall zum Beweis der Übertragbarkeit:** 1er (F70) in Europa.

## 2. Warum wir gewinnen: fünf Unterschiede, jeder mit Brief-Zitat

| # | Was wir zeigen | Brief-Zitat (wörtlich) |
|---|---|---|
| 1 | **Evidenz vs. Annahme sichtbar:** Stufe A-D nach festen Regeln, Annahmen pro Anforderung | "Make clear where your conclusions are based on available evidence and where they rely on forward-looking assumptions." |
| 2 | **Widersprüche werden gezeigt, nicht weggemittelt** (z. B. Display gelobt vs. Touch-Bedienung kritisiert) | "a clear understanding of uncertainty and conflicting evidence" |
| 3 | **"Gibt es das schon?"-Check** gegen die Optionsliste: Manchmal ist die Antwort ein Paket, keine neue Funktion | "variant and package offering" (in scope) |
| 4 | **Prüfpfad mit Hash-Kette** + "Challenge"-Dialog mit Belegen UND Gegenbelegen | "review, challenge, modify, approve, or reject AI-generated proposals" |
| 5 | **Priorisierung als Formel, live einstellbar**; neues Modell/Markt = eine JSON-Datei | "Prioritize them with a logic you define and can explain" · "adaptable to other BMW vehicles and markets" |

Unser Satz für den Pitch: **"Wir sagen nicht nur WAS gebaut werden soll, sondern WIE SICHER wir uns sind und WARUM."**

## 3. Unser Fokus ("Make it yours")

Wir gehen **tief** bei: BMW-Daten integrieren, Evidenz/Annahmen transparent machen, PM-Entscheidung + Prüfpfad.
Wir gehen **gezielt** bei: Webrecherche (Wettbewerb + Trends, nur mit Quelle und Vertrauensstufe).
Wir machen **bewusst nicht**: Engineering-Specs, Regulatorik, Preis-/Business-Case (laut Brief out of scope),
Login/Rollen, Echtzeit-Ingest, eigenes ML-Training.

## 4. Der Workflow (Pflicht-Deliverable): wer macht was?

Spiegelt die BMW-Folie "THE PROCESS" (Situation → Structure → Requirements → Prioritization → Documentation).

| Stufe | Eingang → Ausgang | KI autonom? | Mensch Pflicht? | Pfad |
|---|---|---|---|---|
| 1 Einlesen | Excel/PDF → Belege (`evidence.json`) | Code, kein LLM | nein | A |
| 2 Befunde | Belege → Befunde mit Zitat-IDs | **KI autonom** (Taxonomie + LLM) | nein, aber prüfbar | A |
| 3 Web | Befunde → Web-Belege mit URL, Trend-Annahmen | **KI autonom** (Websuche) | nein, Quellen sichtbar | B |
| 4 Anforderungen | Befunde → Anforderungen + Kriterien + Annahmen | **KI schlägt vor** | **ja: jede Anforderung startet als "proposed"** | C |
| 5 Priorisierung | Faktoren → Score → Rang | **Formel (kein LLM)** | PM darf Gewichte ändern (protokolliert) | C |
| 6 Entscheidung | approve / reject / edit / challenge | KI antwortet auf Challenge | **ja: nur der PM ändert den Status** | Lead + D |
| 7 Dokumentation | jede Änderung → Prüfpfad, Export CSV | automatisch | nein | Lead |

## 5. Die Pfade

Alle vier Pfade arbeiten **ab Minute 1 parallel**, weil jede Stufe eine JSON-Datei schreibt und
jeder Pfad bis zur echten Datei die Beispieldatei aus `src/shared/beispiele/stufen/` nimmt.

| Pfad | Ziel in einem Satz | Ordner (schreibt nur hier + eigene Tests) | Liefert an |
|---|---|---|---|
| **Lead** (Piyush) | Rückgrat, Verträge, Integration, Pitch-Deck, Abgabe | `src/backend/core/`, `api/`, `main.py`, `pipeline.py`, `src/shared/`, `config/`, Root | alle |
| **A · Interne Evidenz + Eval** | BMW-Daten zu sauberen Belegen und Befunden mit Zitat-IDs; die "eine Zahl" für den Pitch | `src/backend/evidence_internal/`, `tests/pfad_a/`, `tests/eval/` | `evidence.json`, `context.json`, `signals.json`, Eval-Report |
| **B · Externe Evidenz** | Wettbewerb/Trends aus dem Web mit Quelle und Vertrauensstufe | `src/backend/evidence_external/`, `tests/pfad_b/` | `web_evidence.json`, `web_signals.json` |
| **C · Anforderungen + Priorisierung** | Befunde zu messbaren Anforderungen, Score, Evidenzstufe, Challenge-Antwort | `src/backend/requirements_engine/`, `tests/pfad_c/` | `requirements.json` |
| **D · PM-Cockpit** | Die Oberfläche, in der der PM alles sieht und entscheidet | `src/frontend/` | Demo |

**Jeder Pfad liefert zusätzlich Inhalt für 1 Pitch-Folie + 1 Demo-Abschnitt** (in der jeweiligen Pfad-Datei).
Die Arbeitsbücher mit fertigen Tickets und Prompts stehen in `docs/pfade/`, die Gesamt-Roadmap in [`ROADMAP.md`](ROADMAP.md).

## 6. Wer macht welchen Pfad (entschieden Sa 14:50, 4 Personen, Fabian ist nicht dabei)

| Pfad | Name | GitHub |
|---|---|---|
| Lead + B | Piyush | @PiyushPapaya |
| A | Aditya | @AdiAvocado |
| C | Dennis | @Di0n-0 |
| D | Lasse | @JoleEight |

Warum B beim Lead: Das Rückgrat steht schon, der Lead hätte bis zum Durchstich sonst Leerlauf. Die Eval-Zahl liegt bei A, weil sie auf seinen Daten beruht.

## 7. Meilensteine (hart; wackelt einer, wird gekürzt, nicht verlängert; Details: `ROADMAP.md` §3)

| Phase | Bis | Ergebnis (prüfbar) |
|---|---|---|
| 0 Start | Sa 15:45 | Pfade verteilt, jeder: venv, `.env`, Entire, Backend läuft lokal mit Beispiel |
| 1 Durchstich | **Sa 18:30** | Pipeline läuft für G60-US mit **echten** Belegen (A) und erster Anforderungsliste (C); UI zeigt Liste + Detail (D); 5 Webbelege mit URL (B) |
| 2 MVP | **Sa 22:00** | Befunde per LLM, Konflikte, Challenge-Antwort, Gewichte-Regler, Prüfpfad-Ansicht; **erste Abgabe auf ehl.gg** |
| 3 Tiefe | So 07:30 | Zweites Szenario F70-EU läuft; Eval-Zahl steht; Triangulation Web ↔ intern; UI-Politur |
| 4 Freeze | **So 08:00** | Feature-Freeze. Danach nur Bugs, Texte, Demo, Deck |
| 5 Abgabe | **So 10:30 / 11:30** | Code-Freeze 10:30, abgegeben 11:30 (Skill `abgabe`) |

## 8. Integrationsregeln

1. **Verträge** sind `src/backend/core/models.py` (Code) und `src/shared/API.md` (für Menschen). Änderung nur durch den Lead.
2. Jede Pfad-Funktion hat eine feste Signatur (steht im Kopf der Datei). **Innen frei, außen fix.**
3. Jede Stufe ist einzeln startbar: `python src/backend/pipeline.py --scenario G60-US --stage signals`.
4. **LLM nur über `core/llm.py`** (Cache + Demo-Modus). Kein eigener OpenAI-Client in den Pfaden.
5. **Jedes LLM-Ergebnis zitiert IDs aus der Eingabe**; Tests prüfen, dass jede zitierte ID existiert (Halluzinationsschutz).
6. **Alle pushen direkt auf main**, automatisch nach jedem getesteten Schritt (Skill `sync`): klein, grün, "geprüft: …" in der Commit-Nachricht. Nur im eigenen Ordner, dann gibt es keine Konflikte.

## 9. Kürzungsliste (von oben nach unten streichen, wenn es eng wird)

1. Zweites Szenario F70-EU → nur Screenshot/Folie "so einfach geht's"
2. Triangulation Web ↔ intern → Webbelege nur als eigene Befunde
3. LLM-Challenge-Antwort → regelbasierte Startversion (existiert schon)
4. Optionslisten-PDF → Status "unknown"
5. Gewichte-Regler im UI → feste Gewichte, Formel auf Folie
**Nie streichen:** Belege→Befund→Anforderung-Kette mit Zitaten, PM-Entscheidung, Prüfpfad, Evidenzstufe.

## 10. Risiken und Gegenmittel

| Risiko | Gegenmittel |
|---|---|
| LLM erfindet Zitate/IDs | Nur IDs aus Eingabe erlaubt + Test + Grounding-Zahl im Pitch |
| OpenAI langsam/teuer | Vorgruppieren per Taxonomie (wenige LLM-Aufrufe), Cache, kleines Modell |
| Netz im Saal fällt aus | `DEMO_MODUS=true` + Cache + Backup-Video |
| BMW-Daten landen im öffentlichen Repo | `data/` ist gitignored; Beispiele sind synthetisch; Secret-Scan in CI |
| Frontend wird nicht fertig | FastAPI `/docs` + CSV-Export als Notfall-Demo |
