# [PROJEKTNAME]

> TUM.ai × EHL Grand Finale · 10.–11. Oktober 2026 · Garching

| | |
|---|---|
| **Teamname** | [TEAMNAME] |
| **Gewählte Challenge** | [SPONSOR – TITEL DER CHALLENGE] |
| **Demo-Link** | [DEMO-LINK] |

## Problem

[Welches Problem lösen wir, für wen? Ein bis zwei Sätze.]

## Lösung in 2 Sätzen

[Satz 1: Was macht unser Produkt?] [Satz 2: Warum ist das besser als der Status quo?]

## Tech-Stack

Vorläufig, kann vor Ort angepasst werden:

| Teil | Technik | Ordner |
|---|---|---|
| Frontend (App) | Next.js (React, TypeScript) | `src/frontend/` |
| Backend (API) | Python + FastAPI | `src/backend/` |
| Tests | pytest / Playwright | `tests/` |

Eine genauere Erklärung steht in [`docs/ARCHITEKTUR.md`](docs/ARCHITEKTUR.md).

## Setup in 3 Befehlen

```bash
git clone https://github.com/PiyushPapaya/TUMHackathon26.git && cd TUMHackathon26
cp .env.example .env          # danach eigene Keys in .env eintragen (nie committen!)
claude                        # Claude Code starten, der Rest läuft über Claude
```

Die ausführliche Anleitung für Einsteiger steht in [`docs/SETUP.md`](docs/SETUP.md).
Start-Befehle für Frontend und Backend ergänzen wir hier, sobald der Stack feststeht:

- Frontend: `[BEFEHL, z. B. cd src/frontend && npm install && npm run dev]`
- Backend: `[BEFEHL, z. B. cd src/backend && pip install -r requirements.txt && uvicorn main:app --reload]`

## Team

| Name | GitHub | Rolle | Zuständig für |
|---|---|---|---|
| Piyush | [@PiyushPapaya](https://github.com/PiyushPapaya) | Lead & Developer, merged PRs | alles, v. a. `src/backend/` |
| Lasse | [@JoleEight](https://github.com/JoleEight) | Developer (App/Frontend), darf PRs freigeben | `src/frontend/` |
| Aditya | [@adityarawat1804](https://github.com/adityarawat1804) | Testing & Demo (+ Design-Support) | `tests/`, `demo/` |
| Dennis | [@Di0n-0](https://github.com/Di0n-0) | Product & Research (+ Python-Support im Backend) | `docs/research/` |
| Fabian | [GitHub-Username folgt] | Pitch & Story, Design & Slides | `docs/pitch/`, `design/` |

Jede Person hat eine eigene Steckbrief-Datei in [`team/`](team/).

## So arbeitest du mit Claude Code

Du musst keine Git-Befehle auswendig kennen. Sag Claude einfach in normalen Sätzen, was du willst:

- „Hol dir den neuesten Stand."
- „Speicher meine Arbeit und mach einen Pull Request."
- „Ich habe einen Konflikt, erklär ihn mir."
- „Erklär mir, wie unser Backend funktioniert."
- „Was ist meine Rolle und woran sollte ich gerade arbeiten?"
- „Schreib mir eine Antwort auf die Jury-Frage: Warum dieser Ansatz?"

Claude hält sich dabei an die Regeln in [`CLAUDE.md`](CLAUDE.md): nie direkt auf `main`, immer über einen Pull Request.

## Glossar

- **clone**: Du lädst das ganze Projekt einmalig von GitHub auf deinen Rechner.
- **pull**: Du holst die neuesten Änderungen der anderen von GitHub auf deinen Rechner.
- **commit**: Du speicherst einen Zwischenstand deiner Arbeit mit einer kurzen Beschreibung.
- **push**: Du schickst deine gespeicherten Commits zu GitHub, damit andere sie sehen können.
- **Branch**: Eine eigene Arbeitskopie, in der du Neues ausprobierst, ohne das Hauptprojekt (`main`) zu stören.
- **Pull Request (PR)**: Eine Anfrage „bitte prüft meine Änderungen und übernehmt sie in `main`".
- **Merge-Konflikt**: Zwei Personen haben dieselbe Stelle geändert und Git weiß nicht, welche Version gelten soll, also entscheidet ein Mensch.

## Konflikt-Übung

Hier schreibt jeder seinen Namen rein (jede Person auf eine eigene Zeile, alle gleichzeitig, das erzeugt absichtlich einen Konflikt):

- Piyush
