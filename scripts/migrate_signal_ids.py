"""Create a reviewed ID-only copy of processed data and optionally its fingerprinted audit DB.

Never changes the source directory or source DB. Stop the backend before switching to the output.
python scripts/migrate_signal_ids.py --output-dir outputs/semantic-ids
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from core.audit import AuditLog  # noqa: E402
from core.identity import migrate_bundle, recorded_fingerprint, replace_ids  # noqa: E402
from core.models import Actor, Evidence  # noqa: E402


def migrate(source: Path, output: Path, audit_db: Path | None = None) -> dict:
    if output.exists():
        raise ValueError("Output already exists; choose a new directory")
    plans = []
    for path in sorted(source.glob("*.json")):
        bundle = json.loads(path.read_text(encoding="utf-8"))
        evidence_path = source / path.stem / "evidence.json"
        if not evidence_path.exists():
            raise ValueError(f"{evidence_path}: original evidence is required, quoted bundle evidence is insufficient")
        evidence = [Evidence(**e) for e in json.loads(evidence_path.read_text(encoding="utf-8"))]
        migrated, transition = migrate_bundle(bundle, evidence)
        plans.append((path, migrated, transition))
    if not plans:
        raise ValueError("No bundles found")
    # Inspect a SQLite backup rather than opening the live database through AuditLog.
    if audit_db:
        if not audit_db.is_file():
            raise ValueError("Source audit DB does not exist")
        with tempfile.TemporaryDirectory(prefix="signal-id-migration-") as folder:
            snapshot_path = Path(folder) / "audit.db"
            with closing(sqlite3.connect(f"{audit_db.resolve().as_uri()}?mode=ro", uri=True)) as origin:
                with closing(sqlite3.connect(snapshot_path)) as snapshot:
                    origin.backup(snapshot)
            audit = AuditLog(snapshot_path)
            try:
                if not audit.verify()["valid"]:
                    raise ValueError("Source audit chain is invalid; migration refused")
                for path, _, transition in plans:
                    events = audit.events(path.stem)
                    if events and recorded_fingerprint(events) != transition["from_bundle_sha256"]:
                        raise ValueError(f"{path.stem}: source identity unverified or changed; migration refused")
                    if events:
                        audit.append("IDENTITY_MIGRATED", path.stem, Actor(type="system", name="identity-migration"),
                                     "Verified ID-only migration from original evidence; historical events unchanged.",
                                     transition)
            finally:
                audit.close()
            # Export only after every fingerprint and the audit chain have been validated.
            output.mkdir(parents=True)
            shutil.copy2(snapshot_path, output / "audit.db")
    else:
        output.mkdir(parents=True)
    processed = output / "processed"
    shutil.copytree(source, processed)
    for path, migrated, transition in plans:
        mapping = transition["signal_ids"] | transition["requirement_ids"]
        (processed / path.name).write_text(json.dumps(migrated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for stage in (processed / path.stem).glob("*.json"):
            value = replace_ids(json.loads(stage.read_text(encoding="utf-8")), mapping)
            if stage.stem == "requirements":
                keys = {r["id"]: r["stable_key"] for r in migrated["requirements"]}
                for req in value:
                    req["stable_key"] = keys[req["id"]]
            stage.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    report = {path.stem: transition for path, _, transition in plans}
    (output / "migration.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--audit-db", type=Path)
    args = parser.parse_args()
    result = migrate(args.source_dir, args.output_dir, args.audit_db)
    print(json.dumps({sid: {"signals": len(p["signal_ids"]), "requirements": len(p["requirement_ids"])}
                      for sid, p in result.items()}, indent=2))
