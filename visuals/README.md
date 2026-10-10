# visuals/

Diagramme, Charts, Mockups und Pitch-Grafiken. Wer braucht das: Pitch (Folien), Demo, Visual-Designer.
Alle Bilder entstehen aus Skripten, damit jede Person sie anpassen kann: `python scripts/make_diagrams.py` und `python scripts/make_visuals.py`.
Es gibt jeweils PNG (Folien) und SVG (verlustfrei, bei Diagrammen). Kein BMW-Logo.

| Bild | Was es zeigt | Wo wir es nutzen |
|---|---|---|
| `techflow.png` / `.svg` | Der Weg der Daten in 7 Schritten. Blau = KI allein, grau = Code, orange = Mensch entscheidet. Pflicht-Deliverable "Workflow-Diagramm". | Pitch, Folie Workflow; `docs/04_techflow.md` |
| `zitat_zu_requirement.png` / `.svg` | Vom Kundenzitat `G60-0019` über Befund, Anforderung und Priorität bis zur PM-Entscheidung | Pitch, erste Folie; Einstieg ins Problem |
| `mockup_1_liste.png` / `.svg` | Startseite: Anforderungen mit Rang, Score, Evidenz, Konflikt, Status (Beispielwerte) | Abstimmung mit Lasse; Karte E03 |
| `mockup_2_detail.png` / `.svg` | Detailseite: Beschreibung, Wasserfall, Zitate, Buttons, Pflicht-Begründung (Beispielwerte) | Abstimmung mit Lasse; Ticket D3/D4 |
| `mockup_3_audit.png` / `.svg` | Audit-Trail-Seite mit Hash-Kette (Beispieleinträge) | Abstimmung mit Lasse; Ticket D4 |
| `charts/01_top_beschwerden_g60_us.png` | Häufigste Kritik-Themen im US-Feedback zum G60 (echte Daten) | Folie Trichter; Daten-Detektiv |
| `charts/02_feedback_typen_g60_us.png` | Likes, Difficult to Use, Wants, Defect im US-Feedback (echte Daten) | Folie Trichter |
| `charts/03_studie_g60_vs_g70.png` | Die 10 Attribute des G60 mit dem höchsten Unzufriedenheitsanteil, neben dem G70 (echte US-Studie) | Folie "Evidenz aus der Studie"; Challenge-Beispiele |
| `charts/04_absatz_pro_markt.png` | Absatz des 5er (G60/G68) je Markt 2024, 2025, Prognose 2030 (echte Daten) | Folie Reichweite im Score |

| `werkbank/*.png` | Echte Screenshots der Werkbank (`/studio`): Start, Duell, Konflikt-Arena, Annahmen-Schalter, Kundenstimmen, Entscheidungslauf. Daten: synthetisches Beispiel-Bundle | Deck, Backup, Abstimmung mit Lasse |

Mockups: Alle Zahlen sind Beispielwerte. Nur das Zitat `G60-0019` und die Charts in `charts/` sind echte Daten.
