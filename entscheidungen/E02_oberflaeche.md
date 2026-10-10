# E02 Oberfläche: Streamlit, einfache Web-App oder etwas anderes?

**Frage:** Womit bauen wir die Oberfläche für den Produktmanager?

## Optionen

| | Option | Plus | Minus |
|---|---|---|---|
| A | **Next.js (haben wir schon)** | Startseite mit Liste, Dropdown, Badges und Score-Balken läuft bereits. Sieht professionell aus, Lasse arbeitet daran. | Mehr Code. Nicht-Coder können kaum direkt mitbauen. |
| B | Streamlit (Python) | Sehr schnell für Tabellen und Charts. Auch Python-Anfänger kommen klar. | Alles neu. Buttons und Formulare wirken schnell wie ein Prototyp. Wir würden die Arbeit von Lasse wegwerfen. |
| C | Nur FastAPI `/docs` + CSV | Null Aufwand. | Kein PM-Cockpit. Das ist laut Brief der Kern. |

## Was es für die Demo bedeutet

A: Die Demo sieht aus wie ein echtes Produkt. B: schneller Start, aber später Grenzen. C: Notfall, steht schon als letzte Reserve in `PLAN.md` §10.

## Empfehlung

**A, Next.js behalten.** Es läuft schon, die API passt dazu. Das Team baut mit durch Inhalte (Texte, Prompts, Gewichte, Grafiken), nicht durch React-Code. Für schnelle Experimente von Nicht-Codern kann jede Person in `werkstatt/<name>/` ein kleines Streamlit-Skript haben, das nicht in die Abgabe geht.

## Unsere Entscheidung
_(leer)_

## Warum
_(leer)_
