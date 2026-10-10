# Challenge-Partner: BMW Group, Atira, tacto

> Die Challenges werden erst Samstag 10:00 enthüllt. Alles hier ist **Vorbereitung**: belegte Fakten
> über die Firmen plus **Hypothesen**, was sie stellen könnten. Hypothesen sind als solche markiert.
> Über Personen nur öffentlich bekannte berufliche Rollen, denn das Repo ist öffentlich.

## Bewertungsschema für Ideen (wird im Skill `challenge-intake` benutzt)

Jede Idee bekommt 1-5 Punkte pro Kriterium:

| Kriterium | Gewicht | Frage |
|---|---|---|
| Code-Qualität-Potenzial | 30 % | Können wir das sauber und lesbar in 20 h bauen? |
| Architektur | 25 % | Gibt es eine klare, erklärbare Pipeline (Diagramm in 1 Minute)? |
| Challenge-Alignment | 25 % | Trifft es die Kriterien des Briefs wörtlich? |
| Innovation | 20 % | Neuer Ansatz oder nur Chatbot-Wrapper? |

`Review-Score = (CQ·30 + Arch·25 + Align·25 + Inn·20) / 100` (Gewichte aus `tum-ai/ehl` `lib/code-review/pipeline.ts:38-43`, können pro Challenge abweichen)

`Gesamt = 0,6 · Review-Score + 0,2 · Machbarkeit + 0,2 · Demo-Fähigkeit` (unsere eigene Gewichtung: Die menschliche Jury entscheidet über Demo und Ergebnis).

---

## BMW Group

**Fakten**
- Bisherige EHL-Challenge (Zürich, 12.-13.09.2026): **BMW Motorrad „Best Route“ / „Find Your Thrill“**. Zwei Anwendungsfälle (Route A→B und Rundtour „X Stunden ab hier“). **Sechs bewertete Kriterien:** BMW-Crowd-Daten, persönliche Fahrerdaten, externe Quellen, Skalierbarkeit/Effizienz, Fun-Score-Berechnung, Fahrersicherheit. **Bonus für Erklärbarkeit und Live-Demo.** Rote Flaggen: Innenstadt, Stillstand, schlechtes Wetter, schlechter Belag. Abgabe: Pitch-Deck + Repo (mit Entire) + Live-Demo. Daten: Telemetrie-Stichproben mit 8.000 Fahrten (~1,7 GB). Quelle: `european-hackathon-league/zurich-no-idea`, `CONTEXT.md`.
- Gewinner dort: PolyETHylene, AskOnce, Benevolent Agent Hive (ehl.gg/matches/zurich).
- BMW × TUM.ai: „BMW Open Innovation Robotics AI Hackathon“ im Oktober 2025, Motto **„AI systems that act rather than just answer“** (tum-ai.com/events). Außerdem ein 48-h-Hackathon von BMW und OpenAI mit 40 Teilnehmenden (tum-ai.com/partners).
- Beim Grand Finale ist der Partner als „BMW“ gelistet, nicht „BMW Motorrad“ (ehl.gg/matches). **UNBESTÄTIGT**, welche Sparte die Challenge stellt.

**Wahrscheinliche Themen (Hypothese):** agentische KI, die handelt (Robotik, Produktion), Flotten-/Telemetrie-Daten, Routing, Qualitätssicherung in der Produktion, After-Sales.
**Vermutlich ausgegebene Daten (Hypothese):** anonymisierte Telemetrie oder Fahrtdaten, Produktionsdaten, Fehlerberichte, ggf. Bilder. Format eher CSV/Parquet als API.

### Ideen-Hypothesen BMW

