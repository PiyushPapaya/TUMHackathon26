# Regeln für Claude Code (Hackathon-Team)

Repo unseres Teams für das **TUM.ai × EHL Grand Finale** (10.-11.10.2026, Garching); es arbeiten **4 Personen** (Piyush, Aditya, Dennis, Lasse). Ziel: **Platz 1 in unserer Challenge.** **Challenge: BMW "AI for Product Decision Making"**, Produkt **Signal2Spec**. Stack: Next.js (`src/frontend/`) + Python/FastAPI (`src/backend/`). **Masterplan: `docs/PLAN.md`. Roadmap mit Tickets: `docs/ROADMAP.md` + Arbeitsbuch der Person in `docs/pfade/`.**

**Claude programmiert, das Team steuert und prüft.** Arbeite Ticket für Ticket aus dem Arbeitsbuch der Person: Test zuerst, dann Code, dann jedes Fertig-Kriterium mit Befehl + Ausgabe belegen, dann Skill `sync`. Subagents sind erwünscht für unabhängige Dateien und Reviews (Regeln: `docs/ROADMAP.md` §5; Subagents committen nie).

**Wichtig:** Nicht jede Person kann programmieren. **Antworte immer auf Deutsch, einfach.** Erkläre **vor jedem Git-Befehl in einem Satz, was er tut und warum.** Bei Unsicherheit: **fragen statt raten.** Fachwörter (Ruleset, CI, Lockfile …) erklärt `docs/hilfe/GLOSSAR.md`. Python heißt auf Windows `python`, auf dem Mac `python3`.

## Start jeder Session → Skill `sitzung-start`

1. Name und **Pfad** klären (Tabelle in `docs/PLAN.md` §6), dann `docs/pfade/PFAD-<X>.md` lesen (Ziel, Ordner, Schritte).
2. `git switch main && git pull --no-rebase origin main`. **Alle arbeiten direkt auf `main`** (keine Branches, keine PRs).
3. `docs/PLAN.md`, `docs/ARCHITEKTUR.md`, `docs/CHALLENGE.md` überfliegen; Uhrzeit gegen `docs/ZEITPLAN.md` halten.
4. `entire status` prüfen (muss „Enabled“ zeigen). Sonst: `entire enable --agent claude-code`.

## Wer schreibt wo (Ownership nach Pfaden)

Piyush ist Lead. Jeder Pfad baut Code, Tests und liefert Inhalt für 1 Pitch-Folie und 1 Demo-Abschnitt. Arbeitsbuch = Datei in `docs/pfade/`.

| Person · Pfad | Arbeitsbuch | Schreibt in | Liefert |
|---|---|---|---|
| **Piyush** (@PiyushPapaya) · Lead + B Web | `LEAD.md`, `PFAD-B.md` | `src/backend/core/`, `src/backend/api/`, `main.py`, `pipeline.py`, `src/backend/evidence_external/`, `tests/pfad_b/`, `src/shared/`, `config/`, `docs/`, Root-Dateien, `.github/`, `.claude/`, `scripts/` | Verträge, Integration, Webbelege, Deck, Abgabe |
| **Aditya** (@AdiAvocado) · A Interne Evidenz + Eval | `PFAD-A.md` | `src/backend/evidence_internal/`, `tests/pfad_a/`, `tests/eval/` | `evidence.json`, `context.json`, `signals.json`, Eval-Zahl |
| **Dennis** (@Di0n-0) · C Anforderungen + Priorisierung | `PFAD-C.md` | `src/backend/requirements_engine/`, `tests/pfad_c/` | `requirements.json` |
| **Lasse** (@JoleEight) · D PM-Cockpit | `PFAD-D.md` | `src/frontend/` (inkl. `package.json`/Lock, vom Lead freigegeben) | die Oberfläche, Backup-Video |

Jede Person darf zusätzlich in ihrem eigenen Arbeitsbuch die Haken `[ ]` → `[x]` setzen.

