"""Command line interface for offline MPA evidence workbench."""
import argparse
import json
import os
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path

from .core import (SPINE_LINKS, EvidenceError, add_claim, add_evidence, audit,
                   export_registry, import_document, initialize, list_segments, progress,
                   review_evidence)
from .draft import check_draft
from .redact import Redactor
from .workspace import initialize_workspace, inspect_environment


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
    s.add_argument("--rival-of", help="Register this claim as a rival explanation of C####")

    s = sub.add_parser("cite", help="Link an exact source quote to a claim")
    s.add_argument("workspace")
    s.add_argument("--claim", required=True)
    s.add_argument("--document", required=True)
    s.add_argument("--locator", required=True,
                   help="Single locator (L3, p.2, para.5, fn.1) or a range such as L3-L5")
    q = s.add_mutually_exclusive_group(required=True)
    q.add_argument("--quote")
    q.add_argument("--quote-file", help="UTF-8 text file holding an exact quote")
    s.add_argument("--relation", choices=["supports", "challenges", "context"],
                   default="supports")
    s.add_argument("--normalized", action="store_true",
                   help="Allow a match that ignores whitespace and full/half-width differences; "
                        "the verbatim source span is stored")

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
    add_redaction_options(s)

    s = sub.add_parser("check-draft", help="Check a draft's [C####] tags against the registry")
    s.add_argument("workspace")
    s.add_argument("draft", help="Draft file (.md, .txt or .docx)")

    s = sub.add_parser("progress", help="Show or update MPA Research Spine progress and tasks")
    s.add_argument("workspace")
    s.add_argument("--set", action="append", default=[], metavar="LINK=STATUS",
                   help=f"Links: {', '.join(SPINE_LINKS)}; "
                        "statuses: missing, partial, established, out_of_scope")
    s.add_argument("--note", default="")
    s.add_argument("--todo", help="Add an open task")
    s.add_argument("--done", help="Close task T####")
    s.add_argument("--next", dest="next_task", help="Mark open task T#### as the next step")

    s = sub.add_parser("redact", help="Write a de-identified copy of a UTF-8 text file")
    s.add_argument("file")
    s.add_argument("--output", required=True)
    s.add_argument("--overwrite", action="store_true")
    add_redaction_options(s, required=True)

    s = sub.add_parser("workspace-init", help="Create workspace folders and a local config file")
    s.add_argument("workspace_root")
    s.add_argument("--config", help="Config path (default: platform config directory)")
    s.add_argument("--zotero", help="Zotero application/executable path")
    s.add_argument("--dry-run", action="store_true")

    s = sub.add_parser("env-check", help="Read-only check of workspace config and Zotero")
    s.add_argument("--config")
    s.add_argument("--no-zotero-probe", action="store_true")
    return p


def add_redaction_options(s, required=False):
    s.add_argument("--redact", action="store_true", default=required,
                   help="Replace common identifiers (ID, phone, email, document numbers)")
    s.add_argument("--redact-terms",
                   help="UTF-8 file: one term per line, optionally 原词=替代词")
    s.add_argument("--no-auto-patterns", action="store_true",
                   help="Use only --redact-terms, skip automatic patterns")


def build_redactor(args):
    if not (args.redact or args.redact_terms):
        return None
    auto = not args.no_auto_patterns
    if args.redact_terms:
        return Redactor.from_file(args.redact_terms, auto=auto)
    return Redactor(auto=auto)


def write_atomic(output, payload, overwrite):
    out = Path(output).expanduser().resolve()
    if out.exists() and not overwrite:
        raise EvidenceError("Output target exists; use --overwrite explicitly.")
    if not out.parent.is_dir():
        raise EvidenceError("Output parent directory does not exist.")
    handle, temp_name = tempfile.mkstemp(prefix=".mpa-export-", dir=str(out.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
        os.replace(temp_name, out)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return out


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
                                            args.statement, args.kind, args.rival_of)}
        elif args.command == "cite":
            quote = args.quote if args.quote is not None else Path(args.quote_file).read_text(encoding="utf-8-sig")
            evidence_id = add_evidence(args.workspace, args.claim, args.document, args.locator,
                                       quote, args.relation, normalized=args.normalized)
            result = {"evidence_id": evidence_id}
        elif args.command == "review":
            result = {"evidence_id": review_evidence(args.workspace, args.evidence, args.status,
                                                     args.reviewer, args.note), "status": args.status}
        elif args.command == "audit":
            result = audit(args.workspace)
        elif args.command == "export":
            redactor = build_redactor(args)
            payload = export_registry(args.workspace, args.format, args.include_quotes, redactor)
            out = write_atomic(args.output, payload, args.overwrite)
            result = {"exported": str(out), "format": args.format,
                      "quotes_included": args.include_quotes,
                      "redaction": redactor.summary() if redactor else None}
        elif args.command == "check-draft":
            result = check_draft(args.workspace, args.draft)
        elif args.command == "progress":
            result = progress(args.workspace, args.set, args.note, args.todo, args.done,
                              args.next_task)
        elif args.command == "redact":
            source = Path(args.file).expanduser()
            if source.suffix.lower() not in (".txt", ".md", ".csv"):
                raise EvidenceError("redact accepts UTF-8 .txt, .md or .csv files.")
            redactor = build_redactor(args)
            out = write_atomic(args.output,
                               redactor.text(source.read_text(encoding="utf-8-sig")),
                               args.overwrite)
            result = {"redacted": str(out), **redactor.summary(),
                      "note": "Review the output before sharing; patterns are not exhaustive."}
        elif args.command == "workspace-init":
            result = initialize_workspace(args.workspace_root, args.config, args.zotero,
                                          args.dry_run)
        else:
            result = inspect_environment(args.config, probe_zotero=not args.no_zotero_probe)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command in ("audit", "check-draft") and not result["ok"]:
            return 2
        return 0
    except (EvidenceError, FileNotFoundError, PermissionError, OSError,
            UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
