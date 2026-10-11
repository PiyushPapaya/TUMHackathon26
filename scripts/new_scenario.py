"""Create a scenario config by copying an existing one.

Example:
    python scripts/new_scenario.py G70-CN --from G68-CN --derivative G70 --market CN

The script only creates `config/scenarios/<id>.json`. Dataset column/sheet names
stay in `config/datasets.json`; raw file names remain editable in the new JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "config" / "scenarios"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id", help="New scenario id, e.g. G70-CN")
    parser.add_argument("--from", dest="source", default="G60-US", help="Template scenario id")
    parser.add_argument("--derivative", help="Derivative code, default: part before '-' in id")
    parser.add_argument("--market", help="Market code, default: part after '-' in id")
    parser.add_argument("--model-name", help="Human readable model name")
    args = parser.parse_args()

    target = SCENARIOS / f"{args.id}.json"
    if target.exists():
        raise SystemExit(f"{target} exists; refusing to overwrite.")
    source = SCENARIOS / f"{args.source}.json"
    cfg = json.loads(source.read_text(encoding="utf-8"))
    derivative, _, market = args.id.partition("-")
    cfg["id"] = args.id
    cfg["derivative"] = args.derivative or derivative
    cfg["market"] = args.market or market or cfg.get("market", "")
    if args.model_name:
        cfg["model_name"] = args.model_name
    cfg["warnings"] = [
        "Neu erzeugtes Szenario: Datenfelder, Laender, Wettbewerber und Dateien pruefen.",
    ]
    target.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {target}")
    print(f"next: edit {target}, then run python src/backend/pipeline.py --scenario {args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
