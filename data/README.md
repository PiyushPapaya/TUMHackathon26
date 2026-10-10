# data/ (lokal, nicht im Git)

Alles hier außer dieser Datei ist per `.gitignore` gesperrt, weil das Repo öffentlich ist
und die BMW-Daten vertraulich sind.

| Ordner/Datei | Inhalt | Wer erzeugt |
|---|---|---|
| `raw/` | Originaldateien von BMW (Feedback-Excel, Studien, Absatz, Optionslisten-PDF) | per USB/Drive von Piyush kopieren |
| `processed/<szenario>/*.json` | Ergebnisse je Pipeline-Stufe | `python src/backend/pipeline.py --scenario G60-US` |
| `processed/<szenario>.json` | Bundle, das die App beim Start lädt | Stufe `bundle` |
| `cache/` | LLM-Antworten (spart Credits, Demo ohne Netz) | automatisch durch `core/llm.py` |
| `audit.db` | Prüfpfad (SQLite) | automatisch beim Start des Backends |

Erwartete Dateien in `raw/`:
`F70_feedback_hackathon.xlsx`, `G60_feedback_hackathon.xlsx`, `G70_feedback_hackathon.xlsx`,
`F70_G60_G68_G70_customer_studies.xlsx`, `sales_volumes.xlsx`,
`F70_OptionList.PDF`, `G60_OptionList.PDF`, `G70_OptionList.PDF`.

Ohne diese Dateien laufen Backend und Tests trotzdem: Dann nimmt die App das synthetische
Beispiel aus `src/shared/beispiele/`.
