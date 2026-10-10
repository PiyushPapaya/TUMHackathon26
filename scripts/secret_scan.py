"""Sucht nach API-Keys und Passwörtern, bevor sie im ÖFFENTLICHEN Repo landen.

Warum ein eigenes Skript statt gitleaks: läuft überall, wo Python ist (Windows, Mac, CI),
ohne Extra-Installation. Für eine gründlichere Prüfung siehe docs/ABGABE.md (gitleaks).

Aufruf:
  python scripts/secret_scan.py            # alle getrackten + gestagten Dateien
  python scripts/secret_scan.py --historie # zusätzlich die komplette Git-Historie
Exit-Code 1 = Fund. Dann: Key SOFORT beim Anbieter widerrufen, erst danach aufräumen.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

# Muster bekannter Key-Formate. Die Präfixe sind zusammengesetzt, damit diese Datei
# sich nicht selbst als Fund meldet.
PATTERNS = {
    "OpenAI-Key": r"\b" + "sk-" + r"(?:proj-|svcacct-|admin-)?[A-Za-z0-9_\-]{20,}",
    "Anthropic-Key": r"\b" + "sk-" + r"ant-[A-Za-z0-9_\-]{20,}",
    "GitHub-Token": r"\b(?:" + "gh" + r"[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})",
    "AWS-Key": r"\b" + "AK" + r"IA[0-9A-Z]{16}\b",
    "Google-API-Key": r"\b" + "AI" + r"za[0-9A-Za-z_\-]{35}\b",
    "Private Key": "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Key=Wert in Code": r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{16,}['\"]",
}
FORBIDDEN_FILES = re.compile(r"(^|/)(\.env(\..+)?|.*\.pem|.*\.key|settings\.local\.json)$")
ALLOWED_FILES = {".env.example"}
SELF = "scripts/secret_scan.py"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=True).stdout


def scan_text(label: str, text: str) -> list[str]:
    hits = []
    for name, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            line_no = text.count("\n", 0, match.start()) + 1
            shown = match.group(0)[:12] + "…"  # nie den ganzen Key ausgeben
            hits.append(f"{label}:{line_no}: {name} ({shown})")
    return hits


def main(argv: list[str] | None = None) -> int:
    # Windows-Konsolen nutzen oft cp1252; ohne das werden Umlaute zu Fragezeichen.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Secret-Scan für das öffentliche Repo")
    parser.add_argument("--historie", action="store_true", help="auch alle alten Commits prüfen")
    args = parser.parse_args(argv)

    files = sorted(set(git("ls-files").splitlines()) | set(git("diff", "--cached", "--name-only").splitlines()))
    findings: list[str] = []
    for path in files:
        if FORBIDDEN_FILES.search(path) and path.split("/")[-1] not in ALLOWED_FILES:
            findings.append(f"{path}: Diese Datei darf nie committed werden")
        if path == SELF:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                findings += scan_text(path, handle.read())
        except (FileNotFoundError, IsADirectoryError):
            continue  # gelöscht, aber noch im Index

    if args.historie:
        history = git("log", "-p", "--all", "--no-color", "--", ".", f":(exclude){SELF}")
        findings += scan_text("git-historie", history)

    if findings:
        print("MÖGLICHE SECRETS GEFUNDEN:")
        print("\n".join(f"  - {f}" for f in findings))
        print("\nWas jetzt? Key beim Anbieter widerrufen (neuen erzeugen), dann Piyush holen.")
        return 1
    print(f"Secret-Scan sauber: {len(files)} Dateien geprüft" + (" + Historie" if args.historie else "") + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
