"""Read price references from the supplied PDFs without estimating future costs."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=12)
def _prices(path: str, modified: int) -> dict:
    import pymupdf

    amounts, pages = [], []
    with pymupdf.open(path) as document:
        for number, page in enumerate(document, start=1):
            text = page.get_text()
            if "FAHRZEUGGRUNDPREIS" not in text:
                continue
            found = []
            for block in text.split("FAHRZEUGGRUNDPREIS")[1:]:
                block = block.split("EUR inkl.")[0]
                found.extend(int(value.replace(".", "")) for value in
                             re.findall(r"(?m)^\s*(\d{2,3}\.\d{3}),[–−-]\s*$", block))
            if found:
                amounts.extend(found)
                pages.append(number)
    return {"min_eur": min(amounts) if amounts else None,
            "max_eur": max(amounts) if amounts else None, "pages": pages}


def product_context(state, root: Path) -> dict:
    path = root / "data" / "raw" / f"{state.scenario.derivative}_OptionList.PDF"
    engines = sorted({e.meta.get("engine", "").replace("BEVE", "BEV")
                      for e in state.evidence.values() if e.meta.get("engine")})
    result = {"source": path.name, "reference_market": "Germany", "currency": "EUR",
              "note": "Supplied German list prices including 19% VAT, excluding delivery. "
                      "Reference only; not a local-market quote or a successor cost estimate.",
              "engines": engines, "min_eur": None, "max_eur": None, "pages": []}
    if not path.exists():
        return {**result, "note": "No supplied option list for this model. Price reference unavailable."}
    try:
        return {**result, **_prices(str(path), path.stat().st_mtime_ns)}
    except (OSError, RuntimeError, ValueError):
        return {**result, "note": "The supplied option list could not be read. Price reference unavailable."}
