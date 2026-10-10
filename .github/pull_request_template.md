## Was

<!-- 1-3 Sätze in einfacher Sprache: Was kann man jetzt, was vorher nicht ging? -->

## Entscheidung + Warum

<!-- Ownership-Sprache: "Wir nehmen X, weil …; Y verworfen, weil …" -->

## Wie verifiziert

<!-- Konkret: Befehl + Ergebnis. z. B. "pytest: 12 passed", "lokal gestartet, Pipeline G60-US läuft, Detailseite zeigt Belege" -->

## Screenshots

<!-- Bei UI-Änderungen: vorher/nachher -->

## Betroffene Ordner

<!-- Nur eigene Ordner? Wenn nicht: warum, und wer ist Owner? -->

## Checkliste

- [ ] Nur Dateien in meinem Pfad geändert (Tabelle in `CLAUDE.md`)
- [ ] `git merge origin/main` gemacht, keine Konflikte
- [ ] Checks lokal grün (Lint, Tests, App startet)
- [ ] Keine Secrets, keine `.env` (`python scripts/secret_scan.py`)
- [ ] Neue Dependencies: keine / beantragt: <!-- welche, warum, Alternative -->
- [ ] `docs/ARCHITEKTUR.md` aktualisiert (bei Code)
- [ ] `docs/ARCHITEKTUR.md` (Entscheidungen) ergänzt, falls neue Designentscheidung
- [ ] Commit-Nachrichten auf Deutsch mit „Warum“
