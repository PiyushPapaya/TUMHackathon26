# Mission: Daten-Detektiv

**Ziel:** Du findest die 15 bis 25 stärksten Kundenthemen im G60-US-Feedback, wählst die besten Zitate und schreibst selbst Anforderungsentwürfe. Wir vergleichen sie mit dem, was die KI findet.
**Warum für die Demo:** Das ist unsere "eine Zahl" für Vertrauen. Beispiel: "Von deinen 20 Themen hat die KI 17 auch gefunden." Das beweist der Jury, dass die KI nicht erfindet.

## Das entscheidest du selbst

- Was zählt als "stark": viele Kommentare, harte Wörter ("terrible", "dangerous") oder viele Quellen?
- Welche Kommentare sind keine Kundenstimmen? In Source B stehen viele Servicenotizen ("Writer explained ..."). Nimmst du sie mit oder nicht, und warum?
- Welche Zitate sind die besten? Kurz, klar, ohne Namen.

## Schritt für Schritt

1. Öffne `data/raw/G60_feedback_hackathon.xlsx` in Excel. Blatt `Feedback_Explorer`.
2. Filter: Spalte `Country` = US. Filter `Feedback Type` ≠ Likes.
3. Zähle pro `Vfc level2 Name` (Pivot-Tabelle: Zeilen = Thema, Werte = Anzahl von ID). Sortiere absteigend. Die Top-Themen kennst du schon aus `visuals/charts/01_top_beschwerden_g60_us.png`.
4. Nimm die 20 größten Themen. Pro Thema: lies 10 Kommentare. Notiere ein Muster in einem Satz.
5. Wähle pro Thema 1 bis 2 Zitate. Schreib die **ID** dazu (z. B. `G60-0019`). Ohne ID zählt das Zitat nicht.
6. Schreib pro Thema einen Anforderungsentwurf: *Was muss das Auto können, und woran messen wir es?* (Vorlage unten).
7. Warte, bis die Pipeline echte Befunde hat (Ticket A5/A6 von Aditya). Dann vergleichen: Welche deiner Themen hat die KI auch? Welche hat sie extra? Was hat sie übersehen?

## Vorlage

| Thema | Anzahl | Muster in einem Satz | Zitat-ID | Anforderungsentwurf | Messkriterium |
|---|---|---|---|---|---|
| Center console, front | | Tasten zu nah beieinander | G60-0019 | Start/Stop-Taste ist nicht mit anderen Tasten verwechselbar | ... |

## Werkzeuge

Excel (Pivot-Tabelle und Filter) · Claude: "Fasse diese 10 Kommentare in einem Satz zusammen" · Claude Code für schnelles Zählen:

> Zähle in `data/raw/G60_feedback_hackathon.xlsx` für Country US und Feedback Type ungleich Likes die Kommentare pro `Vfc level2 Name` und gib mir die Top 25 als CSV in `werkstatt/<name>/themen.csv`. Ich will damit meine Excel-Zahlen gegenprüfen.

## Fertig, wenn …

- [ ] Tabelle mit 15 bis 25 Themen, jedes mit Anzahl, Muster und mindestens einer Zitat-ID
- [ ] Zu jedem Thema ein Anforderungsentwurf mit Messkriterium
- [ ] Eine Zeile pro Entscheidung in `notizen.md` ("Source B ausgeschlossen, weil ...")
- [ ] Vergleich mit der KI: wie viele Themen deckungsgleich

## Ablage und Weg in die App

Datei `werkstatt/<name>/daten-detektiv.csv` (Spalten wie in der Vorlage). Aditya nutzt sie für die Eval-Stichprobe (Tickets A9/A10), der Vergleich landet als Zahl auf der Folie "Vertrauen" und in `tests/eval/REPORT.md`. Dennis nutzt die Entwürfe, um die KI-Texte zu bewerten.
