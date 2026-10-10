---
name: sync
description: Speichert die Arbeit, holt den neuesten Stand von main und pusht direkt auf main. Claude führt das AUTOMATISCH nach jedem fertigen, getesteten Schritt aus; zusätzlich bei „speicher meine Arbeit“, „push“, „hol den neuesten Stand“, „ich bin fertig“.
---

# Sync: committen, main holen, auf main pushen

Wir arbeiten alle direkt auf `main` (kein Branch, kein PR). Darum muss jeder Push klein, getestet und aktuell sein.
Erkläre **vor jedem Git-Befehl in einem Satz**, was er tut. Nicht um Erlaubnis fragen, außer bei Konflikten.

## Wann (automatisch)

Nach **jedem logischen Schritt**, der fertig und geprüft ist (Funktion + Test grün), spätestens alle 30-45 Minuten.
Nicht pushen, wenn Tests/Lint rot sind; dann erst reparieren.

## Schritte

1. **Prüfen** (nur was existiert): `ruff check src/backend tests` · `python -m pytest -q` · bei Frontend-Änderung `cd src/frontend && npm run lint && npm run build` · `python scripts/secret_scan.py`.
2. **Änderungen zeigen:** `git status --short`. Nur Dateien im eigenen Pfad (Tabelle in `CLAUDE.md`) stagen. Niemals `data/`, `.env` oder BMW-Daten.
3. **Gezielt stagen:** `git add <dateien>` (nicht `git add .`).
4. **Committen** mit Ownership-Sprache: `Was, weil Warum; verworfen: Y; geprüft: <Befehl + Ergebnis>`. Commit **aus der laufenden Claude-Session** (sonst kein Entire-Checkpoint).
5. **Neuesten Stand holen:** `git pull --no-rebase origin main` (holt die Arbeit der anderen und führt sie per Merge zusammen; kein Rebase).
6. **Konflikt?** Nicht raten, nicht wegräumen. Konflikt zeigen, beide Versionen einfach erklären, Person fragen. Fremder Code → „Hol Piyush.“ Danach Tests erneut (Schritt 1).
7. **Nach dem Pull kurz prüfen:** `python -m pytest -q` (die anderen könnten etwas geändert haben). Rot wegen fremder Änderung → nicht pushen, Person + Lead informieren.
8. **Pushen:** `git push origin main`. Erwartet: `[entire] Pushing N checkpoint ref(s) to origin… done`. Abgelehnt („fetch first“)? → zurück zu Schritt 5.

## Ausgabe an die Person (kurz)

```
Gespeichert und auf main: <Commit-Titel> (<kurzer Hash>)
Geprüft: <Befehle + Ergebnis>
Entire-Checkpoints gepusht ✅/❌
```
