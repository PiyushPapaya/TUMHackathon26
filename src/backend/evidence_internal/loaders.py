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
- US-Studie: Blöcke à 8 Zeilen (Attribut, Sample total, 7 Stufen "I Hate It".."I Love It").
- CN/EU-Studie: Attribut-Zeile, darunter "Mean" (Skala ~1-10), Spalten = Modell je Land.
"""

from __future__ import annotations

from pathlib import Path

from core.models import Evidence


def load_all_evidence(cfg: dict, raw_dir: Path) -> list[Evidence]:
    """Feedback + Studie des Szenarios als Belege.

    TODO Pfad A (in dieser Reihenfolge, je mit Test in tests/pfad_a/):
    1. load_feedback: nur Zeilen mit Country in cfg["countries"]; ID-Duplikate zusammenführen;
       polarity aus Feedback Type (Likes=+1, Defect/Difficult to Use=-1, Wants=-1, leer=0).
    2. load_study: pro Attribut ein Beleg mit Satz wie
       "Rear interior roominess: 12 % negativ (I Hate It..Unsatisfactory), Top-2-Box 61 %".
    3. Out-of-Scope markieren (meta["scope"]="out"): reine Defekte/Werkstattfälle sind
       Qualität, keine Kundenanforderung -> behalten, aber kennzeichnen.
    """
    raise NotImplementedError("Pfad A: load_all_evidence noch nicht gebaut (siehe docs/pfade/PFAD-A.md)")
