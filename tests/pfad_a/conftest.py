"""Pfad-A-Tests rufen nie OpenAI auf: ask_json wirft, extract_signals fällt auf v1 zurück."""

import pytest


@pytest.fixture(autouse=True)
def kein_openai(monkeypatch):
    def _verboten(*args, **kwargs):
        raise RuntimeError("Tests dürfen nie OpenAI aufrufen")

    monkeypatch.setattr("evidence_internal.signals_llm.ask_json", _verboten)
