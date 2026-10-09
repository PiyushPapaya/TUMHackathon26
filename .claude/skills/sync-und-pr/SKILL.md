---
name: sync-und-pr
description: Speichert die Arbeit sicher, holt main herein und erstellt einen Pull Request. Benutzen bei „speicher meine Arbeit“, „mach einen PR“, „hol den neuesten Stand“, „ich bin fertig“ oder spätestens alle 1-2 Stunden.
---

# Synchronisieren und Pull Request

Erkläre **vor jedem Git-Befehl in einem Satz**, was er tut. Nichts Destruktives: kein force-push, kein reset --hard, kein rebase, kein --no-verify.

## Schritte

1. **Branch prüfen:** `git branch --show-current`. Auf `main`? Dann zuerst `git switch -c <name>/<thema>` (nimmt Änderungen mit).
2. **Änderungen zeigen:** `git status --short`. Nur Dateien im eigenen Bereich (Tabelle in `CLAUDE.md`) und `workspace/<name>/`. Fremde Dateien: nicht stagen, Person fragen.
3. **Secret-Check:** `python scripts/secret_scan.py` (Mac: `python3`). Fund → stoppen, Key widerrufen lassen, Piyush holen.
4. **Committen**, gezielt: `git add <dateien>` (nicht blind `git add .`), dann `git commit -m "<Was>, weil <Warum>"`. Läuft eine Claude-Session, verknüpft Entire den Commit automatisch.
5. **main hereinholen:** `git fetch origin` und `git merge origin/main`.
   - **Konflikt?** Nicht raten, nicht wegräumen. Konfliktstellen zeigen, beide Versionen in einfachen Worten erklären, fragen, welche gilt. Fremder Code betroffen → „Hol Piyush“. Abbrechen: `git merge --abort`.
6. **Checks lokal** (nur was existiert): `ruff check src/backend` · `python -m pytest tests -q` · `cd src/frontend && npm run lint && npm run build` · App startet. Ergebnis notieren.
7. **Pushen:** `git push -u origin <branch>`. Erwartet: `[entire] Pushing N checkpoint ref(s) to origin… done`.
8. **PR erstellen** mit Vorlage `.github/pull_request_template.md`:
   `gh pr create --base main --title "<Was>" --body-file <temp-datei>` (Body = ausgefüllte Vorlage: Was / Entscheidung + Warum / Wie verifiziert / Ordner / Checkliste). Reviewer `PiyushPapaya` hinzufügen (`--reviewer PiyushPapaya`), außer Piyush ist selbst Autor.
9. **CI abwarten:** `gh pr checks <nr> --watch`. Rot → Fehler zeigen, erklären, beheben, neu pushen.
10. **Merge-Fenster zeigen** (`docs/ZEITPLAN.md`): Sa jede volle Stunde 14-24 Uhr, So 08:00 / 09:00 / 10:00 / 10:30 (letzter). Aktuelle Uhrzeit holen (`date +%H:%M`, PowerShell `Get-Date -Format HH:mm`) und das nächste Fenster nennen. **5 Minuten vor dem Fenster** prüfen: CI grün und PR aktuell mit main (`gh pr view <nr> --json mergeStateStatus`; bei `BEHIND` Schritt 5 wiederholen und pushen). Wir holen main per Merge herein, nicht per Rebase.

## Ausgabe

```
PR #<nr>: <Titel> → <Link>
Checks: ✅/❌   Konflikte: keine/gelöst
Nächstes Merge-Fenster: <hh:mm>. Bis dahin grün und aktuell halten.
Nächster Schritt: Piyush reviewt und merged (nur er kann das).
```

**Nie selbst mergen.** Das Ruleset verhindert es ohnehin.
