"""Tests für scripts/secret_scan.py. Die Beispiel-Keys sind erfunden und zusammengesetzt."""

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import secret_scan as ss


class SecretScanTests(unittest.TestCase):
    def test_detects_openai_key(self):
        fake = "sk-" + "proj-" + "A" * 40
        self.assertTrue(ss.scan_text("x.py", f'client = OpenAI(api_key="{fake}")'))

    def test_detects_github_token(self):
        fake = "gh" + "p_" + "b" * 36
        self.assertTrue(ss.scan_text("x.sh", f"TOKEN={fake}"))

    def test_output_never_contains_full_key(self):
        fake = "sk-" + "proj-" + "C" * 40
        hit = ss.scan_text("x.py", fake)[0]
        self.assertNotIn(fake, hit)

    def test_env_example_placeholders_are_clean(self):
        self.assertEqual(ss.scan_text(".env.example", "OPENAI_API_KEY=\nOPENAI_MODEL=gpt-mini\n"), [])

    def test_forbidden_filenames(self):
        self.assertTrue(ss.FORBIDDEN_FILES.search(".env"))
        self.assertTrue(ss.FORBIDDEN_FILES.search("src/backend/.env.local"))
        self.assertTrue(ss.FORBIDDEN_FILES.search(".claude/settings.local.json"))
        self.assertIsNone(ss.FORBIDDEN_FILES.search("docs/env.md"))

    def test_stream_detects_key_split_between_chunks_without_duplicate_or_leak(self):
        fake = "sk-" + "proj-" + "D" * 40
        text = "first line\n" + " " * 50 + fake + "\nlast line"
        hits = ss.scan_stream("history", io.StringIO(text), chunk_size=64)
        self.assertEqual(len(hits), 1)
        self.assertIn("history:2:", hits[0])
        self.assertNotIn(fake, hits[0])


if __name__ == "__main__":
    unittest.main()
