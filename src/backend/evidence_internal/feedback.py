"""Pfad A, A1: Feedback-Excel -> Belege (Evidence). Ohne LLM.

Warum pandas statt LLM: Das Einlesen muss reproduzierbar sein, und jeder Kommentar
braucht eine stabile ID, auf die Befunde und Anforderungen später zeigen.

Warum ein Beleg pro ID (nicht pro Zeile): Die Excel hat eine Zeile je (Kommentar x Label).
Pro Zeile würde derselbe Kommentar mehrfach zählen und Mengen verfälschen.

Der Text bleibt unverändert (nur strip()), weil die Eval später prüft, dass jedes
Zitat wörtlich in der Excel steht.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.models import Evidence, SourceType

SHEET = "Feedback_Explorer"
SEPARATOR = " | "  # Absprache mit Pfad C (PFAD-A.md, Abschnitt "Absprache mit Dennis")

# Vorzeichen je Feedback-Typ. Wants zählt negativ: ein Wunsch ist ein Mangel im heutigen Auto.
POLARITY = {"Likes": 1, "Defect": -1, "Difficult to Use": -1, "Wants": -1}

# Quelle D beantwortet nur die Frage "Was liebst du am meisten?". BMW lässt den Typ dort leer
# (Fehleinstufung), inhaltlich ist es Lob. Quelle A/C ohne Typ mischen Lob und Beschwerden und
# bleiben deshalb neutral (für sie bräuchte es eine Stimmungsanalyse je Kommentar).
PRAISE_ONLY_SOURCE = "D"


def _clean(value: object) -> str:
    """NaN/None -> '', sonst getrimmter Text."""
    return "" if pd.isna(value) else str(value).strip()


def _unique(values: list[str]) -> list[str]:
    """Reihenfolge behalten, Duplikate und leere Werte entfernen."""
    return list(dict.fromkeys(v for v in values if v))


def _sign(total: int) -> int:
    return (total > 0) - (total < 0)


def feedback_to_evidence(df: pd.DataFrame, cfg: dict) -> list[Evidence]:
    """Rein und ohne Datei testbar: Feedback-Zeilen -> ein Beleg je BMW-ID."""
    countries = set(cfg["countries"])
    rows = df.assign(_country=df["Country"].map(_clean))
    rows = rows[rows["_country"].isin(countries)]

    evidence: list[Evidence] = []
    # sort=False: Reihenfolge der ersten Nennung bleibt, damit Läufe identisch sind.
    for raw_id, group in rows.groupby(rows["ID"].map(_clean), sort=False):
        text = _clean(group["Customer Feedback"].iloc[0])
        if not raw_id or not text:
            continue  # ohne Text gibt es nichts zu zitieren

        types = [_clean(t) for t in group["Feedback Type"]]
        vfc2 = [_clean(v) for v in group["Vfc level2 Name"]]
        vfc3 = [_clean(v) for v in group["Vfc level3 Name"]]
        labels = _unique([f"{v}/{t}" for v, t in zip(vfc2, types, strict=True)])
        source = _clean(group["Source"].iloc[0]).split()[-1] if _clean(group["Source"].iloc[0]) else ""

        # Werkstattfälle (nur Defects aus Quelle B) sind Qualität, keine Kundenanforderung.
        only_defects = all(t == "Defect" for t in types)
        scope = "out" if only_defects and source == "B" else "in"

        polarity = _sign(sum(POLARITY.get(t, 0) for t in types))
        meta = {
            "vfc2": SEPARATOR.join(_unique(vfc2)),
            "vfc3": SEPARATOR.join(_unique(vfc3)),
            "feedback_type": SEPARATOR.join(_unique(types)),
            "labels": SEPARATOR.join(labels),
            "engine": _clean(group["Engine Type"].iloc[0]),
            "source": source,
            "scope": scope,
        }
        if source == PRAISE_ONLY_SOURCE and not any(types):  # nur bei ganz leerem Typ, echte Typen gewinnen
            polarity = 1
            meta["polarity_basis"] = "source_d_praise"  # für Review und UI: warum +1 trotz leerem Typ

        evidence.append(
            Evidence(
                id=f"EV-{cfg['id']}-FB-{raw_id}",
                source_type=SourceType.FEEDBACK,
                source_name=f"Feedback Quelle {source}" if source else "Feedback",
                derivative=cfg["derivative"],
                market=cfg["market"],
                text=text,
                polarity=polarity,
                meta=meta,
            )
        )
    return evidence


def load_feedback(cfg: dict, raw_dir: Path) -> list[Evidence]:
    """Liest die Feedback-Excel des Szenarios und baut die Belege."""
    path = Path(raw_dir) / cfg["data"]["feedback_file"]
    df = pd.read_excel(path, sheet_name=SHEET)
    return feedback_to_evidence(df, cfg)
