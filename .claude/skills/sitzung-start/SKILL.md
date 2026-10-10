---
name: sitzung-start
description: Startet die Arbeitssitzung eines Teammitglieds. Benutzen, wenn jemand „Starte meine Sitzung“, „Ich bin <Name>“, „Was soll ich machen?“ sagt oder eine neue Claude-Session im Repo beginnt.
---

# Sitzung starten

Ziel: Die Person arbeitet in 2 Minuten auf aktuellem Stand, im eigenen Branch, mit Entire, und kennt den nächsten Schritt ihres Pfads.

Erkläre **vor jedem Git-Befehl in einem Satz**, was er tut und warum. Antworte auf Deutsch, einfach.

## Schritte

1. **Name und Pfad klären.** Namen: piyush (immer Lead), lasse, aditya, dennis, fabian. Pfad aus der Tabelle in `docs/PLAN.md` §6 lesen; ist sie leer: fragen (A, B, C oder D).
2. **Pfad-Datei lesen:** `docs/pfade/PFAD-<X>.md` (Lead: `docs/pfade/LEAD.md`): Ziel, Ordner, Schritte mit Zeitbox.
3. **Uncommittete Änderungen?** `git status --short`. Wenn ja: zeigen und fragen, ob sie auf einen Branch sollen (`git switch -c <name>/rettung`), nie verwerfen.
4. **Neuester Stand:** `git switch main` und `git pull`.
5. **Branch:** `git switch -c <name>/pfad-<x>-<thema>`. Existiert er schon: `git switch <branch>` und `git merge origin/main`.
6. **Setup prüfen:** `.venv` vorhanden? `pip install -r requirements.txt`. `.env` mit `OPENAI_API_KEY`? `data/raw/` gefüllt (sonst beim Lead holen; Tests laufen auch ohne)?
7. **Entire prüfen:** `entire status`. Erwartet: „Enabled“ und „Claude Code“. Sonst `entire enable --agent claude-code`.
8. **Uhrzeit gegen `docs/ZEITPLAN.md`:** Welcher Meilenstein kommt als Nächstes, und welcher Schritt der Pfad-Datei ist dran?
9. **Smoke-Test:** `python -m pytest -q` (muss grün sein, bevor die Person anfängt).

## Ausgabe an die Person (kurz)

```
Hallo <Name>! Stand: main aktuell, Branch <branch>, Entire läuft ✅/❌, Tests ✅/❌.
Dein Pfad: <X> – <Ziel in einem Satz>. Du schreibst in: <Ordner>.
Nächster Meilenstein: <Zeit> <Meilenstein>.
Dein nächster Schritt (Zeitbox <min>): <Schritt aus der Pfad-Datei>
Fertig, wenn: <Kriterium>
Vorschlag für deinen ersten Prompt: <Start-Prompt aus der Pfad-Datei, angepasst>
```

## Regeln für die ganze Sitzung

- Nur im eigenen Pfad schreiben (Tabelle in `CLAUDE.md`). Fremde Ordner: erklären und den Lead fragen.
- Ownership-Sprache in Prompts, Commits und PRs: Was + Warum + Verworfen + Wie prüfen.
- Alle 1-2 Stunden: Skill `sync-und-pr` (vor dem nächsten Merge-Fenster).
