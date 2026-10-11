"""Scope-Wächter messen (W-C12): Testmenge durch die echte Ableitung schicken und zählen.

Aufruf (aus dem Repo-Root, braucht OPENAI_API_KEY oder den Cache):  python tests/pfad_c/scope_eval.py
Ergebnis: Zahlen nach stdout und tests/pfad_c/SCOPE_REPORT.md (nur synthetische Fälle, keine BMW-Daten).

Gezählt wird je Klasse: erkannt (der Befund steckt in einem verworfenen Entwurf mit Scope-Grund), durchgerutscht (steckt
in einer Anforderung UND wurde nicht verworfen) und geteilt (beides: die KI verwirft die Spezifikation und formuliert
daneben ein Kundenziel, so erlaubt es der Prompt). Bei der Gegenprobe zählt jedes Verwerfen als Fehler.
Nicht-Scope-Gründe zählen nicht mit: "Not covered" (KI ließ den Befund aus) und Wetten-Prüfungen (Annahme/Trend).
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src" / "backend"))

from scope_cases import CASES, signals_for_cases  # noqa: E402

CLASSES = ("regulatory", "engineering", "price", "in_scope")
NOT_SCOPE_PREFIXES = ("Not covered:",)
NOT_SCOPE_REASONS = ("Bet on the next generation",)


def _is_scope_decision(entry: dict) -> bool:
    return not entry["title"].startswith(NOT_SCOPE_PREFIXES) and not entry["reason"].startswith(NOT_SCOPE_REASONS)


def score_scope(cases, requirements, discarded) -> dict[str, dict[str, int]]:
    """{Klasse: Zähler}. requirements: Objekte mit signal_ids; discarded: Einträge wie derive_all sie liefert."""
    dropped = {i for e in discarded if _is_scope_decision(e) for i in e["signal_ids"]}
    uncovered = {i for e in discarded if e["title"].startswith(NOT_SCOPE_PREFIXES) for i in e["signal_ids"]}
    used = {i for r in requirements for i in r.signal_ids}
    result = {name: {"total": 0, "caught": 0, "leaked": 0, "split": 0, "wrongly_discarded": 0, "not_covered": 0}
              for name in CLASSES}
    for case in cases:
        row = result[case.label]
        row["total"] += 1
        row["caught"] += case.id in dropped and case.label != "in_scope"
        row["leaked"] += case.id in used and case.id not in dropped and case.label != "in_scope"
        row["split"] += case.id in used and case.id in dropped and case.label != "in_scope"
        row["wrongly_discarded"] += case.id in dropped and case.label == "in_scope"
        row["not_covered"] += case.id in uncovered and case.id not in used and case.id not in dropped
    return result


def _report(runs: list[dict], title: str) -> str:
    names = {"regulatory": "Regulatorik / Zulassung", "engineering": "Engineering-Spezifikation",
             "price": "Preis / Business-Case"}

    def per_run(cls: str, key: str) -> str:
        return " / ".join(str(r[cls][key]) for r in runs)

    lines = [f"# Scope-Wächter: Messung (W-C12){title}", "",
             "Erzeugt mit `python tests/pfad_c/scope_eval.py [Läufe]`. 48 erfundene Befunde (`scope_cases.py`), "
             "keine BMW-Daten.", f"{len(runs)} unabhängige Läufe der echten Ableitung (anderer Szenarioname = neuer "
             "Aufruf an die KI). Zahlen je Lauf, durch Schrägstrich getrennt.", "",
             "| Klasse | Fälle | erkannt (verworfen) | durchgerutscht |", "|---|---|---|---|"]
    for key, label in names.items():
        lines.append(f"| {label} | {runs[0][key]['total']} | {per_run(key, 'caught')} | {per_run(key, 'leaked')} |")
    total = sum(runs[0][k]["total"] for k in names)
    caught = [sum(r[k]["caught"] for k in names) for r in runs]
    leaked = [sum(r[k]["leaked"] for k in names) for r in runs]
    wrong = [r["in_scope"]["wrongly_discarded"] for r in runs]
    lines += ["", f"**Out-of-scope gesamt ({total} Fälle):** erkannt {' / '.join(map(str, caught))}, "
              f"durchgerutscht {' / '.join(map(str, leaked))}.",
              f"**Gegenprobe ({runs[0]['in_scope']['total']} normale Kundenwünsche):** zu Unrecht verworfen "
              f"{' / '.join(map(str, wrong))}.", "",
              "## Grenzen", "- 48 Fälle, von uns formuliert: Größenordnung, kein Konfidenzintervall.",
              "- Die meisten Fälle sind eindeutig formuliert, nur 8 sind knifflig (Preis ohne Preiswort, Technik-Nähe "
              "mit echtem Kundenwert); echte Befunde sind unschärfer.",
              "- Die KI schwankt von Lauf zu Lauf; darum mehrere Läufe statt einer Zahl."]
    return "\n".join(lines) + "\n"


def main() -> None:
    from core.models import Scenario
    from requirements_engine.derive import derive_all

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    title = f" {sys.argv[2]}" if len(sys.argv) > 2 else ""
    runs = []
    for k in range(n):  # anderer Name = anderer Prompt = unabhängiger Aufruf (der Cache hält jeden Lauf fest)
        name = "BMW 5 Series (test set)" if k == 0 else f"BMW 5 Series (test set, run {k})"
        scenario = Scenario(id="SCOPE-TEST", derivative="G60", model_name=name, market="US", countries=["US"],
                            competitors=[])
        requirements, discarded = derive_all(scenario, signals_for_cases(), [], {})
        runs.append(score_scope(CASES, requirements, discarded))
    report = _report(runs, title)
    (HERE / "SCOPE_REPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
