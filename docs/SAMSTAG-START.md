# Samstag 09:55-14:00: exakter Ablauf

Rollen: **P** Piyush · **L** Lasse · **A** Aditya · **D** Dennis · **F** Fabian. Vorbereitung: [`docs/wissen/SPONSOREN.md`](wissen/SPONSOREN.md) (Fakten, Fragen) und [`docs/wissen/SCAFFOLD-PLAENE.md`](wissen/SCAFFOLD-PLAENE.md) (fertige Pläne pro Idee).

## 09:55 Transparenz-Marke (P)

`git switch main && git pull && git tag vor-event && git push origin vor-event`. **Warum:** Damit ist belegt, dass alles bis hier nur Tooling und Doku ist. Die README verweist darauf.

## 10:00-11:00 Kick-off + Challenge-Reveal (AudiMax)

| Wer | Notiert | Wohin |
|---|---|---|
| D | Brief **BMW** wörtlich + Bewertungskriterien | `workspace/dennis/briefs.md` |
| A | Brief **Atira** wörtlich + Kriterien + gegebene Daten/APIs | `workspace/aditya/notizen.md` |
| F | Brief **tacto** wörtlich + Kriterien + gegebene Daten/APIs | `workspace/fabian/notizen.md` |
| L | **Fotos jeder Slide** (Handy), danach in die Gruppe | Gruppe |
| P | Abgabefelder, Deadlines, Entire-Hinweise, Raum der Deep Dives | `workspace/piyush/notizen.md` |

## 11:00-11:30 Entire-Onboarding

- **P + L hören zu** und gleichen mit `docs/wissen/OPENAI-UND-ENTIRE.md` ab (`commit_linking`, Ref-Format, „signed“-Bonus, Abgabe-Anforderungen); Abweichungen → `workspace/piyush/notizen.md`. D, A, F tippen ihre Brief-Notizen ab.

## 11:30-12:00 `challenge-intake` für alle 3 Challenges parallel

- D → BMW, A → Atira, F → tacto: jeweils eigene Claude-Session: „Starte challenge-intake für <Partner> mit diesem Brief: …“.
- Ergebnis pro Partner: Kriterien, Ideen-Score (inkl. Scaffold-Plan), die eine Zahl, 5 Fragen.
- 11:55 **P legt die Raum-Verteilung fest**: Partner-Rangliste nach Gesamt-Score.

## 12:00-13:00 Deep Dives (3 Räume im EG)

| Raum | Wer | Aufgabe |
|---|---|---|
| Favorit 1 | **P + D** | 5 Fragen aus SPONSOREN.md + intake; nach Testdaten mit „richtiger Antwort“ fragen |
| Favorit 2 | **L + F** | 5 Fragen; Demo-Erwartung und Nutzer klären |
| Favorit 3 | **A** | 5 Fragen; Datenformat und Größe notieren |

- Antworten live in die Gruppe („Partner, Frage, Antwort, ändert das die Wahl?“). **12:45** alle am Team-Tisch.

## 12:50 Entscheidung (10 min, P moderiert)

1. Gesamt-Score je Top-Idee aus intake (nachgerechnet) + Deep-Dive-Antworten.
2. Wer hat eine messbare Zahl mit Testdaten? Ohne Zahl kein Sieg.
3. Ownership-Satz in `docs/research/CHALLENGE.md`: „Wir nehmen X, weil …; Y verworfen, weil …“.

## 12:55 Challenge-Wahl auf ehl.gg (P als Captain)

**Voraussetzung: alle 5 eingecheckt** (sonst lässt die Plattform die Wahl nicht zu). Wahl bis 13:00 änderbar. Screenshot in `workspace/piyush/`.

## 13:00-14:00 Vertrag + Aufgaben

| Wer | Bis 14:00 |
|---|---|
| P | `src/shared/API.md` + `src/shared/beispiele/*.json` aus dem Scaffold-Plan, PR, Merge um 14:00 |
| P | je Person 2-3 Issues (Vorlage „Aufgabe“) mit Owner + Deadline |
| L | Frontend-Gerüst (`docs/wissen/STACK.md`), Seite gegen Mock-JSON |
| A | Testset: 20-50 Fälle labeln → `tests/data/`; Baseline-Idee |
| D | `CHALLENGE.md` final, README Problem/Lösung (Entwurf) |
| F | One-Liner + Pitch-Gerüst, Logo |

Ab 14:00 gilt das Merge-Fenster jede volle Stunde ([ZEITPLAN.md](ZEITPLAN.md)).
