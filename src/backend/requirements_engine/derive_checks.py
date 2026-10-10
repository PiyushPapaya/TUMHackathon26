"""Prüfungen und Schlüssel rund um derive_all (Pfad C): stabile IDs, Abdeckung, Widersprüche.

Eigene Datei, damit derive.py unter ~200 Zeilen bleibt und diese Regeln einzeln testbar sind.
Alles hier ist Code, keine KI: gleiche Eingabe ergibt gleiches Ergebnis.
"""

from __future__ import annotations

import hashlib

from core.models import Requirement, Signal, SignalKind


def stable_key(signal_ids: list[str]) -> str:
    """6 Zeichen aus den Befund-IDs (sortiert): gleiche Befunde ergeben bei jedem Lauf dieselbe ID.

    Warum nicht die KI-Reihenfolge: Prüfpfad und PM-Entscheidungen hängen an der ID, und ein neuer Lauf
    würde sie sonst auf andere Anforderungen zeigen lassen. Verworfen: Hash des Titels (wechselt mit jeder
    Formulierung der KI). Grenze: Ändern sich die Befunde selbst, ändert sich die ID, das ist gewollt.
    """
    return hashlib.sha1("|".join(sorted(signal_ids)).encode()).hexdigest()[:6]



def make_ids_unique(requirements: list[Requirement]) -> None:
    """Zwei Entwürfe auf denselben Befunden dürfen nicht dieselbe ID tragen (Prüfpfad braucht Eindeutigkeit)."""
    seen: dict[str, int] = {}
    for req in requirements:
        seen[req.id] = seen.get(req.id, 0) + 1
        if seen[req.id] > 1:
            req.id = f"{req.id}-{seen[req.id]}"



def not_covered(signals: list[Signal], kept: list, discarded: list[dict]) -> list[dict]:
    """Beschwerden/Wünsche, die die KI in keine Anforderung übernommen hat: sichtbar machen statt still verlieren.

    Echter Fund (Sa 10.10.): Trotz Prompt-Regel "Cover EVERY complaint" fehlte zweimal "Start-Stopp lässt sich
    nicht dauerhaft abschalten" (22 Nennungen). Der Prompt allein garantiert es nicht, darum prüft der Code.
    Verworfen: automatisch eine Anforderung erzeugen (Text wäre ungeprüft) oder die KI erneut fragen (teuer, schwankt).
    """
    cited = {s.id for _, linked in kept for s in linked} | {i for d in discarded for i in d["signal_ids"]}
    needs = (SignalKind.COMPLAINT, SignalKind.UNMET_NEED)
    return [
        {"title": f"Not covered: {s.title}",
         "reason": f"The AI derived no requirement from this {s.kind.value} ({s.mention_count} mentions); PM to check.",
         "signal_ids": [s.id]}
        for s in signals if s.kind in needs and s.id not in cited
    ]



def conflict_notes(linked: list[Signal]) -> list[str]:
    """Widersprechen sich zitierte Befunde, steht das als Unsicherheit da: sichtbar, egal was die KI schreibt."""
    by_id = {s.id: s for s in linked}
    pairs = {tuple(sorted((s.id, other))) for s in linked for other in s.conflicts_with if other in by_id}
    return [f'Conflicting evidence: "{by_id[a].title}" vs. "{by_id[b].title}"' for a, b in sorted(pairs)[:3]]
