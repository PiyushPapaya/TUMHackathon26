"""Scope-Wächter im Code (Pfad C, W-C12): zweite Verteidigungslinie hinter dem Prompt.

Brief: "Focus on customer value rather than engineering specifications, regulatory requirements, or detailed
business-case calculations." Der Prompt sagt das der KI, aber sie hält sich nicht zuverlässig daran (Messung,
8 Läufe mit 48 erfundenen Befunden: 87 % der Out-of-scope-Wünsche erkannt, in 2 von 8 Läufen 8 Preiswünsche zu einer
Anforderung "MSRP < $50,000" zusammengefasst). Darum prüft der Code Titel und Akzeptanzkriterium auf EINDEUTIGE Preis-
und Zulassungswörter. Wer trifft, wird verworfen und steht mit Grund im Prüfpfad (der PM sieht, was wir
ausgesondert haben).

Bewusst eng: keine Einheiten wie "kW" oder "mm" (Kriterien dürfen "7.5 W" nennen), und kein bloßes "regulate"
(Temperaturregelung ist Kundenwert). Verworfen: alles der KI überlassen (schwankt), Engineering-Wörter (zu viele echte
Kriterien mit Zahlen). Grenze: Eine Umschreibung ohne diese Wörter kommt durch; dafür gilt weiter der Prompt.
"""

from __future__ import annotations

import re

PRICE = re.compile(
    r"\b(msrp|pric(?:e|es|ed|ing)|lease|leasing|financing|discounts?|residual value|dealer margin|affordab\w+"
    r"|cheaper)\b"
    r"|[$€£]\s?\d|\b\d[\d.,]*\s?(?:usd|eur|dollars?|euros?)\b", re.IGNORECASE)
REGULATORY = re.compile(
    r"\b(type[- ]approvals?|homologat\w*|certif\w+|fmvss|carb|gdpr|ccc|un[- ]?r\d+|ece[- ]?r\d+|euro ncap|regulatory"
    r"|(?:legal|government\w*|statutory|official|eu|us|national)\s+(?:regulations?|requirements?)"
    r"|compliance|compliant|comply|complies)\b", re.IGNORECASE)


def guard_reason(title: str, acceptance_criterion: str) -> str | None:
    """Grund (englisch, steht im Prüfpfad), wenn die Anforderung Preis- oder Zulassungswörter enthält, sonst None."""
    text = f"{title}\n{acceptance_criterion}"
    if match := PRICE.search(text):
        return f"Scope guard: price / business-case wording ('{match.group(0)}'); out of scope per brief."
    if match := REGULATORY.search(text):
        return f"Scope guard: regulatory / certification wording ('{match.group(0)}'); out of scope per brief."
    return None
