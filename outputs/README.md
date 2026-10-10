# outputs/

Fertige Ergebnisse zum Weitergeben: Anforderungsliste (CSV), Audit-Auszug. Wer braucht das: die Abgabe und der Pitch.

| Datei | Inhalt |
|---|---|
| `BEISPIEL_anforderungsliste_G60-US.csv` | Export der **synthetischen** Beispiel-Anforderungen (Semikolon-getrennt). Zeigt das Format. |

## Echten Export erzeugen

Backend starten (`uvicorn main:app --app-dir src/backend --port 8000`), dann im Browser oder mit `curl`:

```
http://localhost:8000/api/scenarios/G60-US/export
```

Speichere das Ergebnis als `outputs/anforderungsliste_G60-US.csv`. Die Spalten: id, rank, title, description, acceptance_criterion, signals, score, rationale, evidence_level, assumptions, uncertainties, status.
Den Audit Trail prüfst du mit `GET /api/audit/verify`. Erwartet: `{"valid": true, ...}`.

Hinweis: Echte Exporte enthalten BMW-Auswertungen. Vor dem Commit Piyush fragen (Karte E08).
