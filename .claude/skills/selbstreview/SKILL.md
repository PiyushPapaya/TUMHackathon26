---
name: selbstreview
description: Simuliert die EHL-KI-Review auf unserem Repo und liefert eine Report Card mit priorisierter Fix-Liste. Benutzen bei „Selbstreview“, „wie würde die Jury-KI uns bewerten“, „Report Card“, oder alle paar Stunden ab Sa 18:00.
---

# Selbstreview (EHL-Report-Card-Simulation)

Delegiere die Bewertung an den read-only Subagent `ehl-reviewer` (`.claude/agents/ehl-reviewer.md`), damit die Rubrik unbeeinflusst vom laufenden Gespräch angewendet wird.

## Schritte

1. **Budget-Simulation:** `python scripts/ehl_budget.py` (Zipball-Modus, wie bei der echten Abgabe). Notieren: Anteil `src/`, Doku-Anteil, wo das Budget endet, erkannte Frameworks, Flags.
2. **Bewertungsgrundlage:** genau die Dateien, die das Skript als „gelesen“ ausgibt (README und Manifeste zuerst, kleinste zuerst, Kappung nach 200 Zeilen). Dateien außerhalb des Budgets existieren für den Reviewer nicht.
3. **Challenge-Kontext:** `docs/CHALLENGE.md` (Brief-Zitate und Kriterien), den echte Reviewer auch bekommen.
4. **Rubriken anwenden** mit den **exakten JSON-Formen** aus `tum-ai/ehl` `lib/code-review/prompts.ts` (dokumentiert in `docs/hilfe/EHL-BEWERTUNG.md` §5):
   - A `{project_summary, tech_stack[], tech_stack_reasoning, architecture_pattern, key_dependencies[]}`
   - B `{readability, structure, error_handling, best_practices, overall_code_quality}` je `{score 1-10, rationale}`; 5 = ok, 7+ = beeindruckend, ≤3 = deutliche Probleme
   - C `{highlights[2-5]: {description, file, line, why_notable}, concerns[2-5]: {description, file, severity, explanation}, would_it_run: {verdict yes|probably|unlikely|no, reasoning}}`
   - D `{boilerplate_ratio, custom_code_ratio, boilerplate_indicators[], custom_work_indicators[], git_activity_assessment, assessment}`
   - Koordinator `{executive_summary, scores: {code_quality 30, architecture 25, challenge_alignment 25, innovation 20} je {score, max 10, weight, rationale}, weighted_total, highlights[2-4], concerns[2-4], strengths[3], weaknesses[3], notable_patterns}`; `weighted_total = Σ(score·weight)/Σweight`, 1 Nachkommastelle.
5. **Entire-Bonus grob schätzen:** 10 letzte eigene Prompts nach Ownership 35 / Spezifität 25 / Iteration 25 / Edge Cases 15.

## Ausgabe

1. Budget-Zeile: `src/ = X % der gelesenen Zeichen, Doku = Y % des Budgets, Frameworks: …`
2. Report Card als JSON (Koordinator-Form) + die drei Sätze Executive Summary.
3. **Fix-Liste**, priorisiert nach Wirkung pro Minute (max. 8): `[Priorität] Problem → konkrete Änderung → Datei → Owner`.
   Typische Top-Fixes: README-Zahl fehlt; Quickstart nicht getestet; Alignment-Map fehlt; großer Code-Block > 200 Zeilen; fehlende Fehlerbehandlung beim LLM-Aufruf; keine Tests.
4. Ergebnis lokal als `data/notizen/selbstreview-<uhrzeit>.md` speichern (nicht im Git).
