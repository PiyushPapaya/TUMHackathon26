# Recherche-Kurzfassung (in 5 Minuten lesen)

Ausführlich und mit Quellen: [`docs/wissen/`](../wissen/README.md).

## 1. Wie wir gewinnen

- **Menschen entscheiden die Platzierung.** Jede Jurorin und jeder Juror sortiert alle Teams; Durchschnittsplatz gewinnt. Der KI-Report ist nur ihre Lesehilfe. → [EHL-BEWERTUNG](../wissen/EHL-BEWERTUNG.md#die-kurzfassung-in-10-sätzen)
- **Die Jury sieht:** Projektname, Kurzbeschreibung, Tech-Stack, Repo- und Demo-Link, **unser Pitch-Deck eingebettet**, KI-Report. Dazu 6 Minuten Pitch inkl. Fragen.
- **Bei früheren Gewinnern** stand eine harte Zahl in den ersten Zeilen (z. B. „MRR = 1.000“, „Platz 1 von 17“), außerdem Vergleich gegen Alternativen, ehrliche Grenzen, eine Demo, die nie ausfällt, und ein Mermaid-Diagramm. → [VERGANGENE-PROJEKTE](../wissen/VERGANGENE-PROJEKTE.md#winning-patterns-mit-beleg)
- **Viel Doku und viele Commits gewinnen nicht.** binbusy hatte beides und keinen Platz.

**Snapshot-Fazit (geprüft 10.10.):** Die EHL lädt bei jeder neuen Abgabe den **GitHub-Zipball** des eingefrorenen Commits (Revision ≥ 1 → `frozen_sha` → `archive.ts:52`), packt also nicht selbst.
`export-ignore` wirkt deshalb (am eigenen Repo getestet). Doku belegt 11 % des Budgets; nur im Alt-Modus ohne SHA wären es 43 %.
Notfallplan zum Auslagern nach `archiv/wissen` steht getestet in `docs/ABGABE.md` (Notfall A), wird aber nicht gebraucht.

## 2. Abgabe: die 6 Fallen

1. Bewertet wird **der Commit oben auf `main` beim Klick auf Submit**. Später gepushter Code zählt nur nach **„Update Submission“**. → [EHL-BEWERTUNG §2](../wissen/EHL-BEWERTUNG.md#2-die-abgabe-submit)
2. **Ohne Entire-Checkpoints keine Abgabe.** Jede Person: `entire enable --agent claude-code`.
3. **Pitch-Deck (PDF) ist standardmäßig Pflichtfeld** im Formular.
4. Der KI-Reviewer liest nur ~200.000 Zeichen, **kleinste Dateien zuerst**. Doku ist per `export-ignore` ausgeschlossen (getestet). Prüfen: `python scripts/ehl_budget.py`.
5. Frameworks erkennt er nur aus `requirements.txt` / `package.json` **im Root**.
6. Prompt-Injection wird erkannt und markiert. **Niemals.**

## 3. KI-Report: worauf er schaut

| Teil | Kriterium | Gewicht |
|---|---|---|
| Koordinator | Code-Qualität | 30 |
| | Architektur | 25 |
| | Challenge-Alignment (gegen den Brief-Text!) | 25 |
| | Innovation | 20 |
| Highlights | „Would it run?“ yes/probably/unlikely/no | – |
| Originalität | Boilerplate-Anteil (typisch 30-50 %), keine KI-Erkennung | – |
| Entire (Bonus) | Ownership-Sprache 35, Spezifität 25, Iteration 25, Edge Cases 15 | beratend |

Der Session-Reviewer bewertet **einen praktisch zufälligen Checkpoint**. Deshalb gilt Ownership-Sprache für alle, immer.

## 4. Die Partner in einem Satz

| Partner | Was sie machen | Top-Idee (Hypothese) | Die eine Zahl |
|---|---|---|---|
| **BMW** | Zürich-Challenge war Motorrad-Routing mit 6 Kriterien + Bonus Erklärbarkeit/Live-Demo | B1 erklärbares Routing aus Flottendaten (4,3) | weniger Rote-Flaggen-km bei mehr Fun-Score vs. schnellste Route |
| **Atira** | KI-Agenten: technische Kundenanfrage → Angebot (Industrie-Vertrieb) | A1 Anfrage-zu-Angebot-Agent (4,3) | Extraktions-F1 + Zeit pro Anfrage |
| **tacto** | KI-Plattform für Einkauf: Angebote, Should-Cost, Lieferanten | T1 Angebotsvergleich aus PDFs (4,4) | Feld-Genauigkeit + Zeit pro Vergleich |

Jeweils 3 Ideen mit Score und 5 Deep-Dive-Fragen: [SPONSOREN](../wissen/SPONSOREN.md). **Victor (Cherry Ventures) ist Juror; Cherry ist tacto-Investor.** Atira hat Sa 16:00 einen Fireside Chat.

**Gemeinsame Grundarchitektur, die auf alle passt:**
`Dokument/Daten → LLM extrahiert (JSON-Schema) → Python prüft/rechnet → Ergebnis mit Begründung → UI`

## 5. Stack

Wir nehmen **FastAPI (Python) + Next.js**, weil das Team Python kann, Daten/PDF dort am stärksten sind und Claude Code Next.js-Seiten für Nicht-Coder gut baut. Plan B bei reiner Datenanalyse: Streamlit. Scaffold erst Samstag. → [STACK](../wissen/STACK.md)

## 6. OpenAI und Entire

- 75 USD Credits pro Person (Einmal-Code per E-Mail). **Eigener Key in `.env`, nie teilen.** Für die Demo ein Key in den Deploy-Variablen.
- Responses API + Structured Outputs als Kernbaustein; Modellnamen Samstag per `models.list()` prüfen (UNBESTÄTIGT).
- Entire: `commit_linking: always` ist gesetzt, sonst hängen Commits aus Claude heraus. → [OPENAI-UND-ENTIRE](../wissen/OPENAI-UND-ENTIRE.md)

## 7. Offene Punkte (UNBESTÄTIGT)

- Vorab-Code: Einzige Regel ist „Cheating, plagiarism, or any form of misconduct will result in disqualification“ (`tum-ai/ehl` `app/(public)/rules/page.tsx:373-375`). Wir scaffolden erst Samstag und markieren den Stand davor mit dem Tag `vor-event`.
- Wer sitzt in welcher Jury? Welche BMW-Sparte stellt die Challenge?
- Welche Abgabefelder verlangt jede Challenge genau (Deck, Demo-Link, Video)?
- Kommen die OpenAI-Credit-Codes vorab per Mail oder vor Ort?
