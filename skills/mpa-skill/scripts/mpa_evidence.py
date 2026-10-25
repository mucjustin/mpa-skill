#!/usr/bin/env python3
"""Portable local entrypoint. Run from any cwd after installing *only* mpa-skill.

    python "<skill-root>/scripts/mpa_evidence.py" doctor
"""
from evidence_workbench.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
