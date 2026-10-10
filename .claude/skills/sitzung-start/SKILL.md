---
name: sitzung-start
description: Startet die Arbeitssitzung eines Teammitglieds. Benutzen, wenn jemand „Starte meine Sitzung“, „Ich bin <Name>“, „Was soll ich machen?“ sagt oder eine neue Claude-Session im Repo beginnt.
---

# Sitzung starten

Ziel: Die Person arbeitet in 2 Minuten auf aktuellem Stand, im eigenen Branch, mit Entire, und kennt ihre nächste Aufgabe.

Erkläre **vor jedem Git-Befehl in einem Satz**, was er tut und warum. Antworte auf Deutsch, einfach.

## Schritte

1. **Name klären.** Falls unbekannt: fragen. Erlaubt: piyush, lasse, aditya, dennis, fabian.
2. **Steckbrief lesen:** `team/<name>.md` (Rolle, Ordner, Aufgaben).
3. **Uncommittete Änderungen?** `git status --short`. Wenn ja: zeigen und fragen, ob sie auf einen Branch sollen (`git switch -c <name>/rettung`), nie verwerfen.
4. **Neuester Stand:** `git switch main` und `git pull`.
5. **Thema fragen** („Woran arbeitest du jetzt, in 2-3 Worten?“), dann Branch anlegen: `git switch -c <name>/<thema-mit-bindestrichen>`. Existiert der Branch schon: `git switch <branch>` und `git merge origin/main`.
6. **Architektur lesen:** `docs/ARCHITEKTUR.md` und, falls gefüllt, `docs/research/CHALLENGE.md`.
7. **Entire prüfen:** `entire status`. Erwartet: „Enabled“ und „Claude Code“. Sonst: `entire enable --agent claude-code` vorschlagen (Anleitung `docs/SETUP.md` Schritt 5-6).
8. **Uhrzeit gegen `docs/ZEITPLAN.md`** halten: Welcher Meilenstein kommt als Nächstes?
9. **Offene Aufgaben:** `gh issue list --assignee @me --state open` (falls gh eingeloggt).

## Ausgabe an die Person (kurz)

```
Hallo <Name>! Stand: main aktuell, du bist auf Branch <branch>, Entire läuft ✅/❌.
Deine Rolle: <Rolle>. Du schreibst in: <Ordner> und workspace/<name>/.
Nächster Meilenstein: <Zeit> <Meilenstein>.
Deine nächsten Aufgaben:
1. …
2. …
Sag mir, womit wir anfangen.
```

## Regeln für die ganze Sitzung

- Nur in den Ordnern der Person und in `workspace/<name>/` schreiben. Fremde Ordner: erklären und fragen.
- Ownership-Sprache in Commits: „Was + Warum“.
- Alle 1-2 Stunden: Skill `sync-und-pr`.
