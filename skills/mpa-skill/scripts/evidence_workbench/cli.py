"""Command line interface for offline MPA evidence workbench."""
import argparse
import json
import os
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path

from .core import (EvidenceError, add_claim, add_evidence, audit, export_registry,
                   import_document, initialize, list_segments, review_evidence)


def parser():
    p = argparse.ArgumentParser(prog="mpa-evidence",
        description="Offline evidence registry. Source match is not a causal validity check.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("doctor", help="Read-only capability and workspace preflight")
    s.add_argument("--workspace", help="Optional existing workspace to inspect")

    s = sub.add_parser("init", help="Initialize private local registry")
    s.add_argument("workspace")

    s = sub.add_parser("ingest", help="Snapshot and index a source")
    s.add_argument("workspace")
    s.add_argument("file")

    s = sub.add_parser("segments", help="Search/show exact source locators")
    s.add_argument("workspace")
    s.add_argument("document")
    s.add_argument("--search")
    s.add_argument("--locator")
    s.add_argument("--limit", type=int, default=25)

    s = sub.add_parser("claim", help="Register a research claim or hypothesis")
    s.add_argument("workspace")
    s.add_argument("--question", required=True)
    s.add_argument("--statement", required=True)
    s.add_argument("--kind", choices=["fact", "inference", "causal", "recommendation"],
                   default="fact")

    s = sub.add_parser("cite", help="Link an exact source quote to a claim")
    s.add_argument("workspace")
    s.add_argument("--claim", required=True)
    s.add_argument("--document", required=True)
    s.add_argument("--locator", required=True)
    q = s.add_mutually_exclusive_group(required=True)
    q.add_argument("--quote")
    q.add_argument("--quote-file", help="UTF-8 text file holding an exact quote")
    s.add_argument("--relation", choices=["supports", "challenges", "context"],
                   default="supports")

    s = sub.add_parser("review", help="Explicitly record a human review decision")
    s.add_argument("workspace")
    s.add_argument("evidence")
    s.add_argument("--status", choices=["verified", "disputed", "rejected"], required=True)
    s.add_argument("--reviewer", required=True)
    s.add_argument("--note", default="")

    s = sub.add_parser("audit", help="Check source integrity and unresolved gaps")
    s.add_argument("workspace")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("export", help="Export a privacy-conscious evidence register")
    s.add_argument("workspace")
    s.add_argument("--format", choices=["md", "json"], default="md")
    s.add_argument("--output", required=True)
    s.add_argument("--include-quotes", action="store_true")
    s.add_argument("--overwrite", action="store_true")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            root = Path(__file__).resolve().parent.parent
            workspace_db = None
            if args.workspace is not None:
                workspace_db = (
                    Path(args.workspace).expanduser().resolve() /
                    ".mpa-evidence" / "registry.sqlite3"
                )
            result = {
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "python_supported": sys.version_info >= (3, 10),
                "sqlite_available": True,
                "bundled_scripts": str(root),
                "text_formats": [".txt", ".md", ".csv", ".docx"],
                "pdf_text_available": find_spec("pypdf") is not None,
                "pdf_requires_optional_dependency": True,
                "workspace_initialized": (
                    workspace_db.is_file() if workspace_db is not None else None
                ),
                "read_only": True,
            }
        elif args.command == "init":
            result = {"registry": initialize(args.workspace)}
        elif args.command == "ingest":
            result = import_document(args.workspace, args.file)
        elif args.command == "segments":
            if args.limit <= 0 or args.limit > 1000:
                raise EvidenceError("--limit must be 1..1000.")
            result = list_segments(args.workspace, args.document,
                                   args.search, args.locator, args.limit)
        elif args.command == "claim":
            result = {"claim_id": add_claim(args.workspace, args.question,
                                            args.statement, args.kind)}
        elif args.command == "cite":
            quote = args.quote if args.quote is not None else Path(args.quote_file).read_text(encoding="utf-8-sig")
            result = {"evidence_id": add_evidence(args.workspace, args.claim, args.document,
                                                   args.locator, quote, args.relation)}
        elif args.command == "review":
            result = {"evidence_id": review_evidence(args.workspace, args.evidence, args.status,
                                                     args.reviewer, args.note), "status": args.status}
        elif args.command == "audit":
            result = audit(args.workspace)
        else:
            out = Path(args.output).expanduser().resolve()
            if out.exists() and not args.overwrite:
                raise EvidenceError("Export target exists; use --overwrite explicitly.")
            if not out.parent.is_dir():
                raise EvidenceError("Export parent directory does not exist.")
            payload = export_registry(args.workspace, args.format, args.include_quotes)
            handle, temp_name = tempfile.mkstemp(prefix=".mpa-export-", dir=str(out.parent))
            try:
                with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(payload)
                os.replace(temp_name, out)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
            result = {"exported": str(out), "format": args.format,
                      "quotes_included": args.include_quotes}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "audit" and not result["ok"]:
            return 2
        return 0
    except (EvidenceError, FileNotFoundError, PermissionError, OSError,
            UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
