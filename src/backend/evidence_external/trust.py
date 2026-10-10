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


def is_plain_web_url(url: str) -> bool:
    """Nur eindeutige http(s)-URLs. Warum: urlparse und Browser lesen manche Tricks verschieden
    ("https://evil.com\\@caranddriver.com": Browser -> evil.com, urlparse -> caranddriver.com).
    Was mehrdeutig sein kann (Backslash, Leer-/Steuerzeichen, Userinfo, anderes Schema), gilt nicht."""
    if any(ch == "\\" or ch.isspace() or not ch.isprintable() for ch in url):
        return False
    try:
        parts = urlparse(url)
        return parts.scheme in ("http", "https") and bool(parts.hostname) and "@" not in parts.netloc
    except ValueError:
        return False


def _host(url: str) -> str:
    if not is_plain_web_url(url.strip()):
        return ""
    return (urlparse(url.strip()).hostname or "").lower().removeprefix("www.")


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
