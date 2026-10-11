"""ID-only migration: reconstruct semantic groups from original evidence, never LLM titles."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy

from core.models import Evidence, Requirement, Scenario, SourceType
from evidence_internal.signals import _build
from requirements_engine.derive_checks import make_ids_unique, stable_key


def bundle_fingerprint(bundle: dict) -> str:
    return hashlib.sha256(json.dumps(bundle, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def replace_ids(value, mapping: dict[str, str]):
    """Replace exact identifiers and dictionary keys, never prose or source text."""
    if isinstance(value, dict):
        return {mapping.get(k, k): ("|".join(mapping.get(i, i) for i in v.split("|"))
                                    if k == "supports_signal_ids" and isinstance(v, str)
                                    else replace_ids(v, mapping)) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_ids(v, mapping) for v in value]
    return mapping.get(value, value) if isinstance(value, str) else value


def migrate_bundle(bundle: dict, evidence: list[Evidence]) -> tuple[dict, dict]:
    scenario = Scenario(**bundle["scenario"])
    current, drafts = _build(scenario, evidence)
    internal = {e.id for e in evidence if e.source_type in (SourceType.FEEDBACK, SourceType.STUDY)}
    groups = [(s, set(d.get("ids", [])) | set(d["study"]))
              for s, d in zip(current, drafts, strict=True)]
    signal_ids = {}
    for old in bundle["signals"]:
        if not re.fullmatch(rf"SIG-{re.escape(scenario.id)}-\d+", old["id"]):
            continue  # preserve historical external groups whose exact research question was not recorded
        cited = set(old["evidence_ids"]) & internal
        candidates = [s for s, members in groups if cited and cited <= members
                      and s.kind.value == old["kind"] and s.category.value == old["category"]]
        if len(candidates) != 1:
            raise ValueError(f"{old['id']}: semantic group is missing or ambiguous; migration refused")
        signal_ids[old["id"]] = candidates[0].id
    if len(set(signal_ids.values())) != len(signal_ids):
        raise ValueError("Several legacy signals map to one semantic group; review required")
    migrated = replace_ids(deepcopy(bundle), signal_ids)
    requirements = [Requirement(**r) for r in migrated["requirements"]]
    old_requirement_ids = [r.id for r in requirements]
    for req in requirements:
        req.stable_key = stable_key(req.signal_ids)
        req.id = f"REQ-{scenario.id}-{req.stable_key}"
    make_ids_unique(requirements)
    requirement_ids = dict(zip(old_requirement_ids, [r.id for r in requirements], strict=True))
    migrated = replace_ids(migrated, requirement_ids)
    for row, req in zip(migrated["requirements"], requirements, strict=True):
        row["stable_key"] = req.stable_key
    return migrated, {"signal_ids": signal_ids, "requirement_ids": requirement_ids,
                      "retained_legacy_external_ids": [s["id"] for s in bundle["signals"]
                                                      if s["id"] not in signal_ids and "-g1-" not in s["id"]],
                      "from_bundle_sha256": bundle_fingerprint(bundle),
                      "bundle_sha256": bundle_fingerprint(migrated)}


def recorded_fingerprint(events: list) -> str | None:
    """Only explicit ID-only transitions may advance the fingerprint for replay."""
    fingerprint = None
    for event in events:
        if event.event_type == "PIPELINE_LOADED":
            fingerprint = event.payload.get("bundle_sha256")
        elif event.event_type == "IDENTITY_MIGRATED":
            if not fingerprint or event.payload.get("from_bundle_sha256") != fingerprint:
                raise RuntimeError("Identity migration has no matching source fingerprint; replay refused")
            fingerprint = event.payload["bundle_sha256"]
    return fingerprint
