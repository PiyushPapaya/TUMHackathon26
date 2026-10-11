# Neulauf: Vollständige Neuerzeugung aller Szenarien

## Zweck

Die offene P1-Aufgabe "Vollständige Neuerzeugung nicht bestätigt" (siehe `OFFENE_AUFGABEN.md`, `docs/REPO_CHECK.md`) fragt: Entsteht aus den Rohdaten mit dem aktuellen Code wieder ein vollständiger, gültiger Stand? Wir haben das am So 11.10. ab 08:31 getestet, getrennt von den Demo-Daten.

## Wie ausführen

```
python src/backend/pipeline.py --scenario all --out data/regen
python scripts/verify_stack.py --processed-dir data/regen
```

- Neue Option `--out` (Commit 7fd12e5): schreibt alles nach `data/regen` statt nach `data/processed`. Warum: Demo-Bundles und PM-Verläufe dürfen beim Testen nie überschrieben werden. `data/regen` ist gitignored.
- Stand: aktueller Code inkl. stabiler Signal-IDs (8bb2826), Modell `gpt-5-mini` (`OPENAI_MODEL` leer).
- LLM-Cache `data/cache` wird bei identischen Prompts wiederverwendet. Dünne Szenarien liefen live mit Websuche. Die G68-CN-Websuche dauerte ca. 50 Minuten; G70-EU und G70-US liefen parallel in eigenen Prozessen.

## Ergebnis je Szenario (alt = data/processed, neu = data/regen)

| Szenario | Web-Belege alt -> neu | Anforderungen alt -> neu | Horizont neu (today / next_gen) | gleiche Titel |
|---|---|---|---|---|
| F70-EU | 100 -> 112 | 20 -> 21 | 19 / 2 | 0 |
| G60-EU | 0 -> 105 | 10 -> 9 | 6 / 3 | 0 |
| G60-US | 98 -> 112 | 19 -> 16 | 15 / 1 | 0 |
| G68-CN | 0 -> 140 | 3 -> 5 | 3 / 2 | 0 |
| G70-EU | 0 -> 98 | 2 -> 4 | 3 / 1 | 0 |
| G70-US | 90 -> 113 | 15 -> 20 | 17 / 3 | 0 |

Weitere Befunde:
- Keine Webfrage wurde übersprungen, keine Stufe ist gescheitert (alle 6 Szenarien). Es gab keine Warnungen.
- API-Prüfung `verify_stack.py --processed-dir data/regen` (Temp-Audit-DB): bestanden für alle 6 Szenarien. Das sind 186 HTTP-Reads, 30 PM-Aktionen, Neustart-Replay ok, offline ok.
- Cache-Fails: je Szenario genau 1 Challenge-Antwort fällt offline auf Regeln zurück, weil es für die neue Anforderung noch keinen Cache-Eintrag gibt (6 insgesamt). Das ist erwartbar.

## Was wir daraus schließen

- Die Pipeline erzeugt aus den Rohdaten wieder vollständige, gültige Bundles. Das ist bestätigt.
- Die Neuerzeugung ist NICHT wortgleich reproduzierbar: 0 gleiche Anforderungstitel in allen 6 Szenarien, und die Anzahl schwankt (z. B. G60-US 19 -> 16). Gründe: LLM-Formulierung, neue Prompts und neue IDs.
- Folge: Die Demo nutzt eingefrorene Snapshots (`data/processed`). Neuerzeugung ist ein Werkzeug, kein Determinismus-Versprechen.

## Was übernommen wurde und warum

Übernommen in `data/processed` (Aufgabe 2 "dünne Szenarien"):
- G60-EU: Web 0 -> 105 Belege, 3 Zukunftsanforderungen (`next_gen`), Quellen u. a. MotorTrend, Consumer Reports, Edmunds, McKinsey mit Vertrauen high/medium. Vorher fehlte Web-Evidenz ganz.
- G68-CN: 3 -> 5 Anforderungen, davon 2 `next_gen`.
- G70-EU: Web 0 -> 98 Belege, 2 -> 4 Anforderungen, davon 1 `next_gen`; alle 4 zitieren Webbefunde mit Vertrauen
  high/medium (u. a. Car and Driver, Edmunds, Consumer Reports, Porsche/Mercedes-Newsroom). Grenze: Rang 3 und 4
  stützen sich auf denselben einen Trend-Befund.

Bewusst alte Snapshots behalten: F70-EU, G60-US, G70-US. Grund: Ränge und Pitch-Demo bleiben stabil.

Verworfen: alle 6 übernehmen, weil sich dann die Ränge der Pitch-Demo verschieben und die Pitch-Zahlen neu geprüft werden müssten, obwohl diese drei Szenarien schon gut belegt sind.

Hinweis: Alte PM-Entscheidungen hängen am Bundle-Fingerabdruck und werden auf neue Bundles nicht übertragen. Bei G60-EU und G68-CN beginnt der PM-Verlauf daher leer.

## Eval auf den neuen Bundles

Alle 6 Szenarien in `data/regen` (run_eval über einen Temp-Root, keine Repo-Änderung): Grounding Befunde und
Anforderungen je 100 %, Wortlaut 100 % wo Kommentare zitiert sind, Zahl im Akzeptanzkriterium 100 %. Befund-Treue
dort n/a, weil die Label-Stichprobe zu den alten Signal-IDs gehört.

Nach der Übernahme (`python tests/eval/run_eval.py all`, `python scripts/verify_stack.py`):

| Szenario | Grounding Befunde | Grounding Anforderungen | Wortlaut | Zahl im Kriterium |
|---|---|---|---|---|
| G60-EU | 100 % | 100 % | 100 % | 100 % |
| G68-CN | 100 % | 100 % | n/a (Kaltstart, keine Kommentare) | 100 % |
| G70-EU | 100 % | 100 % | n/a (keine zitierten Kommentare) | 100 % |

API-Prüfung auf `data/processed` mit allen 6 Szenarien nach der Übernahme: bestanden (183 HTTP-Reads,
30 PM-Aktionen, Neustart-Replay ok, offline ok). `pytest -q`: 475 passed.

## Grenzen

- G70-US wurde ebenfalls neu erzeugt (15 -> 20 Anforderungen, 3 `next_gen`), aber bewusst nicht übernommen
  (Pitch-Demo-Ränge stabil). Eine Übernahme wäre der nächste Schritt nach dem Pitch.
- Kein Wort-für-Wort-Vergleich möglich: Wir vergleichen Zahlen (Anzahl, Horizont, Vertrauen), nicht Texte.
- Ergebnis hängt vom Modell (`gpt-5-mini`) und vom Websuche-Zeitpunkt ab; ein zweiter Lauf kann wieder anders ausfallen.
- Offline-Challenge-Antworten für neue Anforderungen sind Regel-Fallbacks, nicht LLM-Texte.
