# scripts/

Hilfsskripte für Prüfung, Daten und Demo.

| Skript | Was es tut |
|---|---|
| `secret_scan.py` | Sucht Passwörter und API-Keys. Vor jedem Push ausführen. |
| `ehl_budget.py` | Zeigt, welche Dateien die Jury-KI beim Review sieht (Budget 200.000 Zeichen). |
| `verify_stack.py` | Offline-Check aller sechs Szenarien: API, PM-Entscheidung, Neustart. |
| `check_bundles.py` | Prüft die Snapshots in `data/processed/` auf Regelverstöße. |
| `refresh_bundles.py` | Ergänzt Metadaten in vorhandenen Snapshots ohne LLM. |
| `new_scenario.py` | Legt eine neue Modell/Markt-Config in `config/scenarios/` an. |
| `make_view_examples.py` | Erzeugt die Beispielantworten in `src/shared/beispiele/views/`. |
| `migrate_signal_ids.py` | Einmalige Umstellung auf stabile Signal-IDs. |
| `start_demo.sh` | Startet Backend und Cockpit im Demo-Modus. |
