"""Pfad B, B4: Triangulation. Webbelege stützen interne Befunde oder widersprechen ihnen.

Warum: Zwei unabhängige Quellenarten (Kundenfeedback + Web) heben die Evidenzstufe
(requirements_engine/evidence_level.py). Dafür muss der interne Befund den Webbeleg zitieren
und "web" in source_types führen.

Regeln (bewusst einfach und erklärbar):
- Nur Belege mit Vertrauen high/medium und stance=supports werden angehängt (Forum-Stimmen heben nichts).
- stance=contradicts wird NICHT angehängt, sondern als Gegenbeleg für die Challenge gemeldet.
  Verworfen: Widerspruch einfach ignorieren, weil der PM sonst nur die schöne Seite sieht.
- Die Eingabe wird kopiert, nie verändert (die Stufe darf beliebig oft laufen).
"""

from __future__ import annotations

from core.models import Evidence, Signal, SourceType

TRUSTED = ("high", "medium")


def triangulate(signals: list[Signal], web_evidence: list[Evidence]) -> tuple[list[Signal], dict[str, list[str]]]:
    """Liefert (interne Befunde mit Webbelegen, {befund_id: [IDs widersprechender Webbelege]})."""
    known = {s.id for s in signals}
    supports: dict[str, list[str]] = {}
    counter: dict[str, list[str]] = {}
    for ev in web_evidence:
        target = ev.meta.get("supports_signal_id")
        if target not in known or ev.meta.get("trust") not in TRUSTED:
            continue
        if ev.meta.get("stance") == "supports":
            supports.setdefault(target, []).append(ev.id)
        elif ev.meta.get("stance") == "contradicts":
            counter.setdefault(target, []).append(ev.id)

    result: list[Signal] = []
    for signal in signals:
        new_ids = [i for i in supports.get(signal.id, []) if i not in signal.evidence_ids]
        copy = signal.model_copy(deep=True)
        if signal.id in supports:
            copy.evidence_ids += new_ids
            if SourceType.WEB not in copy.source_types:
                copy.source_types.append(SourceType.WEB)
        result.append(copy)
    return result, counter
