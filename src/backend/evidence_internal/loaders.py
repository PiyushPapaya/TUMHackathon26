"""Pfad A: BMW-Rohdaten -> einheitliche Belege (Evidence). Autonom, ohne LLM.

Warum ohne LLM: Einlesen muss reproduzierbar und vollständig sein. Jede Zeile
bekommt eine stabile ID, damit Anforderungen später exakt auf sie zeigen können.

Vertrag (nicht ändern ohne Lead):
    load_all_evidence(cfg: dict, raw_dir: Path) -> list[Evidence]

Fakten zu den Daten (geprüft am 10.10.):
- Feedback-Excel: 1 Zeile pro (Kommentar, Klassifikation). Gleiche "ID" = gleicher
  Kommentar mit mehreren Labels -> zu EINEM Beleg zusammenfassen, Labels in meta.
- Spalten: ID, Source (A-D), Country, Engine Type (ICE/BEVE/PHEV), Feedback Type
  (Likes/Difficult to Use/Defect/Wants/leer), Customer Feedback, Vfc level2 Name, Vfc level3 Name.
- Quellen: A = Online-Bewertungen, B = Händler/Service-Notizen ("Customer stated"),
  C = Umfrage-Freitext, D = "das liebe ich am meisten"-Antworten.
- US-Studie: Blöcke à 9 Zeilen (Attribut, Sample total, 7 Stufen "I Hate It".."I Love It"),
  zwei Blöcke mit einer zusätzlichen leeren Zeile; deshalb liest study.py nach Label, nicht nach Abstand.
- CN/EU-Studie: Attribut-Zeile, darunter "Mean" (Skala ~1-10), Spalten = Modell je Land.
"""

from __future__ import annotations

from pathlib import Path

from core.models import Evidence
from evidence_internal.feedback import load_feedback
from evidence_internal.study import load_study


def load_all_evidence(cfg: dict, raw_dir: Path) -> list[Evidence]:
    """Feedback + Studie des Szenarios als Belege (A1 + A2)."""
    return load_feedback(cfg, raw_dir) + load_study(cfg, raw_dir)
