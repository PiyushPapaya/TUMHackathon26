"""Pfad B, B1: Aussagen aus der OpenAI-Websuche holen (Claims mit Quelle).

Warum Websuche statt Scraping: Sie liefert Quellen-URLs mit, und in 24 h wird kein Scraper robust
(Testmagazine haben Paywalls). Alles läuft über core.llm.ask_json, damit Cache und Demo-Modus greifen.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.llm import ask_json

SYSTEM = (
    "Du bist Recherche-Assistent für Automobil-Produktentscheidungen. Nutze die Websuche und liefere "
    "nur überprüfbare Einzelaussagen. Jede Aussage MUSS die echte URL der Quelle enthalten. "
    "Erfinde nichts: Findest du nichts, gib eine leere Liste zurück. Antworte auf Englisch."
)


class Claim(BaseModel):
    text: str  # eine einzelne, überprüfbare Aussage
    url: str  # Quelle; ohne http(s)-URL wird die Aussage verworfen
    publisher: str  # z. B. "Car and Driver"
    published: str  # Veröffentlichungsdatum (YYYY-MM-DD oder Jahr), "" wenn unbekannt
    stance: Literal["supports", "contradicts", "neutral"]  # Haltung zur Frage
    about: str  # Fahrzeug/Thema, z. B. "Audi A6 e-tron"


class Claims(BaseModel):
    claims: list[Claim]


def has_real_url(claim: Claim) -> bool:
    """Kein Webbeleg ohne URL: nur http(s) zählt, sonst wäre die Quelle nicht prüfbar."""
    return claim.url.strip().lower().startswith(("http://", "https://"))


def ask_claims(question: str) -> list[Claim]:
    result = ask_json(system=SYSTEM, user=question, schema=Claims, tools=[{"type": "web_search"}])
    return [claim for claim in result.claims if has_real_url(claim)]
