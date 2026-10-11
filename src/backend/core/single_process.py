"""Sperre: genau ein API-Prozess pro Audit-DB.

Warum: Der Store hält Anforderungen, Gewichte und PM-Status im RAM und baut sie beim Start
aus dem Prüfpfad nach. Zwei Prozesse (z. B. `uvicorn --workers 2`) schrieben zwar beide gültige
Audit-Einträge, sähen aber die Entscheidungen des anderen nicht: Prozess A zeigt „approved“,
Prozess B noch „proposed“. Statt still falsche Stände zu zeigen, bricht der zweite Prozess ab.

Verworfen: RAM-Stände über die DB synchronisieren (vor jeder Anfrage nachladen). Für die
Hackathon-Demo mit einem Laptop unnötig und schwerer zu prüfen; der nächste Schritt wäre ein
gemeinsamer Store (z. B. Postgres) statt RAM.

Prüfen: tests/pfad_b/test_single_process.py (startet einen echten zweiten Prozess).
"""

from __future__ import annotations

import os
from pathlib import Path

if os.name == "nt":  # Teammitglieder arbeiten auch unter Windows
    import msvcrt
else:
    import fcntl


class SecondProcessError(RuntimeError):
    pass


class ProcessLock:
    """Betriebssystem-Sperre auf `<audit-db>.lock`; endet der Prozess, gibt das OS sie frei."""

    def __init__(self, db_path: Path | str):
        self.path = Path(f"{db_path}.lock")
        self._file = None

    def __enter__(self) -> ProcessLock:
        self._file = open(self.path, "a+")  # noqa: SIM115 – bleibt bis __exit__ offen, sonst fällt die Sperre
        try:
            if os.name == "nt":
                self._file.seek(0)
                msvcrt.locking(self._file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as err:
            self._file.close()
            self._file = None
            raise SecondProcessError(
                f"Audit DB {self.path.with_suffix('')} is already used by another API process. "
                "Signal2Spec runs as one API process (state lives in RAM); "
                "stop the other process or set a separate AUDIT_DB.") from err
        return self

    def __exit__(self, *exc) -> None:
        if self._file is None:
            return
        if os.name == "nt":
            self._file.seek(0)
            msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        self._file.close()
        self._file = None
