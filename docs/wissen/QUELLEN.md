# Quellen

Abrufdatum aller Webquellen: 09.10.2026. Primärquellen (Code, offizielle Doku) stehen oben.

## Primärquellen: EHL-Plattform (Quellcode)

Repo `github.com/tum-ai/ehl`, Commit `5afdadb` (03.10.2026):

| Datei | Wofür wir sie zitieren |
|---|---|
| `lib/code-review/ingest.ts` | Dateiauswahl, Sortierung, Budget, Framework-Erkennung, Flags |
| `lib/code-review/archive.ts` | Zipball-Download des eingefrorenen Commits, 50-KB-Grenze |
| `lib/code-review/prompts.ts` | exakte Rubriken A-D, Koordinator, Session-Reviewer |
| `lib/code-review/pipeline.ts` | Modelle, Gewichte, Ablauf, was in den Report kommt |
| `lib/submission-snapshots/prepare.ts` | Submit: Default-Branch-HEAD, Entire-Pflicht, Bot-Einladung |
| `lib/submission-snapshots/types.ts` | Formularfelder und Limits |
| `lib/entire.ts` | Checkpoint-Refs, Gate, Session-Stichprobe (nur erster Tree, 40 Prompts) |
| `lib/actions/jury.ts` | Ranking-Mittelung, Gleichstand |
| `lib/scoring.ts` | Punkte 8/7/6/4/4, Teilnahme 2 |
| `lib/credit-codes.ts` | Credit-Codes pro Person |
| `app/jury/[chapter-slug]/submission/[id]/page.tsx` | was die Jury pro Team sieht |
| `supabase/migrations/00003_phase2_schema.sql` | Standard-Abgabefelder (Deck, Repo, Demo) |
| `docs/FEATURES.md` | Update-Submission-Pflicht, Report Cards, Jury-Ablauf |

## Primärquellen: Event und Regeln

- Event-Guide: https://tum-ai.notion.site/EHL-Finale-All-you-need-to-know-3eb7306bfd62808993e9ec18c2d64834 (Inhalt aus dem Auftrag übernommen; die Seite rendert ohne JavaScript nicht)
- https://ehl.gg/rules: Teamgröße, Punkte, Disqualifikation
- https://ehl.gg/matches, /munich-1, /paris, /munich-2, /zurich: Ergebnisse
- Abgabe-Snapshots: https://github.com/european-hackathon-league (56 Repos ausgewertet)
  - `munich-2-codacabana`, `munich-2-makalu`, `paris-takethemoneyandrun`, `munich-2-ihsg`, `paris-oasis`, `munich-2-binbusy`, `zurich-no-idea` (README, CONTEXT.md)

## Primärquellen: Entire

- https://docs.entire.io/cli/installation.md: Installation Windows/macOS/Linux, PATH
- https://docs.entire.io/guides/checkpoints/capture-checkpoints.md: `commit_linking: always`, Link-Abfrage
- https://docs.entire.io/guides/checkpoints/troubleshooting: Squash-Merges verlieren Trailer, GUI-Clients, Remote-Prüfung
- https://docs.entire.io/cli/checkpoints.md: Checkpoints und Trailer
- `entire --help`, `entire enable --help`, `entire configure --help` (CLI 0.11.4, lokal)

## Primärquellen: GitHub (eigene Tests)

- Zipball-Test: `gh api repos/PiyushPapaya/TUMHackathon26/zipball/b52ee3c…`; `docs/wissen/` und `team/` fehlen
- Ruleset: `gh api repos/PiyushPapaya/TUMHackathon26/rulesets/24814533`

## Sekundärquellen: Partner

- Atira: https://atira.ai/about-us · https://fortune.com/2026/09/03/exclusive-german-ai-startup-atira-raises-17-5-million-to-unclog-the-paperwork-bottleneck-in-industrial-dealmaking/ · https://tech.eu/2026/09/03/atira-raises-175m-to-bring-ai-orchestration-to-industrial-sales · https://www.startbase.com/news/atira-sammelt-15-millionen-dollar-fuer-ki-agenten-im-industriellen-vertrieb-ein
- tacto: https://www.tacto.ai/en · https://www.tacto.ai/en/career · https://tech.eu/2022/03/22/tacto-procures-eur53-million-to-transform-industrial-supply-management/
- BMW: https://www.tum-ai.com/events · https://www.tum-ai.com/partners

## Sekundärquellen: OpenAI

- https://openai.com/index/new-tools-for-building-agents/ (Responses API, Agents SDK)
- https://openai.github.io/openai-agents-python/ (Agents SDK)
- Preisvergleiche (widersprüchlich, daher UNBESTÄTIGT): https://mem0.ai/library/llms-and-models/openai-api-pricing · https://benchlm.ai/openai/api-pricing
