"""Reference prices must remain source-grounded and market-labelled."""

from types import SimpleNamespace

import pymupdf

from core.product_context import _prices, product_context


def test_prices_exclude_net_amounts_and_option_prices(tmp_path):
    path = tmp_path / "prices.pdf"
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "FAHRZEUGGRUNDPREIS\n60.000,-\n[50.420,17]\n100.200,-\n"
                                   "[84.201,68]\nEUR inkl.19%\n1.200,-")
        page = document.new_page()
        page.insert_text((72, 72), "OPTION PRICES\n500.000,-")
        document.save(path)
    assert _prices(str(path), path.stat().st_mtime_ns) == {"min_eur": 60000, "max_eur": 100200, "pages": [1]}


def test_missing_reference_is_unavailable_not_zero(tmp_path):
    state = SimpleNamespace(scenario=SimpleNamespace(derivative="G68"), evidence={})
    result = product_context(state, tmp_path)
    assert result["min_eur"] is None and result["max_eur"] is None
    assert result["reference_market"] == "Germany"
    assert "unavailable" in result["note"]


def test_product_reference_route_is_read_only(client):
    before = client.get("/api/audit").json()
    result = client.get("/api/scenarios/G60-US/product-context")
    assert result.status_code == 200
    assert result.json()["reference_market"] == "Germany"
    assert result.json()["currency"] == "EUR"
    assert client.get("/api/audit").json() == before
    assert client.get("/api/scenarios/not-a-scenario/product-context").status_code == 404
