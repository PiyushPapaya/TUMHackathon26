# Setup für Einsteiger

Du brauchst dafür keine Programmiererfahrung. Nimm dir etwa 30 Minuten Zeit und arbeite die Schritte der Reihe nach ab.

## 1. Einladung annehmen

Du bekommst eine E-Mail von GitHub („Invitation to collaborate"). Klick auf **Accept invitation**. Hast du noch keinen GitHub-Account, lege auf github.com einen an und schick deinen Username an Piyush.

## 2. Git installieren

- **Windows:** [git-scm.com/download/win](https://git-scm.com/download/win), Installer mit den Standardeinstellungen durchklicken.
- **Mac:** Terminal öffnen, `git --version` eingeben. Macht macOS einen Installationsvorschlag, bestätige ihn.

Prüfen: `git --version` zeigt eine Versionsnummer.

## 3. GitHub CLI installieren und einloggen

- Installation: [cli.github.com](https://cli.github.com) (Windows: `winget install GitHub.cli`, Mac: `brew install gh`).
- Einloggen: `gh auth login`. Wähle *GitHub.com*, *HTTPS*, *Login with a web browser* und folge den Anweisungen.

Prüfen: `gh auth status` zeigt „Logged in".

## 4. Claude Code installieren und einloggen

Du brauchst dafür ein **Claude-Pro-Abo** (oder höher).

- Installation laut offizieller Anleitung: [docs.claude.com/de/docs/claude-code](https://docs.claude.com/de/docs/claude-code/overview)
- Starten mit `claude` und mit deinem Claude-Account einloggen.

## 5. Entire CLI installieren (Sponsor-Tool)

Installiere die Entire CLI **genau nach der Anleitung des Sponsors** in deren Dokumentation: [PLATZHALTER: Link zur Entire-Doku hier eintragen]. Wir ergänzen den Befehl, sobald wir ihn geprüft haben.

## 6. Repo klonen

```bash
gh repo clone PiyushPapaya/TUMHackathon26
cd TUMHackathon26
```

## 7. Claude Code im Ordner starten

```bash
claude
```

Dein **erster Satz** an Claude:

> Lies CLAUDE.md und team/<dein Vorname>.md und sag mir, was meine Rolle ist.

Ersetze `<dein Vorname>` durch z. B. `lasse`, `aditya`, `dennis`, `fabian` oder `piyush`. Ab hier führt dich Claude durch alles Weitere, auch durch Git.

## Probleme?

Frag Claude („Das hat nicht funktioniert, hier ist die Fehlermeldung: …") oder hol Piyush.
