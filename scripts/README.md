# scripts/

Helper scripts for checks, data and the demo.

| Script | What it does |
|---|---|
| `start_demo.sh` | Starts backend and cockpit in demo mode |
| `verify_stack.py` | Offline check of all six scenarios: API, PM decisions, restart replay |
| `check_bundles.py` | Rule checks on the snapshots in `data/processed/` |
| `refresh_bundles.py` | Adds metadata to existing snapshots without calling the LLM |
| `new_scenario.py` | Creates a new model/market config in `config/scenarios/` |
| `make_view_examples.py` | Regenerates the example responses in `src/shared/beispiele/views/` |
| `migrate_signal_ids.py` | One-off migration to stable finding IDs |
| `secret_scan.py` | Looks for passwords and API keys. Run before every push |
| `ehl_budget.py` | Shows which files the hackathon's AI reviewer gets to see (200,000 character budget) |
