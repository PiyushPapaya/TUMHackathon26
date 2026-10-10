# Zeitplan Sa 15:15 bis So 12:00 (4 Personen)

**P** = Piyush (Lead + Web) · **A** = Aditya (Daten + Eval) · **C** = Dennis (Anforderungen) · **D** = Lasse (Frontend)
Ticket-Nummern = Arbeitsbücher in `docs/pfade/`. Erklärung, Arbeitsschleife, Subagents: [`ROADMAP.md`](ROADMAP.md).
**Fett** = harter Meilenstein: wackelt er, wird gekürzt (ROADMAP §8), nicht verlängert.

## Samstag

| Zeit | P | A | C | D |
|---|---|---|---|---|
| 15:15 | L0 Kick-off, L1 Setup-Runde | A0 Setup | C0 Setup | D0 Gerüst |
| 15:30 | B1 Websuche-Probe | A1 Feedback | C1 Formel + BMW-Mentor | D0 / D1 api.ts |
| **15:45** | **M0: alle Setup grün** | | | |
| 16:00 | B2 Fragen + Vertrauen | A1 → A2 Studie | C2 derive v1 | D1 → D2 Liste |
| 17:00 | B3 `research()` v1 | A3 Absatz, A4 Push | C2 → C3 Faktoren | D2 → D3 Detail |
| **17:30** | **M1: L2 echte Belege** | A5 Befunde v1 | C3 | D3 |
| 17:45 | L3 Pipeline ↔ `derive_all` | A5 | C3 | D3 |
| **18:30** | **M2 Durchstich: L4, alle schauen auf Lasses Bildschirm** | | | |
| 19:00 | Essen + Stand-up | | | |
| 19:30 | B4 Triangulation | A6 Befunde v2 (LLM) | C4 Scope, C5 Optionsliste | D4 Entscheiden + Prüfpfad |
| 20:30 | L5 Audit-Ereignisse | A6 | C5 | D4 |
| 21:00 | L6 README | A7 Konflikte | C6 Challenge-LLM | D5 Regler |
| 21:45 | L7 Selbstreview | A7 | C6 | D5 |
| **22:00** | **M3 MVP + L8 1. Abgabe ehl.gg** | gepusht | gepusht | gepusht |
| 22:15 | L9 Cache füllen, Offline-Test | Pause / Bugs aus L7 | C7 Kalibrierung | D6 Trichter-Seite |
| 23:00 | L10 F70-EU | A8 F70-EU + G70-US | C7 | D6 |

## Nacht (zwei Schichten, immer 2 wach)

| Zeit | P | A | C | D |
|---|---|---|---|---|
| 23:30-03:30 | L11 Deck v1, L12 Drehbuch, L13 2. Abgabe | A9 Eval labeln, A10 Eval-Skript + REPORT | **schläft** | **schläft** |
| 03:30-07:30 | **schläft** | **schläft** | C8 Textqualität, C9 Randfälle, C10 Was-wäre-wenn | D7 Politur, D8 Demo 3× |

Regeln nachts: nur kleine, getestete Pushes. Wer ins Bett geht: letzter `sync`, CI grün, im Chat „bin weg, Stand: …“.

## Sonntag

| Zeit | P | A | C | D |
|---|---|---|---|---|
| 07:30 | **M4:** L14 Pull, alle Szenarien, Offline-Test | Bugs | Bugs | Bugs |
| **08:00** | **Feature-Freeze** + Frühstücks-Stand-up | | | |
| 08:15 | L15 `demo-check` (frischer Klon) | A11 Folie „Vertrauen“ | C11 Folie „Priorität“ | D9 Backup-Video |
| 08:45 | L16 Deck final | Jury-Fragen üben | Jury-Fragen üben | Screenshot ans Deck |
| 09:30 | Pitch-Text auswendig | Demo-Teil üben | Demo-Teil üben | D10 Demo klicken üben |
| **10:00** | **Pitch-Probe mit Stoppuhr** (Skill `pitch-prep`), jede Person beantwortet 2 Jury-Fragen | | | |
| **10:30** | **Code-Freeze** → Skill `abgabe` | | | |
| **11:30** | **Abgegeben** (30 min Puffer vor 12:00) | | | |

## Pushen (alle direkt auf main)

Claude committet und pusht automatisch nach jedem getesteten Schritt (Skill `sync`): `git pull --no-rebase origin main` → Tests → `git push origin main`.
Mindestens alle 30-45 min (Entire-Checkpoints!). Ab So 10:30 pusht nur noch Piyush, und nur Fixes aus `docs/ABGABE.md`.
