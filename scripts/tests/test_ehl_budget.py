"""Tests für scripts/ehl_budget.py (nur Standardbibliothek, läuft mit `python -m unittest`).

Warum hier und nicht in tests/: tests/ landet im Abgabe-Snapshot und soll nur
Produkt-Tests enthalten. scripts/ ist per export-ignore ausgeschlossen.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ehl_budget as eb


def blob(path: str, text: str) -> tuple[str, bytes]:
    return path, text.encode("utf-8")


class SimulateTests(unittest.TestCase):
    def test_priority_files_come_first_then_smallest(self):
        # README.md in einem Unterordner zählt als Priority-Datei (ingest.ts:230 prüft nur den Dateinamen).
        result = eb.simulate([
            blob("src/big.py", "x" * 500),
            blob("src/small.py", "x" * 10),
            blob("workspace/anna/README.md", "y" * 300),
        ])
        self.assertEqual([f.path for f in result.included],
                         ["workspace/anna/README.md", "src/small.py", "src/big.py"])

    def test_files_over_50kb_and_binaries_are_dropped(self):
        result = eb.simulate([
            ("src/huge.py", b"a" * 50_001),
            ("src/bin.py", b"abc\x00def"),
            blob("src/ok.py", "print(1)"),
        ])
        self.assertEqual([f.path for f in result.included], ["src/ok.py"])

    def test_ignored_dirs_and_irrelevant_extensions(self):
        result = eb.simulate([
            blob("node_modules/x/index.js", "1"),
            blob("src/app/out/page.tsx", "1"),   # "out" ist ein ignoriertes Segment
            blob("notes.txt", "1"),              # .txt ist nicht relevant
            blob("Makefile", "all:"),            # Name ist in RELEVANT_FILES
        ])
        self.assertEqual([f.path for f in result.included], ["Makefile"])

    def test_truncation_needs_both_8000_chars_and_200_lines(self):
        long_lines = "\n".join(["z" * 100] * 100)   # >8000 Zeichen, aber nur 100 Zeilen
        many_lines = "\n".join(["z" * 50] * 300)    # >8000 Zeichen und >200 Zeilen
        result = eb.simulate([blob("a.py", long_lines), blob("b.py", many_lines)])
        by_path = {f.path: f for f in result.included}
        self.assertFalse(by_path["a.py"].truncated)
        self.assertTrue(by_path["b.py"].truncated)

    def test_budget_cuts_last_file_and_marks_rest_unseen(self):
        result = eb.simulate([blob("a.py", "a" * 30), blob("b.py", "b" * 40), blob("c.py", "c" * 50)],
                             token_budget=15)  # 60 Zeichen
        self.assertTrue(result.sampled)
        self.assertEqual(result.total_chars, 60)
        self.assertTrue(result.included[-1].cut_by_budget)
        self.assertEqual(result.skipped_after_budget, ["c.py"])

    def test_frameworks_only_from_root_manifests(self):
        result = eb.simulate([
            blob("src/frontend/package.json", '{"dependencies": {"next": "15"}}'),
            blob("requirements.txt", "fastapi==0.115\nuvicorn\n"),
        ])
        self.assertEqual(result.metadata["frameworks_detected"], ["FastAPI"])

    def test_tests_flag_from_any_tests_segment(self):
        result = eb.simulate([blob("tests/test_api.py", "def test(): pass")])
        self.assertTrue(result.metadata["has_tests"])

    def test_report_shares(self):
        result = eb.simulate([blob("src/a.py", "a" * 100), blob("docs/x.md", "d" * 100)], token_budget=100)
        rep = eb.report(result)
        self.assertEqual(rep["src_share_of_included_pct"], 50.0)
        self.assertEqual(rep["doku_share_of_budget_pct"], 25.0)


if __name__ == "__main__":
    unittest.main()
