# E05 Wie priorisieren wir? Faktoren und Gewichte

**Frage:** Welche Faktoren zählen, und wie viel? Der Score ist eine Formel in Python (kein KI-Urteil), damit wir sie erklären können.

## Stand heute (`src/backend/requirements_engine/scoring.py`)

| Faktor | Gewicht | Frage dahinter | Beispiel (synthetische Beispieldaten, `REQ-G60-US-001`) |
|---|---|---|---|
| Kundenschmerz | 25 % | Wie stark stört es? | 61 Kommentare, 70 % Bedienprobleme |
| Reichweite | 20 % | Wie viele Kunden, wie viel Absatz? | US: 78.000 Fahrzeuge 2025, 80.000 in 2030 |
| Zufriedenheitslücke | 20 % | Abstand in der Kundenstudie | Beispielwert: 9 % unzufrieden mit "Intuitiveness of controls". Echte Studie: 15,0 % unzufrieden mit "Operation of heater/ AC controls" |
| Wettbewerbsdruck | 15 % | Bieten es andere schon an? | 3 Webquellen: Wettbewerb kehrt zu Tasten zurück |
| Zukunftsrelevanz | 10 % | Zählt es in 3-5 Jahren noch? (Annahme!) | Trend unklar: Sprachsteuerung könnte den Bedarf senken |
| Aufwand (invers) | 10 % | Wenig Aufwand = höher | Aufwand M = 0,6 |

Danach wird der Score mit der **Evidenz-Sicherheit** multipliziert: A = 1,0 · B = 0,85 · C = 0,7 · D = 0,5. Eine schlecht belegte Anforderung rutscht also nach unten, auch wenn der Schmerz groß ist.

## Optionen

| | Option | Plus | Minus |
|---|---|---|---|
| A | **So lassen** | Funktioniert, getestet, erklärt sich selbst. | Gewichte sind unsere Schätzung. |
| B | Anderer Fokus (z. B. Reichweite höher) | Passt, wenn wir "Wo ist der größte Markt?" betonen wollen. | Muss begründet werden. |
| C | Zusätzlicher Faktor (z. B. "Differenzierung") | Mehr Tiefe. | Mehr Erklärung, mehr Tests, Zeit. |

## Was es für die Demo bedeutet

Die Gewichte sind live im Cockpit einstellbar (Regler), jede Änderung steht im Prüfpfad. Wir zeigen: Reichweite hoch, und das Ranking ändert sich.

## Empfehlung

**A als Startwerte, aber ihr entscheidet die Gewichte selbst.** Frage ans Team: Ist "Kundenschmerz" wirklich wichtiger als "Reichweite"? Eine Begründung pro Gewicht reicht, dann gehört sie euch (und der Jury-KI gefällt es). Der Regler macht die Unsicherheit sichtbar.

## Unsere Entscheidung
_(leer. Gewichte hier eintragen: Schmerz __ · Reichweite __ · Lücke __ · Wettbewerb __ · Zukunft __ · Aufwand __)_

## Warum
_(leer)_
