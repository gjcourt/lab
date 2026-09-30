#!/usr/bin/env python3
"""Validate repo invariants stated in .github/copilot-instructions.md.

Checks:
1. Every project file under `0?-*/` matching `0?-NNN-*.md` has:
   - YAML frontmatter delimited by `---` lines
   - Required keys: title, number, category, difficulty, time_commitment,
     target_skills, status
   - Allowed values for `difficulty` (Easy|Medium|Hard) and
     `status` (Not Started|In Progress|Done)
   - `number:` value matches the filename prefix (e.g. `01-001`)
   - An `## Exit Criteria` section is present
2. Per-category counts in each `<cat>/projects.md` heading match the actual
   file count in that directory.
3. The README tagline total ("A curated list of 132 ... projects") matches
   the sum of per-category counts.

Exits non-zero on any violation; prints all violations.

Note: this script intentionally does not fail on the boilerplate placeholder
Exit Criteria text -- that is tracked as a deferred content task. It only
checks that the section header exists. If/when placeholders are replaced,
add a stricter check here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_KEYS = [
    "title",
    "number",
    "category",
    "difficulty",
    "time_commitment",
    "target_skills",
    "status",
]
ALLOWED_DIFFICULTY = {"Easy", "Medium", "Hard"}
ALLOWED_STATUS = {"Not Started", "In Progress", "Done"}

PROJECT_FILE_RE = re.compile(r"^(\d{2})-(\d{3})-.+\.md$")
CATEGORY_DIR_RE = re.compile(r"^\d{2}-[a-z0-9-]+$")
# The README standard (gjcourt/.github) makes the H1 the bare repo name, so
# the total lives in the tagline line below it.
README_TOTAL_RE = re.compile(r"^A curated list of (\d+) multidisciplinary", re.MULTILINE)
PROJECTS_MD_COUNT_RE = re.compile(r"^# .+ \((\d+)\)\s*$", re.MULTILINE)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return dict of top-level key: value strings, or None if missing."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    body = text[4:end]
    out: dict[str, str] = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # strip surrounding quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {"'", '"'}:
            val = val[1:-1]
        out[key] = val
    return out


def check_project_file(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(REPO_ROOT)
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{rel}: missing or malformed YAML frontmatter")
        return
    for key in REQUIRED_KEYS:
        if key not in fm:
            errors.append(f"{rel}: frontmatter missing required key '{key}'")
    if "difficulty" in fm and fm["difficulty"] not in ALLOWED_DIFFICULTY:
        errors.append(
            f"{rel}: difficulty '{fm['difficulty']}' not in "
            f"{sorted(ALLOWED_DIFFICULTY)}"
        )
    if "status" in fm and fm["status"] not in ALLOWED_STATUS:
        errors.append(
            f"{rel}: status '{fm['status']}' not in {sorted(ALLOWED_STATUS)}"
        )
    # Filename prefix vs frontmatter number
    m = PROJECT_FILE_RE.match(path.name)
    if m and "number" in fm:
        expected = f"{m.group(1)}-{m.group(2)}"
        if fm["number"] != expected:
            errors.append(
                f"{rel}: frontmatter number '{fm['number']}' does not match "
                f"filename prefix '{expected}'"
            )
    if "## Exit Criteria" not in text:
        errors.append(f"{rel}: missing '## Exit Criteria' section")


def collect_project_files() -> dict[Path, list[Path]]:
    """Return {category_dir: [project_file, ...]} for all category dirs."""
    out: dict[Path, list[Path]] = {}
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir() or not CATEGORY_DIR_RE.match(entry.name):
            continue
        files = sorted(
            f for f in entry.iterdir() if PROJECT_FILE_RE.match(f.name)
        )
        out[entry] = files
    return out


def check_counts(by_cat: dict[Path, list[Path]], errors: list[str]) -> int:
    total = 0
    for cat_dir, files in by_cat.items():
        total += len(files)
        projects_md = cat_dir / "projects.md"
        if not projects_md.exists():
            errors.append(f"{cat_dir.name}/projects.md missing")
            continue
        text = projects_md.read_text(encoding="utf-8")
        m = PROJECTS_MD_COUNT_RE.search(text)
        if not m:
            errors.append(
                f"{cat_dir.name}/projects.md: top heading does not match "
                "'# <Title> (<count>)'"
            )
            continue
        declared = int(m.group(1))
        if declared != len(files):
            errors.append(
                f"{cat_dir.name}/projects.md declares {declared} projects "
                f"but directory contains {len(files)}"
            )
    return total


def check_readme_total(total: int, errors: list[str]) -> None:
    readme = REPO_ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    m = README_TOTAL_RE.search(text)
    if not m:
        errors.append(
            "README.md: tagline does not match "
            "'A curated list of <N> multidisciplinary ...'"
        )
        return
    declared = int(m.group(1))
    if declared != total:
        errors.append(
            f"README.md declares {declared} total projects but repo "
            f"contains {total}"
        )


def main() -> int:
    errors: list[str] = []
    by_cat = collect_project_files()
    for files in by_cat.values():
        for f in files:
            check_project_file(f, errors)
    total = check_counts(by_cat, errors)
    check_readme_total(total, errors)

    if errors:
        print("Repository invariant violations:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {total} project files, all invariants satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
