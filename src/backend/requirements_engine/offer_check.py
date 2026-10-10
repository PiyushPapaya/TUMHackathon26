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

from pydantic import BaseModel

from core.llm import ask_json
from core.models import OfferCheck
from requirements_engine.offer_parser import parse_option_lines, parse_series_lines

SYSTEM_PROMPT = """You check whether a customer requirement for a BMW is ALREADY covered by today's
equipment list (German price list: standard equipment and optional extras, incl. packages).
Answer only from the numbered list you get. Match by meaning, the list is German and the
requirement is English; package contents ("contains") count.
- status "standard": covered by standard equipment. status "optional": covered by an optional extra
  or package. status "not_offered": nothing in the list covers it.
- For standard/optional you MUST give the option_id (the number like O12, not the code) of the best match.
- note: one short English sentence on why (max 25 words). Never invent options."""


class OfferAnswer(BaseModel):
    status: str  # standard | optional | not_offered
    option_id: str | None = None
    note: str = ""


def _page_lines(pdf_path: Path) -> list[list[str]]:
    import pymupdf  # erst hier importieren: Tests ohne PDF brauchen es nicht

    with pymupdf.open(pdf_path) as doc:
        return [page.get_text().splitlines() for page in doc]


def load_offer(pdf_path: Path) -> list[dict]:
    """Liste aller Optionen: {"name", "code", "status", "contents", "note"} (Code leer bei Serie)."""
    offer: list[dict] = []
    for lines in _page_lines(Path(pdf_path)):
        options = parse_option_lines(lines)
        # Seiten mit Codes sind Sonderausstattung; Seiten nur mit ■ sind die Serienübersicht.
        offer.extend(options if options else (parse_series_lines(lines) if "■" in lines else []))
    return offer


def _as_prompt_line(number: int, option: dict) -> str:
    contents = f" | contains: {'; '.join(option['contents'][:8])}" if option.get("contents") else ""
    return f"O{number} | {option['code'] or '-'} | {option['status']} | {option['name']}{contents}"


def check(requirement_title: str, offer: list[dict]) -> OfferCheck:
    if not offer:
        return OfferCheck(status="unknown", note="No option list available.")
    by_id = {f"O{n}": option for n, option in enumerate(offer, start=1)}
    by_id.update({o["code"]: o for o in offer if o["code"]})  # die KI nennt manchmal den Code statt "O12"
    listing = "\n".join(_as_prompt_line(n, o) for n, o in enumerate(offer, start=1))
    try:
        answer = ask_json(SYSTEM_PROMPT, f"Requirement: {requirement_title}\nOptions:\n{listing}", OfferAnswer)
    except Exception as error:  # kein Netz, Demo-Cache-Fehlschlag, Schemafehler: nie die Pipeline stoppen
        return OfferCheck(status="unknown", note=f"Check not possible ({type(error).__name__}).")
    if answer.status == "not_offered":
        return OfferCheck(status="not_offered", note=answer.note)
    option = by_id.get(answer.option_id or "")
    if answer.status not in ("standard", "optional") or option is None:
        return OfferCheck(status="unknown", note="The AI named no valid option from the list.")
    # Status aus dem PDF, nicht aus der KI: sie darf Serie/Option nicht umdeuten.
    return OfferCheck(status=option["status"] if option["status"] != "unknown" else answer.status,
                      option_code=option["code"] or None, note=f"{answer.note} ({option['name']})".strip())
