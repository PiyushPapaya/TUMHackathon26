---
name: challenge-intake
description: Wertet einen Sponsor-Brief aus und bereitet die Ideenentscheidung vor. Benutzen, wenn jemand einen Challenge-Text, Brief, Foto-Notizen vom Reveal oder Deep Dive einfügt oder „bewerte die Challenge“, „welche Idee nehmen wir“ sagt (Sa 10:00-13:00).
---

# Challenge-Intake

Ziel: In 20 Minuten von Brief zu Entscheidungsvorlage. Ergebnis landet in `docs/research/CHALLENGE.md` (Owner Dennis; andere schreiben in ihren Workspace und schicken es Dennis).

## Eingaben lesen

1. Den Brief **wörtlich** übernehmen (Kernsätze zitieren). Der EHL-KI-Reviewer misst Challenge-Alignment am Brief-Text.
2. Vorbereitung lesen: `docs/wissen/SPONSOREN.md` (Fakten, 3 Ideen-Hypothesen, Fragen pro Partner) und `docs/wissen/VERGANGENE-PROJEKTE.md` (Winning Patterns).

## Schritte

1. **Bewertungskriterien extrahieren**, wörtlich, mit Gewicht falls genannt → Tabelle in `CHALLENGE.md`.
2. **Daten und Tools** des Partners auflisten (Format, Größe, Lizenz).
3. **3-5 Ideen** sammeln: die Hypothesen aus `SPONSOREN.md` anpassen und eigene ergänzen. Jede Idee in einer Zeile: Nutzer, Problem, Kern-Feature.
4. **Bewerten** je 1-5: Code-Qualität-Potenzial (30), Architektur (25), Alignment (25), Innovation (20), dazu Machbarkeit in 20 h, Demo-Fähigkeit, Sponsor-Fit.
   `Review = (CQ·30+Arch·25+Align·25+Inn·20)/100`, `Gesamt = 0,6·Review + 0,2·Machbarkeit + 0,2·Demo`. Rechne mit Python nach, nicht im Kopf.
5. **Die eine Zahl** pro Top-Idee: Metrik, Testset (wer labelt wie viele Fälle bis wann), Baseline.
6. **MVP-Schnitt** für die Top-Idee: Must-have bis Sa 22:00 / Nice-to-have / bewusst NICHT.
7. **API-Vertrag-Entwurf**: 2-4 Endpunkte mit Beispiel-Request/Response (geht an Piyush für `src/shared/API.md`).
8. **Aufgabenverteilung** auf die 5 Rollen (Tabelle in `CLAUDE.md`), jede Aufgabe mit Deadline aus `docs/ZEITPLAN.md`.
9. **Fragen an den Partner** für den Deep Dive (aus `SPONSOREN.md` + neue aus dem Brief), max. 5, die Antworten ändern unsere Entscheidung.

## Ausgabe

- Ausgefülltes `docs/research/CHALLENGE.md` (oder Entwurf in `workspace/<name>/`).
- Im Chat: Ranking-Tabelle + Empfehlung in Ownership-Sprache: „Wir empfehlen X, weil …; Y verworfen, weil …“.
- **Die Entscheidung trifft das Team, die Challenge-Wahl auf ehl.gg macht Piyush bis 13:00.**
