"""Rechenfunktionen der Eval (A9/A10). Rein, ohne Dateien, damit sie mit Fake-Daten testbar sind.

Warum eigene Zahlen statt "fühlt sich gut an": Die Jury fragt "Warum soll ich der KI trauen?". Jede Zahl hier
ist nachrechenbar und kommt aus dem Code, nicht aus einem Modell.
"""

from __future__ import annotations

import random
import re


def share(part: int, total: int) -> float | None:
    """Anteil 0-1, None wenn es nichts zu messen gibt (statt einer erfundenen 100 %)."""
    return part / total if total else None


def grounding_rate(cited_ids: list[str], known_ids: set[str]) -> float | None:
    """Anteil zitierter Beleg-IDs, die es in evidence.json wirklich gibt (Ziel 100 %)."""
    return share(sum(i in known_ids for i in cited_ids), len(cited_ids))


def verbatim_rate(texts: list[str], source_texts: set[str]) -> float | None:
    """Anteil der Belegtexte, die wörtlich (nur strip) in der Excel stehen (Ziel 100 %)."""
    return share(sum(t.strip() in source_texts for t in texts), len(texts))


def coverage(groups: dict[str, list[str]], comment_ids: set[str]) -> float | None:
    """Anteil der Kommentare, die in mindestens einem Befund landen."""
    covered = {i for ids in groups.values() for i in ids} & comment_ids
    return share(len(covered), len(comment_ids))


def numbers_share(criteria: list[str]) -> float | None:
    """Anteil der Akzeptanzkriterien mit mindestens einer Zahl (messbar statt "besser")."""
    return share(sum(bool(re.search(r"\d", c)) for c in criteria), len(criteria))


def fidelity(labels: list[str]) -> float | None:
    """Befund-Treue: Anteil 'j' unter den ausgefüllten Zeilen (j/n). Leere Zeilen zählen nicht."""
    given = [label.strip().lower() for label in labels if label.strip().lower() in {"j", "n"}]
    return share(given.count("j"), len(given))


def sample_pairs(pairs: list[tuple[str, str]], n: int = 50, seed: int = 42) -> list[tuple[str, str]]:
    """n zufällige (Befund-ID, Beleg-ID)-Paare. Sortiert vor dem Ziehen, damit Seed 42 immer dasselbe liefert."""
    ordered = sorted(set(pairs))
    return sorted(random.Random(seed).sample(ordered, min(n, len(ordered))))
