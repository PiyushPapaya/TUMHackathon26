"""Vorhandene KI-Texte mit aktuellen Metadaten und Robustheit neu bündeln, ohne LLM.

Behält IDs, Titel, Evidenzstufen, Offer-Checks und Entscheidungen. Neue Texte/Webrecherche
brauchen weiterhin einen normalen Pipeline-Lauf. Aufruf: python scripts/refresh_bundles.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))

import pipeline  # noqa: E402
from core.models import Evidence, Requirement, Scenario, Signal  # noqa: E402
from evidence_internal.conflicts import segment_conflicts  # noqa: E402
from evidence_internal.context import load_context  # noqa: E402
from evidence_internal.opportunities import opportunities_from_evidence  # noqa: E402
from evidence_internal.segments import signal_segments  # noqa: E402
from evidence_internal.signals import _build, _study_link, signal_groups  # noqa: E402
from evidence_internal.taxonomy import unmapped_topics  # noqa: E402
from requirements_engine.robustness import compute_robustness  # noqa: E402


def refresh(sid: str) -> None:
    cfg = pipeline.load_config(sid)
    scenario = Scenario(**cfg)
    evidence = [Evidence(**e) for e in pipeline.read_stage(sid, "evidence")]
    by_id = {e.id: e for e in evidence}
    raw_signals, _ = _build(scenario, evidence)
    raw_by_id = {s.id: s for s in raw_signals}
    groups = signal_groups(scenario, evidence)
    signals = [Signal(**s) for s in pipeline.read_stage(sid, "signals")]
    for sig in signals:
        raw = raw_by_id.get(sig.id)
        if (raw is None or raw.kind != sig.kind or raw.category != sig.category
                or raw.mention_count != sig.mention_count):
            raise ValueError(f"{sid}: {sig.id} differs from raw grouping; rerun pipeline instead of reusing texts.")
        members = set(groups.get(sig.id, [])) | set(raw.evidence_ids)
        if any(eid not in members for eid in sig.evidence_ids):
            raise ValueError(f"{sid}: {sig.id} cites different source material; refresh refused.")
        sig.segments = signal_segments(groups.get(sig.id, []), by_id)
        sig.study_link = _study_link([by_id[i] for i in raw.evidence_ids if by_id[i].source_type == "study"])
    old_context = pipeline.read_stage(sid, "context")
    conflicts = segment_conflicts(raw_signals, evidence, groups)
    context = {**old_context, **load_context(cfg, pipeline.RAW_DIR),
               "unmapped_topics": unmapped_topics(evidence), "segment_conflicts": conflicts,
               "opportunities": opportunities_from_evidence(evidence)}
    reqs = [Requirement(**r) for r in pipeline.read_stage(sid, "requirements")]
    robustness = compute_robustness(reqs)
    for req in reqs:
        req.robustness = robustness[req.id]
        merged = []
        for signal_id in req.signal_ids:
            for conflict in conflicts.get(signal_id, []):
                if conflict not in merged:
                    merged.append(conflict)
        req.segment_conflicts = merged
    pipeline._write(sid, "signals", signals)
    pipeline._write(sid, "context", context)
    pipeline._write(sid, "requirements", reqs)
    pipeline.run_stage("external", cfg)
    pipeline.bundle_stage(cfg)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="all")
    args = parser.parse_args()
    os.environ["DEMO_MODUS"] = "true"  # Nie unerwartet Netzaufrufe oder Modellkosten.
    ids = pipeline.all_scenario_ids() if args.scenario == "all" else [args.scenario]
    failed = []
    for sid in ids:
        try:
            refresh(sid)
        except (ValueError, FileNotFoundError, KeyError) as err:
            print(f"{sid}: refresh failed: {err}", file=sys.stderr)
            failed.append(sid)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
