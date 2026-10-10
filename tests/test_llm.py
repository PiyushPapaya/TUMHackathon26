"""core/llm.py: leeres Modell, .env-Laden und der committete Demo-Cache."""

import pytest
from pydantic import BaseModel

from core import llm


class Antwort(BaseModel):
    text: str


def test_leeres_modell_in_env_faellt_auf_standard_zurueck(tmp_path, monkeypatch):
    # Warum: ".env.example" hat "OPENAI_MODEL=" ohne Wert; das darf nicht als Modellname gelten.
    monkeypatch.setenv("OPENAI_MODEL", "")
    monkeypatch.setenv("DEMO_MODUS", "true")
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(llm, "DEMO_CACHE_DIR", tmp_path / "demo")
    with pytest.raises(RuntimeError, match="DEMO_MODUS"):
        llm.ask_json("s", "u", Antwort)
    pfad = llm._cache_path("gpt-5-mini", "s", "u[]", "Antwort", llm.DEMO_CACHE_DIR)
    assert pfad.name.startswith("Antwort_")  # Schlüssel wurde mit "gpt-5-mini" gebildet


def test_demo_cache_wird_gelesen_ohne_netz(tmp_path, monkeypatch):
    # Warum: Die Jury-Demo läuft auf fremdem Laptop; dort fehlt data/cache, aber data/demo_cache liegt im Repo.
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("DEMO_MODUS", "true")
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "leer")
    monkeypatch.setattr(llm, "DEMO_CACHE_DIR", tmp_path / "demo")
    eintrag = llm._cache_path("gpt-5-mini", "s", "u[]", "Antwort", llm.DEMO_CACHE_DIR)
    eintrag.parent.mkdir(parents=True)
    eintrag.write_text(Antwort(text="aus Demo-Cache").model_dump_json(), encoding="utf-8")
    assert llm.ask_json("s", "u", Antwort).text == "aus Demo-Cache"


def test_env_datei_wird_geladen(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=testwert-nur-im-test\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm.lade_env(env)
    import os
    assert os.getenv("OPENAI_API_KEY") == "testwert-nur-im-test"
    monkeypatch.delenv("OPENAI_API_KEY")
