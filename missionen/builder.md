# Mission: Builder

**Ziel:** Pipeline und App laufen auf echten Daten, und alles von den anderen Missionen kommt hinein.
**Warum für die Demo:** Ohne klickbare App gibt es nichts zu zeigen. Alles andere ist Zuarbeit dafür.

## Das entscheidest du selbst

- In welcher Reihenfolge du Tickets abarbeitest (Arbeitsbücher in `docs/pfade/`).
- Was gekürzt wird, wenn es eng wird (Kürzungsliste in `docs/06_roadmap.md`).

## Schritt für Schritt

1. `git switch main && git pull --no-rebase origin main`
2. App starten (siehe `START_HIER.md`), Backend und Frontend.
3. Nimm das nächste offene Ticket aus deinem Arbeitsbuch. Prompt kopieren, Claude baut zuerst den Test, dann den Code.
4. Beweise jedes "Fertig, wenn ..." mit Befehl und Ausgabe: `python -m pytest -q`, `cd src/frontend && npm run lint && npm run build`.
5. Skill `sync`: committen und auf `main` pushen.
6. Wenn jemand eine Mission fertig hat (Tabelle, Prompt, Bild), baue sie ein und sage ihm, wo sie jetzt steht.

## Werkzeuge

Claude Code (mit den Skills `sitzung-start`, `sync`, `demo-check`) · `pytest` · `npm` · die API-Doku `src/shared/API.md`.

## Befehle zum Kopieren

```
python -m pytest -q
python src/backend/pipeline.py --scenario G60-US --stage requirements
uvicorn main:app --app-dir src/backend --port 8000
cd src/frontend && npm run dev
```

## Fertig, wenn …

- [ ] Pipeline G60-US läuft von Belegen bis zum Bundle ohne Fehler
- [ ] Cockpit zeigt Liste, Detail, Entscheiden mit Pflicht-Begründung, Audit-Seite
- [ ] `python -m pytest -q` grün, `npm run build` grün, CI grün
- [ ] Frischer Klon läuft nach Anleitung (Skill `demo-check`)

## Ablage

Code in `src/`, Ergebnisse in `data/processed/` und `outputs/`.
