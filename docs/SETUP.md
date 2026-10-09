# Setup (Windows und Mac), ca. 30-45 Minuten

Keine Programmiererfahrung nötig. Die Schritte der Reihe nach abarbeiten und nach jedem Schritt den **Prüfen**-Befehl ausführen. Bei Fehlern: Tabelle ganz unten, oder Claude die Fehlermeldung zeigen.

> **Windows:** Alle Befehle in **PowerShell** (Startmenü → „PowerShell“). Nach jeder Installation das Fenster schließen und neu öffnen, damit neue Programme gefunden werden.
> **Mac:** Alle Befehle im **Terminal**. Für `brew` zuerst Homebrew installieren: https://brew.sh

## 1. GitHub-Einladung annehmen

E-Mail „Invitation to collaborate on PiyushPapaya/TUMHackathon26“ → **Accept invitation**. Noch kein Account? Auf github.com anlegen und den Usernamen an Piyush schicken.

## 2. Programme installieren

| Programm | Windows (PowerShell) | Mac (Terminal) | Prüfen |
|---|---|---|---|
| Git | `winget install --id Git.Git -e` | `xcode-select --install` oder `brew install git` | `git --version` |
| GitHub CLI | `winget install --id GitHub.cli -e` | `brew install gh` | `gh --version` |
| Node.js (LTS) | `winget install --id OpenJS.NodeJS.LTS -e` | `brew install node` | `node --version` (≥ 20) |
| Python 3.12 | `winget install --id Python.Python.3.12 -e` | `brew install python@3.12` | `python --version` (Mac: `python3 --version`) |

Git-Name und E-Mail setzen. **Die E-Mail muss die deines GitHub-Accounts sein**, sonst zeigt Entire „Unknown author“:

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine-github-email@example.com"
```

## 3. Bei GitHub einloggen

```bash
gh auth login
```

Auswahl: *GitHub.com* → *HTTPS* → *Yes* (Git-Zugangsdaten) → *Login with a web browser*. Den angezeigten Code im Browser eingeben.

**Prüfen:** `gh auth status` zeigt „Logged in to github.com account <du>“.

## 4. Claude Code installieren

Du brauchst ein Claude-Abo (Pro oder höher). Offizielle Anleitung: https://docs.claude.com/en/docs/claude-code/setup

| Windows (PowerShell) | Mac (Terminal) |
|---|---|
| `irm https://claude.ai/install.ps1 \| iex` | `curl -fsSL https://claude.ai/install.sh \| bash` |

**Windows:** Claude Code braucht Git for Windows (Schritt 2), denn unsere Hooks laufen über Git Bash.

**Prüfen:** `claude --version`. Beim ersten Start `claude` mit deinem Claude-Account einloggen.

## 5. Entire installieren (Pflicht-Tool, ohne Entire keine Abgabe)

Offiziell laut https://docs.entire.io/cli/installation:

| Windows (PowerShell) | Mac (Terminal) |
|---|---|
| `irm https://entire.io/install.ps1 \| iex` | `brew install --cask entireio/tap/entire` |

- **Windows-PATH-Falle:** Entire landet in `%USERPROFILE%\.local\bin`. Das Skript trägt den Ordner in den PATH ein, aber **erst ein neues PowerShell-Fenster** sieht ihn. Alternative: `scoop bucket add entire https://github.com/entireio/scoop-bucket.git` und `scoop install entire/entire`.
- Mac ohne Homebrew: `curl -fsSL https://entire.io/install.sh | bash` (landet in `~/.local/bin`; falls „command not found“: den Befehl ausführen, den das Skript am Ende anzeigt).

**Prüfen:** `entire version` zeigt eine Versionsnummer (getestet mit 0.11.4).

## 6. Repo klonen und Entire aktivieren

```bash
gh repo clone PiyushPapaya/TUMHackathon26
cd TUMHackathon26
entire enable --agent claude-code
entire status
```

**Prüfen:** `entire status` zeigt „● Enabled“ und „Agents · Claude Code“.

Warum `entire enable` bei jeder Person: Die Git-Hooks liegen in `.git/hooks/` und werden nicht mitgeklont. Zeigt `git status` danach `.claude/settings.json` oder `.entire/settings.json` als geändert: **nicht committen**, Piyush fragen.

## 7. OpenAI-Key eintragen

1. Credit-Code einlösen: Er kommt laut EHL-Plattform per E-Mail (einmalig pro Person). Einlösen auf https://platform.openai.com unter *Settings → Billing*.
2. Key erzeugen: https://platform.openai.com/api-keys → *Create new secret key*. Nur einmal sichtbar, sofort kopieren.
3. `.env` anlegen:

| Windows (PowerShell) | Mac (Terminal) |
|---|---|
| `Copy-Item .env.example .env` | `cp .env.example .env` |

4. `.env` im Editor öffnen und hinter `OPENAI_API_KEY=` deinen Key einfügen. **Diese Datei nie committen, nie in Discord posten.**

**Prüfen:** `git check-ignore -v .env` zeigt eine Zeile aus `.gitignore`. Dann ist die Datei vor Git geschützt.

## 8. Claude Code starten

```bash
claude
```

Erster Satz an Claude:

> Starte meine Sitzung. Ich bin <dein Vorname>.

Claude führt dann den Skill `sitzung-start` aus: neuester Stand, eigener Branch, deine Aufgaben.

## 9. Discord

https://discord.gg/4UDNd5TAg beitreten. Dort kommen Ankündigungen der Orga.

## Troubleshooting

| Fehlermeldung / Problem | Ursache | Lösung |
|---|---|---|
| `winget` nicht gefunden | altes Windows | „App Installer“ im Microsoft Store aktualisieren, oder Installer von der Herstellerseite |
| `git`, `gh`, `node` oder `entire`: „nicht erkannt“ / „command not found“ | PATH noch alt | Terminal schließen und neu öffnen; danach Rechner neu starten |
| `python` öffnet den Microsoft Store (Windows) | Windows-Platzhalter | Python per winget installieren, dann Einstellungen → Apps → App-Ausführungsaliase → `python.exe` aus |
| `Permission denied (publickey)` | SSH statt HTTPS | `gh auth login` erneut mit **HTTPS**; `gh repo clone` benutzen |
| `remote: Permission to … denied` | Einladung nicht angenommen | E-Mail-Einladung annehmen (Schritt 1) |
| PowerShell: „Ausführung von Skripts ist deaktiviert“ | Execution Policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, dann erneut |
| Claude meldet „Entire CLI is enabled but not installed or not on PATH“ | Entire fehlt oder PATH alt | Schritt 5, dann neues Terminal und `claude` neu starten |
| `git commit` hängt ewig | Entire wartet auf „Link this commit?“ | `.entire/settings.json` muss `"commit_linking": "always"` enthalten (ist im Repo); `git pull`; sonst `entire doctor` |
| `push` zeigt keine `[entire] Pushing … checkpoint` | keine Session aktiv beim Commit / Hooks fehlen | `entire status`; `entire enable --agent claude-code --force` |
| „BLOCKIERT durch .claude/hooks/git-schutz.sh“ | gefährlicher Git-Befehl | Absicht! Claude erklärt den sicheren Weg |
| PR: „Merging is blocked“ | Ruleset: nur Piyush merged | Normal. Piyush anpingen |
| `npm install` scheitert hinter Firmen-Proxy | Netzwerk | Handy-Hotspot oder Event-WLAN |
