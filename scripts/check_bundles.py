"""W-L8: Bundle-Prüfer. Liest data/processed/*.json und meldet je Regel GRUEN oder ROT.

Warum: Nach dem Nachtlauf (6 Szenarien, mehrere Stunden) soll in einer Minute klar sein, ob die Demo-Daten
tragen. Ein stilles Loch (leere Stufe D, fehlende Robustheit, hängende ID) fiele sonst erst im Pitch auf.

Regeln:
  1. G60-US hat mindestens 15 Anforderungen.
  2. Über alle Bundles gibt es mindestens einmal Stufe D.
  3. Jede Stufe-D-Anforderung nennt ihre Annahmen (assumptions).
  4. Jede Anforderung hat eine Robustheit (robustness).
  5. G68-CN: kein internes Feedback (Kaltstart), aber mehr als 0 Anforderungen.
  6. Jede zitierte ID existiert (Anforderung -> Befund -> Beleg).
  7. IDs bleiben stabil: gleiche Befunde ergeben gegenüber dem letzten committeten Stand dieselbe ID.

Aufruf:
  python scripts/check_bundles.py               # Exit-Code 1 bei mindestens einer roten Regel
  python scripts/check_bundles.py --ohne-git    # Regel 7 überspringen (z. B. ohne Git-Historie)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MIN_G60_US = 15

Check = tuple[bool, str]  # (grün?, Satz für den Menschen)


def _key(req: dict) -> str:
    """stable_key des Laufs; ältere Bundles haben ihn nicht, dann die sortierten Befund-IDs."""
    return req.get("stable_key") or "|".join(sorted(req.get("signal_ids", [])))


def check_scenario(bundle: dict) -> list[Check]:
    """Regeln 1, 3-6 für ein einzelnes Bundle (Regel 2 und 7 brauchen mehrere Bundles bzw. Git)."""
    sid = bundle.get("scenario", {}).get("id", "?")
    reqs = bundle.get("requirements", [])
    out: list[Check] = []
    if sid == "G60-US":
        out.append((len(reqs) >= MIN_G60_US, f"G60-US hat {len(reqs)} Anforderungen (Soll: mindestens {MIN_G60_US})"))
    if sid == "G68-CN":
        feedback = bundle.get("scenario", {}).get("data_coverage", {}).get("feedback")
        out.append((feedback == 0, f"G68-CN internes Feedback: {feedback} (Soll: 0, Kaltstart)"))
        out.append((len(reqs) > 0, f"G68-CN hat {len(reqs)} Anforderungen (Soll: mehr als 0)"))
    missing_assumptions = [r["id"] for r in reqs if r.get("evidence_level") == "D" and not r.get("assumptions")]
    out.append((not missing_assumptions, f"{sid}: Stufe D ohne Annahmen: {missing_assumptions or 'keine'}"))
    no_robustness = [r["id"] for r in reqs if not r.get("robustness")]
    out.append((not no_robustness, f"{sid}: Anforderungen ohne Robustheit: {len(no_robustness)} von {len(reqs)}"))
    signal_ids = {s["id"] for s in bundle.get("signals", [])}
    evidence_ids = {e["id"] for e in bundle.get("evidence", [])}
    dangling = [i for r in reqs for i in r.get("signal_ids", []) if i not in signal_ids]
    dangling += [i for s in bundle.get("signals", []) for i in s.get("evidence_ids", []) if i not in evidence_ids]
    out.append((not dangling, f"{sid}: zitierte IDs ohne Gegenstück: {sorted(set(dangling))[:5] or 'keine'}"))
    return out


def check_stable_ids(new: dict, old: dict) -> Check:
    """Regel 7: gleicher Schlüssel (gleiche Befunde) muss dieselbe ID tragen wie im letzten Stand."""
    sid = new.get("scenario", {}).get("id", "?")
    old_ids = {_key(r): r["id"] for r in old.get("requirements", [])}
    changed = [(old_ids[_key(r)], r["id"]) for r in new.get("requirements", [])
               if _key(r) in old_ids and old_ids[_key(r)] != r["id"]]
    return not changed, f"{sid}: IDs gegenüber letztem Stand geändert: {changed[:3] or 'keine'}"


def _previous(path: Path) -> dict | None:
    """Letzter committeter Stand der Datei (HEAD) oder None, wenn es keinen gibt."""
    rel = path.relative_to(ROOT).as_posix()
    shown = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", check=False)
    return json.loads(shown.stdout) if shown.returncode == 0 and shown.stdout.strip() else None


def run(processed: Path = PROCESSED, use_git: bool = True) -> list[Check]:
    paths = sorted(processed.glob("*.json"))
    bundles = {p: json.loads(p.read_text(encoding="utf-8")) for p in paths}
    results: list[Check] = []
    ids = {b.get("scenario", {}).get("id") for b in bundles.values()}
    for needed in ("G60-US", "G68-CN"):
        if needed not in ids:
            results.append((False, f"Bundle {needed}.json fehlt in {processed.name}/"))
    for path, bundle in bundles.items():
        results += check_scenario(bundle)
        old = _previous(path) if use_git else None
        if old:
            results.append(check_stable_ids(bundle, old))
    has_d = any(r.get("evidence_level") == "D" for b in bundles.values() for r in b.get("requirements", []))
    results.append((has_d, "Mindestens eine Anforderung mit Stufe D (Zukunftswette) vorhanden"))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ohne-git", action="store_true", help="Regel 7 (stabile IDs) überspringen")
    args = parser.parse_args()
    results = run(use_git=not args.ohne_git)
    for ok, text in results:
        print(f"[{'GRUEN' if ok else 'ROT  '}] {text}")
    red = sum(1 for ok, _ in results if not ok)
    print(f"\n{len(results) - red} grün, {red} rot")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
