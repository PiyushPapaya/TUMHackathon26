"""Business-Seite einer Anforderung (Pfad C, W-C6): Volumen 2030, Wachstum 2025 -> 2030, Marktanteil.

Quelle: context["sales"] aus sales_volumes.xlsx (Pfad A). Fehlt eine Zahl, bleibt sie None und die Notiz sagt es:
nie still 0. Der Wert fließt NICHT in "reach" (verworfen, siehe tests/pfad_c/test_business.py), sondern wird sichtbar
gemacht und wirkt multiplikativ auf future_relevance.
"""

from __future__ import annotations

from core.model_parts import BusinessContext


def business_context(sales: dict) -> BusinessContext:
    """Zahlen aus dem Absatz-Kontext. Ein gelieferter growth_pct (z. B. aus W-A5) hat Vorrang vor der Eigenrechnung."""
    v2025, v2030 = sales.get("volume_2025"), sales.get("volume_2030")
    growth = sales.get("growth_pct")
    if growth is None and v2025 and v2030 is not None:  # v2025 = 0 ergäbe eine Division durch 0
        growth = round((v2030 - v2025) / v2025 * 100, 3)
    missing = [name for name, value in (("2025 volume", v2025), ("2030 volume", v2030), ("growth", growth))
               if value is None]
    return BusinessContext(volume_2025=v2025, volume_2030=v2030, growth_pct=growth,
                           market_share=sales.get("share_of_total_2030"),
                           note=f"Not available: {', '.join(missing)}." if missing else "")
