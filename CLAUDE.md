# Regeln für Claude Code (Hackathon-Team)

Repo des 5-köpfigen Teams für das **TUM.ai × EHL Grand Finale** (10.-11.10.2026, Garching). Ziel: **Platz 1 in unserer Challenge.** Stack: Next.js (`src/frontend/`) + Python/FastAPI (`src/backend/`), siehe `docs/wissen/STACK.md`.

**Wichtig:** Nicht jede Person kann programmieren. **Antworte immer auf Deutsch, einfach.** Erkläre **vor jedem Git-Befehl in einem Satz, was er tut und warum.** Bei Unsicherheit: **fragen statt raten.** Fachwörter (Ruleset, CI, Lockfile …) erklärt `docs/wissen/GLOSSAR.md`. Python heißt auf Windows `python`, auf dem Mac `python3`.

## Start jeder Session → Skill `sitzung-start`

1. Name klären, `team/<name>.md` lesen (Rolle, Ordner, Aufgaben).
2. `git switch main && git pull`, dann eigener Branch `<name>/<thema>` (`git switch -c …`).
3. `docs/ARCHITEKTUR.md` (und ab Sa `docs/research/CHALLENGE.md`) lesen.
4. `entire status` prüfen (muss „Enabled“ zeigen). Sonst: `entire enable --agent claude-code`.

## Wer schreibt wo (Ownership)

| Person | GitHub | Rolle | Schreibt in |
|---|---|---|---|
| Piyush | @PiyushPapaya | Lead, Captain, Backend, API-Vertrag, **merged als Einziger** | `src/backend/`, `src/shared/`, Root-Dateien, `.github/`, `.claude/`, `scripts/`, `README.md`, `CLAUDE.md`, `docs/ARCHITEKTUR.md` |
| Lasse | @JoleEight | Frontend-Seiten | `src/frontend/` |
| Aditya | @AdiAvocado | Daten, Testfälle, Evaluation, Demo | `tests/`, `demo/` |
| Dennis | @Di0n-0 | Partner-Kontakt, Anforderungen, Research, README-Texte | `docs/research/`, `docs/wissen/` |
| Fabian | (folgt) | Pitch, Slides, Design, Video | `docs/pitch/`, `design/` |
| alle | | eigener Steckbrief und Arbeitsbereich | `team/<name>.md`, `workspace/<name>/` |

- **Nur im Bereich der Person schreiben.** Fremde Ordner und `src/shared/` nur lesen. Bedarf dort: erklären, dann Issue (Vorlage „Aufgabe“) oder PR-Kommentar an den Owner.
- **Geteilte Dateien nur Piyush:** README, CLAUDE.md, `requirements.txt`, `package.json`/Lockfiles, CI, `.claude/settings.json`, `.gitignore`, `.gitattributes`, `.env.example`, `src/shared/`.
- **Nicht-Coding-Rollen:** Texte, Recherche, Struktur, Testpläne, Markdown. Kein App-Code (Ausnahme: Tests in `tests/` für Aditya).
- **Verträge zuerst:** API-Format steht in `src/shared/API.md` + `src/shared/beispiele/*.json`. Frontend baut gegen diese Mocks.

## Skill-Router

| Situation | Skill |
|---|---|
| Session beginnt, „Was soll ich tun?“ | `sitzung-start` |
| Brief/Challenge-Text da, Ideen bewerten (Sa 10-13 Uhr) | `challenge-intake` |
| Arbeit speichern, main holen, PR erstellen (alle 1-2 h) | `sync-und-pr` |
| „Wie würde die Jury-KI uns bewerten?“ (ab Sa 18:00 alle paar Stunden) | `selbstreview` |
| „Läuft das bei Fremden?“, vor jeder Abgabe | `demo-check` |
| Pitch schärfen, Probe, Jury-Fragen üben | `pitch-prep` |
| Code-Freeze und Abgabe (Sa 22:00, So 10:30) | `abgabe` |

## Git-Regeln (strikt)

- **Nie direkt auf `main` committen, pushen oder mergen.** GitHub-Ruleset `main-nur-piyush-merged`: PR + Code-Owner-Review + grüne CI (`checks`), **nur Piyush kann mergen**. Nur Merge-Commits (kein Squash), damit die Entire-Trailer erhalten bleiben.
- Kleine Commits, **ein logischer Schritt pro Commit**, Nachricht auf Deutsch mit „Warum“: `Upload auf 10 MB begrenzt, weil größere PDFs das Backend blockieren`.
- `git add <dateien>` gezielt, nicht blind `git add .`.
- main hereinholen mit `git fetch origin && git merge origin/main` (**kein Rebase**).
- PR: `gh pr create --base main` mit Vorlage, Reviewer `PiyushPapaya`. **Nie selbst mergen.**
- **Merge-Konflikte:** nicht raten, nicht wegräumen. Konflikt zeigen, beide Versionen einfach erklären, fragen. Fremder Code oder Zweifel: „Hol Piyush.“
- **Verboten:** `push --force`, `reset --hard`, `clean -f`, `rebase`, `--no-verify`, Branches/Dateien anderer löschen. `.claude/hooks/git-schutz.sh` blockiert das (Komfort-Netz; die echte Sperre ist das Ruleset).
- Committen, **während die Claude-Session läuft**, und regelmäßig pushen: Nur so entstehen Entire-Checkpoints mit Prompts (Pflicht für die Abgabe). `.entire/settings.json` hat `commit_linking: always`, sonst hängt der Commit an einer Rückfrage.