| | B1 Erklärbares Routing aus Flottendaten | B2 Qualitäts-Agent für die Produktion | B3 Werkstatt-Diagnose-Agent |
|---|---|---|---|
| Nutzer & Problem | Fahrer will Strecke nach Fahrspaß und Sicherheit, nicht nur Zeit | Qualitätsingenieur sucht in tausenden Fehlerberichten die Ursache | Serviceberater übersetzt Kundenbeschwerde + Fehlercodes in Diagnose und Teile |
| Must-have (24 h) | Graph aus Crowd-Daten, Score pro Abschnitt, Route + Begründung pro Abschnitt, Karte | Einlesen der Berichte, Clustering + LLM-Zusammenfassung pro Cluster, Ursachen-Ranking mit Belegen | Formular → LLM extrahiert Symptome → regelbasierte Zuordnung zu Diagnosen → Teileliste |
| Nice-to-have | Persönliches Fahrerprofil, Wetter-API | Bilder (Vision-Modell), Alarm bei neuem Cluster | Sprachaufnahme, Werkstatt-Terminbuchung |
| Architektur | Pandas/NetworkX → Score-Funktion → FastAPI → Karte (Leaflet) | Embeddings → HDBSCAN → LLM pro Cluster → Dashboard | Structured Outputs → Regel-Engine → UI |
| **Die eine Zahl** | „X % weniger Rote-Flaggen-Kilometer bei +Y % Fun-Score vs. schnellste Route, auf N Testfahrten“ | „Top-3-Trefferquote der Ursache: X % auf N gelabelten Fällen“ | „Richtige Diagnose in X von N Testfällen“ |
| Risiken | Daten groß, Kartendarstellung zeitintensiv | gelabelte Testfälle fehlen evtl. | ohne echte Fehlercode-Daten nur Spielzeug |
| CQ / Arch / Align / Inn | 4 / 5 / 5* / 4 | 4 / 4 / 3 / 3 | 4 / 3 / 3 / 3 |
| Machbarkeit / Demo | 3 / 5 | 4 / 4 | 4 / 3 |
| **Gesamt** | **4,3** | 3,7 | 3,4 |

\* nur falls BMW wieder Routing stellt.

**5 Fragen an BMW im Deep Dive**
1. Welche drei Kriterien sind euch am wichtigsten, falls wir nicht alle schaffen?
2. Wie messt ihr intern, ob eine Lösung „gut“ ist? Gibt es eine Referenz-Baseline oder einen Testdatensatz?
3. Dürfen wir externe Daten/APIs nutzen (OSM, Wetter), und gibt es Lizenzgrenzen für eure Daten?
4. Wer ist der echte Nutzer, und in welcher Situation benutzt er das (Fahrt, Werk, Werkstatt)?
5. Was wäre für euch ein Ergebnis, das ihr nach dem Hackathon intern weiterzeigen würdet?

---

## Atira

**Fakten**
- Münchner KI-Startup (Gräfelfing), gegründet November 2024 von **Florian Diegruber** (CEO, vorher Commercial Lead bei Palantir) und **August DuMont Schütte** (CTO, vorher ML Engineer bei Google). Quelle: fortune.com, 03.09.2026; startbase.com.
- Seed 15 Mio. USD (Accel), insgesamt 17,5 Mio. USD (tech.eu, 03.09.2026).
- Produkt: **KI-Agenten für Sales Engineering in der Industrie**. Kundenanfrage lesen, mit eigenen Standards und Historie abgleichen, nicht erfüllbare Spezifikationen markieren, technische Dokumente, Konfigurationen und Preisoptionen erzeugen. Bezeichnet sich als „commercial brain between CRM and ERP“. Bis zu **80 % schneller** von Anfrage zu Angebot (Firmenangabe). Kunden laut Presse: ABB E-mobility, Chiron Group, Robel. Team-Stichworte: „agentic harness“, „configurator for manufacturers with large product lines“ (atira.ai/about-us).
- Event-Guide: **Fireside Chat mit Atira am Samstag 16:00**.
- Jury: **UNBESTÄTIGT**, vermutlich Gründer oder Engineers. Diegruber kommt aus dem Palantir-Commercial-Umfeld (Fokus: messbarer Kundennutzen), DuMont Schütte aus Google ML (Fokus: saubere Evaluation).

**Wahrscheinliche Themen (Hypothese):** Anfrage/RFQ → Angebot, Lastenheft-Abgleich, Produktkonfiguration bei großen Katalogen, Agent-Harness.
**Vermutlich ausgegebene Daten (Hypothese):** anonymisierte Kundenanfragen (PDF, E-Mail), Produktkataloge/Datenblätter, Preislisten, Konfigurationsregeln.

