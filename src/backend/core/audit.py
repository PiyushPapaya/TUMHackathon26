"""Prüfpfad (Audit-Trail): append-only Ereignisliste mit Hash-Kette in SQLite.

Warum so:
- Der Brief verlangt einen "complete, chronological record of all actions, changes".
  Deshalb wird NIE ein Eintrag geändert oder gelöscht, nur angehängt (Event-Log).
- Jeder Eintrag enthält den Hash des vorherigen. Wird ein alter Eintrag nachträglich
  verändert, bricht die Kette und `verify()` meldet die Stelle. So kann der PM (und die
  Jury) sehen, dass der Verlauf nicht manipuliert wurde.
- SQLite statt Postgres: eine Datei, kein Server, läuft auf jedem Laptop in der Demo.

Verworfen: Audit nur als Log-Datei (nicht abfragbar pro Anforderung) und Blockchain
(Overkill, kein Mehrwert gegenüber einer Hash-Kette in einer Datenbank).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path

from core.models import Actor, AuditEvent

GENESIS_HASH = "0" * 64

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    event_type TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    requirement_id TEXT,
    actor_type TEXT NOT NULL,
    actor_name TEXT NOT NULL,
    rationale TEXT NOT NULL,
    payload TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_req ON audit_events(requirement_id);
"""


def _hash_event(fields: dict) -> str:
    """Stabiler Hash: sortierte Schlüssel, damit dieselben Daten immer denselben Hash geben."""
    canonical = json.dumps(fields, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, db_path: Path | str):
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        # Eine Verbindung, viele Threads: FastAPI beantwortet Anfragen parallel. Ohne Sperre liest ein Thread
        # halbe Zeilen, und zwei Einträge können denselben Vorgänger-Hash bekommen (Kette kaputt).
        self._lock = threading.Lock()

    def append(
        self,
        event_type: str,
        scenario_id: str,
        actor: Actor,
        rationale: str,
        payload: dict | None = None,
        requirement_id: str | None = None,
    ) -> AuditEvent:
        """Hängt ein Ereignis an. Begründung ist Pflicht, weil der Brief sie verlangt."""
        if not rationale.strip():
            raise ValueError("Jedes Audit-Ereignis braucht eine Begründung (rationale).")
        with self._lock:
            return self._append_locked(event_type, scenario_id, actor, rationale, payload, requirement_id)

    def _append_locked(self, event_type, scenario_id, actor, rationale, payload, requirement_id) -> AuditEvent:
        last = self._conn.execute("SELECT hash FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
        prev_hash = last["hash"] if last else GENESIS_HASH
        fields = {
            "ts": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "scenario_id": scenario_id,
            "requirement_id": requirement_id,
            "actor_type": actor.type.value,
            "actor_name": actor.name,
            "rationale": rationale,
            "payload": payload or {},
            "prev_hash": prev_hash,
        }
        event_hash = _hash_event(fields)
        cur = self._conn.execute(
            "INSERT INTO audit_events (ts, event_type, scenario_id, requirement_id, actor_type,"
            " actor_name, rationale, payload, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                fields["ts"], event_type, scenario_id, requirement_id, actor.type.value,
                actor.name, rationale, json.dumps(fields["payload"], ensure_ascii=False, default=str),
                prev_hash, event_hash,
            ),
        )
        self._conn.commit()
        return self._row_to_event(self._conn.execute(
            "SELECT * FROM audit_events WHERE seq = ?", (cur.lastrowid,)).fetchone())

    def events(self, scenario_id: str | None = None, requirement_id: str | None = None) -> list[AuditEvent]:
        """Chronologisch (älteste zuerst), optional gefiltert."""
        query, params = "SELECT * FROM audit_events WHERE 1=1", []
        if scenario_id:
            query, params = query + " AND scenario_id = ?", [*params, scenario_id]
        if requirement_id:
            query, params = query + " AND requirement_id = ?", [*params, requirement_id]
        with self._lock:
            rows = self._conn.execute(query + " ORDER BY seq", params).fetchall()
        return [self._row_to_event(r) for r in rows]

    def verify(self) -> dict:
        """Prüft die komplette Kette. Liefert die erste kaputte Stelle, falls manipuliert."""
        prev_hash = GENESIS_HASH
        with self._lock:
            rows = self._conn.execute("SELECT * FROM audit_events ORDER BY seq").fetchall()
        for row in rows:
            fields = {
                "ts": row["ts"], "event_type": row["event_type"], "scenario_id": row["scenario_id"],
                "requirement_id": row["requirement_id"], "actor_type": row["actor_type"],
                "actor_name": row["actor_name"], "rationale": row["rationale"],
                "payload": json.loads(row["payload"]), "prev_hash": row["prev_hash"],
            }
            if row["prev_hash"] != prev_hash or _hash_event(fields) != row["hash"]:
                return {"valid": False, "broken_at_seq": row["seq"], "checked": len(rows)}
            prev_hash = row["hash"]
        return {"valid": True, "broken_at_seq": None, "checked": len(rows)}

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> AuditEvent:
        return AuditEvent(
            seq=row["seq"], ts=row["ts"], event_type=row["event_type"],
            scenario_id=row["scenario_id"], requirement_id=row["requirement_id"],
            actor=Actor(type=row["actor_type"], name=row["actor_name"]),
            rationale=row["rationale"], payload=json.loads(row["payload"]),
            prev_hash=row["prev_hash"], hash=row["hash"],
        )
