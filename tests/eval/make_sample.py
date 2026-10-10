"""A9: Stichprobe zum Handlabeln. Aufruf: python tests/eval/make_sample.py [Szenario]

Schreibt data/eval/<Szenario>_sample.csv (data/ ist gitignored, die Zeilen enthalten BMW-Kommentare).
Spalte `passt` füllt ein Mensch in Excel mit j/n aus: "Belegt dieser Kommentar die Aussage des Befunds?".
Wir labeln absichtlich nicht per KI, weil die Zahl sonst die KI mit sich selbst prüft.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from eval_metrics import sample_pairs

ROOT = Path(__file__).resolve().parents[2]


def main(scenario: str = "G60-US", n: int = 50) -> Path:
    processed = ROOT / "data" / "processed" / scenario
    evidence = {e["id"]: e for e in json.loads((processed / "evidence.json").read_text(encoding="utf-8"))}
    signals = {s["id"]: s for s in json.loads((processed / "signals.json").read_text(encoding="utf-8"))}
    pairs = [(sid, eid) for sid, s in signals.items() for eid in s["evidence_ids"] if eid in evidence]
    out = ROOT / "data" / "eval" / f"{scenario}_sample.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: Excel zeigt Umlaute richtig
        writer = csv.writer(f)
        writer.writerow(["signal_id", "signal_title", "evidence_id", "text", "passt (j/n)"])
        for sid, eid in sample_pairs(pairs, n=n, seed=42):
            writer.writerow([sid, signals[sid]["title"], eid, evidence[eid]["text"], ""])
    return out


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
