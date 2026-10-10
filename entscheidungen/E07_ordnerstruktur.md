# E07 Ordnerstruktur: umbauen oder ergänzen?

**Frage:** Der Auftrag schlägt eine neue Struktur vor (`docs/01_…`, `missionen/`, `werkstatt/`, `visuals/`, `app/`, `outputs/`). Im Repo gibt es schon eine funktionierende. Was machen wir?

## Heute

```
src/backend/…   Code, ein Ordner pro Pipeline-Stufe (evidence_internal, evidence_external, requirements_engine, core, api)
src/frontend/   Next.js (App, Komponenten)
src/shared/     Verträge (API.md, Beispieldaten)
tests/          Tests je Pfad
docs/           20+ Dateien, teils doppelt
workspace/<name>/ und team/<name>.md   (inklusive Fabian, der nicht dabei ist)
data/           raw, processed, cache (lokal)
```

## Optionen

| | Option | Plus | Minus |
|---|---|---|---|
| A | **Ergänzen, Code bleibt** | Neu dazu: `START_HIER.md`, `missionen/`, `visuals/`, `entscheidungen/`. `workspace/` wird zu `werkstatt/`. Docs bekommen eine klare Reihenfolge. Nichts bricht. | Struktur ist nicht 1:1 wie im Vorschlag (`app/` und `outputs/` fehlen). |
| B | **Komplett umbauen** wie vorgeschlagen | Sieht sauber aus. | `src/frontend` nach `app/` und `data/processed` nach `outputs/` brechen Import-Pfade, CI, `CLAUDE.md`, 5 Skills, Entire und die Besitzregeln. Bei 91 Tests und 17 Stunden bis zur Abgabe ein unnötiges Risiko. |
| C | Nur Docs aufräumen | Schnell. | Team bekommt keine Missionen und keine Werkstatt. |

## Was es für die Demo bedeutet

A und C ändern am Produkt nichts. B kann die Demo im schlechtesten Fall kaputt machen.

## Empfehlung

**A.** Docs neu ordnen (`docs/01_projekt.md` … `07_pitch.md`), alte Dateien nach `archiv/` verschieben statt löschen, `workspace/` in `werkstatt/` umbenennen (ohne Fabian). `outputs/` als Ordner für Exporte (CSV, Audit-Auszug) anlegen. `CLAUDE.md` bleibt, wird nur um die neuen Ordner ergänzt.

## Unsere Entscheidung
_(leer)_

## Warum
_(leer)_
