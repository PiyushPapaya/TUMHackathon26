"""A10: Eval-Zahlen und REPORT.md. Aufruf: python tests/eval/run_eval.py [Szenario]

Läuft nur lokal mit Daten. Fehlt data/processed/<Szenario>/, bricht das Skript sauber ab (z. B. in der CI).
REPORT.md enthält nur Zahlen, Methode und Grenzen, keine BMW-Zitate (das Repo ist öffentlich).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src" / "backend"), str(Path(__file__).parent)]

from eval_metrics import coverage, fidelity, grounding_rate, numbers_share, verbatim_rate  # noqa: E402


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _pct(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None else f"{value * 100:.{digits}f} %"


def compute(scenario_id: str) -> dict:
    from core.models import Evidence, Scenario
    from evidence_internal.signals import signal_groups

    processed = ROOT / "data" / "processed" / scenario_id
    cfg = json.loads((ROOT / "config" / "scenarios" / f"{scenario_id}.json").read_text(encoding="utf-8"))
    evidence, signals = _json(processed / "evidence.json"), _json(processed / "signals.json")
    if evidence is None or signals is None:
        raise FileNotFoundError(f"{processed}: erst pipeline.py --stage evidence und --stage signals laufen lassen")
    requirements = _json(processed / "requirements.json") or []
    known = {e["id"] for e in evidence}
    cited = [i for s in signals for i in s["evidence_ids"]]
    excel = pd.read_excel(ROOT / "data" / "raw" / cfg["data"]["feedback_file"], sheet_name="Feedback_Explorer")
    source_texts = set(excel["Customer Feedback"].dropna().astype(str).str.strip())
    by_id = {e["id"]: e for e in evidence}
    cited_texts = [by_id[i]["text"] for i in set(cited) if i in by_id and by_id[i]["source_type"] == "feedback"]
    comments = {e["id"] for e in evidence if e["source_type"] == "feedback" and e["meta"].get("scope", "in") == "in"}
    scenario = Scenario(**{k: v for k, v in cfg.items() if k in Scenario.model_fields})
    groups = signal_groups(scenario, [Evidence(**e) for e in evidence])
    sample = ROOT / "data" / "eval" / f"{scenario_id}_sample.csv"
    labels = []
    if sample.exists():
        with sample.open(encoding="utf-8-sig", newline="") as f:
            labels = [row[-1] for row in list(csv.reader(f))[1:]]
    return {
        "scenario": scenario_id, "evidence": len(evidence), "comments": len(comments), "signals": len(signals),
        "requirements": len(requirements),
        "ground_signals": grounding_rate(cited, known),
        "ground_requirements": grounding_rate([i for r in requirements for i in r["signal_ids"]],
                                              {s["id"] for s in signals}),
        "verbatim": verbatim_rate(cited_texts, source_texts),
        "fidelity": fidelity(labels), "labelled": sum(1 for x in labels if x.strip()), "sample": len(labels),
        "coverage": coverage(groups, comments),
        "numbers": numbers_share([r["acceptance_criterion"] for r in requirements]),
    }  # fmt: skip


def report(m: dict) -> str:
    return f"""# Eval-Report {m['scenario']}

Erzeugt mit `python tests/eval/run_eval.py {m['scenario']}`. Nur Zahlen, keine BMW-Zitate (öffentliches Repo).

## Trichter

{m['evidence']} Belege (davon {m['comments']} Kommentare im Umfang) -> {m['signals']} Befunde
-> {m['requirements']} Anforderungen.

## Die Zahlen

| Messung | Ergebnis | Ziel |
|---|---|---|
| Grounding Befunde: zitierte Beleg-IDs, die existieren | {_pct(m['ground_signals'])} | 100 % |
| Grounding Anforderungen: zitierte Befund-IDs, die existieren | {_pct(m['ground_requirements'])} | 100 % |
| Wortlaut: zitierte Kommentare, wörtlich in der Excel | {_pct(m['verbatim'])} | 100 % |
| Befund-Treue: "passt" ({m['labelled']} von {m['sample']} gelabelt) | {_pct(m['fidelity'])} | >= 80 % |
| Abdeckung: Kommentare in mindestens einem Befund | {_pct(m['coverage'])} | Orientierung |
| Anforderungen mit Zahl im Akzeptanzkriterium | {_pct(m['numbers'])} | >= 80 % |

## Methode

- **Grounding/Wortlaut:** automatisch aus den erzeugten Dateien und der Original-Excel, jede ID einzeln geprüft.
- **Befund-Treue:** 50 zufällige Paare (Befund, zitierter Beleg), Seed 42, von einem Teammitglied mit j/n gelabelt
  ("belegt der Kommentar die Aussage des Befunds?"). Nicht per KI, sonst prüft die KI sich selbst.
- **Abdeckung:** Kommentare im Umfang (ohne Werkstattfälle), die zu einer Gruppe eines ausgegebenen Befunds gehören.
- **Akzeptanzkriterium mit Zahl:** mindestens eine Ziffer im Text. Das ist ein Näherungswert für "messbar".

## Grenzen

- Stichprobe von 50 Paaren, ein Labler: grobe Größenordnung, kein Konfidenzintervall.
- Grounding sagt, dass Quellen existieren, nicht dass die Schlussfolgerung richtig ist; dafür ist die Befund-Treue da.
- "Zahl im Kriterium" prüft nicht, ob die Zahl sinnvoll ist.
- Abdeckung < 100 % ist gewollt: Themen ohne BMW-Zuordnung und Gruppen unter 5 Nennungen fallen bewusst weg.
"""


if __name__ == "__main__":
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else "G60-US"
    try:
        metrics = compute(scenario_id)
    except FileNotFoundError as err:
        print(f"Eval übersprungen: {err}")
        sys.exit(0)
    (Path(__file__).parent / "REPORT.md").write_text(report(metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, default=str))
