"""Pipeline: Rohdaten -> Belege -> Befunde -> Webbelege -> Anforderungen (Owner: Lead).

Jede Stufe schreibt eine JSON-Datei nach data/processed/<szenario>/. Warum:
- Die 4 Pfade arbeiten parallel. Pfad C muss nicht auf Pfad A warten, sondern nimmt
  solange die Beispieldatei aus src/shared/beispiele/stufen/.
- Teure LLM-Stufen laufen einmal; die App liest nur das Ergebnis (schnelle Demo).
- Jede Stufe ist einzeln testbar und erklärbar ("Was hat die KI autonom gemacht?").

Aufruf (aus dem Repo-Root):
  python src/backend/pipeline.py --scenario G60-US              # alle Stufen
  python src/backend/pipeline.py --scenario G60-US --stage signals
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.models import Evidence, Requirement, Scenario, Signal  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
STAGE_EXAMPLES = ROOT / "src" / "shared" / "beispiele" / "stufen"
STAGES = ["evidence", "signals", "web", "requirements", "bundle"]


def load_config(scenario_id: str) -> dict:
    return json.loads((ROOT / "config" / "scenarios" / f"{scenario_id}.json").read_text(encoding="utf-8"))


def _write(scenario_id: str, stage: str, items: list | dict) -> None:
    folder = OUT_DIR / scenario_id
    folder.mkdir(parents=True, exist_ok=True)
    # Listen enthalten Modelle (evidence, signals ...) oder fertige Dicts (discarded)
    data = items
    if isinstance(items, list):
        data = [i.model_dump(mode="json") if hasattr(i, "model_dump") else i for i in items]
    (folder / f"{stage}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {stage}.json ({len(data)} Einträge)")


def read_stage(scenario_id: str, stage: str) -> list | dict:
    """Ergebnis einer früheren Stufe; fehlt es, die Beispieldatei (damit Pfade parallel arbeiten)."""
    real = OUT_DIR / scenario_id / f"{stage}.json"
    path = real if real.exists() else STAGE_EXAMPLES / f"{stage}.json"
    if path != real:
        print(f"  (Hinweis: {stage} fehlt für {scenario_id}, nehme Beispiel {path.name})")
    return json.loads(path.read_text(encoding="utf-8"))


def triangulated_internal(scenario_id: str) -> tuple[list[Signal], dict[str, list[str]]]:
    """Interne Befunde mit angehängten Webbelegen. Nur im Speicher, signals.json bleibt Pfad-A-Rohergebnis."""
    from evidence_external.triangulation import triangulate
    internal = [Signal(**s) for s in read_stage(scenario_id, "signals")]
    web = [Evidence(**e) for e in read_stage(scenario_id, "web_evidence")]
    return triangulate(internal, web)


def run_stage(stage: str, cfg: dict) -> None:
    sid = cfg["id"]
    scenario = Scenario(**cfg)
    print(f"[{sid}] Stufe {stage}")
    if stage == "evidence":  # Pfad A, autonom, ohne LLM
        from evidence_internal.loaders import load_all_evidence
        _write(sid, "evidence", load_all_evidence(cfg, RAW_DIR))
        from evidence_internal.context import load_context
        _write(sid, "context", load_context(cfg, RAW_DIR))
    elif stage == "signals":  # Pfad A, KI autonom
        from evidence_internal.signals import extract_signals
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence")]
        _write(sid, "signals", extract_signals(scenario, evidence))
    elif stage == "web":  # Pfad B, KI autonom mit Quellen
        from evidence_external.web_research import research
        signals = [Signal(**s) for s in read_stage(sid, "signals")]
        web_evidence, web_signals = research(scenario, signals)
        _write(sid, "web_evidence", web_evidence)
        _write(sid, "web_signals", web_signals)
    elif stage == "requirements":  # Pfad C, KI schlägt vor, Formel priorisiert
        from requirements_engine.derive import derive_all
        internal, counter = triangulated_internal(sid)
        signals = internal + [Signal(**s) for s in read_stage(sid, "web_signals")]
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence") + read_stage(sid, "web_evidence")]
        context = {**read_stage(sid, "context"), "option_list_path": str(RAW_DIR / cfg["data"]["option_list_file"]),
                   "counter_evidence": counter}  # Webbelege, die interne Befunde widerlegen (für die Challenge)
        requirements, discarded = derive_all(scenario, signals, evidence, context)
        _write(sid, "requirements", requirements)
        _write(sid, "discarded", discarded)  # Out-of-scope-Entwürfe: der PM soll sehen, was wir verworfen haben
    elif stage == "bundle":  # Lead: alles zusammen für die App
        bundle_stage(cfg)


def bundle_stage(cfg: dict) -> None:
    sid = cfg["id"]
    evidence = read_stage(sid, "evidence") + read_stage(sid, "web_evidence")
    internal, _ = triangulated_internal(sid)  # sonst sähe die App "web" nur an den reinen Web-Befunden
    signals = [s.model_dump(mode="json") for s in internal] + read_stage(sid, "web_signals")
    reqs = [Requirement(**r).model_dump(mode="json") for r in read_stage(sid, "requirements")]
    used = {e for s in signals for e in s["evidence_ids"]}  # nur zitierte Belege an die App geben
    # Ältere Läufe haben keine discarded.json; dann leer, statt auf die Beispieldatei zurückzufallen.
    discarded_file = OUT_DIR / sid / "discarded.json"
    discarded = json.loads(discarded_file.read_text(encoding="utf-8")) if discarded_file.exists() else []
    bundle = {
        "scenario": {k: v for k, v in cfg.items() if k != "data"},
        "funnel": {"evidence": len(evidence), "signals": len(signals), "requirements": len(reqs), "approved": 0},
        "weights": {}, "evidence": [e for e in evidence if e["id"] in used], "signals": signals, "requirements": reqs,
        "discarded": discarded,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{sid}.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {sid}.json (App lädt diese Datei beim Start)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", required=True, help="z. B. G60-US (Datei in config/scenarios/)")
    parser.add_argument("--stage", choices=[*STAGES, "all"], default="all")
    args = parser.parse_args()
    cfg = load_config(args.scenario)
    for stage in STAGES if args.stage == "all" else [args.stage]:
        run_stage(stage, cfg)


if __name__ == "__main__":
    main()
