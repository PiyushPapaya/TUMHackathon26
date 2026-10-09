# Abgabe-Runbook (Sonntag)

> Ausführen mit dem Skill `abgabe`. Jeder ❌ blockiert, bis er behoben ist.
> Deadline **So 12:00 hart**. Unser Ziel: **abgegeben um 11:30**.
> Warum so streng: Bewertet wird genau der Commit auf `main` beim Klick auf Submit (`tum-ai/ehl` `prepare.ts:162-180`), und ohne Entire-Checkpoints wird die Abgabe abgelehnt.

## Schon vorher erledigt (Fr/Sa)

- [x] `ehl-gg` als Collaborator eingeladen (09.10., Einladung offen; die Plattform nimmt sie beim Submit selbst an, `prepare.ts:153-154`)
- [ ] **Sa 22:00: erste Abgabe** auf ehl.gg mit MVP-Stand (Sicherheitsnetz; Updates sind beliebig oft möglich)

## So 10:30 Code-Freeze

- [ ] Ansage im Team: **ab jetzt keine neuen Features**, nur Fixes aus dieser Liste
- [ ] Alle offenen, grünen PRs gemerged (Piyush); alle anderen bleiben zu

## So 10:30-11:15 Checks (Piyush + Aditya)

| # | Check | Befehl / Ort | ✅/❌ |
|---|---|---|---|
| 1 | Secret-Scan inkl. Historie sauber | `python scripts/secret_scan.py --historie` | |
| 2 | Optional gründlicher: gitleaks | `gitleaks detect --source . -v` (falls installiert) | |
| 3 | Keine `.env`, keine lokalen Settings, keine Logs getrackt | `git ls-files \| grep -E "\.env$\|settings.local\|\.log$"` → leer | |
| 4 | CI auf `main` grün | GitHub → Actions | |
| 5 | **Fresh-Clone-Lauftest**: README-Quickstart wörtlich befolgt, Hauptflow klappt | Skill `demo-check` | |
| 6 | README vollständig: keine `[PLATZHALTER]` mehr, Zahl oben, Demo-Link, Video-Link | `grep -n "\[" README.md` prüfen | |
| 7 | Budget: Produkt-Code wird gelesen, Doku < 25 % | `python scripts/ehl_budget.py` | |
| 8 | **Entire-Checkpoints auf GitHub** | `git ls-remote origin 'refs/entire/checkpoints/*' \| wc -l` > 0 | |
| 9 | **Checkpoints von allen 5** (jede Person hat mit laufender Claude-Session committet) | `git log origin/main --format='%an %(trailers:key=Entire-Checkpoint,valueonly)' \| sort \| uniq -c` | |
| 10 | Live-Demo-URL erreichbar (Backend aufgeweckt) | Browser, Inkognito | |
| 11 | Backup-Video hochgeladen, Link öffentlich | Inkognito öffnen | |
| 12 | Pitch-Deck als PDF exportiert | `docs/pitch/` bzw. Drive | |
| 13 | `docs/ARCHITEKTUR.md` und `docs/pitch/JURY-FAQ.md` aktuell | lesen | |

## So 11:15-11:30 Formular auf ehl.gg (Piyush als Captain)

Felder laut Plattform: `project_name`, `short_description`, `fields` (Repo, Deck, Demo …), `tech_stack` (`lib/submission-snapshots/types.ts:10-20`). **Vorab ausformuliert** (Dennis + Fabian, bis So 10:00):

| Feld | Unser Text |
|---|---|
| Projektname | [ ] |
| Kurzbeschreibung (EN, 1-2 Sätze, mit Zahl) | [ ] |
| GitHub-Repo | `https://github.com/PiyushPapaya/TUMHackathon26` |
| Pitch-Deck (PDF) | [Datei] |
| Live-Demo | [URL] |
| Tech-Stack-Tags | Python, FastAPI, Next.js, TypeScript, OpenAI, [ ] |

- [ ] „Verify“ klicken → grün (Repo lesbar, Entire gefunden)
- [ ] **Submit** → Bestätigung als Screenshot in `workspace/piyush/`
- [ ] Notiert: Uhrzeit und Commit-SHA von `main` beim Submit (`git rev-parse origin/main`)

## Nach jedem weiteren Push bis 12:00

- [ ] **„Update Submission“** klicken. Sonst zählt der alte Stand (`docs/FEATURES.md` der EHL: „a late push is never included automatically“)

## Notfälle

| Problem | Lösung |
|---|---|
| „We could not read your repository“ | Repo öffentlich? Einladung `ehl-gg` offen? URL exakt `https://github.com/PiyushPapaya/TUMHackathon26` |
| „no recognized Entire checkpoint branch or ref“ | `git push` aus einer Session mit Entire; `git ls-remote origin 'refs/entire/checkpoints/*'` |
| „checkpoint data present but no captured prompts“ | Mit laufender Claude-Session eine kleine Änderung committen + pushen |
| „temporarily unavailable or rate limited“ | Organisator-Problem: in 2 min erneut; Discord; **nichts am Repo ändern** |
| Demo-URL tot | Backup-Video-Link ins Demo-Feld, im Pitch lokale Demo |
