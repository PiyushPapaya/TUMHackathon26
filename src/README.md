# src/

Der Code. Wer braucht das: Builder (Piyush, Lasse) und alle, die erklären müssen, wie es funktioniert.

| Ordner | Inhalt | Pfad / Owner |
|---|---|---|
| `backend/core/` | Datenmodell, Audit Trail, Store, LLM-Zugang | Lead (Piyush) |
| `backend/api/`, `main.py`, `pipeline.py` | REST-Endpunkte und die Pipeline | Lead (Piyush) |
| `backend/evidence_internal/` | Schritt 1 und 2: Belege und Befunde aus BMW-Daten | A (Aditya) |
| `backend/evidence_external/` | Schritt 3: Webrecherche | B (Piyush) |
| `backend/requirements_engine/` | Schritt 4 und 5: Anforderungen, Score, Challenge | C (Dennis) |
| `frontend/` | Das PM-Cockpit (Next.js). Entspricht dem `app/`-Ordner aus dem Vorschlag. | D (Lasse) |
| `shared/` | Verträge (`API.md`) und synthetische Beispieldaten | Lead (Piyush) |

Warum `frontend/` nicht `app/` heißt: Umbenennen würde CI, Skills und Entire-Setup brechen (Karte E07).
