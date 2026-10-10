# Pfad C · Anforderungen + Priorisierung

**Ziel:** Aus Befunden klare, kundenorientierte, **messbare** Anforderungen machen und sie mit einer
erklärbaren Formel priorisieren. Dazu kommen Evidenzstufe, Annahmen, Unsicherheiten, der "Gibt es das schon?"-Check
und die KI-Antwort, wenn der PM nachhakt.
**Du schreibst in:** `src/backend/requirements_engine/`, `tests/pfad_c/`.
**Du lieferst:** `requirements.json` (Liste von `Requirement`, siehe `core/models.py`).
**Schon da (Startversion vom Lead, darfst du verbessern):** `scoring.py`, `evidence_level.py`, `challenge.py`.

## Schritte

| # | Zeitbox | Aufgabe | Fertig, wenn … |
|---|---|---|---|
| 1 | 20 min | `scoring.py`, `evidence_level.py` lesen, Tests laufen lassen, Formel verstehen | Du kannst die Formel in 2 Sätzen erklären |
| 2 | 75 min | `derive.py` v1: Befunde (Beispiel `stufen/signals.json`) → LLM bündelt zu Anforderungen. Schema `RequirementDraft`: title, description, acceptance_criterion, category, signal_ids, assumptions, uncertainties, effort, in_scope, scope_reason | 5+ Entwürfe für das Beispiel; Test: nur existierende `signal_ids` |
| 3 | 45 min | **Faktoren im Code**, nicht im LLM: `customer_pain` (Anteil Defekt/Bedienproblem, Nennungen), `reach` (Nennungen × `context.sales.share_of_total_2030`), `satisfaction_gap` (Studienbeleg Negativanteil), `competitive_pressure` (Webbefunde), `future_relevance` (Trendbefunde), Effort → `effort_inverse`; je 1 Erklärsatz | **Sa 18:00**: `requirements.json` mit Score + Breakdown |
| 4 | 30 min | Scope-Wächter: `in_scope=false` (Regulatorik, Technik-Spec, Preis) → nicht in die Liste, aber im Prüfpfad als "verworfen mit Grund" (Liste an Lead) | Test mit 3 Out-of-scope-Beispielen |
| 5 | 60 min | `offer_check.py`: Optionsliste-PDF lesen (pymupdf), Code + Name + Serie/Option; Abgleich erst per Wortliste, dann LLM nur gegen die Kandidaten | "berührungslose Heckklappe" → optional (**Sa 22:00**) |
| 6 | 60 min | `challenge.py` v2 mit LLM: Antwort nur mit Beleg-IDs aus der Eingabe, nennt Gegenbelege + Vorschlag ("Kriterium auf X ändern?") | Test: unbekannte IDs werden entfernt |
| 7 | Nacht | Schwellen der Evidenzstufe mit echten Zahlen kalibrieren (wie viele A/B/C/D?) und begründen | Verteilung plausibel, Begründung im Docstring |
| 8 | Nacht | Stretch: **"Was wäre wenn"**: Annahme als falsch markieren → Score ohne `future_relevance` | Endpoint-Wunsch an Lead |

## Regeln für Anforderungen (in den Prompt übernehmen)

- **Kundensicht:** "Lautstärke ohne Blick auf den Bildschirm regeln", nicht "Drehgeber Bauteil X".
- **Messbar:** Zahl oder Testbedingung wie auf der BMW-Folie ("Range: 600 or 700 mi?", "Cooler for how many bottles?").
- **Realistisch** für den Nachfolger in 3-5 Jahren; Annahmen explizit.
- Stärken ("delight") werden zu **Erhalten-Anforderungen** ("Fahrkomfort mindestens auf heutigem Niveau").

## Start-Prompt für Claude

> "Ich baue Pfad C. Das LLM formuliert nur die Anforderungen. Die Priorität rechnen wir in Python
> (`scoring.py`), weil Modelle nicht reproduzierbar rechnen und der PM jeden Punkt nachvollziehen
> muss. Verworfen: LLM vergibt den Score direkt. Bitte implementiere `derive_requirements` in
> `src/backend/requirements_engine/derive.py` mit Schema `RequirementDraft` über `core.llm.ask_json`,
> dann die Faktoren im Code. Test: jede `signal_id` existiert in der Eingabe. Prüfen mit
> `python -m pytest tests/pfad_c -q`."

## Deine Pitch-Folie + Demo-Abschnitt

- Folie "Priorität, die man erklären kann": Formel + Wasserfall einer Anforderung + Evidenzstufen A-D.
- Demo (45 s): Gewicht "Zukunft" hochziehen → Rangfolge ändert sich → Eintrag im Prüfpfad.
