# Lead · Piyush · Integration, Pitch, Abgabe (+ Web, siehe PFAD-B)

**Ziel:** Die drei anderen sind nie blockiert, und um 18:30 / 22:00 / 07:30 läuft auf `main` ein Stand, der die Demo trägt.
Seit Fabian fehlt, baust du auch das **Deck**.
**Schreibt in:** `src/backend/core/`, `api/`, `main.py`, `pipeline.py`, `evidence_external/`, `src/shared/`, `config/`, `docs/`, Root, `.github/`, `.claude/`, `scripts/`.
Gesamtplan: [`ROADMAP.md`](../ROADMAP.md) · Web-Tickets: [`PFAD-B.md`](PFAD-B.md).

## Schon fertig (auf main)

Datenmodell, Prüfpfad mit Hash-Kette, Store mit PM-Aktionen, API (Szenarien, Trichter, Befunde, Anforderungen, Detail, Entscheidung, Gewichte, Prüfpfad, Verify, CSV-Export),
Pipeline mit Stufendateien + Beispiel-Fallback, 3 Szenario-Configs, Startversionen von Scoring/Evidenzstufe/Challenge, CI, 26 Tests.

## Dein Tag (Tickets in Reihenfolge, Web-Tickets B1-B5 dazwischen)

| Zeit | Ticket | Fertig, wenn |
|---|---|---|
| 15:15 | [x] **L0 Kick-off (15 min):** Idee in 3 Sätzen, ROADMAP §1 vorlesen, Arbeitsbücher verteilen, USB-Stick mit `data/raw/` rumgeben, Team-Chat für Blocker | alle 4 kennen ihr erstes Ticket |
| 15:30 | [x] **L1 Setup-Runde (15 min):** reihum M0 abhaken (Tests, Entire, `.env` mit eigenem Key). Eigene `.env` anlegen (fehlt noch!) | M0 für alle ✓ |
| 15:30 | B1, B2, B3 (Web) | siehe PFAD-B |
| 17:30 | [ ] **L2 M1:** `pipeline.py --scenario G60-US --stage evidence` mit Adityas Code | ~3.700 Belege |
| 17:45 | [ ] **L3 Pipeline an `derive_all` anschließen:** Stufe requirements nutzt `derive_all` (Dennis, C2), schreibt `discarded.json`; Bundle-Stufe schreibt verworfene als Audit `REQUIREMENT_DISCARDED` | Test in `tests/test_pipeline.py` |
| **18:30** | [ ] **L4 Durchstich:** alle Stufen, Bundle, Backend neu starten, mit allen 4 auf Lasses Bildschirm schauen | echte Liste + Detail im UI |
| 19:00 | Stand-up beim Essen (ROADMAP §3) | Kürzungen entschieden |
| 19:30 | B4 Triangulation | siehe PFAD-B |
| 20:30 | [ ] **L5 Audit-Ereignisse der Pipeline:** `EVIDENCE_INGESTED`, `SIGNALS_EXTRACTED`, `REQUIREMENT_PROPOSED` (Akteur KI/System, Modell, Anzahl) beim Bundle-Laden | `/audit` zeigt die KI-Schritte |
| 21:15 | [ ] **L6 README** für Jury + KI-Reviewer: Problem, Lösung, Mermaid-Diagramm, Alignment-Map Brief → Code, Start in 3 Befehlen, Ergebnis-Zahlen (Platzhalter bis A10), `docs/ARCHITEKTUR.md` aktualisieren | `ehl_budget.py --pruefen` grün |
| 21:45 | [ ] **L7 Selbstreview** (Skill `selbstreview`), die 3 wichtigsten Punkte als Tickets verteilen | Liste im Chat |
| **22:00** | [ ] **L8 M3 + 1. Abgabe:** CI grün, Skill `abgabe` (Sicherheits-Abgabe), Submit auf ehl.gg mit Deck-Platzhalter-PDF | Submit bestätigt |
| 22:15 | [ ] **L9 Cache füllen:** alle 3 Challenge-Vorschlagsfragen für die Top-5-Anforderungen einmal auslösen, dann `DEMO_MODUS=true` testen (WLAN aus) | Demo läuft offline |
| 23:00 | [ ] **L10 F70-EU integrieren** (mit Aditya A8): Config-Änderungen, Bundle, Umschalter im UI | 2 Szenarien im UI |
| 00:00 | [ ] **L11 Deck v1** mit Skill `anthropic-skills:pptx`: 9 Folien (unten), Screenshots aus der laufenden App | PPTX + PDF lokal |
| 01:30 | [ ] **L12 Demo-Drehbuch** in `docs/pitch/PITCH.md` mit echten Zahlen und Titeln | Drehbuch steht |
| 02:30 | [ ] **L13 Zweite Abgabe** (Update Submission), dann schlafen 03:30-07:30 | Submit aktualisiert |
| 07:30 | [ ] **L14 M4:** `git pull`, alle Szenarien neu, `DEMO_MODUS=true`-Test, Eval-Zahl ins Deck + README | alles grün |
| **08:00** | **Feature-Freeze** + Frühstücks-Stand-up | |
| 08:15 | [ ] **L15** Skill `demo-check` (frischer Klon, läuft bei Fremden?) | grün |
| 08:45 | [ ] **L16 Deck final:** Folien von A, C, D einbauen, Zahlen prüfen (nur aus Code/REPORT) | PDF fertig |
| **10:00** | Pitch-Probe (Skill `pitch-prep`), 2 Durchläufe, jede Person beantwortet 2 Jury-Fragen | unter 4:00 |
| **10:30** | **Code-Freeze** → Skill `abgabe` | |
| **11:30** | **Abgegeben** + Deck hochgeladen | |

## Pitch-Deck (9 Folien, 4:00 Minuten)

1. Problem: „Thousands of voices, one car“ (BMW-Folie in unseren Worten) · 2. Lösung in 1 Satz + Trichter ·
3. **Live-Demo** (Platzhalter-Folie mit Screenshot, falls Technik streikt) · 4. Belege → Befunde (Aditya) · 5. Priorität, die man erklären kann (Dennis) ·
6. Vertrauen: die Zahl (Aditya) · 7. Übertragbar: eine Config-Datei · 8. Workflow KI vs. Mensch · 9. Schluss-Satz + nächste Schritte

## Fragen an BMW (stellt Dennis, du trägst Antworten in `docs/CHALLENGE.md` ein)

1. Welche Rolle hat der PM heute bei der Freigabe: Einzelperson oder Gremium?
2. Gibt es interne Begriffe für Evidenzstufen oder Must/Should/Could, die wir übernehmen sollten?
3. Was bedeuten die Quellen A-D im Feedback genau, und ist eine davon vertrauenswürdiger?

## Integrations-Checkliste bei jedem Sync-Punkt

`git pull` → `python -m pytest -q` → `pipeline.py --scenario G60-US` → Backend neu starten → Liste + Detail im UI anklicken → CI auf GitHub grün?
Rot → Verursacher (ROADMAP §1) anpingen, nicht selbst in fremdem Ordner reparieren.
