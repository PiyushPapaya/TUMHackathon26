# data/

What is in Git and what stays on your machine (rules in `.gitignore`):

| Folder / file | Content | In Git? | Created by |
|---|---|---|---|
| `raw/` | BMW's original files (feedback Excel, study, sales, option list PDFs, brief) | **no** (since Oct 11): confidential challenge material | BMW |
| `processed/<scenario>/*.json` | Output of each pipeline step (contains customer quotes) | yes, approved by the organizers on Oct 11 | `python src/backend/pipeline.py --scenario G60-US` |
| `processed/<scenario>.json` | The bundle the app loads at start | yes | pipeline step `bundle` |
| `demo_cache/` | Checked LLM and web answers for the offline demo | yes | `core/llm.py`, picked by hand |
| `cache/` | Every LLM answer (saves credits) | yes | `core/llm.py`, automatically |
| `external_cache/` | Answers from the public NHTSA and EPA APIs (US government, public domain) | yes | `evidence_external/nhtsa.py`, `fueleconomy.py` |
| `audit.db` | The audit trail (SQLite, hash chain) | no | the backend, on start |
| `eval/` | Samples and human labels | no | `tests/eval/make_sample.py` |

Files expected in `raw/` if you re-run the pipeline: `F70_feedback_hackathon.xlsx`, `G60_feedback_hackathon.xlsx`,
`G70_feedback_hackathon.xlsx`, `F70_G60_G68_G70_customer_studies.xlsx`, `sales_volumes.xlsx`, `F70_OptionList.PDF`,
`G60_OptionList.PDF`, `G70_OptionList.PDF`. Column and sheet names are described in `config/datasets.json`.

**Privacy.** The raw BMW files are not in the repo. Without them, everything runs except the list-price
reference from the option list, which then shows "unavailable". `.env` (keys) and `audit.db` never go into Git.
`cache/`, `external_cache/` and `processed/` are marked `export-ignore`, so a zip download of the repo stays small.

Without `processed/`, backend and tests still run: the app then uses the synthetic example in
`src/shared/beispiele/`. Tests never use real BMW data, only tiny made-up samples.

With the shipped snapshots the app runs fully offline (`DEMO_MODUS=true`). A complete new pipeline run needs an
OpenAI key, or cache entries that match the current prompts. Missing steps fail with an error; they are never
replaced with example data.

`python scripts/refresh_bundles.py` adds current metadata, segment conflicts, public cache data and robustness
to existing snapshots without calling the LLM. IDs, texts and evidence levels stay the same.
