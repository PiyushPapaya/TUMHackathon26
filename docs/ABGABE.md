# Abgabe-Runbook (Sonntag)

> Ausführen mit dem Skill `abgabe`. Jeder ❌ blockiert, bis er behoben ist.
> Deadline **So 12:00 hart**. Unser Ziel: **abgegeben um 11:30**.
> Warum so streng: Bewertet wird genau der Commit auf `main` beim Klick auf Submit (`tum-ai/ehl` `prepare.ts:162-180`), und ohne Entire-Checkpoints wird die Abgabe abgelehnt.

## Schon vorher erledigt (Fr/Sa)

- [x] `ehl-gg` als Collaborator eingeladen (09.10., Einladung offen; die Plattform nimmt sie beim Submit selbst an, `prepare.ts:153-154`)
- [ ] **Sa 22:00: erste Abgabe** auf ehl.gg mit MVP-Stand (Sicherheitsnetz; Updates sind beliebig oft möglich)

## So 10:30 Code-Freeze

- [ ] Ansage im Team: **ab jetzt keine neuen Features**, nur Fixes aus dieser Liste
- [ ] Alle haben ihren letzten getesteten Stand auf main gepusht; CI auf main grün

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
| 13 | `docs/ARCHITEKTUR.md` und `docs/pitch/PITCH.md` (Jury-Fragen) aktuell | lesen | |

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
- [ ] **Submit** → Bestätigung als Screenshot lokal in `data/notizen/` (nicht im Git)
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

## Notfall A: Wissen aus `main` auslagern (nur wenn nötig)

**Warum normalerweise unnötig:** Jede neue Abgabe hat Revision ≥ 1 (`tum-ai/ehl` `supabase/migrations/00072_verified_submission_versions.sql:77`). Damit lädt die EHL den GitHub-Zipball des eingefrorenen Commits (`lib/code-review/ingest.ts:158`, `archive.ts:52`), und der beachtet `export-ignore` (getestet am 09.10.). Nur im Alt-Modus ohne SHA (Trees-API, `ingest.ts:164-169`) würden Doku und `.claude` einen Teil des Budgets belegen (prüfen mit `python scripts/ehl_budget.py --modus baum`).

**Auslöser:** Der Report zeigt Doku-Dateien als gelesen, oder die Orga bestätigt, dass ohne Zipball gelesen wird. Dann So 11:00 (Piyush), Befehle am 10.10. in einem Wegwerf-Clone getestet:

```bash
git switch main && git pull
git branch archiv/wissen && git push -u origin archiv/wissen      # alles bleibt im Archiv-Branch erhalten
git switch -c piyush/wissen-auslagern
git rm -r docs/pfade docs/hilfe .claude/skills .claude/agents
git commit -m "Wissen nach archiv/wissen ausgelagert, weil die Review-KI sonst Doku statt Code liest"
git push -u origin piyush/wissen-auslagern && gh pr create --base main --fill
```

Ergebnis im Test: Archiv enthält alle 10 Wissensdateien, `main` danach keine; Fallback-Budget Doku 28 %. Danach mergen (Bypass) und „Update Submission“.

## Notfall B: Piyush fällt aus

Seit Sa 10.10. pushen alle direkt auf main (Ruleset `main-schutz-nur-unfaelle` verbietet nur Löschen und Force-Push von main).
Es gibt also nichts freizuschalten: Fällt Piyush aus, übernimmt **Lasse** die Abgabe auf ehl.gg (Captain-Zugang vorher klären) und führt den Skill `abgabe` aus.
