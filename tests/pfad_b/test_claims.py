"""B1: Claims aus der Websuche. Ohne Netz: ask_json wird durch ein Fake ersetzt."""

from evidence_external import claims as claims_mod
from evidence_external.claims import Claim, Claims, ask_claims


def _claim(url: str, text: str = "E-Class hat Touch-Klima") -> Claim:
    return Claim(text=text, url=url, publisher="Car and Driver", published="2025-03-01",
                 stance="neutral", about="Mercedes-Benz E-Class")


def test_claims_ohne_oder_ungueltige_url_werden_verworfen(monkeypatch):
    fake = Claims(claims=[
        _claim("https://www.caranddriver.com/a"),
        _claim(""),
        _claim("ftp://example.com/x"),
        _claim("www.ohne-schema.de/y"),
        _claim("http://motortrend.com/b"),
    ])
    monkeypatch.setattr(claims_mod, "ask_json", lambda **kwargs: fake)

    result = ask_claims("Frage?")

    assert [c.url for c in result] == ["https://www.caranddriver.com/a", "http://motortrend.com/b"]


def test_ask_claims_nutzt_websuche_tool(monkeypatch):
    seen = {}

    def fake_ask_json(**kwargs):
        seen.update(kwargs)
        return Claims(claims=[])

    monkeypatch.setattr(claims_mod, "ask_json", fake_ask_json)
    ask_claims("Frage?")

    assert seen["tools"] == [{"type": "web_search"}]
    assert seen["schema"] is Claims
    assert "Frage?" in seen["user"]