### Ideen-Hypothesen Atira

| | A1 Anfrage-zu-Angebot-Agent | A2 Lastenheft-Prüfer mit Belegstellen | A3 Konfigurator in natürlicher Sprache |
|---|---|---|---|
| Nutzer & Problem | Sales Engineer braucht Tage, um eine technische Anfrage in ein Angebot zu übersetzen | Angebot verspricht etwas, das das Produkt nicht kann → teure Nacharbeit | Kunde/Vertrieb findet in tausenden Varianten die gültige Konfiguration nicht |
| Must-have (24 h) | PDF rein → Anforderungen extrahieren (Structured Outputs) → Katalog-Abgleich → Angebotsentwurf mit offenen Punkten | Jede Anforderung: erfüllt / nicht erfüllt / unklar + Zitat aus Datenblatt | Regeln als Constraints, LLM übersetzt Wunsch in Constraints, Solver prüft Gültigkeit |
| Nice-to-have | Preisoptionen, CRM-Export | Risiko-Score, Rückfragen-Mail an Kunden | Erklärung „warum nicht möglich“ + Alternativen |
| Architektur | Parser → Extraktor-Agent → Retrieval über Katalog → Prüf-Agent → Angebots-Generator (FastAPI) + Review-UI | Chunking + Embeddings → Klassifikation pro Anforderung mit Quelle → Tabelle | LLM → JSON-Constraints → Python-Solver (z. B. OR-Tools) → UI |
| **Die eine Zahl** | „Extraktion: F1 = X auf N handgelabelten Anforderungen; Zeit pro Anfrage von ~Y h auf Z min“ | „X % der Anforderungen korrekt klassifiziert, 100 % mit Belegstelle“ | „0 ungültige Konfigurationen in N Testwünschen (LLM allein: X %)“ |
| Risiken | Umfang groß; sauber schneiden | braucht gelabelte Testfälle | Regeln evtl. nicht verfügbar |
| CQ / Arch / Align / Inn | 4 / 5 / 5 / 4 | 4 / 4 / 4 / 3 | 4 / 4 / 4 / 5 |
| Machbarkeit / Demo | 3 / 5 | 5 / 4 | 3 / 4 |
| **Gesamt** | **4,3** | 4,1 | 3,9 |

**5 Fragen an Atira im Deep Dive**
1. Wo verliert ein Sales Engineer heute die meiste Zeit: Lesen, Abgleichen oder Schreiben?
2. Wie sieht eine typische Anfrage aus (Format, Länge, Sprache), und habt ihr Beispiele mit „richtigem“ Ergebnis?
3. Was ist schlimmer: eine übersehene Anforderung oder eine falsch markierte? (Damit wir die Metrik richtig wählen)
4. Wie wichtig ist Nachvollziehbarkeit (Belegstellen) im Vergleich zu Geschwindigkeit?
5. Welche Systeme müsste das am Ende anbinden (CRM, ERP, CPQ), und reicht für die Demo ein Export?

---

## tacto

**Fakten**
- Münchner Startup, „born at TU Munich“, **KI-Plattform für den industriellen Einkauf** (tacto.ai). Module: Supplier Intelligence, Spend & Cost Intelligence, **Sourcing Intelligence (RFQs, Angebots-PDFs auswerten)**, Compliance Intelligence. Agenten: **Defender Agent, Should Cost Agent, RFQ Agent, Negotiation Agent**. Firmenangabe: 10 % Einkaufsvolumen gespart, 75 % Zeit gespart. Kunden u. a. voestalpine, SUSS MicroTec, HERMA, VEMAG, Arburg.
- Finanzierung: Cherry Ventures führte 2022 die Runde über 5,3 Mio. € (tech.eu, 22.03.2022); heute „backed by Sequoia & Index with over €50M“ (tacto.ai/career).
- **Cherry Ventures ist tacto-Investor, und Victor von Cherry Ventures ist laut Event-Guide Juror und bietet Office Hours an.** Wer zu tacto geht, sollte die Office Hours nutzen.
- tacto hat mit TUM.ai schon Events gemacht und veranstaltet eigene 2-Tages-Hackathons (tum-ai.com/events, tacto.ai/career).
- Gründer und Jury: **UNBESTÄTIGT**.

