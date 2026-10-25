"""Offline, source-linked evidence registry for public-management case research.

No model calls, uploads, authentication, or background tasks. Local copies of
original sources and extracted text contain potentially sensitive information.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import sqlite3
import uuid
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

STORE = ".mpa-evidence"
DB_FILE = "registry.sqlite3"
MAX_BYTES = 30 * 1024 * 1024
MAX_SEGMENTS = 100_000
FORMATS = {".txt", ".md", ".csv", ".docx", ".pdf"}
STATUSES = {"unverified", "verified", "disputed", "rejected"}
RELATIONS = {"supports", "challenges", "context"}
KINDS = {"fact", "inference", "causal", "recommendation"}


class EvidenceError(Exception):
    """Actionable input or integrity failure."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def private_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def private_file(path: Path):
    try:
        path.chmod(0o600)
    except OSError:
        pass


def store_path(workspace: str | Path) -> Path:
    return Path(workspace).expanduser().resolve() / STORE


def initialize(workspace: str | Path):
    root = store_path(workspace)
    private_dir(root)
    private_dir(root / "sources")
    with connect(workspace, create=True) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                format TEXT NOT NULL,
                extractor TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                relative_source TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS segments (
                doc_id TEXT NOT NULL REFERENCES documents(doc_id),
                locator TEXT NOT NULL,
                content TEXT NOT NULL,
                PRIMARY KEY (doc_id, locator)
            );
            CREATE TABLE IF NOT EXISTS claims (
                claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                statement TEXT NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('fact','inference','causal','recommendation')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER NOT NULL REFERENCES claims(claim_id),
                doc_id TEXT NOT NULL,
                locator TEXT NOT NULL,
                quote TEXT NOT NULL,
                relation TEXT NOT NULL CHECK(relation IN ('supports','challenges','context')),
                status TEXT NOT NULL DEFAULT 'unverified'
                    CHECK(status IN ('unverified','verified','disputed','rejected')),
                reviewer TEXT,
                reviewed_at TEXT,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(doc_id, locator) REFERENCES segments(doc_id, locator),
                UNIQUE(claim_id, doc_id, locator, quote, relation)
            );
            PRAGMA user_version = 1;
        """)
    private_file(root / DB_FILE)
    return str(root)


@contextmanager
def connect(workspace: str | Path, *, create=False):
    path = store_path(workspace) / DB_FILE
    if not create and not path.is_file():
        raise EvidenceError("Workspace not initialized; run init WORKSPACE first.")
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0 if create else 1, 1):
            raise EvidenceError(f"Unsupported registry schema version: {version}")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def extract(path: Path):
    """Return (extractor, [(stable_locator, literal_extracted_text), ...])."""
    ext = path.suffix.lower()
    if ext not in FORMATS:
        raise EvidenceError(f"Unsupported format {ext}. Allowed: {', '.join(sorted(FORMATS))}")
    if ext in (".txt", ".md"):
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeError as exc:
            raise EvidenceError("Text must be UTF-8; convert the file before importing.") from exc
        segments = [(f"L{i}", line) for i, line in enumerate(content.splitlines(), 1)]
        extractor = "utf8-lines-v1"
    elif ext == ".csv":
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream)
                segments = [(f"row.{i}", json.dumps(row, ensure_ascii=False))
                            for i, row in enumerate(reader, 1)]
        except UnicodeError as exc:
            raise EvidenceError("CSV must be UTF-8.") from exc
        extractor = "csv-rows-v1"
    elif ext == ".docx":
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        try:
            with zipfile.ZipFile(path) as zf:
                item = zf.getinfo("word/document.xml")
                if item.file_size > MAX_BYTES:
                    raise EvidenceError("DOCX XML exceeds the extraction size limit.")
                root = ET.fromstring(zf.read(item))
            segments = []
            for i, para in enumerate(root.iter(ns + "p"), 1):
                parts = []
                for node in para.iter():
                    if node.tag == ns + "t":
                        parts.append(node.text or "")
                    elif node.tag == ns + "tab":
                        parts.append("\t")
                segments.append((f"para.{i}", "".join(parts)))
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
            raise EvidenceError("Invalid DOCX or missing word/document.xml.") from exc
        extractor = "docx-body-paragraphs-v1"
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise EvidenceError("PDF support requires: python -m pip install '.[pdf]'") from exc
        try:
            reader = PdfReader(str(path), strict=True)
            if reader.is_encrypted:
                raise EvidenceError("Encrypted PDF not supported; use an authorized decrypted copy.")
            if len(reader.pages) > 1000:
                raise EvidenceError("PDF exceeds the 1000-page limit.")
            segments = []
            for i, page in enumerate(reader.pages, 1):
                content = page.extract_text() or ""
                if len(content) > MAX_BYTES:
                    raise EvidenceError("Extracted PDF page exceeds the size limit.")
                segments.append((f"p.{i}", content))
        except EvidenceError:
            raise
        except Exception as exc:
            raise EvidenceError(f"PDF extraction failed: {type(exc).__name__}") from exc
        extractor = "pypdf-pages-v1"
    if len(segments) > MAX_SEGMENTS:
        raise EvidenceError(f"Source exceeds {MAX_SEGMENTS} segments.")
    if not any(text.strip() for _, text in segments):
        raise EvidenceError("Source has no extractable text; scanned PDFs require separate authorized OCR.")
    return extractor, segments


def snapshot_path(workspace, row):
    store = store_path(workspace)
    name = Path(row["relative_source"])
    path = (store / name).resolve()
    if store.resolve() not in path.parents:
        raise EvidenceError("Unsafe stored source path.")
    return path


def document_integrity(workspace, row):
    path = snapshot_path(workspace, row)
    return path.is_file() and digest_file(path) == row["sha256"]


def import_document(workspace: str | Path, filename: str | Path):
    input_path = Path(filename).expanduser()
    if input_path.is_symlink():
        raise EvidenceError("Source symlinks are not accepted.")
    source = input_path.resolve(strict=True)
    if not source.is_file():
        raise EvidenceError("Source must be a regular file, not a symlink.")
    if source.stat().st_size > MAX_BYTES:
        raise EvidenceError("Source exceeds the 30 MiB limit.")
    filehash = digest_file(source)
    doc_id = "D-" + filehash[:16]
    ext = source.suffix.lower()
    with connect(workspace) as conn:
        existing = conn.execute("SELECT * FROM documents WHERE sha256=?", (filehash,)).fetchone()
        if existing:
            if not document_integrity(workspace, existing):
                raise EvidenceError("Existing source snapshot has changed or is missing; audit before reuse.")
            return {"doc_id": existing["doc_id"], "duplicate": True}
        if conn.execute("SELECT 1 FROM documents WHERE doc_id=?", (doc_id,)).fetchone():
            raise EvidenceError("Source ID collision; manual resolution required.")
        temp = store_path(workspace) / "sources" / (uuid.uuid4().hex + ext)
        target = store_path(workspace) / "sources" / (filehash + ext)
        try:
            shutil.copyfile(source, temp)
            private_file(temp)
            if digest_file(temp) != filehash:
                raise EvidenceError("Source changed during copy; import aborted.")
            extractor, segments = extract(temp)
            if target.exists():
                if digest_file(target) != filehash:
                    raise EvidenceError("Existing snapshot target was modified.")
                temp.unlink()
            else:
                os.replace(temp, target)
                private_file(target)
            conn.execute(
                "INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
                (doc_id, filehash, source.name, ext, extractor, now(), str(Path("sources") / target.name)))
            conn.executemany("INSERT INTO segments VALUES (?,?,?)",
                             [(doc_id, locator, content) for locator, content in segments])
        finally:
            if temp.exists():
                temp.unlink()
        return {"doc_id": doc_id, "segments": len(segments), "duplicate": False,
                "snapshot_sha256": filehash}


def list_segments(workspace, doc_id, search=None, locator=None, limit=25):
    with connect(workspace) as conn:
        if locator:
            rows = conn.execute("SELECT locator,content FROM segments WHERE doc_id=? AND locator=?",
                                (doc_id, locator)).fetchall()
        else:
            rows = conn.execute("SELECT locator,content FROM segments WHERE doc_id=? ORDER BY rowid",
                                (doc_id,)).fetchall()
        if not conn.execute("SELECT 1 FROM documents WHERE doc_id=?", (doc_id,)).fetchone():
            raise EvidenceError("Unknown document ID.")
        result = [{"locator": r["locator"], "content": r["content"]} for r in rows]
        if search:
            result = [r for r in result if search in r["content"]]
        if not locator:
            result = result[:limit]
            for r in result:
                if len(r["content"]) > 300:
                    r["content"] = r["content"][:300] + " [preview only; use --locator for full]"
        return result


def add_claim(workspace, question, statement, kind="fact"):
    if kind not in KINDS or not question.strip() or not statement.strip():
        raise EvidenceError("Valid kind, nonempty question and statement are required.")
    with connect(workspace) as conn:
        cursor = conn.execute("INSERT INTO claims(question,statement,kind,created_at) VALUES (?,?,?,?)",
                              (question.strip(), statement.strip(), kind, now()))
        return f"C{cursor.lastrowid:04d}"


def parse_identifier(identifier, prefix):
    if not identifier.startswith(prefix) or not identifier[len(prefix):].isdigit():
        raise EvidenceError(f"Invalid ID: {identifier}")
    return int(identifier[len(prefix):])


def add_evidence(workspace, claim_id, doc_id, locator, quote, relation="supports"):
    if relation not in RELATIONS or not quote.strip():
        raise EvidenceError("Valid relation and nonempty exact quote required.")
    cid = parse_identifier(claim_id, "C")
    with connect(workspace) as conn:
        row = conn.execute("SELECT * FROM documents WHERE doc_id=?", (doc_id,)).fetchone()
        if row is None:
            raise EvidenceError("Unknown document ID.")
        if not document_integrity(workspace, row):
            raise EvidenceError("Source snapshot integrity check failed.")
        segment = conn.execute("SELECT content FROM segments WHERE doc_id=? AND locator=?",
                               (doc_id, locator)).fetchone()
        if segment is None:
            raise EvidenceError("Unknown source locator.")
        if quote not in segment["content"]:
            raise EvidenceError("Quote not found verbatim at locator; no approximate matching.")
        if not conn.execute("SELECT 1 FROM claims WHERE claim_id=?", (cid,)).fetchone():
            raise EvidenceError("Unknown claim ID.")
        try:
            cursor = conn.execute(
                "INSERT INTO evidence(claim_id,doc_id,locator,quote,relation,created_at) VALUES (?,?,?,?,?,?)",
                (cid, doc_id, locator, quote, relation, now()))
        except sqlite3.IntegrityError as exc:
            raise EvidenceError("Evidence link already exists; refusing duplicate.") from exc
        return f"E{cursor.lastrowid:04d}"


def review_evidence(workspace, evidence_id, status, reviewer, note=""):
    if status not in {"verified", "disputed", "rejected"}:
        raise EvidenceError("Review status must be verified, disputed or rejected.")
    if not reviewer.strip() or (status != "verified" and not note.strip()):
        raise EvidenceError("Reviewer required; disputed/rejected reviews require a reason.")
    eid = parse_identifier(evidence_id, "E")
    with connect(workspace) as conn:
        item = conn.execute(
            """SELECT e.*,s.content,d.sha256,d.relative_source FROM evidence e
            JOIN segments s ON e.doc_id=s.doc_id AND e.locator=s.locator
            JOIN documents d ON d.doc_id=e.doc_id WHERE e.evidence_id=?""",
            (eid,)).fetchone()
        if not item:
            raise EvidenceError("Evidence ID not found.")
        if not document_integrity(workspace, item) or item["quote"] not in item["content"]:
            raise EvidenceError("Quote or source snapshot integrity failed; cannot review.")
        conn.execute(
            "UPDATE evidence SET status=?,reviewer=?,reviewed_at=?,note=? WHERE evidence_id=?",
            (status, reviewer.strip(), now(), note.strip(), eid))
        return f"E{eid:04d}"


def audit(workspace):
    issues = []
    with connect(workspace) as conn:
        docs = conn.execute("SELECT * FROM documents ORDER BY doc_id").fetchall()
        claims = conn.execute("SELECT * FROM claims ORDER BY claim_id").fetchall()
        evidence = conn.execute(
            """SELECT e.*,s.content AS segment_content FROM evidence e
            JOIN segments s ON e.doc_id=s.doc_id AND e.locator=s.locator ORDER BY e.evidence_id"""
        ).fetchall()
        for doc in docs:
            if not document_integrity(workspace, doc):
                issues.append({"severity": "error", "code": "source_hash_mismatch",
                               "item": doc["doc_id"]})
        for item in evidence:
            eid = f"E{item['evidence_id']:04d}"
            if item["quote"] not in item["segment_content"]:
                issues.append({"severity": "error", "code": "quote_locator_mismatch", "item": eid})
            if item["status"] == "unverified":
                issues.append({"severity": "warning", "code": "pending_manual_review", "item": eid})
            if item["status"] == "disputed":
                issues.append({"severity": "warning", "code": "disputed_evidence", "item": eid})
            if item["status"] in ("verified", "disputed", "rejected") and not item["reviewer"]:
                issues.append({"severity": "error", "code": "missing_reviewer", "item": eid})
        evidence_counts = {row["claim_id"]: row["total"] for row in conn.execute(
            "SELECT claim_id, COUNT(*) total FROM evidence WHERE status != 'rejected' GROUP BY claim_id"
        )}
        for claim in claims:
            if not evidence_counts.get(claim["claim_id"], 0):
                issues.append({"severity": "warning", "code": "claim_without_evidence",
                               "item": f"C{claim['claim_id']:04d}"})
            if claim["kind"] == "causal":
                issues.append({"severity": "warning", "code": "causal_design_requires_review",
                               "item": f"C{claim['claim_id']:04d}"})
    return {"documents": len(docs), "claims": len(claims), "evidence": len(evidence),
            "ok": not any(i["severity"] == "error" for i in issues), "issues": issues}


def export_registry(workspace, fmt="md", include_quotes=False):
    if fmt not in ("md", "json"):
        raise EvidenceError("Export must be md or json.")
    with connect(workspace) as conn:
        claims = [dict(r) for r in conn.execute("SELECT * FROM claims ORDER BY claim_id")]
        evidence = [dict(r) for r in conn.execute(
            """SELECT evidence_id,claim_id,doc_id,locator,quote,relation,status,reviewer,
               reviewed_at,note FROM evidence ORDER BY evidence_id""")]
        for item in evidence:
            if not include_quotes:
                item.pop("quote")
        report = audit(workspace)
    if fmt == "json":
        return json.dumps({"audit": report, "claims": claims, "evidence": evidence},
                          ensure_ascii=False, indent=2) + "\n"
    def cell(s):
        return str(s or "").replace("\n", " ").replace("|", r"\|")
    out = ["# Evidence register (local research artifact)", "",
           "> Source matching is not research validity. Verified indicates manually reviewed provenance,",
           "> not proven causal inference. Do not publish without checking privacy and authorization.",
           "", f"Sources: {report['documents']} · Claims: {report['claims']} · Evidence: {report['evidence']}",
           "", "| Claim | Question | Statement | Type |", "|---|---|---|---|"]
    for c in claims:
        out.append(f"| C{c['claim_id']:04d} | {cell(c['question'])} | {cell(c['statement'])} | {c['kind']} |")
    out += ["", "| Evidence | Claim | Source | Locator | Relation | Review status |",
            "|---|---|---|---|---|---|"]
    for e in evidence:
        out.append(f"| E{e['evidence_id']:04d} | C{e['claim_id']:04d} | {e['doc_id']} | "
                   f"{cell(e['locator'])} | {e['relation']} | {e['status']} |")
        if include_quotes:
            out.append(f"\n> E{e['evidence_id']:04d} excerpt: {cell(e['quote'])}\n")
    out += ["", "## Integrity and research gaps"]
    for issue in report["issues"]:
        out.append(f"- {issue['severity']}: {issue['code']} — {issue['item']}")
    if not report["issues"]:
        out.append("- No registry-level issues found; this does not prove claim validity.")
    return "\n".join(out) + "\n"
