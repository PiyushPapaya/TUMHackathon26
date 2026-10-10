# Scope-Wächter: Messung (W-C12) (Basis, nur Prompt)

Erzeugt mit `python tests/pfad_c/scope_eval.py [Läufe]`. 48 erfundene Befunde (`scope_cases.py`), keine BMW-Daten.
8 unabhängige Läufe der echten Ableitung (anderer Szenarioname = neuer Aufruf an die KI). Zahlen je Lauf, durch Schrägstrich getrennt.

| Klasse | Fälle | erkannt (verworfen) | durchgerutscht |
|---|---|---|---|
| Regulatorik / Zulassung | 9 | 7 / 9 / 9 / 9 / 7 / 6 / 7 / 9 | 2 / 0 / 0 / 0 / 2 / 3 / 2 / 0 |
| Engineering-Spezifikation | 9 | 9 / 9 / 9 / 9 / 9 / 9 / 9 / 9 | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| Preis / Business-Case | 10 | 2 / 10 / 9 / 9 / 2 / 9 / 10 / 9 | 8 / 0 / 1 / 1 / 8 / 1 / 0 / 1 |

**Out-of-scope gesamt (28 Fälle):** erkannt 18 / 28 / 27 / 27 / 18 / 24 / 26 / 27, durchgerutscht 10 / 0 / 1 / 1 / 10 / 4 / 2 / 1.
**Gegenprobe (20 normale Kundenwünsche):** zu Unrecht verworfen 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0.

## Grenzen
- 48 Fälle, von uns formuliert: Größenordnung, kein Konfidenzintervall.
- Die meisten Fälle sind eindeutig formuliert, nur 8 sind knifflig (Preis ohne Preiswort, Technik-Nähe mit echtem Kundenwert); echte Befunde sind unschärfer.
- Die KI schwankt von Lauf zu Lauf; darum mehrere Läufe statt einer Zahl.
