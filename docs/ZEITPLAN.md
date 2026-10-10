# Zeitplan Sa 14:45 bis So 12:00 (pro Pfad)

**L** = Lead (Piyush) · **A** = Interne Evidenz · **B** = Externe Evidenz + Qualitätsbeweis · **C** = Anforderungen + Priorisierung · **D** = PM-Cockpit
Details pro Pfad: `docs/pfade/`. **Fett** = harter Meilenstein: wackelt er, wird gekürzt (`docs/PLAN.md` §9), nicht verlängert.

## Samstag

| Zeit | L | A | B | C | D |
|---|---|---|---|---|---|
| 14:45 | Kick-off: Idee, Pfade verteilen | Pfad wählen, Setup | dto. | dto. | dto. |
| 15:00 | Kick-off-Fragen klären, Daten verteilen (USB) | `load_feedback` + Test | Websuche-Probe, `Claims`-Schema | Formel lesen, `derive.py` v1 (Beispiel-Befunde) | Next.js-Gerüst, `api.ts` |
| 16:00 | Mentor-Fragen, CI auf main prüfen | `load_study`, `load_context` | Fragen-Generator, `trust.py` | Faktoren im Code | Seite 1 Liste |
| **17:00** | Stufe `evidence` echt laufen lassen | **echte Belege auf main** | `research()` v1 | Score auf echten Belegen | Seite 2 Detail |
| **18:00** | **Durchstich**: Pipeline → Bundle → UI zeigt echte Liste | Befunde v1 ohne LLM | **5+ Webbelege mit URL** | **`requirements.json` echt** | **Liste → Detail mit Wasserfall** |
| 19:00 | Dinner + Stand-up (je 1 min, Kürzungen?) | | | | |
| 19:30 | Audit-Ereignisse Pipeline | Befunde v2 mit LLM | Triangulation | Scope-Wächter, Offer-Check | Entscheiden + Prüfpfad |
| 21:00 | `selbstreview` vorbereiten | Konflikte | Triangulation fertig | Challenge mit LLM | Gewichte-Regler |
| **22:00** | **MVP auf main + 1. Abgabe ehl.gg** | gepusht | gepusht | gepusht | gepusht |

## Nacht (Schlaf in zwei Schichten, je ~4 h)

| Schicht | Schläft | Wach und macht |
|---|---|---|
| 23:00-03:00 | **B, D** | L Integration + Deck-Rahmen · A Szenarien F70-EU/G70-US · C Kalibrierung Evidenzstufen |
| 03:00-07:00 | **L, A, C** | B Eval-Set labeln + `run_eval.py` · D UI-Politur + Trichter-Seite |

Regel nachts: nur kleine, getestete Pushes; nach 02:00 nichts Neues anfangen. Vor dem Schlafen: letzter Push, CI grün.

## Sonntag

| Zeit | L | A | B | C | D |
|---|---|---|---|---|---|
| 07:00 | Pull + CI-Check, Pipeline alle Szenarien | Bugs | **Eval-Zahl in `REPORT.md`** | Bugs | Bugs |
| **08:00** | **Feature-Freeze** + Frühstück-Stand-up | | | | |
| 08:30 | Skill `demo-check` (Fresh Clone) | Pitch-Folie A | Pitch-Folie B, Zahl in README | Pitch-Folie C | Demo-Strecke 3× + **Backup-Video** |
| 09:30 | Deck zusammenbauen | Jury-Fragen üben | dto. | dto. | dto. |
| **10:00** | **Pitch-Probe mit Stoppuhr** (Skill `pitch-prep`), jede Person beantwortet 2 Jury-Fragen | | | | |
| **10:30** | **Code-Freeze** → Skill `abgabe` | | | | |
| **11:30** | **Abgegeben** (30 min Puffer vor 12:00) | | | | |

## Pushen (alle direkt auf main)

Claude committet und pusht automatisch nach jedem getesteten Schritt (Skill `sync`): `git pull --no-rebase origin main` → Tests → `git push origin main`.
Ab So 10:30 (Code-Freeze) pusht nur noch der Lead, und nur Fixes aus `docs/ABGABE.md`.

## Timeboxing

- Jede Aufgabe hat die Zeitbox aus der Pfad-Datei. **45 min ohne Fortschritt → Lead fragen.**
- Mindestens alle 30-45 min committen + pushen (Entire-Checkpoints!).
