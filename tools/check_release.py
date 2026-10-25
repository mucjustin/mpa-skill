#!/usr/bin/env python3
"""Check release metadata consistency without accessing GitHub or modifying files."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def skill_version(root: Path = ROOT) -> str:
    content = (root / "skills/mpa-skill/SKILL.md").read_text(encoding="utf-8")
    blocks = content.split("---", 2)
    if len(blocks) < 3 or blocks[0].strip():
        raise ValueError("SKILL.md YAML frontmatter is missing")
    versions = re.findall(r'(?m)^version:\s*"([0-9]+\.[0-9]+\.[0-9]+)"\s*$', blocks[1])
    if len(versions) != 1:
        raise ValueError("SKILL.md frontmatter requires one quoted semantic version")
    return versions[0]


def validate(root: Path = ROOT) -> str:
    version = skill_version(root)
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    dated_release = re.compile(
        r"(?m)^## \[" + re.escape(version) + r"\] - \d{4}-\d{2}-\d{2}\s*$"
    )
    if len(dated_release.findall(changelog)) != 1:
        raise ValueError(f"CHANGELOG must contain exactly one dated [{version}] section")
    if len(re.findall(r"(?m)^## \[Unreleased\]", changelog)) != 1:
        raise ValueError("CHANGELOG must contain exactly one [Unreleased] section")
    older = changelog.find("## [2.1.0]")
    if older < 0 or changelog.find(f"## [{version}]") >= older:
        raise ValueError("Current release must precede the archived v2.1.0 section")
    notes = root / "docs" / "releases" / f"v{version}.md"
    if not notes.is_file() or f"v{version}" not in notes.read_text(encoding="utf-8"):
        raise ValueError("Versioned GitHub release notes are missing")
    for path in ("README.md", "README.en.md", "docs/install-and-compatibility.md"):
        doc = (root / path).read_text(encoding="utf-8")
        if f"v{version}" not in doc:
            raise ValueError(f"Version drift in {path}")
    return version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args()
    try:
        version = validate()
    except (OSError, ValueError) as exc:
        print(f"RELEASE METADATA FAIL: {exc}", file=sys.stderr)
        return 2
    if args.print_version:
        print(version)
    else:
        print(f"RELEASE METADATA PASS: v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
