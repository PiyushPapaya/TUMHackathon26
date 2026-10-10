# data/

Was hier im Git liegt und was lokal bleibt (Regeln in `.gitignore`):

| Ordner/Datei | Inhalt | Im Git? | Wer erzeugt |
|---|---|---|---|
| `raw/` | Originaldateien von BMW (Feedback-Excel, Studie, Absatz, Optionslisten-PDF, Brief) | **ja**, bewusste Entscheidung des Leads (10.10.): ein Ort für alle Quellen, Jury kann die Pipeline nachlaufen lassen | BMW |
| `demo_cache/` | geprüfte LLM-/Webantworten für die Offline-Demo | ja | `core/llm.py`, von Hand ausgewählt |
| `external_cache/nhtsa/` | Antworten der öffentlichen NHTSA-API (US-Behörde, gemeinfrei) | ja | `evidence_external/nhtsa.py` |
| `processed/<szenario>/*.json` | Ergebnisse je Pipeline-Stufe (enthalten Kundenzitate) | nein | `python src/backend/pipeline.py --scenario G60-US` |
| `processed/<szenario>.json` | Bundle, das die App beim Start lädt | nein | Stufe `bundle` |
| `cache/` | alle LLM-Antworten (spart Credits) | nein | automatisch durch `core/llm.py` |
| `audit.db` | Prüfpfad (SQLite, Hash-Kette) | nein | automatisch beim Start des Backends |

Dateien in `raw/`: `F70_feedback_hackathon.xlsx`, `G60_feedback_hackathon.xlsx`, `G70_feedback_hackathon.xlsx`,
`F70_G60_G68_G70_customer_studies.xlsx`, `sales_volumes.xlsx`, `F70_OptionList.PDF`, `G60_OptionList.PDF`,
`G70_OptionList.PDF`. Spalten- und Blattnamen beschreibt `config/datasets.json`.

Ohne `processed/` laufen Backend und Tests trotzdem: Dann nimmt die App das synthetische
Beispiel aus `src/shared/beispiele/`. Tests nutzen nie echte BMW-Daten, nur Mini-Daten.
