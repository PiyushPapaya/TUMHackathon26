"""Pfad C: "Gibt es das heute schon?" Abgleich mit der Optionsliste (Preisliste-PDF).

Vertrag (nicht ändern ohne Lead):
    load_offer(pdf_path: Path) -> list[dict]          # [{"name", "code", "status"}]
    check(requirement_title: str, offer: list[dict]) -> OfferCheck

Warum das wertvoll ist: Wünschen Kunden etwas, das es als Sonderausstattung schon gibt,
ist die richtige Anforderung oft "in ein Paket/Serie aufnehmen" oder "besser erklären",
nicht "neu entwickeln". Variante und Paket sind laut Brief ausdrücklich in scope.

Fakten zur PDF (geprüft am 10.10.): Text mit pymupdf lesbar. SA-Nr. = 3-stelliger Code
(z. B. 337, 4MA), Preise wie "1.120,–", Symbole ■ = Serie, □ = Sonderausstattung.
Start: einfacher Wortabgleich; danach LLM-Abgleich nur gegen die Kandidaten.
"""

from __future__ import annotations

from pathlib import Path

from core.models import OfferCheck


def load_offer(pdf_path: Path) -> list[dict]:
    raise NotImplementedError("Pfad C: load_offer noch nicht gebaut (siehe docs/pfade/PFAD-C.md)")


def check(requirement_title: str, offer: list[dict]) -> OfferCheck:
    return OfferCheck(status="unknown", note="Abgleich noch nicht gebaut.")
