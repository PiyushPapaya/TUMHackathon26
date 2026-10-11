"""Ein API-Prozess pro Audit-DB: der zweite muss mit klarer Meldung abbrechen."""

import subprocess
import sys
from pathlib import Path

import pytest

from core.single_process import ProcessLock, SecondProcessError

BACKEND = Path(__file__).resolve().parents[2] / "src" / "backend"


def test_zweiter_prozess_wird_abgewiesen(tmp_path):
    db = tmp_path / "audit.db"
    with ProcessLock(db):
        # Echter zweiter Prozess, weil genau der Fall (zweiter uvicorn-Worker) abgesichert werden soll.
        code = ("import sys; sys.path.insert(0, sys.argv[1]);"
                "from core.single_process import ProcessLock, SecondProcessError\n"
                "try:\n    ProcessLock(sys.argv[2]).__enter__()\n"
                "except SecondProcessError:\n    sys.exit(3)\n")
        result = subprocess.run([sys.executable, "-c", code, str(BACKEND), str(db)], timeout=30)
        assert result.returncode == 3


def test_sperre_wird_nach_ende_freigegeben(tmp_path):
    db = tmp_path / "audit.db"
    with ProcessLock(db):
        pass
    with ProcessLock(db):  # Neustart derselben App (z. B. --reload) muss wieder starten
        pass


def test_doppelt_im_selben_prozess_abgewiesen(tmp_path):
    db = tmp_path / "audit.db"
    with ProcessLock(db), pytest.raises(SecondProcessError, match="one API process"):
        ProcessLock(db).__enter__()
