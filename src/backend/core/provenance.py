"""Herkunft eines Pipeline-Laufs: welches Modell, welcher Prompt-Stand, welcher Commit.

Warum: Der Prüfpfad soll zeigen, WOHER die KI-Vorschläge stammen. Bisher stand dort nur
„model: not recorded in snapshot“, weil das Bundle das Modell nicht kannte. Jetzt schreibt
die Pipeline diese Angaben ins Bundle und der Store übernimmt sie in den Prüfpfad.

Prompt-Stand als Hash über die Dateien, die LLM-Prompts enthalten: ändert jemand einen Prompt,
ändert sich der Hash. Verworfen: jeden einzelnen Prompt-Text speichern (Bundle wird groß und
die Texte stehen ohnehin im Commit). Alte Bundles bleiben ohne Herkunft und werden NICHT
nachträglich ergänzt, weil wir Modell und Prompts von damals nicht sicher kennen.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
# Alle Dateien, die über core/llm.py ein Modell fragen (Befunde, Web, Anforderungen, Angebotsabgleich).
PROMPT_SOURCES = [
    "evidence_internal/signals_llm.py",
    "evidence_external/web_research.py",
    "evidence_external/claims.py",
    "requirements_engine/prompts.py",
    "requirements_engine/derive.py",
    "requirements_engine/offer_check.py",
]


def _code_commit() -> str | None:
    """Git-Commit des Codes; None z. B. im entpackten Abgabe-Archiv ohne .git."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BACKEND, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def pipeline_provenance() -> dict:
    digest = hashlib.sha256()
    for name in PROMPT_SOURCES:
        digest.update(name.encode())
        digest.update((BACKEND / name).read_bytes())
    return {
        # Modell zum Zeitpunkt der Bündelung, gleiche Regel wie core/llm.py. Wer zwischen den Stufen
        # OPENAI_MODEL wechselt, verfälscht das; der LLM-Cache ist aber je Modell getrennt.
        "llm_model": os.getenv("OPENAI_MODEL") or "gpt-5-mini",
        "prompt_sources_sha256": digest.hexdigest(),
        "code_commit": _code_commit(),
    }
