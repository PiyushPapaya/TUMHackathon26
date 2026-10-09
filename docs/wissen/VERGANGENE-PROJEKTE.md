# Vergangene EHL-Projekte (Season 1) und was wir daraus lernen

> Quellen: Ergebnisseiten auf ehl.gg (Abruf 09.10.2026) und die öffentlichen Abgabe-Snapshots
> unter `github.com/european-hackathon-league` (56 Repos von Paris, München 2 und Zürich).
> Die Auswertung wurde mit einem Skript über die Git-Metadaten gemacht. Die Stichprobe ist klein
> (14 Teams auf Platz 1-3), deshalb sind die Muster **Tendenzen, keine Gesetze**.

## Alle Matches und Ergebnisse

| Match | Datum | Challenge | 1. | 2. | 3. |
|---|---|---|---|---|---|
| München 1 (Makeathon) | 17.-19.04. | HappyRobot | Multiply | Yantra | AskOnce |
| | | Spherecast | bussies | Harissa | Default Name |
| | | Osapiens | Non Deterministic | Aguacates | OMEGA-EARTH |
| | | Reply | TakeTheMoneyAndRun | AgenTUM | y/agent |
| Paris | 27.-28.06. | Cross-modal Retrieval 3D Medical Images (Inria) | TakeTheMoneyAndRun | Masloriji | undeterministic tornado |
| | | Lucky Loop (Hyperparameter) | BaoByte | Pegasus | Kraft |
| | | Mirror Mirror (Floor Plans, Davis) | Oasis | lihua | Bourbaki |
| München 2 | 22.-23.08. | Find an Industry, Give it an Engineer (Viktor) | makalu | Harissa | ScoobaNi |
| | | Insurance Invoice Poker (QuantCo) | Codacabana | error404.ai | TakeTheMoneyAndRun |
| | | The Router: Right Model, Every Prompt | Tetrad | IHSG | Baile de Munique |
| Zürich | 12.-13.09. | Give AI a Sense of Time (Agentic Systems Lab) | Swiss Clocks | y/agent | AlleGuteDingeSindDrei |
| | | BMW Motorrad „Best Route“ / „Find Your Thrill“ | PolyETHylene | AskOnce | Benevolent Agent Hive |

Quellen: ehl.gg/matches/munich-1, /paris, /munich-2, /zurich. Die Sponsor-Zuordnung in Klammern stammt aus den READMEs der Teams.

**Serien-Gewinner:** *TakeTheMoneyAndRun* (2× Platz 1, 1× Platz 3), *Harissa* (2× Platz 2), *y/agent*, *AskOnce* und *Yantra* (je mehrfach Top 5).

## Kennzahlen: platziert vs. nicht platziert

| Gruppe | n | Commits (Median) | README (Median Zeichen) | Mermaid-Diagramm | Tests-Ordner | CI | Python dominiert |
|---|---|---|---|---|---|---|---|
| Platz 1 | 4 | 42 | 10.067 | 25 % | 50 % | 50 % | 50 % |
| Platz 1-3 | 14 | 42 | 9.059 | 21 % | 64 % | 21 % | 71 % |
| ohne Platz | 34 | 51,5 | 7.665 | 6 % | 68 % | 18 % | 76 % |

**Lesart:** Mehr Commits oder mehr Tests machen keinen Sieger. Auffällig ist der **Mermaid-Unterschied** (21 % vs. 6 %) und die etwas längere README. `paris-lihua` wurde Zweiter mit **1 Commit und 18 Zeichen README**. Das zeigt: **Die Jury entscheidet über Pitch, Demo und Ergebnis, nicht über das Repo.**

## Die Gewinner im Detail

| Team (Match) | Idee in einem Satz | Stack | Evaluation / Zahl | Demo-Form | README / Historie |
|---|---|---|---|---|---|
| **Codacabana** (M2, 1.) | Autonomer Schadens-Prüfer für QuantCos Versicherungs-Spiel: 4 „blinde“ LLM-Stimmen + deterministische Preislogik | Python, uv, Next.js-Dashboard | „Rank 1 of 17, +848.081 EUR“, „Median 7,6 s über 121 Läufe“ | Live-Dashboard + 2-seitiges PDF | Mermaid mit Dateinamen pro Schritt, Repo-Map, 103 Tests, Beispieldaten ohne Key lauffähig |
| **makalu** (M2, 1.) | „ARES“: Retail-Agent, der Signale prüft, Pläne von Devin erzeugen lässt und jeden Plan unabhängig verifiziert | FastAPI + Next.js | Demo-Matrix: alle Szenarien `passed`/`escalated` | Command Center + „Playground“ mit Safe-demo/Mock/Live-Modus | Ehrlicher Alpha-Hinweis, Lockfiles, Betriebshandbuch |
| **TakeTheMoneyAndRun** (Paris, 1.) | Gehirn-MRT-Suche über Modalitäten hinweg mit klassischer Registrierung statt Deep Learning | Python, GPU-Registrierung | **MRR = 1.000** auf 3 Datensätzen; 3 DL-Alternativen verloren | Report-PDF + 2 Pitch-Decks + Cheatsheet | Tabelle Ergebnis pro Datensatz ganz oben, „Why we trust it (not overfit)“ |
| **Oasis** (Paris, 1.) | Grundriss-Generierung aus Wohnungsumriss | Python + Web | (Metrik in README-Kopf nicht genannt) | **Öffentliche Live-Website** mit „Studio“ | Daten, Aufgabe und Ideen sauber erklärt |
| **IHSG** (M2, 2.) | Cache-bewusster Modell-Router für Agent-Trajektorien | Python | „honest observational evaluation“, eigene Model Card | CLI + Auswertung | Tabelle „Challenge → unsere Antwort“, Abschnitt „What we do not claim“, Mermaid |
| **No Idea** (Zürich, 5., BMW) | Motorrad-Routen nach „Fahrspaß“ aus BMW-Crowd-Daten (8.000 Fahrten) | Python, OSM | jede Behauptung gegen Daten geprüft, Features als „weak/rejected“ markiert | Live-Demo, Pitch | `CONTEXT.md` als Agent-Gedächtnis, Entire-Skills |

