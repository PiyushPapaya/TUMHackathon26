# Scope-Wächter: Messung (W-C12) (mit schärferem Prompt und Code-Wächter)

Erzeugt mit `python tests/pfad_c/scope_eval.py [Läufe]`. 48 erfundene Befunde (`scope_cases.py`), keine BMW-Daten.
8 unabhängige Läufe der echten Ableitung (anderer Szenarioname = neuer Aufruf an die KI). Zahlen je Lauf, durch Schrägstrich getrennt.

| Klasse | Fälle | erkannt (verworfen) | durchgerutscht |
|---|---|---|---|
| Regulatorik / Zulassung | 9 | 8 / 8 / 9 / 9 / 9 / 9 / 8 / 9 | 1 / 1 / 0 / 0 / 0 / 0 / 1 / 0 |
| Engineering-Spezifikation | 9 | 9 / 9 / 9 / 9 / 9 / 9 / 9 / 8 | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| Preis / Business-Case | 10 | 8 / 10 / 9 / 10 / 8 / 9 / 8 / 9 | 2 / 0 / 1 / 0 / 2 / 1 / 2 / 1 |

**Out-of-scope gesamt (28 Fälle):** erkannt 25 / 27 / 27 / 28 / 26 / 27 / 25 / 26, durchgerutscht 3 / 1 / 1 / 0 / 2 / 1 / 3 / 2.
**Gegenprobe (20 normale Kundenwünsche):** zu Unrecht verworfen 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0.

## Grenzen
- 48 Fälle, von uns formuliert: Größenordnung, kein Konfidenzintervall.
- Die meisten Fälle sind eindeutig formuliert, nur 8 sind knifflig (Preis ohne Preiswort, Technik-Nähe mit echtem Kundenwert); echte Befunde sind unschärfer.
- Die KI schwankt von Lauf zu Lauf; darum mehrere Läufe statt einer Zahl.
