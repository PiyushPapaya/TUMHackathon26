"""Evidenzstufe A-D: feste Regeln statt LLM-Bauchgefühl (Owner: Pfad C).

Warum Regeln: Der Brief will klar sehen, wo eine Aussage auf Belegen beruht und wo
auf Annahmen. Eine Regel ist prüfbar und für den PM in einem Satz erklärbar.

Die Regel in einem Satz (Entscheidung Sa 10.10., kalibriert an den echten G60-US-Daten):
  Basis nur nach Nennungen (15+ = B, sonst C); bestätigt eine zweite, unabhängige Quellenart
  die Aussage (mindestens 5 Nennungen), steigt die Stufe um eine (B -> A, C -> B). Auf A hebt nur
  eine zweite BMW-Quelle; Web hebt höchstens auf B.

Echte Zahlen (G60-US, 16 Anforderungen, Nennungen von 7 bis 581): Nur 6 sind durch eine Studie
bestätigt. Mit der alten Regel (A = zwei Quellenarten UND 20 Nennungen) gab es 1 x A, 12 x B, 3 x C,
und eine Spracherkennung mit 8 Nennungen plus Studie (16 % unzufrieden) stand gleichauf mit einer
Vermutung. Jetzt: 3 x A, 13 x B. Verworfen: A schon ab 10 Nennungen (Schwelle schwer zu begründen,
setzt eine kleine Anforderung vor den Touchscreen mit 161 Nennungen).
Viele Nennungen aus EINER Quelle ergeben nie A: Die Stufe sagt, wie sicher wir sind, und eine Quelle
kann sich irren.

Nachkalibrierung mit Webbelegen (Sa 10.10. abends): Mit Webrecherche standen beim G60-US 10 von 12
Anforderungen auf A (F70-EU 9 von 16), weil fast jede einen Webtreffer hat, und der streift oft nur das
Thema (z. B. Kofferraumvolumen eines Wettbewerbers als "Beleg" für ein Türschloss-Problem). Darum hebt
Web nur bis B; A braucht zwei BMW-eigene Quellen (Feedback + Studie), passend zur Mentor-Aussage
"BMW-Daten > Web". Ergebnis: G60-US 4 x A, F70-EU 3 x A. Verworfen: Web gar nicht mehr zählen lassen
(dann wäre die Triangulation wertlos und ein dünner Befund mit Webbestätigung bliebe C).
"""

from __future__ import annotations

from core.models import EvidenceLevel, SourceType

# Unabhängige Quellenarten. Absatz und Optionsliste sind Kontext, kein Kundenbeleg.
CUSTOMER_SOURCES = {SourceType.FEEDBACK, SourceType.STUDY, SourceType.WEB}

# Rangfolge laut BMW-Mentor: BMW-eigene Daten zählen mehr als Web/Social Media. Die
# Feedback-Quellen A-D untereinander sind gleichwertig, darum gibt es dafür keine Regel.
# Web darf bestätigen (zweite Quellenart), aber allein nie eine Anforderung tragen.
BMW_SOURCES = {SourceType.FEEDBACK, SourceType.STUDY}

SOLID_MENTIONS = 15  # ab hier ist ein Thema mit einer Quelle belastbar genug für B
MIN_MENTIONS_FOR_LIFT = 5  # darunter hebt auch eine Bestätigung nicht: zu dünn, um mehr als Zufall zu sein


def classify(mention_count: int, source_types: set[SourceType], forward_looking: bool) -> tuple[EvidenceLevel, str]:
    """Liefert Stufe + Begründungssatz (englisch, steht im Wasserfall für den PM)."""
    independent = source_types & CUSTOMER_SOURCES
    if forward_looking and mention_count < 5:
        return EvidenceLevel.D, "Forward-looking assumption: few direct customer data points, rests on trends."
    if not independent:
        return EvidenceLevel.C, "No customer data behind it: at most a hint."
    if not independent & BMW_SOURCES:
        return EvidenceLevel.C, f"{mention_count} mentions from web sources only: without BMW data at most a hint."
    solid = mention_count >= SOLID_MENTIONS
    confirmed = len(independent) >= 2 and mention_count >= MIN_MENTIONS_FOR_LIFT
    bmw_confirmed = len(independent & BMW_SOURCES) >= 2  # nur Feedback + Studie reicht für A
    if solid and confirmed and bmw_confirmed:
        return EvidenceLevel.A, f"{mention_count} mentions, confirmed by {len(independent)} independent source types."
    if solid and confirmed:
        return EvidenceLevel.B, (f"{mention_count} mentions, confirmed only by web sources: "
                                 "A needs a second BMW source (study).")
    if confirmed:
        return EvidenceLevel.B, (f"Only {mention_count} mentions, but confirmed by {len(independent)} "
                                 "independent source types.")
    if solid:
        return EvidenceLevel.B, f"{mention_count} mentions, but from a single source type."
    return EvidenceLevel.C, f"Only {mention_count} mentions: a hint, not a solid finding."
