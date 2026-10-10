# [PROJEKTNAME]

> **[ONE-LINER IN ENGLISH: what it does, for whom, with the one number]**
> TUM.ai × European Hackathon League Grand Finale · 10-11 Oct 2026 · Garching

| | |
|---|---|
| **Challenge** | [PARTNER: CHALLENGE TITLE] |
| **Team** | Piyush · Lasse · Aditya · Dennis · Fabian |
| **Live demo** | [DEMO-LINK] |
| **Backup video** | [VIDEO-LINK] |
| **Pitch deck** | [`docs/pitch/`](docs/pitch/) / [DECK-LINK] |

## English summary (for the jury)

**Result:** [THE ONE NUMBER, e.g. "Extraction F1 = 0.91 on 40 hand-labelled requests vs. 0.62 for a plain LLM prompt"]. Method and limits in [Evaluation](#evaluation--ergebnisse).

**Problem.** [Who loses how much time/money today, with source.]

**Solution.** [What our product does in 2 sentences. Why it is better than the status quo.]

**How it works.** [One sentence: e.g. "The LLM reads, our code decides: structured extraction → deterministic checks → answer with source citation."] Diagram below.

**Judges, start here:** ① [Live demo](#) (1 min) · ② [How it works](#so-funktionierts) · ③ [Challenge alignment](#challenge-alignment-map) · ④ [Evaluation](#evaluation--ergebnisse) · ⑤ [What we do not claim](#grenzen-und-nächste-schritte)

---

## Problem

[Wer hat welches Problem, wie oft, was kostet es? Zahl mit Quelle (Brief, Partner, Studie).]

## Lösung

[Was macht unser Produkt? Was ist die eine Designidee, die es besser macht?]

## So funktioniert's

```mermaid
flowchart LR
  U[User] -->|input| FE[Frontend<br/><i>src/frontend/</i>]
  FE -->|POST /[endpoint]| BE[API<br/><i>src/backend/main.py</i>]
  BE -->|1 extract| LLM[OpenAI<br/>structured outputs]
  BE -->|2 check / compute| LOGIC[Rules<br/><i>src/backend/[file].py</i>]
  LOGIC -->|result + reason| FE
```

1. [Nutzer gibt … ein / lädt … hoch.]
2. [Frontend sendet … an `POST /…` (Vertrag: `src/shared/API.md`, entsteht Sa 14:00).]
3. [Backend lässt das Modell … als JSON extrahieren.]
4. [Python prüft/rechnet …, weil …]
5. [Ergebnis mit Begründung und Belegstelle wird angezeigt.]

Details: [`docs/ARCHITEKTUR.md`](docs/ARCHITEKTUR.md)

## Tech-Stack

| Teil | Technik | Warum |
|---|---|---|
| Frontend | Next.js, TypeScript, Tailwind | schnelle, saubere UI für die Live-Demo |
| Backend | Python, FastAPI | Daten- und PDF-Verarbeitung, automatische API-Doku unter `/docs` |
| KI | OpenAI Responses API, Structured Outputs | zuverlässige JSON-Extraktion statt freiem Text |
| Tests / Evaluation | pytest | misst unsere Zahl reproduzierbar |

## Quickstart

```bash
git clone https://github.com/PiyushPapaya/TUMHackathon26.git && cd TUMHackathon26
[BEFEHL 2, z. B. cp .env.example .env && pip install -r requirements.txt && (cd src/frontend && npm ci)]
[BEFEHL 3, z. B. Start-Skript für Backend + Frontend]
```

Ohne OpenAI-Key: `DEMO_MODUS=true` in `.env` nutzt gespeicherte Antworten aus `demo/cache/`.
*(Wird vor der Abgabe mit dem Skill `demo-check` in einem frischen Clone getestet.)*

## Challenge-Alignment-Map

| Kriterium des Partners (wörtlich) | Unser Feature | Wo im Code |
|---|---|---|
| [Kriterium 1] | [Feature] | [`src/…`](src/) |
| [Kriterium 2] | [Feature] | [`src/…`](src/) |
| [Kriterium 3] | [Feature] | [`src/…`](src/) |

## Evaluation / Ergebnisse

| Metrik | Unser Ergebnis | Baseline | Testset |
|---|---|---|---|
| [z. B. F1] | [X] | [Y, z. B. LLM ohne Regeln] | [N Fälle, wie gelabelt] |

- **Messmethode:** [Skript `tests/…`, Befehl zum Reproduzieren]
- **Unsicherheit:** [Spanne / Konfidenzintervall bzw. „N ist klein“]

## Grenzen und nächste Schritte

**Was wir nicht behaupten:** [ehrliche Grenze 1] · [ehrliche Grenze 2]

**Nächste Schritte:** [1.] [2.] [3.]

## Repo-Struktur

| Pfad | Inhalt |
|---|---|
| `src/frontend/` | Web-Oberfläche (Next.js) |
| `src/backend/` | API und Logik (FastAPI) |
| `src/shared/` | API-Vertrag zwischen Frontend und Backend |
| `tests/` | Tests und Evaluation |
| `demo/` | Demo-Daten, Cache, Backup-Video-Link |
| `docs/` | Architektur, Setup, Pitch, Recherche |
| `scripts/` | Team-Werkzeuge (Review-Budget-Simulation, Secret-Scan) |

## Wie wir gebaut haben

- **5 Personen, 5 Claude-Code-Agenten parallel.** Jede Person arbeitet nur in ihrem Ordner und eigenem Branch; Regeln in [`CLAUDE.md`](CLAUDE.md) und [`docs/ZUSAMMENARBEIT.md`](docs/ZUSAMMENARBEIT.md).
- **Entire** zeichnet alle Agent-Sessions auf; jeder Commit ist mit seinem Checkpoint verknüpft (`Entire-Checkpoint`-Trailer). Mit `entire why <datei>:<zeile>` sieht man, welcher Prompt eine Zeile erzeugt hat.
- **Qualitätssicherung:** CI bei jedem PR (Secret-Scan, Tests, Lint), `main` geschützt (nur per PR, Review durch Code-Owner).

### Vor dem Event vorbereitet: nur Tooling, kein Produkt-Code

Alles bis zum Git-Tag [`vor-event`](https://github.com/PiyushPapaya/TUMHackathon26/tree/vor-event) (gesetzt Sa 10.10., 09:55, vor dem Challenge-Reveal) ist Team-Infrastruktur: Regeln für unsere Claude-Agenten, CI, Secret-Scan, Doku-Templates und Recherche. **Jede Zeile Produkt-Code in `src/`, `tests/` und `demo/` entstand nach dem Reveal.** Prüfen: `git diff --stat vor-event..main -- src tests demo`.

## Team

| Name | GitHub | Rolle |
|---|---|---|
| Piyush | [@PiyushPapaya](https://github.com/PiyushPapaya) | Lead, Backend |
| Lasse | [@JoleEight](https://github.com/JoleEight) | Frontend |
| Aditya | [@AdiAvocado](https://github.com/AdiAvocado) | Daten, Tests, Demo |
| Dennis | [@Di0n-0](https://github.com/Di0n-0) | Partner-Anforderungen, Research |
| Fabian | [GitHub folgt] | Pitch, Design |

*Fürs Team: Einstieg über [`docs/SETUP.md`](docs/SETUP.md), danach in Claude Code: „Starte meine Sitzung.“*