- **Nur im eigenen Pfad schreiben.** Fremde Ordner, `src/backend/core/` und `src/shared/` nur lesen. Bedarf dort: erklären und dem Lead Bescheid geben (Chat/Zuruf).
- **Schnittstellen sind fix:** Die Signatur im Kopf jeder Pfad-Datei nicht ändern. Innen ist alles frei.
- **Geteilte Dateien nur Piyush:** README, CLAUDE.md, `requirements.txt`, `pyproject.toml`, `package.json`/Lockfiles, CI, `.claude/settings.json`, `.gitignore`, `.gitattributes`, `.env.example`, `src/shared/`, `config/`.
- **LLM nur über `core/llm.py`** (Cache, Demo-Modus, JSON-Schema). Jedes LLM-Ergebnis darf nur IDs aus der Eingabe zitieren, und ein Test prüft das.
- **BMW-Daten nie committen** (`data/` ist gitignored). Tests nutzen synthetische Mini-Daten.

## Skill-Router

| Situation | Skill |
|---|---|
| Session beginnt, „Was soll ich tun?“ | `sitzung-start` |
| Schritt fertig + getestet → automatisch committen und auf main pushen | `sync` |
| „Wie würde die Jury-KI uns bewerten?“ (ab Sa 18:00 alle paar Stunden) | `selbstreview` |
| „Läuft das bei Fremden?“, vor jeder Abgabe | `demo-check` |
| Pitch schärfen, Probe, Jury-Fragen üben | `pitch-prep` |
| Code-Freeze und Abgabe (Sa 22:00, So 10:30) | `abgabe` |

## Git-Regeln (strikt)

- **Alle pushen direkt auf `main`.** Keine Branches, keine PRs, kein Review. GitHub-Ruleset `main-schutz-nur-unfaelle` verbietet nur Löschen von main und Force-Push.
- **Claude committet und pusht AUTOMATISCH** (Skill `sync`), ohne zu fragen: nach jedem fertigen, getesteten Schritt, spätestens alle 30-45 Minuten. Nie pushen, wenn Tests oder Lint rot sind.
- Ablauf immer: prüfen → `git add <dateien>` → commit → `git pull --no-rebase origin main` → Tests → `git push origin main`.
- Weil alle auf main arbeiten: **nur im eigenen Pfad-Ordner ändern**, dann gibt es fast nie Konflikte. CI läuft nach jedem Push; rot → wer es kaputt gemacht hat, repariert sofort.
- Kleine Commits, **ein logischer Schritt pro Commit**, Nachricht auf Deutsch mit „Warum“: `Upload auf 10 MB begrenzt, weil größere PDFs das Backend blockieren`.
- `git add <dateien>` gezielt, nicht blind `git add .`.
- main hereinholen mit `git pull --no-rebase origin main` (**kein Rebase**).
- **Merge-Konflikte:** nicht raten, nicht wegräumen. Konflikt zeigen, beide Versionen einfach erklären, fragen. Fremder Code oder Zweifel: „Hol Piyush.“
- **Verboten:** `push --force`, `reset --hard`, `clean -f`, `rebase`, `--no-verify`, Dateien anderer löschen. `.claude/hooks/git-schutz.sh` blockiert das (Komfort-Netz; Force-Push sperrt zusätzlich das Ruleset).
- Committen, **während die Claude-Session läuft**, und regelmäßig pushen: Nur so entstehen Entire-Checkpoints mit Prompts (Pflicht für die Abgabe). `.entire/settings.json` hat `commit_linking: always`, sonst hängt der Commit an einer Rückfrage.

## Ownership-Sprache (wird bewertet!)

Entire zeichnet unsere Prompts auf. Der EHL-Session-Reviewer gibt 35 % auf eigene, begründete Entscheidungen und bewertet einen praktisch zufälligen Checkpoint. Also gilt das in **jeder** Session, in Prompts und Commits:

