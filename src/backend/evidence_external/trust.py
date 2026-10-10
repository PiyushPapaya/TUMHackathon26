"""Pfad B, B2: Vertrauensstufe einer Webquelle allein aus der Domain.

Warum Regeln statt LLM: Die Stufe entscheidet, ob eine Aussage in einen Befund darf (nur high/medium).
Das muss für den PM nachvollziehbar und reproduzierbar sein; ein Modell könnte dieselbe URL
mal so, mal so bewerten.
"""

from __future__ import annotations

from typing import Literal
from urllib.parse import urlparse

Trust = Literal["high", "medium", "low"]

# Hersteller, Testmagazine und Studien/Institute: primäre oder methodisch geprüfte Quellen.
HIGH_DOMAINS = (
    "bmw.com", "bmwusa.com", "mbusa.com", "mercedes-benz.com", "audi.com", "audiusa.com",
    "tesla.com", "genesis.com", "lucidmotors.com", "porsche.com", "volvocars.com",
    "caranddriver.com", "motortrend.com", "edmunds.com", "autobild.de", "whatcar.com",
    "jdpower.com", "consumerreports.org", "mckinsey.com", "deloitte.com",
)

# Fachpresse und Nachrichten: redaktionell, aber ohne eigene Testmethodik.
MEDIUM_DOMAINS = (
    "reuters.com", "bloomberg.com", "wsj.com", "nytimes.com", "cnbc.com", "forbes.com",
    "autonews.com", "electrek.co", "insideevs.com", "autoblog.com", "theverge.com",
    "techcrunch.com", "automotiveworld.com", "just-auto.com", "autocar.co.uk",
    "motor1.com", "caranddriver.co.uk", "topgear.com", "autoexpress.co.uk", "cars.com",
)


def _host(url: str) -> str:
    host = (urlparse(url.strip()).hostname or "").lower()
    return host.removeprefix("www.")


def _matches(host: str, domains: tuple[str, ...]) -> bool:
    # Exakte Domain oder Subdomain; "notcaranddriver.com" darf nicht auf "caranddriver.com" passen.
    return any(host == d or host.endswith("." + d) for d in domains)


def trust_for_url(url: str) -> Trust:
    """high/medium/low. Foren, Reddit, YouTube und alles Unbekannte sind low (kommt nicht in Befunde)."""
    host = _host(url)
    if _matches(host, HIGH_DOMAINS):
        return "high"
    if _matches(host, MEDIUM_DOMAINS):
        return "medium"
    return "low"