**Wahrscheinliche Themen (Hypothese):** Angebote vergleichen, Should-Cost-Schätzung, Lieferantenrisiko, Verhandlungsvorbereitung, Spend-Klassifikation.
**Vermutlich ausgegebene Daten (Hypothese):** Angebots-PDFs, Spend-Tabellen (CSV), Lieferantenlisten, Rohstoffindizes, Zeichnungen.

### Ideen-Hypothesen tacto

| | T1 Angebotsvergleich aus PDFs | T2 Should-Cost-Agent | T3 Verhandlungs-Copilot |
|---|---|---|---|
| Nutzer & Problem | Einkäufer vergleicht 5 Angebote in 5 Formaten (Staffelpreise, Incoterms, Zahlungsziele) per Hand | Einkäufer weiß nicht, was ein Teil kosten *sollte* | Einkäufer geht schlecht vorbereitet in die Verhandlung |
| Must-have (24 h) | PDF → strukturierte Angebote → Normalisierung auf Gesamtkosten → Vergleichsmatrix mit Empfehlung | Stückliste/Beschreibung → Kostenaufschlüsselung (Material, Maschine, Arbeit) aus Indizes → Abweichung zum Angebot | Daten zu Lieferant + Angebot → Argumente, Zielpreis, Gesprächsleitfaden |
| Nice-to-have | Rückfragen an Lieferanten automatisch | Sensitivität bei Rohstoffpreis | Simulation gegen LLM-Lieferanten |
| Architektur | Extraktor (Structured Outputs) → Normalisierer (Python, deterministisch) → Ranking → UI | LLM liest, Python rechnet („the model reads, the engine prices“) | Retrieval + Prompt-Kette |
| **Die eine Zahl** | „Feld-Genauigkeit X % auf N Angeboten; Vergleich von 2 h auf 3 min“ | „MAPE X % gegen echte Preise auf N Teilen“ | schwer messbar → Risiko |
| Risiken | PDF-Vielfalt | echte Preise als Wahrheit nötig | Demo wirkt wie Chatbot |
| CQ / Arch / Align / Inn | 4 / 4 / 5 / 3 | 4 / 5 / 5 / 4 | 3 / 3 / 4 / 3 |
| Machbarkeit / Demo | 5 / 5 | 3 / 4 | 4 / 3 |
| **Gesamt** | **4,4** | 4,1 | 3,4 |

**5 Fragen an tacto im Deep Dive**
1. Welcher eurer Agenten hat heute die größte Lücke, die wir in 24 h zeigen könnten?
2. Gibt es Beispieldaten mit bekannter „richtiger“ Antwort (echte Preise, gewählter Lieferant)?
3. Was überzeugt einen Einkaufsleiter: Ersparnis in €, gesparte Zeit oder weniger Risiko?
4. Wie viel Automatisierung ist erwünscht: Empfehlung mit Begründung oder autonome Aktion?
5. Welche Datenquellen dürfen wir zusätzlich nutzen (öffentliche Indizes, Nachrichten)?

---

## Gemeinsame Muster aller drei Partner

- Alle drei sind **B2B-Industrie** mit **unstrukturierten Dokumenten** (Anfragen, Angebote, Berichte) und dem Versprechen „Zeit sparen + Fehler vermeiden“.
- Darum bereiten wir vor: PDF-Extraktion mit Structured Outputs, deterministische Logik nach dem LLM, Evaluation gegen ein kleines handgelabeltes Set, Review-UI mit Belegstellen.
- **Unsere Grundarchitektur passt auf alle sechs Top-Ideen:** `Dokument/Daten → LLM extrahiert (JSON-Schema) → Python prüft/rechnet → Ergebnis mit Begründung → UI`.
