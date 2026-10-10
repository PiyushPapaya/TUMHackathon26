---
name: pitch-prep
description: Schärft den Pitch, führt eine Probe mit Zeitmessung durch und drillt Teammitglieder mit Jury-Fragen. Benutzen bei „Pitch üben“, „Probe“, „frag mich Jury-Fragen“, „ist der Pitch zu lang“ und So 10:00.
---

# Pitch-Vorbereitung

Rahmen: **6 Minuten inklusive Fragen, strikt.** Ziel: ~3:30 Pitch mit Live-Demo, ~2:30 Fragen (`docs/pitch/PITCH.md`).

## Modus A: Pitch schärfen

1. `docs/pitch/PITCH.md`, `README.md`, `docs/CHALLENGE.md` lesen.
2. Prüfen gegen die Winning Patterns:
   - Hook mit konkreter Person und Zahl in den ersten 20 s?
   - **Eine** Zahl mit Baseline und Messmethode?
   - Demo zeigt genau einen Kernflow?
   - Jedes Bewertungskriterium des Briefs wird mindestens einmal hörbar adressiert?
   - Ehrliche Grenze genannt?
3. Wortzahl schätzen: ~130 Wörter pro Minute gesprochen. Über 3:30 → **kürzen, Liste was raus soll**.
4. Vorschläge als Diff für `docs/pitch/PITCH.md` (Rahmen: Lead; Pfade liefern je 1 Folie).

## Modus B: Probe mit Stoppuhr

1. Startzeit merken (`date +%T` bzw. PowerShell `Get-Date -Format T`), Person spricht, Endzeit nehmen.
2. Pro Block (Hook, Problem, Demo, Ergebnis, Tech, Ask) Soll vs. Ist als Tabelle.
3. Feedback: max. 3 Punkte, konkret („Demo-Schritt 3 weglassen spart 25 s“).

## Modus C: Jury-Drill

1. Fragen aus `docs/pitch/PITCH.md` (Jury-Fragen) **zufällig** wählen, dazu 2 eigene aus dem aktuellen Code/README.
2. Eine Frage nach der anderen stellen, Antwort abwarten.
3. Bewerten: Antwort zuerst? Unter 20 s? Mit Beleg (Zahl, Datei, Entscheidung)? Ehrlich?
4. Jede Person muss sagen können: **„Unser Produkt in 2 Sätzen“** (aus `docs/PLAN.md` §1).
5. Schwache Antworten → bessere Formulierung vorschlagen und in `docs/pitch/PITCH.md` ergänzen lassen.

## Ausgabe

Kurze Tabelle: Block / Soll / Ist / Fix, oder: Frage / Note (1-3) / bessere Antwort.