## Winning Patterns (mit Beleg)

1. **Eine harte Zahl in den ersten 5 Zeilen der README.** MRR = 1.000 (TTMAR), „rank 1 of 17“ (Codacabana), „7,6 s Median“ (Codacabana).
2. **Ergebnis gegen eine Baseline oder Alternativen.** TTMAR: „Alle 3 Deep-Learning-Alternativen verloren gegen die trainingsfreie Methode.“
3. **Ehrliche Grenzen.** IHSG: „What we do not claim“; makalu: „alpha demonstration“; Codacabana: „honest list of where we did not succeed“. Die Jury fragt sowieso danach.
4. **Mermaid-Diagramm mit Dateinamen an jedem Knoten** (Codacabana, IHSG, ScoobaNi). Häufiger bei Platzierten (21 % vs. 6 %).
5. **Demo, die nie ausfällt:** Safe-demo/Replay-Modus ohne externe KI (makalu), Beispieldaten im Repo (Codacabana: „pipeline runs with no tournament key“).
6. **Live-URL**, die die Jury selbst anklicken kann (Oasis).
7. **„Judges — start here“-Abschnitt** mit 2-4 Links und Lesezeit (binbusy, Codacabana „Start here: docs/approach.pdf“).
8. **Tabelle „Challenge-Anforderung → unsere Umsetzung“** (IHSG „Why This Is Different“). Das trifft genau den Review-Punkt `challenge_alignment`.
9. **Robustes Design statt maximaler Features:** Codacabana schickt sofort eine vorläufige Abgabe, „a failure costs the difference, never everything“.
10. **LLM liest, deterministischer Code entscheidet.** binbusy-ADR „The model reads, the engine prices“, Codacabana genauso. Das wirkt in der Jury verlässlich und erklärbar.
11. **Python für Daten/ML** (71 % der Platzierten), Web-UI nur als dünne Schicht.
12. **Pitch-Material im Repo** (TTMAR: `presentation/pitch_general.pdf` + `pitch_technical.pdf` + Cheatsheet).
13. **Ein Agent-Gedächtnis-Dokument** (`CONTEXT.md` bei No Idea, `CLAUDE.md` bei vielen), damit alle Agent-Sessions denselben Stand haben.

## Losing Patterns (mit Beleg)

1. **Viel Doku ohne Siegerzahl.** binbusy: exzellente README und Write-up, 437 Commits, 11 Autoren, **kein Platz**. Im Wettbewerbs-Spiel lag Codacabana in der Rangliste vorn.
2. **Viel Aktivität ≠ Qualität.** Unplatzierte haben im Median **mehr** Commits (51,5 vs. 42).
3. **Fehlende oder leere README.** `claims-renaissance` (0 Zeichen) blieb ohne Platz. `eyay` (0 Zeichen) kam nur auf Platz 4, obwohl es in der Spiel-Rangliste Zweiter war (laut Codacabana-README: +710.048 EUR).
4. **Binär- und Build-Müll im Repo** (`.pyc`, `.dll`, `.pyd`, Logs bei nowayhome, claims-renaissance, non-deterministic). Das kostet Review-Punkte bei `best_practices`.
5. **Riesige Repos** (devitects: 3.074 Dateien, 3D-Assets) ohne Platz. Der Reviewer sieht nur einen Bruchteil.
6. **Features behaupten, die nicht laufen.** Gegenbeispiel No Idea, das selbst „Joy Meter WEAK, claim REJECTED“ dokumentiert. Die Jury fragt nach.
7. **Kein Fokus auf die Challenge-Kriterien.** BMW nannte 6 explizite Kriterien plus Bonus für Erklärbarkeit und Live-Demo; wer nicht jedes abdeckt, verschenkt Punkte (CONTEXT.md von No Idea).

## Konsequenzen für uns (bereits umgesetzt)

- README-Template mit Zahl oben, „Jury: hier starten“, Mermaid, Alignment-Map, „Was wir nicht behaupten“ → [`README.md`](../../README.md).
- Demo-Modus mit Beispieldaten und Backup-Video ist Pflicht → [`docs/pitch/PITCH.md`](../pitch/PITCH.md).
- Evaluation mit Baseline ab Samstag 18:00 → [`docs/ZEITPLAN.md`](../ZEITPLAN.md).
- `.gitignore` gegen Build-Müll und das Budget-Skript gegen ein zu großes Repo.
