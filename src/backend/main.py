"""Einstieg des Backends.

Start:  uvicorn main:app --app-dir src/backend --reload --port 8000
Doku:   http://localhost:8000/docs  (automatisch aus den Pydantic-Modellen)
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.views import router as views_router
from core.audit import AuditLog
from core.store import ROOT, Store

load_dotenv(ROOT / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eine SQLite-Datei pro Laptop; liegt in data/ und damit außerhalb von Git.
    db_path = Path(os.getenv("AUDIT_DB", ROOT / "data" / "audit.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    store = Store(AuditLog(db_path))
    store.load_all()
    app.state.store = store
    yield


app = FastAPI(title="Signal2Spec", version="0.2.0", lifespan=lifespan,
              description="Von Kundenbelegen zu priorisierten Anforderungen, mit PM im Loop und Prüfpfad.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(views_router)


@app.get("/health")
def health() -> dict:
    """Status für Frontend und demo-check: Version, Demo-Modus, geladene Szenarien."""
    store = getattr(app.state, "store", None)
    return {"status": "ok", "version": app.version, "demo_mode": os.getenv("DEMO_MODUS", "false").lower() == "true",
            "scenarios": sorted(store.states) if store else []}
