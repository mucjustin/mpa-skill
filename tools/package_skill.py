#!/usr/bin/env python3
"""Build a reproducible, single-Skill ZIP consumable by Skill importers.

The package deliberately contains no parent repository, caches or real user data.
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "mpa-skill"
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
FORBIDDEN_DIRS = {"__pycache__", ".mpa-evidence", ".git", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".sqlite", ".sqlite3", ".db", ".key", ".pem"}


def skill_files():
    if not (SKILL / "SKILL.md").is_file():
        raise ValueError("Missing primary SKILL.md")
    files = []
    total = 0
    for path in sorted(SKILL.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink not allowed in Skill bundle: {path}")
        if path.is_dir():
            continue
        relative = path.relative_to(SKILL)
        if any(part in FORBIDDEN_DIRS or part.startswith(".") for part in relative.parts):
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name in {".DS_Store", "Thumbs.db"}:
            continue
        total += path.stat().st_size
        if total > MAX_ARCHIVE_BYTES:
            raise ValueError("Bundle files exceed 50 MiB")
        files.append((path, Path("mpa-skill") / relative))
    if sum(1 for _, r in files if r.name.lower() == "skill.md") != 1:
        raise ValueError("Exactly one SKILL.md required")
    return files


def package(destination):
    output = Path(destination).expanduser().resolve()
    if output == SKILL or SKILL in output.parents:
        raise ValueError("Do not write generated packages inside Skill directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = skill_files()
    temp = output.with_name(output.name + ".tmp")
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for real, arc in files:
                # Fixed timestamps and file perms make the ZIP reproducible across runs.
                info = zipfile.ZipInfo(arc.as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100644 << 16)
                zf.writestr(info, real.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        if temp.stat().st_size > MAX_ARCHIVE_BYTES:
            raise ValueError("Generated ZIP exceeds 50 MiB")
        os.replace(temp, output)
    finally:
        if temp.exists():
            temp.unlink()
    return output, len(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/mpa-skill.zip")
    args = parser.parse_args()
    try:
        file, count = package(args.output)
        print(f"SKILL PACKAGE PASS: {file} ({count} files)")
    except (OSError, ValueError) as exc:
        print(f"SKILL PACKAGE FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
