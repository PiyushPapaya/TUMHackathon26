## Was

<!-- 1-3 Sätze in einfacher Sprache: Was kann man jetzt, was vorher nicht ging? -->

## Entscheidung + Warum

<!-- Ownership-Sprache: "Wir nehmen X, weil …; Y verworfen, weil …" -->

## Wie verifiziert

<!-- Konkret: Befehl + Ergebnis. z. B. "pytest: 12 passed", "lokal gestartet, Upload mit demo/beispiel.pdf klappt" -->

## Screenshots

<!-- Bei UI-Änderungen: vorher/nachher -->

## Betroffene Ordner

<!-- Nur eigene Ordner? Wenn nicht: warum, und wer ist Owner? -->

## Checkliste

- [ ] Nur Dateien in meinem Zuständigkeitsbereich bzw. `workspace/<name>/` geändert
- [ ] `git merge origin/main` gemacht, keine Konflikte
- [ ] Checks lokal grün (Lint, Tests, App startet)
- [ ] Keine Secrets, keine `.env` (`python scripts/secret_scan.py`)
- [ ] Neue Dependencies: keine / beantragt: <!-- welche, warum, Alternative -->
- [ ] `docs/ARCHITEKTUR.md` aktualisiert (bei Code)
- [ ] `docs/pitch/JURY-FAQ.md` ergänzt (bei neuer Designentscheidung)
- [ ] Commit-Nachrichten auf Deutsch mit „Warum“
