---
name: abgabe
description: Führt das Abgabe-Runbook Schritt für Schritt aus und blockiert bei jedem fehlgeschlagenen Check. Benutzen bei „Abgabe“, „submit“, „Code-Freeze“, „sind wir bereit“, So ab 10:30 oder für die Sicherheits-Abgabe Sa 22:00.
---

# Abgabe

Grundlage: `docs/ABGABE.md`. Bewertet wird **der Commit oben auf `main` beim Klick auf Submit**; ohne Entire-Checkpoints wird abgelehnt (`docs/hilfe/EHL-BEWERTUNG.md` §2, §7).

**Regel: Jeder ❌ blockiert.** Nicht weitergehen, bis er behoben oder von Piyush ausdrücklich akzeptiert ist. Nichts Destruktives am Repo.

## Schritte

1. **Code-Freeze ansagen** (So 10:30). Offene PRs auflisten: `gh pr list --state open`. Grüne PRs merged Piyush, der Rest bleibt zu.
2. **Lokal auf main:** `git switch main && git pull`.
3. **Checks aus `docs/ABGABE.md` der Reihe nach**, jeweils Befehl + Ergebnis + ✅/❌:
   1. `python scripts/secret_scan.py --historie`
   2. `git ls-files` ohne `.env`, `settings.local.json`, `.log`
   3. CI auf main grün: `gh run list --branch main --limit 1`
   4. Skill `demo-check` → Urteil mindestens „probably“, besser „yes“
   5. README: keine `[PLATZHALTER]`, Zahl oben, Demo- und Video-Link (`grep -n "\[[A-ZÄÖÜ-]*\]" README.md`)
   6. `python scripts/ehl_budget.py`: `src/` wird gelesen, Doku < 25 %
   7. `git ls-remote origin 'refs/entire/checkpoints/*'` → Anzahl > 0
   8. Checkpoints von allen: `git log origin/main --format='%an %(trailers:key=Entire-Checkpoint,valueonly)'`. Wer fehlt, committet aus seiner Claude-Session eine kleine Änderung (z. B. eigener Workspace), PR, Piyush merged.
   9. Live-URL und Backup-Video öffnen
   10. Pitch-Deck-PDF vorhanden
4. **Formular** (Piyush, ehl.gg): Texte aus `docs/ABGABE.md` (Projektname, Kurzbeschreibung mit Zahl, Repo-URL `https://github.com/PiyushPapaya/TUMHackathon26`, Deck, Demo, Tech-Tags). „Verify“ → grün → **Submit**.
5. **Nachweis:** `git rev-parse origin/main` + Uhrzeit + Screenshot lokal in `data/notizen/`.
6. **Nach jedem weiteren Merge bis 12:00:** „Update Submission“ klicken.

## Ausgabe

Checkliste mit ✅/❌ pro Punkt, dann entweder
`BEREIT ZUM SUBMIT: main = <sha>` oder `BLOCKIERT: <Punkt> → <nächster Schritt> → <wer>`.

Fehlermeldungen der Plattform: Tabelle „Notfälle“ in `docs/ABGABE.md`.