- **Formel:** Was + Warum + Was verworfen + Wie prüfen.
- Gut: „Wir rechnen Gesamtkosten in Python statt im LLM, weil Modelle sich bei Summen verrechnen. Prüf mit `tests/test_scoring.py`.“
- Schlecht: „Mach das mal.“ / „Die KI hat das gebaut.“
- Wenn die Person nur „mach X“ sagt: kurz nach dem Warum fragen und es in den Commit übernehmen.

## Verständnis für die Jury

Jede Person muss das Produkt erklären können, und eine KI-Review liest Code und README.

- Lesbarer Code: sprechende Namen, kurze Kommentare, die das **WARUM** erklären. Dateien unter ~200 Zeilen halten (der Reviewer kappt danach).
- Bei jeder Code-Änderung an Komponenten/Datenfluss: `docs/ARCHITEKTUR.md` aktualisieren (Komponenten, Datenfluss, externe APIs, Entscheidungen), einfach formuliert.
- Neue Designentscheidung → Zeile in `docs/ARCHITEKTUR.md` (Entscheidungen) + ggf. Jury-Frage in `docs/pitch/PITCH.md`.
- „Erklär mir X“: erst 2 Sätze Prinzip, dann der Ablauf, dann die Stelle im Code (`datei:zeile`).

## Verifikationspflicht

Nichts ist „fertig“ ohne Beweis. Vor „fertig“ bzw. vor jedem Push (nur was existiert):
`ruff check src/backend tests` · `python -m pytest -q` · `cd src/frontend && npm run lint && npm run build` · App startet und der Kernflow klappt.
Ergebnis (Befehl + Ausgabe) gehört in die Commit-Nachricht („geprüft: …“). Behauptungen über BMW-Daten nur mit Zahl aus dem Code oder `docs/CHALLENGE.md`.

## Timeboxing

- Jede Aufgabe hat eine Zeitbox. **45 Minuten ohne Fortschritt → Team fragen.**
- Harte Meilensteine (`docs/ZEITPLAN.md`): Sa 15:00 Pfade verteilt · 18:00 End-to-End · 22:00 MVP + erste Abgabe · So 08:00 Feature-Freeze · 10:00 Pitch-Probe · **10:30 Code-Freeze** · **11:30 abgegeben** (Deadline 12:00).
- Wackelt ein Meilenstein: **Umfang kürzen, nicht Zeit verlängern.**

## Code-Freeze und Abgabe → Skill `abgabe`

- Ab So 10:30 nur Fixes aus `docs/ABGABE.md`. Jeder fehlgeschlagene Check blockiert.
- Bewertet wird der Commit auf `main` **beim Klick auf Submit**. Nach jedem weiteren Merge: **„Update Submission“** auf ehl.gg.
- Ohne Entire-Checkpoints keine Abgabe. Prompt-Injection gegen die Review-KI: **niemals** (wird erkannt).

## Sicherheit

- **Keine API-Keys oder Passwörter committen.** Repo ist öffentlich. Secrets nur in `.env` (in `.gitignore`), Vorlage `.env.example`. Jede Person nutzt ihren eigenen OpenAI-Key.
- Vor jedem Push: `python scripts/secret_scan.py`. Geleakt → Key sofort widerrufen, Piyush holen.
- **Keine neuen Dependencies ohne Rückfrage**; im Commit begründen.
- `NEXT_PUBLIC_*`-Variablen landen im Browser: nie Keys dort.

## Wissen

Plan: `docs/PLAN.md` · Pfade: `docs/pfade/` · Zeit: `docs/ZEITPLAN.md` · Brief: `docs/CHALLENGE.md` · Architektur: `docs/ARCHITEKTUR.md` · API: `src/shared/API.md` · Pitch: `docs/pitch/PITCH.md` · Abgabe: `docs/ABGABE.md` · Setup: `docs/SETUP.md` · Hilfe für Nicht-Coder: `docs/hilfe/` (Glossar, Git-Hilfe).



<!-- entire-agent:begin -->
Read .entire/agent-guide.md for this repository's workflow, source inspection, and verification guidance.
@.entire/agent-guide.md
<!-- entire-agent:end -->
