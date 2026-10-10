# Notizen Aditya

## Gute Prompts (zum Wiederverwenden)

<!-- Ownership-Sprache: Was + Warum + Was verworfen + Wie prüfen -->

## Notizen

### Für Piyush: Vorschlag für `docs/ARCHITEKTUR.md` (Pfad A fehlt dort teilweise)

Komponenten (Tabelle), zusätzlich zu "Einlesen" und "Befunde":

| Komponente | Datei | Aufgabe | KI? |
|---|---|---|---|
| Absatz-Kontext | `src/backend/evidence_internal/context.py` | Volumen 2030 und Marktanteil für den Faktor reach | nein |
| Taxonomie | `src/backend/evidence_internal/taxonomy.py`, `study_topics.py` | BMW-Thema bzw. Studienattribut → unsere 9 Kategorien | nein |
| Befund-Texte | `src/backend/evidence_internal/signals_llm.py` | LLM formuliert Titel/Zusammenfassung der Top-30-Gruppen; fremde IDs und Zahlen werden verworfen | ja |
| Konflikte | `src/backend/evidence_internal/conflicts.py` | Lob ↔ Kritik bei gleichem oder verwandtem Thema verknüpfen (`conflicts_with`) | nein |

Entscheidungen:

| Entscheidung | Warum | Verworfen |
|---|---|---|
| Höchstens 45 Befunde, feste Plätze: Feedback+Studie immer, max. 8 reine Studienbefunde, 10 Wünsche | Ein PM prüft keine 160 Punkte; Wünsche zerfallen in kleine Gruppen und kämen sonst nie in die Liste | nur Mindestgröße 5 (162 Befunde) |
| Konflikte nur bei gleichem oder verwandtem Thema (feste Liste) | Pauschal "gleiche Kategorie" ergab Zufallspaare wie Komfort-Lob ↔ Kofferraum-Kritik | nur gleiches Thema (verliert Fahrdynamik ↔ Antrieb), LLM entscheidet |
| LLM-Texte ohne Zahlen | Zahlen kommen nur aus dem Code, ein Modell verrechnet sich | Zahlen vom Modell übernehmen |