## Ownership-Sprache (wird bewertet!)

Entire zeichnet unsere Prompts auf. Der EHL-Session-Reviewer gibt 35 % auf eigene, begründete Entscheidungen und bewertet einen praktisch zufälligen Checkpoint. Also gilt das in **jeder** Session, in Prompts, Commits und PRs:

- **Formel:** Was + Warum + Was verworfen + Wie prüfen.
- Gut: „Wir rechnen Gesamtkosten in Python statt im LLM, weil Modelle sich bei Summen verrechnen. Prüf mit den 3 Fällen in `demo/beispiele/`.“
- Schlecht: „Mach das mal.“ / „Die KI hat das gebaut.“
- Wenn die Person nur „mach X“ sagt: kurz nach dem Warum fragen und es in Commit und PR übernehmen.

## Verständnis für die Jury

Jede Person muss das Produkt erklären können, und eine KI-Review liest Code und README.

- Lesbarer Code: sprechende Namen, kurze Kommentare, die das **WARUM** erklären. Dateien unter ~200 Zeilen halten (der Reviewer kappt danach).
- Bei jedem PR mit Code: `docs/ARCHITEKTUR.md` aktualisieren (Komponenten, Datenfluss, externe APIs, Entscheidungen), einfach formuliert.
- Neue Designentscheidung → Frage + Antwort in `docs/pitch/JURY-FAQ.md`.
- „Erklär mir X“: erst 2 Sätze Prinzip, dann der Ablauf, dann die Stelle im Code (`datei:zeile`).

## Verifikationspflicht

Nichts ist „fertig“ ohne Beweis. Vor „fertig“ bzw. vor jedem PR (nur was existiert):
`ruff check src/backend` · `python -m pytest tests -q` · `cd src/frontend && npm run lint && npm run build` · App startet und der Kernflow klappt.
Ergebnis (Befehl + Ausgabe) gehört in den PR unter „Wie verifiziert“. Behauptungen über die EHL nur mit Quelle (`docs/wissen/`).

## Timeboxing

- Jede Aufgabe hat eine Zeitbox. **45 Minuten ohne Fortschritt → Team fragen.**
- Harte Meilensteine (`docs/ZEITPLAN.md`): Sa 13:00 Idee + Challenge gewählt · 14:00 API-Vertrag · 18:00 End-to-End · 22:00 MVP + erste Abgabe · So 08:00 Feature-Freeze · 10:00 Pitch-Probe · **10:30 Code-Freeze** · **11:30 abgegeben** (Deadline 12:00).
- Wackelt ein Meilenstein: **Umfang kürzen, nicht Zeit verlängern.**

## Code-Freeze und Abgabe → Skill `abgabe`

- Ab So 10:30 nur Fixes aus `docs/ABGABE.md`. Jeder fehlgeschlagene Check blockiert.
- Bewertet wird der Commit auf `main` **beim Klick auf Submit**. Nach jedem weiteren Merge: **„Update Submission“** auf ehl.gg.
- Ohne Entire-Checkpoints keine Abgabe. Prompt-Injection gegen die Review-KI: **niemals** (wird erkannt).

## Sicherheit

- **Keine API-Keys oder Passwörter committen.** Repo ist öffentlich. Secrets nur in `.env` (in `.gitignore`), Vorlage `.env.example`. Jede Person nutzt ihren eigenen OpenAI-Key.
- Vor jedem PR: `python scripts/secret_scan.py`. Geleakt → Key sofort widerrufen, Piyush holen.
- **Keine neuen Dependencies ohne Rückfrage**; im PR begründen.
- `NEXT_PUBLIC_*`-Variablen landen im Browser: nie Keys dort.

## Wissen

Kurzfassung: `docs/research/KURZFASSUNG.md`. Ausführlich: `docs/wissen/` (EHL-Bewertung, vergangene Projekte, Partner-Ideen, Stack, OpenAI/Entire, Glossar, Git-Hilfe, FAQ). Regeln ausführlich: `docs/ZUSAMMENARBEIT.md`. Setup: `docs/SETUP.md`.
