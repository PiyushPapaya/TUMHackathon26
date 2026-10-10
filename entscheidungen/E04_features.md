# E04 Welche Extra-Features bauen wir? (Feature-Speisekarte)

**Frage:** Die Pflicht ist gesetzt (Liste, Detail, Entscheiden, Prüfpfad). Welche Extras kommen dazu? Maximal 3-4 wählen, sonst wird nichts fertig.

Aufwand: klein = unter 1 Stunde mit Claude, mittel = 1-2 Stunden, groß = mehr.

| # | Feature | Was es tut | Warum die Jury es mag | Aufwand | Stand im Repo | Wer |
|---|---|---|---|---|---|---|
| 1 | **Konflikt-Detektor** | Zeigt, wenn Quellen sich widersprechen (Display gelobt vs. Touch-Bedienung kritisiert) | Brief: "conflicting evidence" | klein | Konflikt-Badge in der Liste da, Befunde liefern `conflicts_with` | Aditya, Lasse |
| 2 | **Gewichte-Schieberegler** | Priorisierung live ändern, Ranking sortiert sich neu | Brief: "logic you can explain" | mittel | Backend kann es (`normalize_weights`, Ereignis `WEIGHTS_CHANGED`), UI fehlt | Dennis, Lasse |
| 3 | **Challenge-KI (Devil's Advocate)** | PM klickt "Challenge", KI antwortet mit Belegen und Gegenbelegen | Brief: "challenge" | mittel | regelbasierte Version da (`challenge.py`), KI-Version Ticket C6 | Dennis |
| 4 | **Kundenstimmen-Wand** | Echte Zitate pro Anforderung | Macht die Evidenz greifbar | klein | Zitate stecken in den Belegen | Lasse |
| 5 | **Evidenz-Ampel** | A-D als Farbe pro Anforderung | Zeigt auf einen Blick, wie sicher wir sind | klein | Badge existiert | Lasse |
| 6 | **Markt-Umschalter G60/G70, US/EU** | Szenario-Dropdown | Brief: "adaptable" | klein im UI, mittel für Daten | Dropdown da, Daten für G70/F70 fehlen | Piyush, Aditya |
| 7 | **Audit-Zeitreise** | Geschichte einer Anforderung Schritt für Schritt abspielen | Zeigt den Prüfpfad lebendig | mittel | Hash-Kette da, Ansicht fehlt | Lasse |
| 8 | **Swipe-Modus** | Anforderungen wie Karten annehmen / ablehnen | Spaßig, gute Demo | mittel | fehlt | Lasse |
| 9 | **Optionslisten-Check** | "Gibt es das schon?" gegen die BMW-Optionsliste | Zeigt, dass die Antwort manchmal ein Paket ist | mittel | Ticket C5 | Dennis |

## Empfehlung

**Pflicht dazu: 5 (Ampel, fast fertig), 1 (Konflikte), 2 (Regler), 3 (Challenge).** Das sind die vier, die direkt Brief-Sätze beantworten. **4 (Zitate-Wand)** als Bonus, weil klein. **Nicht jetzt: 8, 7.** Sie sind nett, aber kein Brief-Punkt.

## Unsere Entscheidung
_(leer)_

## Warum
_(leer)_
