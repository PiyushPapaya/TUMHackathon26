"""Die Beispielfragen der Oberfläche liegen im eingecheckten Demo-Cache.

Warum: Ohne OpenAI-Key (Jury, fremder Rechner, DEMO_MODUS) sollen die Knöpfe im Cockpit und im Assistenten
trotzdem die KI-Deutung zeigen. Ändert jemand den Linsen-Prompt, schlägt dieser Test fehl:
dann Fragen neu stellen und data/cache/LensPlan_*.json nach data/demo_cache/ kopieren.
"""

import json

import pytest

from core import lens, llm

# Gleiche Texte wie src/frontend/src/components/cockpit/LensPanel.tsx (EXAMPLES) und der Assistent (QUICK).
DEMO_QUESTIONS = [
    "Families in the US, focus on charging and space",
    "What matters most for the 2030 successor?",
    "Where are we weakest against competitors?",
    "Families and charging",
]


@pytest.mark.parametrize("question", DEMO_QUESTIONS)
def test_demofrage_liegt_im_demo_cache(question):
    user = json.dumps({"question": question}, ensure_ascii=False) + json.dumps([])
    path = llm._cache_path("gpt-5-mini", lens.SYSTEM_PROMPT, user, "LensPlan", ordner=llm.DEMO_CACHE_DIR)
    assert path.exists(), f"Kein Demo-Cache für {question!r} ({path.name})"
