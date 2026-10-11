# src/

The code. How the parts fit together is in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

| Folder | What it does | Built by |
|---|---|---|
| `backend/evidence_internal/` | Steps 1 and 2: evidence and findings from BMW data | Aditya |
| `backend/evidence_external/` | Step 3: web research, NHTSA, EPA | Piyush |
| `backend/requirements_engine/` | Steps 4 and 5: requirements, score, evidence level, challenge | Dennis |
| `backend/core/` | Data model, audit trail, store, LLM access, views | Piyush |
| `backend/api/`, `main.py`, `pipeline.py` | REST endpoints and the pipeline runner | Piyush |
| `frontend/` | The PM cockpit (Next.js) | Lasse |
| `shared/` | API contract (`API.md`) and synthetic example data | Piyush |
