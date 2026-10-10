# Baukasten: die App ändern ohne Code

In diesem Ordner liegen fünf kleine Textdateien. Die App liest sie. Wenn du sie änderst, ändert sich die App. Du brauchst dafür kein Programmieren.

| Datei | Was du damit änderst | Beispiel |
|---|---|---|
| `texte.json` | Alle Überschriften und Erklärsätze der Werkbank (auf Englisch, weil die App englisch ist) | Den Satz unter „Duel“ besser formulieren |
| `features.json` | Welche Werkzeuge in der App erscheinen (`true` = an, `false` = aus) | Den Swipe-Modus für die Demo ausschalten |
| `farben.json` | Die Farben der Werkbank | Die Akzentfarbe ändern |
| `stimmen.json` | Welche Kundenzitate ganz oben angepinnt werden, mit deiner Notiz | Das stärkste Zitat aus der Daten-Detektiv-Mission |
| `duell.json` | Wie viele Runden das Duell hat und welche Frage oben steht | 6 statt 8 Runden |

## So änderst du etwas (5 Minuten)

1. Öffne die Datei in VS Code oder direkt auf GitHub (Stift-Symbol „Edit“).
2. Ändere **nur den Text zwischen den Anführungszeichen** rechts vom Doppelpunkt. Links (z. B. `"title":`) bleibt, wie es ist.
3. Speichern. Läuft die App bei dir (`npm run dev`), siehst du die Änderung sofort.
4. Prüfen lassen: Sag Claude „Prüf den Baukasten“. Claude startet dann `python -m pytest tests/test_baukasten.py -q`. Grün heißt: Alles ist in Ordnung.
5. Committen und pushen lässt du Claude machen (Skill `sync`).

## Die drei häufigsten Fehler

| Fehler | Beispiel | Richtig |
|---|---|---|
| Anführungszeichen vergessen | `"title": Workbench` | `"title": "Workbench"` |
| Komma vergessen oder zu viel | `"duel": true "arena": true` | `"duel": true, "arena": true` (nach dem letzten Eintrag **kein** Komma) |
| Anführungszeichen im Text | `"note": "she said "terrible""` | `"note": "she said 'terrible'"` |

Der Test findet alle drei. Wenn er rot ist, zeigt er die Zeile.

## Ein Zitat anpinnen (stimmen.json)

Die ID findest du in der App unter jedem Zitat (z. B. `EV-G60-0019`). Kopiere sie in `stimmen.json`:

```json
{
  "team_picks": [
    { "evidence_id": "EV-G60-0019", "note": "Safety, not taste." },
    { "evidence_id": "EV-G60-0130", "note": "Wants buttons that click." }
  ]
}
```

## Farben (farben.json)

Farben sind Hex-Codes, also `#` und sechs Zeichen. Einen Farbwähler findest du, wenn du „color picker“ googelst. Achte auf Kontrast: Text muss auf einem Beamer aus fünf Metern lesbar bleiben. `ink` ist die Textfarbe, `paper` der Hintergrund, `accent` die Farbe der Buttons.

## Warum es diesen Ordner gibt

Die meisten im Team programmieren nicht. Trotzdem sollen alle die App mitgestalten können: Texte, Farben, welche Features in die Demo kommen und welche Zitate die Jury sieht. Das sind echte Produktentscheidungen.
