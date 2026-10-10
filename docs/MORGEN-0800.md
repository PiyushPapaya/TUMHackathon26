# Sa 07:30-09:30: Selbsttest vor dem Check-in (jede Person)

Ziel: Um 09:30 hat jede Person einen **offenen PR**. Dann funktioniert alles: Git, GitHub, Claude, Entire, Hooks.
Details zu jedem Schritt: [SETUP.md](SETUP.md). Windows = PowerShell, Mac = Terminal.

| # | Schritt | So sieht Erfolg aus | Wenn Fehler → tue |
|---|---|---|---|
| 1 | Programme da? `git --version`, `gh auth status`, `claude --version`, `entire version` | 4 Versionsnummern, gh „Logged in“ | fehlt etwas → SETUP.md Schritt 2-5; danach **neues Terminal** |
| 2 | Win: Git for Windows installiert (`git --version` zeigt „windows“) | ja | nein → `winget install --id Git.Git -e`, sonst laufen keine Hooks |
| 3 | `gh repo clone PiyushPapaya/TUMHackathon26` und `cd TUMHackathon26` (schon geklont: `git switch main` und `git pull`) | Ordner da, kein Fehler | „Permission denied“ → GitHub-Einladung annehmen |
| 4 | `entire enable --agent claude-code` | „Ready.“ | „not recognized“ → Entire neu installieren, Terminal neu öffnen |
| 5 | `entire status` | „● Enabled“ + „Claude Code“ | „Disabled“ → Schritt 4 mit `--force` |
| 6 | `.env` anlegen (Win `Copy-Item .env.example .env`, Mac `cp .env.example .env`), Key hinter `OPENAI_API_KEY=` | `git check-ignore -v .env` zeigt `.gitignore` | keine Ausgabe → **stopp**, Piyush fragen (Key darf nie ins Repo) |
| 7 | `claude` im Repo-Ordner starten | Claude-Begrüßung, keine Meldung „Entire CLI … not installed“ | Meldung da → Entire-PATH (Schritt 4), Claude neu starten |
| 8 | Zu Claude: „Starte meine Sitzung. Ich bin <Name>.“ | Branch `<name>/…`, Rolle und Aufgaben werden angezeigt | „Du stehst auf main“ → Claude legt Branch an, das ist ok |
| 9 | Zu Claude: „Schreib in workspace/<name>/notizen.md die Zeile: Setup-Test ok.“ | Datei geändert | Claude will woanders schreiben → „nur in meinem Workspace“ |
| 10 | Zu Claude: „Speicher meine Arbeit und mach einen PR.“ (Skill `sync-und-pr`) | PR-Link, CI `checks` grün, Push zeigt `[entire] Pushing … checkpoint` | Commit hängt → `git pull` (holt `commit_linking`), sonst `entire doctor` |
| 11 | PR-Link in die Gruppe posten | Piyush merged die Test-PRs gesammelt beim Check-in (Ausnahme vom Merge-Fenster) | „BLOCKIERT durch git-schutz.sh“ → gewollt, Claude erklärt den sicheren Weg |

**Mac-Unterschiede:** `python3` statt `python`; Entire per `brew install --cask entireio/tap/entire`.
**Hängt etwas länger als 10 Minuten:** Screenshot in die Gruppe, weitermachen; Piyush hilft beim Check-in.
**Nicht vergessen:** Laptop-Ladegerät, 09:00 Check-in vor Ort (sonst kann Piyush keine Challenge wählen).
