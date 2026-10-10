# Schritt 0: Bestandsaufnahme (Sa 10.10., ca. 17:00)

Gelesen: alle Docs, Pfad-Arbeitsbücher, Backend, Frontend, Konfig, Daten-Ordner, Git-Verlauf. Tests laufen: **91 grün** (`python -m pytest -q`).

## Was funktioniert

| Teil | Stand | Beleg |
|---|---|---|
| Backend (FastAPI): Modelle, API, Prüfpfad mit Hash-Kette, LLM-Wrapper mit Cache | fertig | `src/backend/core/`, `api/`, Tests `test_api`, `test_audit`, `test_llm` |
| Priorisierung: 6 Faktoren, Gewichte, Wasserfall, Evidenzstufe A-D | fertig | `requirements_engine/scoring.py`, `evidence_level.py` |
| Anforderungen aus Befunden ableiten (`derive_all`) | lief mit echter KI, 8 Anforderungen | Commit `587313e` |
| Webrecherche (Fragen, Vertrauensstufen, Triangulation) | fast fertig | `PFAD-B.md`: 4 von 5 Tickets erledigt |
| Frontend: Startseite mit Liste, Szenario-Dropdown, Badges, Score-Balken | läuft | `src/frontend/app/page.tsx` |
| Beispieldaten für jede Stufe (synthetisch) | fertig | `src/shared/beispiele/` |
| Entire, CI, Secret-Scan, Git-Schutz | eingerichtet | `.entire/`, `.github/`, `scripts/` |

## Was halb fertig ist

| Teil | Was fehlt |
|---|---|
| Interne Evidenz (Pfad A) | 2 von 12 Tickets. Echte Belege aus den Excel-Dateien, Befunde per KI, Konflikte fehlen noch. |
| Anforderungen (Pfad C) | 1 von 12. 8 statt 15-25 Anforderungen. Challenge-KI, Optionsliste fehlen. |
| Frontend (Pfad D) | Nur die Liste. Detailseite, Entscheiden-Buttons, Prüfpfad-Seite, Regler fehlen. |
| Lead-Aufgaben | README (englisch, gut), Deck, Drehbuch, 1. Abgabe fehlen. |
| Zweites Szenario (G70, F70-EU) | Konfig-Dateien da, Daten noch nicht durchgelaufen. |

## Was weg kann oder aufgeräumt werden sollte

- `team/fabian.md` und `workspace/fabian/`: Fabian ist nicht dabei.
- `workspace/<name>/` und `team/<name>.md` gibt es schon. Das ist fast dasselbe wie `werkstatt/<name>/`.
- Doppelte Docs: `docs/research/CHALLENGE.md` vs. `docs/CHALLENGE.md`, `docs/MORGEN-0800.md`, `docs/SAMSTAG-START.md`, `docs/wissen/SCAFFOLD-PLAENE.md`.
- `src/frontend/public/*.svg` und `app/test-api/` sind Next.js-Reste.
- `design/` ist leer.

## Zwei Dinge, die du wissen musst

1. **Das Repo ist schon weit.** Es ist Samstag 17:00, Meilenstein "Durchstich" ist 18:30. Ein Umbau der Ordner (`src/`, `app/`, `outputs/`) würde Import-Pfade, CI, Entire und die Besitzregeln in `CLAUDE.md` kaputt machen. Mein Vorschlag steht in **E07**: Code bleibt, wo er ist. Neu kommen nur die Team-Ordner dazu.
2. **BMW-Rohdaten liegen im öffentlichen Repo.** `data/raw/` ist per Commit `17727fb` bewusst aus `.gitignore` genommen worden, das Repo ist `PUBLIC`. `data/README.md` und `CLAUDE.md` sagen aber das Gegenteil. Das ist deine Entscheidung (Piyush), ich habe nichts geändert. Siehe **E08**.

## Was ich nicht anfasse

Kein Code wird verschoben oder gelöscht. Aufräumen kommt nach `archiv/`, und erst nach eurer Antwort auf E07.
