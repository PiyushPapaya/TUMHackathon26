"""Pipeline: Rohdaten -> Belege -> Befunde -> Webbelege + Behördendaten -> Anforderungen (Owner: Lead).

Jede Stufe schreibt eine JSON-Datei nach data/processed/<szenario>/. Warum:
- Die 4 Pfade arbeiten parallel. Pfad C muss nicht auf Pfad A warten, sondern nimmt
  solange die Beispieldatei aus src/shared/beispiele/stufen/.
- Teure LLM-Stufen laufen einmal; die App liest nur das Ergebnis (schnelle Demo).
- Jede Stufe ist einzeln testbar und erklärbar ("Was hat die KI autonom gemacht?").

Aufruf (aus dem Repo-Root):
  python src/backend/pipeline.py --scenario G60-US              # alle Stufen
  python src/backend/pipeline.py --scenario G60-US --stage signals
  python src/backend/pipeline.py --scenario all                 # alle Szenarien, Zusammenfassung am Ende
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.model_parts import coverage_badge  # noqa: E402
from core.models import Evidence, Requirement, Scenario, Signal  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
STAGE_EXAMPLES = ROOT / "src" / "shared" / "beispiele" / "stufen"
STAGES = ["evidence", "signals", "web", "external", "requirements", "bundle"]


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
    elif stage == "external":  # Pfad B, ohne LLM: Behördendaten (NHTSA, nur US-Szenarien mit "nhtsa")
        from evidence_external import fueleconomy
        from evidence_external.nhtsa import collect
        external_evidence, external_signals = collect(scenario)
        external_evidence += fueleconomy.collect(scenario)  # EPA-Reichweite der Wettbewerber (W-L10)
        _write(sid, "external_evidence", external_evidence)
        _write(sid, "external_signals", external_signals)
    elif stage == "requirements":  # Pfad C, KI schlägt vor, Formel priorisiert
        from requirements_engine.derive import derive_all
        internal, counter = triangulated_internal(sid)
        signals = internal + [Signal(**s) for s in read_stage(sid, "web_signals") + read_stage(sid, "external_signals")]
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence") + read_stage(sid, "web_evidence")
                    + read_stage(sid, "external_evidence")]
        option_file = cfg["data"].get("option_list_file")  # None bei Kaltstart-Märkten (G68-CN)
        option_path = str(RAW_DIR / option_file) if option_file else None
        context = {**read_stage(sid, "context"), "option_list_path": option_path,
                   "counter_evidence": counter}  # Webbelege, die interne Befunde widerlegen (für die Challenge)
        requirements, discarded = derive_all(scenario, signals, evidence, context)
        _write(sid, "requirements", requirements)
        _write(sid, "discarded", discarded)  # Out-of-scope-Entwürfe: der PM soll sehen, was wir verworfen haben
    elif stage == "bundle":  # Lead: alles zusammen für die App
        bundle_stage(cfg)


def _real_stage(scenario_id: str, stage: str, default):
    """Wie read_stage, aber OHNE Beispiel-Fallback: im Bundle dürfen nie Beispieldaten landen."""
    path = OUT_DIR / scenario_id / f"{stage}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def data_coverage(evidence: list[dict]) -> dict:
    """Belege je Quelle zählen (alle, nicht nur zitierte), daraus das Badge reich / dünn / Kaltstart."""
    counts = Counter(e["source_type"] for e in evidence)
    feedback = counts["feedback"]
    return {"feedback": feedback, "study": counts["study"], "sales": counts["sales"], "options": counts["option_list"],
            "web": counts["web"], "external": counts["external_stat"] + counts["feedback_external"],
            "badge": coverage_badge(feedback)}


def bundle_stage(cfg: dict) -> None:
    sid = cfg["id"]
    evidence = read_stage(sid, "evidence") + read_stage(sid, "web_evidence") + read_stage(sid, "external_evidence")
    internal, _ = triangulated_internal(sid)  # sonst sähe die App "web" nur an den reinen Web-Befunden
    signals = [s.model_dump(mode="json") for s in internal] + read_stage(sid, "web_signals")
    signals += read_stage(sid, "external_signals")
    reqs = [Requirement(**r).model_dump(mode="json") for r in read_stage(sid, "requirements")]
    used = {e for s in signals for e in s["evidence_ids"]}  # nur zitierte Belege an die App geben
    context = _real_stage(sid, "context", {})  # Absatz, unbekannte Themen (A15), Chancen-Karte (A17)
    bundle = {
        "scenario": {**{k: v for k, v in cfg.items() if k != "data"}, "data_coverage": data_coverage(evidence)},
        "funnel": {"evidence": len(evidence), "signals": len(signals), "requirements": len(reqs), "approved": 0,
                   "generated_at": datetime.now(UTC).isoformat(timespec="seconds")},
        "weights": {}, "evidence": [e for e in evidence if e["id"] in used], "signals": signals, "requirements": reqs,
        # Ältere Läufe haben keine discarded.json; dann leer, statt auf die Beispieldatei zurückzufallen.
        "discarded": _real_stage(sid, "discarded", []),
        "context": {k: v for k, v in context.items() if k != "opportunities"},
        "opportunities": context.get("opportunities", []),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{sid}.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {sid}.json (App lädt diese Datei beim Start)")


def all_scenario_ids() -> list[str]:
    return sorted(p.stem for p in (ROOT / "config" / "scenarios").glob("*.json"))


def run_scenario(cfg: dict, stages: list[str]) -> dict:
    """Stufen nacheinander; scheitert eine, stoppt NUR dieses Szenario (spätere Stufen bauen darauf auf)."""
    from evidence_external import claims
    claims.FAILED_QUESTIONS.clear()
    result = {"id": cfg["id"], "done": [], "failed": None, "web_failed": 0}
    for stage in stages:
        try:
            run_stage(stage, cfg)
        except Exception as err:  # Nachtlauf: ein Szenario darf die anderen nicht mitreißen
            result["failed"] = f"{stage}: {type(err).__name__}: {err}"
            print(f"  ! [{cfg['id']}] Stufe {stage} gescheitert: {err}", file=sys.stderr)
            break
        result["done"].append(stage)
    result["web_failed"] = len(claims.FAILED_QUESTIONS)
    bundle = OUT_DIR / f"{cfg['id']}.json"
    if "bundle" in result["done"] and bundle.exists():
        reqs = json.loads(bundle.read_text(encoding="utf-8"))["requirements"]
        result["requirements"] = len(reqs)
        result["levels"] = dict(sorted(Counter(r["evidence_level"] for r in reqs).items()))
    return result


def print_summary(results: list[dict]) -> None:
    print("\nZusammenfassung")
    for r in results:
        status = "OK " if not r["failed"] else "FEHLER"
        counts = f"{r.get('requirements', '-')} Anforderungen {r.get('levels', '')}"
        web = f", {r['web_failed']} Webfragen übersprungen" if r["web_failed"] else ""
        print(f"  {status} {r['id']:8} {counts}{web}" + (f"  <- {r['failed']}" if r["failed"] else ""))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", required=True, help="z. B. G60-US (Datei in config/scenarios/) oder all")
    parser.add_argument("--stage", choices=[*STAGES, "all"], default="all")
    args = parser.parse_args()
    ids = all_scenario_ids() if args.scenario == "all" else [args.scenario]
    stages = STAGES if args.stage == "all" else [args.stage]
    results = [run_scenario(load_config(sid), stages) for sid in ids]
    print_summary(results)
    sys.exit(1 if any(r["failed"] for r in results) else 0)


if __name__ == "__main__":
    main()
