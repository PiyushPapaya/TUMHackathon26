# config/

A **scenario** is one vehicle in one market. Each scenario is one JSON file. Adding a new car or
market means adding a file here, not writing code.

| File | Scenario |
|---|---|
| `scenarios/G60-US.json` | 5 Series Sedan (G60), USA. **Main demo.** |
| `scenarios/F70-EU.json` | 1 Series (F70), Europe |
| `scenarios/G70-US.json` | 7 Series (G70), USA |
| `scenarios/G60-EU.json` | 5 Series Sedan (G60), Europe |
| `scenarios/G70-EU.json` | 7 Series (G70), Europe |
| `scenarios/G68-CN.json` | 5 Series long wheelbase (G68), China |
| `datasets.json` | Column and sheet names of the BMW files |

**New model or market:**

1. Run `python scripts/new_scenario.py` or copy an existing file.
2. Check countries, the study column, source files and competitors.
3. Run `python src/backend/pipeline.py --scenario <id>`.
