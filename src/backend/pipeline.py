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
  python src/backend/pipeline.py --scenario all --out data/regen  # Neulauf getrennt von der Demo
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
    """Ergebnis einer früheren Stufe. Fehlende Eingaben niemals durch fremde Beispieldaten ersetzen."""
    real = OUT_DIR / scenario_id / f"{stage}.json"
    if not real.exists():
        raise FileNotFoundError(f"{scenario_id}: {stage}.json fehlt; zuerst die vorgelagerte Stufe ausführen.")
    return json.loads(real.read_text(encoding="utf-8"))


def external_stage(cfg: dict, stage: str) -> list:
    # Ohne konfigurierte Connectoren gibt es ausdrücklich keine externen Daten.
    if not cfg.get("nhtsa") and not cfg.get("fueleconomy"):
        return _real_stage(cfg["id"], stage, [])
    return read_stage(cfg["id"], stage)


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
        from evidence_internal.opportunities import opportunities_from_evidence
        from evidence_internal.taxonomy import unmapped_topics
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence")]
        context = {**load_context(cfg, RAW_DIR), "unmapped_topics": unmapped_topics(evidence),
                   "opportunities": opportunities_from_evidence(evidence)}
        _write(sid, "context", context)
    elif stage == "signals":  # Pfad A, KI autonom
        from evidence_internal.conflicts import segment_conflicts
        from evidence_internal.signals import _build, extract_signals, signal_groups
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence")]
        _write(sid, "signals", extract_signals(scenario, evidence))
        raw_signals, _ = _build(scenario, evidence)
        context = {**read_stage(sid, "context"),
                   "segment_conflicts": segment_conflicts(raw_signals, evidence, signal_groups(scenario, evidence))}
        _write(sid, "context", context)
    elif stage == "web":  # Pfad B, KI autonom mit Quellen
        from evidence_external.claims import FAILED_QUESTIONS
        from evidence_external.web_research import research
        failed_before = len(FAILED_QUESTIONS)
        signals = [Signal(**s) for s in read_stage(sid, "signals")]
        web_evidence, web_signals = research(scenario, signals)
        failed = len(FAILED_QUESTIONS) - failed_before
        if failed and not web_evidence:
            raise RuntimeError(f"All web research failed ({failed} questions); existing stage files were preserved.")
        _write(sid, "web_evidence", web_evidence)
        _write(sid, "web_signals", web_signals)
        if failed:
            context = read_stage(sid, "context")
            context.setdefault("warnings", []).append(f"Web research incomplete: {failed} questions failed.")
            _write(sid, "context", context)
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
        signals = internal + [Signal(**s) for s in
                              read_stage(sid, "web_signals") + external_stage(cfg, "external_signals")]
        evidence = [Evidence(**e) for e in read_stage(sid, "evidence") + read_stage(sid, "web_evidence")
                    + external_stage(cfg, "external_evidence")]
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
    evidence = read_stage(sid, "evidence") + read_stage(sid, "web_evidence") + external_stage(cfg, "external_evidence")
    internal, counter = triangulated_internal(sid)  # sonst sähe die App "web" nur an den reinen Web-Befunden
    signals = [s.model_dump(mode="json") for s in internal] + read_stage(sid, "web_signals")
    signals += external_stage(cfg, "external_signals")
    reqs = [Requirement(**r).model_dump(mode="json") for r in read_stage(sid, "requirements")]
    used = {e for s in signals for e in s["evidence_ids"]}  # nur zitierte Belege an die App geben
    used.update(i for ids in counter.values() for i in ids)
    context = _real_stage(sid, "context", {})
    used.update(i for conflicts in context.get("segment_conflicts", {}).values()
                for conflict in conflicts for i in conflict.get("evidence_ids", []))
    cov = data_coverage(evidence)
    if context.get("sales", {}).get("volume_2030") is not None:
        cov["sales"] = max(cov["sales"], 1)
    from requirements_engine.offer_check import load_offer_for
    option_file = cfg.get("data", {}).get("option_list_file")
    offer, _ = load_offer_for({"option_list_path": str(RAW_DIR / option_file) if option_file else None})
    cov["options"] = max(cov["options"], len(offer))
    bundle = {
        "scenario": {**{k: v for k, v in cfg.items() if k != "data"}, "data_coverage": cov},
        "funnel": {"evidence": len(evidence), "signals": len(signals), "requirements": len(reqs), "approved": 0,
                   "generated_at": datetime.now(UTC).isoformat(timespec="seconds")},
        "weights": {}, "evidence": [e for e in evidence if e["id"] in used], "signals": signals, "requirements": reqs,
        # Ältere Läufe haben keine discarded.json; dann leer, statt auf die Beispieldatei zurückzufallen.
        "discarded": _real_stage(sid, "discarded", []),
        "context": {**{k: v for k, v in context.items() if k != "opportunities"}, "counter_evidence": counter},
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


def main(argv: list[str] | None = None) -> None:
    global OUT_DIR
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", required=True, help="z. B. G60-US (Datei in config/scenarios/) oder all")
    parser.add_argument("--stage", choices=[*STAGES, "all"], default="all")
    # Getrennter Ordner: Neuerzeugung prüfen, ohne die Demo-Bundles (und ihre PM-Verläufe) zu überschreiben.
    parser.add_argument("--out", type=Path, default=None, help="Ausgabeordner statt data/processed")
    args = parser.parse_args(argv)
    if args.out:
        OUT_DIR = args.out
    ids = all_scenario_ids() if args.scenario == "all" else [args.scenario]
    stages = STAGES if args.stage == "all" else [args.stage]
    results = [run_scenario(load_config(sid), stages) for sid in ids]
    print_summary(results)
    sys.exit(1 if any(r["failed"] for r in results) else 0)


if __name__ == "__main__":
    main()
