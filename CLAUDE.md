# Regeln für Claude Code (Hackathon-Team)

Dieses Repo gehört einem fünfköpfigen Hackathon-Team (TUM.ai × EHL Grand Finale, 10.–11. Oktober 2026). Die Challenge steht erst vor Ort fest, deshalb ist das Repo generisch. Vorläufiger Stack: Next.js (`src/frontend/`) + Python/FastAPI (`src/backend/`).

**Wichtig:** Nicht jede Person hier hat Coding-Erfahrung. Antworte immer auf Deutsch und erkläre **vor jedem Git-Befehl in einem Satz, was du tust und warum**.

## Start jeder Session

1. Frag nach dem Namen, falls unklar, und lies `team/<name>.md` (Rolle, Zuständigkeit, Ordner).
2. Führe `git checkout main && git pull` aus. Wechsle dann auf den Branch `<vorname>/<feature>` oder lege ihn an und merge `main` hinein (`git merge main`).
3. Lies `docs/ARCHITEKTUR.md`, damit du den aktuellen Stand kennst.

## Git-Workflow (strikt)

- **NIE direkt auf `main` committen, pushen oder mergen.**
- Kleine Commits mit klaren deutschen Messages (z. B. `Login-Formular hinzugefügt`).
- Wenn etwas fertig ist und funktioniert: pushen, dann `gh pr create` gegen `main`, Reviewer: `PiyushPapaya` und `JoleEight`. **Nie selbst mergen.**
- **Merge-Konflikte:** nicht raten. Konflikt zeigen, in einfachen Worten erklären, nachfragen. Im Zweifel: „Hol Piyush."
- **Verboten:** `git push --force`, `git reset --hard`, Rebase geteilter Branches, Branches oder Dateien anderer löschen.

## Rollen

- Ändere nur Dateien im Zuständigkeitsbereich der Person (steht in `team/<name>.md`). Wenn etwas außerhalb nötig ist: erst erklären, dann fragen.
- **Nicht-Coding-Rollen** (Research, Pitch, Design, Testing): hilf bei Texten, Recherche, Struktur, Testplänen und Markdown. Kein App-Code, außer Tests in `tests/` für die Testing-Rolle.

| Ordner | Zuständig |
|---|---|
| `src/backend/` | Piyush (Dennis unterstützt mit Python) |
| `src/frontend/` | Lasse |
| `tests/`, `demo/` | Aditya |
| `docs/research/` | Dennis |
| `docs/pitch/`, `design/` | Fabian |

## Verständnis für die Jury (sehr wichtig)

Jede Person muss am Ende der Jury erklären können, wie das Produkt funktioniert. Außerdem bewertet eine KI-Code-Review der EHL-Plattform unseren Code und die README.

- Jede Code-Änderung muss lesbar sein: sprechende Namen, kurze Kommentare, die das **WARUM** erklären.
- Bei jedem PR mit Code aktualisierst du `docs/ARCHITEKTUR.md`: Komponenten, Datenfluss, externe APIs/Modelle, wichtige Designentscheidungen. Einfache Sprache, sodass auch Pitch-Leute es erklären können.
- Wenn eine Designentscheidung getroffen wird, ergänze `docs/pitch/JURY-FAQ.md` um eine wahrscheinliche Jury-Frage plus kurze Antwort.
- Wenn jemand fragt „Erklär mir X": erst in 2 Sätzen das Prinzip, dann der Ablauf, dann die Stelle im Code.

## Sicherheit

- **Keine API-Keys oder Passwörter committen.** Secrets nur in `.env` (steht in `.gitignore`), Vorlage in `.env.example` ohne echte Werte. Das Repo ist öffentlich, ein geleakter Key ist sofort sichtbar.
- Keine neuen Dependencies ohne Rückfrage, und im PR erwähnen.
