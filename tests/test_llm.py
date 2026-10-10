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


def _ohne_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_MODUS", "false")
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(llm, "DEMO_CACHE_DIR", tmp_path / "demo")
    monkeypatch.setattr(llm, "BACKOFF_SECONDS", 0)


def test_retry_nach_netzfehler_und_none(tmp_path, monkeypatch):
    """L17: Erst Netzfehler, dann leere Antwort, dann Erfolg -> Ergebnis kommt an und landet im Cache."""
    _ohne_cache(tmp_path, monkeypatch)
    antworten = iter([ConnectionError("weg"), None, Antwort(text="ok")])

    def fake(*_args):
        a = next(antworten)
        if isinstance(a, Exception):
            raise a
        return a

    monkeypatch.setattr(llm, "_call_openai", fake)
    assert llm.ask_json("s", "u", Antwort).text == "ok"
    assert [p.suffix for p in (tmp_path / "cache").iterdir()] == [".json"]  # keine Temp-Reste


def test_nach_allen_versuchen_klarer_fehler(tmp_path, monkeypatch):
    _ohne_cache(tmp_path, monkeypatch)
    aufrufe = []
    monkeypatch.setattr(llm, "_call_openai", lambda *a: aufrufe.append(1))  # liefert immer None
    with pytest.raises(RuntimeError, match="3 Versuchen"):
        llm.ask_json("s", "u", Antwort)
    assert len(aufrufe) == 3


def test_kaputte_cache_datei_zaehlt_als_fehlend(tmp_path, monkeypatch):
    _ohne_cache(tmp_path, monkeypatch)
    kaputt = llm._cache_path("gpt-5-mini", "s", "u[]", "Antwort", llm.CACHE_DIR)
    kaputt.parent.mkdir(parents=True)
    kaputt.write_text('{"text": ', encoding="utf-8")  # abgebrochener Schreibvorgang
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(llm, "_call_openai", lambda *a: Antwort(text="neu"))
    assert llm.ask_json("s", "u", Antwort).text == "neu"
    assert Antwort.model_validate_json(kaputt.read_text(encoding="utf-8")).text == "neu"
