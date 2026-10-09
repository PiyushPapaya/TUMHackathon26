# Architektur

> Einfache Sprache: Jede Person im Team muss das der Jury erklären können.
> **Bei jedem PR mit Code aktualisieren** (Owner: Piyush; Frontend-Abschnitt: Lasse per PR-Vorschlag).
> Diese Datei liest auch der EHL-KI-Reviewer (Kriterium „Architektur“, 25 %).

## Überblick in 3 Sätzen

[Wer benutzt es?] [Was kommt rein?] [Was kommt raus, und warum ist das besser als vorher?]

## Bild

```mermaid
flowchart LR
  U[Nutzer im Browser] -->|Upload / Eingabe| FE[Frontend<br/><i>src/frontend/</i>]
  FE -->|POST /[endpunkt]<br/>siehe src/shared/API.md| BE[Backend<br/><i>src/backend/main.py</i>]
  BE -->|1. extrahieren| LLM[OpenAI<br/>Structured Outputs]
  LLM -->|JSON| BE
  BE -->|2. prüfen / rechnen| LOGIK[Deterministische Logik<br/><i>src/backend/[datei].py</i>]
  LOGIK -->|Ergebnis + Begründung| FE
```

## Komponenten

| Komponente | Ordner / Datei | Aufgabe | Technik | Owner |
|---|---|---|---|---|
| Frontend | `src/frontend/` | [ ] | Next.js, TypeScript, Tailwind | Lasse |
| Backend-API | `src/backend/main.py` | [ ] | FastAPI | Piyush |
| KI-Schritt | `src/backend/[ ].py` | [ ] | OpenAI Responses API, Structured Outputs | Piyush |
| Logik | `src/backend/[ ].py` | [ ] | Python | Piyush/Dennis |
| API-Vertrag | `src/shared/API.md` | Format zwischen Frontend und Backend | Markdown + Beispiel-JSON | Piyush |
| Evaluation | `tests/` | misst unsere Zahl gegen die Baseline | pytest | Aditya |
| Demo-Daten | `demo/` | Beispiel-Eingaben, Cache, Backup-Video-Link | JSON/PDF | Aditya |

## Datenfluss (nummeriert, so erzählen wir es der Jury)

1. [Nutzer lädt X hoch / gibt Y ein.]
2. [Frontend schickt `POST /…` mit … an das Backend.]
3. [Backend lässt das LLM die Felder A, B, C als JSON extrahieren.]
4. [Python-Code prüft/rechnet: … Warum nicht das LLM? Weil …]
5. [Ergebnis mit Begründung und Belegstelle geht zurück und wird angezeigt.]

## Externe APIs und Modelle

| Dienst | Wofür | Modell / Endpunkt | Kosten pro Lauf (geschätzt) | Was passiert bei Ausfall? |
|---|---|---|---|---|
| OpenAI | [ ] | `OPENAI_MODEL` aus `.env` | [ ] | Cache aus `demo/cache/` / Fehlermeldung |

## Designentscheidungen (Ownership-Sprache)

| Entscheidung | Warum | Verworfen, weil |
|---|---|---|
| Agent-Sessions werden mit Entire aufgezeichnet | Pflicht der EHL; macht nachvollziehbar, welcher Prompt welchen Code erzeugt hat | – |
| FastAPI + Next.js | Team kann Python; Daten/PDF in Python am stärksten; Next.js gut mit Claude Code | Streamlit: schwer schön zu machen; nur Next.js: kein Python für Daten |
| LLM extrahiert, Python rechnet | LLMs verrechnen sich, Code nicht; erklärbar | alles im LLM: nicht reproduzierbar |
| [ ] | [ ] | [ ] |

Jede neue Entscheidung → auch eine Frage in [`docs/pitch/JURY-FAQ.md`](pitch/JURY-FAQ.md).

## Fehlerfälle und Grenzen

| Fall | Verhalten |
|---|---|
| LLM-Timeout / API-Fehler | [ ] |
| Ungültige Eingabe | [ ] |
| [ ] | [ ] |

## Offene Punkte

- [ ]
