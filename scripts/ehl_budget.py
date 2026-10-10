"""Simuliert, welche Dateien die EHL-KI-Review von unserem Repo zu sehen bekommt.

Warum: Die EHL-Plattform liest bei der Abgabe nur ~50.000 Tokens (~200.000 Zeichen)
unseres Repos. Was nicht hineinpasst, sieht der KI-Reviewer nie. Dieses Skript bildet
die Logik von tum-ai/ehl nach, damit wir VOR der Abgabe sehen, ob unser Produkt-Code
drin ist oder ob Doku ihn verdrängt.

Quellen (tum-ai/ehl, Stand Commit 5afdadb vom 2026-10-03):
  - lib/code-review/archive.ts   Zipball entpacken, Dateien > 50.000 Bytes und Binärdateien raus
  - lib/code-review/ingest.ts    Filter, Sortierung, 200-Zeilen-Kappung, Budget, Metadaten

Aufruf:
  python scripts/ehl_budget.py                 # Zipball-Modus (Standard, wie bei echter Abgabe)
  python scripts/ehl_budget.py --modus baum    # Fallback-Modus ohne export-ignore
  python scripts/ehl_budget.py --pruefen       # Exit-Code 1, wenn Doku > 25 % des Budgets belegt
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field

# ─── Konstanten 1:1 aus ingest.ts ──────────────────────────────────────────
EXT_LANGUAGE = {
    "ts": "TypeScript", "tsx": "TypeScript",
    "js": "JavaScript", "jsx": "JavaScript", "mjs": "JavaScript",
    "py": "Python", "java": "Java", "go": "Go", "rs": "Rust", "rb": "Ruby",
    "php": "PHP", "cs": "C#",
    "cpp": "C++", "cc": "C++", "cxx": "C++", "hpp": "C++",
    "c": "C", "h": "C", "swift": "Swift", "kt": "Kotlin", "scala": "Scala",
    "vue": "Vue", "svelte": "Svelte", "dart": "Dart",
    "css": "CSS", "scss": "SCSS", "less": "LESS", "html": "HTML", "sql": "SQL",
    "sh": "Shell", "bash": "Shell", "zsh": "Shell",
}
RELEVANT_EXTENSIONS = set(EXT_LANGUAGE) | {
    "json", "yaml", "yml", "toml", "md", "prisma", "graphql", "proto",
}
RELEVANT_FILES = {
    "README.md", "readme.md", "README.rst", "package.json", "requirements.txt",
    "Cargo.toml", "go.mod", "Gemfile", "build.gradle", "pom.xml",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "Makefile", "Procfile",
}
IGNORE_DIRS = {
    "node_modules", ".next", "dist", "build", ".git", "vendor",
    "__pycache__", ".venv", "venv", "target", "coverage", ".cache",
    ".husky", ".idea", ".vscode", "out", ".turbo",
}
TEST_DIRS = {"__tests__", "tests", "test", "spec", "specs", "e2e", "cypress"}
PRIORITY_FILES = {
    "README.md", "readme.md", "package.json", "requirements.txt",
    "Cargo.toml", "go.mod", "Dockerfile", "tsconfig.json",
}
FRAMEWORK_PATTERNS = {
    "Next.js": ["next"], "React": ["react"], "Vue": ["vue"],
    "Angular": ["@angular/core"], "Svelte": ["svelte"], "Express": ["express"],
    "Fastify": ["fastify"], "NestJS": ["@nestjs/core"],
    "Tailwind CSS": ["tailwindcss"], "Prisma": ["prisma", "@prisma/client"],
    "Supabase": ["@supabase/supabase-js"], "Firebase": ["firebase"], "Stripe": ["stripe"],
}
MAX_FILE_BYTES = 50_000          # archive.ts:32 und ingest.ts:219
TRUNCATE_CHARS = 8_000           # ingest.ts:262
TRUNCATE_LINES = 200             # ingest.ts:264
DEFAULT_TOKEN_BUDGET = 50_000    # pipeline.ts:45
DOC_SHARE_LIMIT = 0.25           # unser eigenes Ziel: Doku < 25 % des Budgets


@dataclass
class IncludedFile:
    path: str
    chars: int
    truncated: bool
    cut_by_budget: bool


@dataclass
class BudgetResult:
    included: list[IncludedFile] = field(default_factory=list)
    skipped_after_budget: list[str] = field(default_factory=list)
    total_chars: int = 0
    char_budget: int = DEFAULT_TOKEN_BUDGET * 4
    sampled: bool = False
    metadata: dict = field(default_factory=dict)


def extension(path: str) -> str:
    # Wie ingest.ts:137 — alles nach dem letzten Punkt, auch bei "Dockerfile" (dann der ganze Name).
    return path.split(".")[-1].lower()


def is_ignored_path(path: str) -> bool:
    return any(segment in IGNORE_DIRS for segment in path.split("/"))


def is_relevant_file(path: str) -> bool:
    return path.split("/")[-1] in RELEVANT_FILES or extension(path) in RELEVANT_EXTENSIONS


def category(path: str) -> str:
    """Grobe Einteilung für unsere Auswertung (nicht Teil der EHL-Logik)."""
    if path.startswith("src/"):
        return "src"
    if extension(path) == "md":
        return "doku"
    return "sonstiges"


def detect_frameworks(files: list[tuple[str, str]]) -> list[str]:
    # Nur die package.json und requirements.txt im Repo-ROOT zählen (ingest.ts:87, 104).
    found: list[str] = []
    contents = dict(files)
    if "package.json" in contents:
        try:
            pkg = json.loads(contents["package.json"])
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            found += [name for name, pkgs in FRAMEWORK_PATTERNS.items() if any(p in deps for p in pkgs)]
        except (ValueError, AttributeError):
            pass
    req = contents.get("requirements.txt") or contents.get("requirements/base.txt")
    if req:
        low = req.lower()
        known = (("Django", "django"), ("Flask", "flask"), ("FastAPI", "fastapi"))
        found += [name for name, key in known if key in low]
    return list(dict.fromkeys(found))


def simulate(blobs: list[tuple[str, bytes]], token_budget: int = DEFAULT_TOKEN_BUDGET) -> BudgetResult:
    """Kernlogik: bekommt (Pfad, Inhalt)-Paare in Archiv-Reihenfolge und rechnet wie ingest.ts."""
    # archive.ts:32,38 — zu große und binäre Dateien werden gar nicht erst entpackt.
    texts = [(p, b.decode("utf-8", errors="replace")) for p, b in blobs
             if len(b) <= MAX_FILE_BYTES and b"\x00" not in b]
    sizes = {p: len(t.encode("utf-8")) for p, t in texts}

    languages: dict[str, int] = {}
    flags = {"has_readme": False, "has_dockerfile": False, "has_tests": False}
    for path, _ in texts:
        if is_ignored_path(path):
            continue
        name = path.split("/")[-1]
        lang = EXT_LANGUAGE.get(extension(path))
        if lang:
            languages[lang] = languages.get(lang, 0) + max(1, round(sizes[path] / 40))
        flags["has_readme"] |= name.lower().startswith("readme")
        flags["has_dockerfile"] |= name in ("Dockerfile", "docker-compose.yml")
        flags["has_tests"] |= any(s in TEST_DIRS for s in path.split("/"))

    relevant = [(p, t) for p, t in texts
                if not is_ignored_path(p) and is_relevant_file(p) and sizes[p] <= MAX_FILE_BYTES]
    # ingest.ts:229 — Priority-Dateinamen zuerst (egal in welchem Ordner!), dann kleinste zuerst.
    relevant.sort(key=lambda item: (0 if item[0].split("/")[-1] in PRIORITY_FILES else 1, sizes[item[0]]))

    result = BudgetResult(char_budget=token_budget * 4)
    taken: list[tuple[str, str]] = []
    for index, (path, content) in enumerate(relevant):
        if result.total_chars >= result.char_budget:
            result.sampled = True
            result.skipped_after_budget = [p for p, _ in relevant[index:]]
            break
        truncated = False
        if len(content) > TRUNCATE_CHARS:
            lines = content.split("\n")
            if len(lines) > TRUNCATE_LINES:
                content = "\n".join(lines[:TRUNCATE_LINES]) + "\n\n[TRUNCATED - showing first 200 lines]"
                truncated = True
        cut = False
        if result.total_chars + len(content) > result.char_budget:
            result.sampled = True
            content = content[: result.char_budget - result.total_chars]
            cut = True
        result.included.append(IncludedFile(path, len(content), truncated, cut))
        taken.append((path, content))
        result.total_chars += len(content)

    primary = max(languages.items(), key=lambda kv: kv[1])[0] if languages else "Unknown"
    result.metadata = {
        **flags,
        "languages": languages,
        "primary_language": primary,
        "frameworks_detected": detect_frameworks(taken),
        "token_count": round(result.total_chars / 4),
        "sampled": result.sampled,
        "file_count": sum(1 for p, _ in texts if not is_ignored_path(p)),
    }
    return result


# ─── Dateien aus Git laden ────────────────────────────────────────────────
def load_zipball(ref: str) -> list[tuple[str, bytes]]:
    """Wie GitHubs Zipball: `git archive` beachtet export-ignore aus .gitattributes."""
    data = subprocess.run(["git", "archive", "--format=zip", ref], capture_output=True, check=True).stdout
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return [(i.filename, zf.read(i)) for i in zf.infolist() if not i.is_dir()]


def load_tree(ref: str) -> list[tuple[str, bytes]]:
    """Fallback-Modus (Trees-API, ingest.ts:164-169): ALLE Dateien, export-ignore wirkt NICHT."""
    paths = subprocess.run(["git", "ls-tree", "-r", "--name-only", "-z", ref],
                           capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    return [(p, subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True, check=True).stdout)
            for p in paths if p]


def report(result: BudgetResult) -> dict:
    by_category: dict[str, int] = {}
    for f in result.included:
        by_category[category(f.path)] = by_category.get(category(f.path), 0) + f.chars
    budget = result.char_budget
    return {
        "chars_total": result.total_chars,
        "budget_chars": budget,
        "budget_used_pct": round(100 * result.total_chars / budget, 1),
        "src_share_of_included_pct": round(100 * by_category.get("src", 0) / max(1, result.total_chars), 1),
        "doku_share_of_budget_pct": round(100 * by_category.get("doku", 0) / budget, 1),
        "chars_by_category": by_category,
        "budget_reached": result.sampled,
        "first_file_not_seen": result.skipped_after_budget[0] if result.skipped_after_budget else None,
        "files_not_seen": len(result.skipped_after_budget),
    }


def main(argv: list[str] | None = None) -> int:
    # Windows-Konsolen nutzen oft cp1252; ohne das werden Umlaute zu Fragezeichen.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Simuliert das EHL-Review-Budget für dieses Repo.")
    parser.add_argument("--ref", default="HEAD", help="Git-Commit, der geprüft wird (Standard: HEAD)")
    parser.add_argument("--modus", choices=["zip", "baum"], default="zip",
                        help="zip = echter Abgabe-Snapshot, baum = Fallback ohne export-ignore")
    parser.add_argument("--json", action="store_true", help="Maschinenlesbare Ausgabe")
    parser.add_argument("--pruefen", action="store_true",
                        help="Exit-Code 1, wenn Doku mehr als 25 %% des Budgets belegt")
    args = parser.parse_args(argv)

    blobs = load_zipball(args.ref) if args.modus == "zip" else load_tree(args.ref)
    result = simulate(blobs)
    summary = report(result)

    if args.json:
        print(json.dumps({"summary": summary, "metadata": result.metadata,
                          "included": [f.__dict__ for f in result.included]}, indent=2, ensure_ascii=False))
    else:
        print(f"EHL-Review-Simulation ({args.modus}-Modus, {args.ref})\n")
        print(f"{'Zeichen':>8}  Datei")
        for f in result.included:
            note = " (auf 200 Zeilen gekappt)" if f.truncated else ""
            note += " (vom Budget abgeschnitten)" if f.cut_by_budget else ""
            print(f"{f.chars:>8}  {f.path}{note}")
        print(f"\nBudget: {summary['chars_total']:,} / {summary['budget_chars']:,} Zeichen "
              f"({summary['budget_used_pct']} %)")
        if summary["budget_reached"]:
            print(f"BUDGET VOLL ab: {summary['first_file_not_seen']} "
                  f"({summary['files_not_seen']} Dateien sieht der Reviewer nicht)")
        print(f"Anteil src/ an gelesenen Zeichen: {summary['src_share_of_included_pct']} %")
        print(f"Doku (.md) belegt vom Budget:     {summary['doku_share_of_budget_pct']} %")
        meta = result.metadata
        print(f"Flags: README={meta['has_readme']} Tests={meta['has_tests']} "
              f"Dockerfile={meta['has_dockerfile']} Frameworks={meta['frameworks_detected'] or 'keine erkannt'}")

    if args.pruefen and summary["doku_share_of_budget_pct"] > DOC_SHARE_LIMIT * 100:
        print(f"FEHLER: Doku belegt mehr als {int(DOC_SHARE_LIMIT * 100)} % des Budgets.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
