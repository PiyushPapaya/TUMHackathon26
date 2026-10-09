"""Tests für .claude/hooks/git-schutz.sh: Er bekommt JSON wie von Claude Code und muss
gefährliche Git-Befehle mit Exit-Code 2 blockieren, harmlose durchlassen."""

import json
import os
import shutil
import subprocess
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "..", ".claude", "hooks", "git-schutz.sh")

MUST_BLOCK = [
    "git push --force",
    "git push -f origin lasse/x",
    "git push origin +lasse/x",
    "git reset --hard HEAD~1",
    "git clean -fd",
    "git commit --no-verify -m x",
    'git commit -m "msg" --no-verify',  # Flag NACH der Nachricht
    "git branch -D lasse/x",
    "git push origin --delete lasse/x",
    "git push origin main",
    "git push origin HEAD:main",
    "git push origin lasse/x:main",
    "git rebase main",
]
MUST_PASS = [
    "git push -u origin lasse/login",
    "git push && git switch main",
    "git switch main && git pull",
    "git merge origin/main",
    "git rebase --abort",
    'git commit -m "kein rebase, kein push --force, reset --hard"',  # nur Text in der Nachricht
    "git branch -d alt",
    "git push origin lasse/main-fix",
    "ls -la",
]


def run_hook(command: str) -> int:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run(["sh", HOOK], check=False, input=payload, text=True, capture_output=True).returncode


@unittest.skipIf(shutil.which("sh") is None, "kein sh verfügbar")
class GitSchutzTests(unittest.TestCase):
    def test_dangerous_commands_are_blocked(self):
        for command in MUST_BLOCK:
            with self.subTest(command=command):
                self.assertEqual(run_hook(command), 2)

    def test_safe_commands_pass(self):
        for command in MUST_PASS:
            with self.subTest(command=command):
                self.assertEqual(run_hook(command), 0)


if __name__ == "__main__":
    unittest.main()
