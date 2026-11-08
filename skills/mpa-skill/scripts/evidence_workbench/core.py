"""Offline, source-linked evidence registry for public-management case research.

No model calls, uploads, authentication, or background tasks. Local copies of
original sources and extracted text contain potentially sensitive information.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import unicodedata
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
SCHEMA_VERSION = 2
MAX_RANGE_SEGMENTS = 20
SPINE_LINKS = ("problem", "stakeholders", "institutions", "theory", "evidence",
               "method", "analysis", "recommendation")
SPINE_STATUSES = {"missing", "partial", "established", "out_of_scope"}


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


SCHEMA_SQL = """
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
    created_at TEXT NOT NULL,
    rival_of INTEGER REFERENCES claims(claim_id)
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
    locator_end TEXT,
    match_mode TEXT NOT NULL DEFAULT 'exact',
    FOREIGN KEY(doc_id, locator) REFERENCES segments(doc_id, locator),
    UNIQUE(claim_id, doc_id, locator, quote, relation)
);
CREATE TABLE IF NOT EXISTS spine_progress (
    link TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','done')),
    is_next INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    done_at TEXT
);
"""


def migrate(conn, version):
    """Upgrade an existing registry in place without rewriting recorded evidence."""
    if version == 1:
        conn.execute("ALTER TABLE claims ADD COLUMN rival_of INTEGER REFERENCES claims(claim_id)")
        conn.execute("ALTER TABLE evidence ADD COLUMN locator_end TEXT")
        conn.execute("ALTER TABLE evidence ADD COLUMN match_mode TEXT NOT NULL DEFAULT 'exact'")
        conn.executescript(SCHEMA_SQL)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()


def initialize(workspace: str | Path):
    root = store_path(workspace)
    private_dir(root)
    private_dir(root / "sources")
    with connect(workspace, create=True) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
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
        if version == 1:
            migrate(conn, version)
        elif version not in ((0, SCHEMA_VERSION) if create else (SCHEMA_VERSION,)):
            raise EvidenceError(f"Unsupported registry schema version: {version}")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx_text(node):
    parts = []
    for item in node.iter():
        if item.tag == W_NS + "t":
            parts.append(item.text or "")
        elif item.tag == W_NS + "tab":
            parts.append("\t")
    return "".join(parts)


def _docx_xml(zf, name):
    item = zf.getinfo(name)
    if item.file_size > MAX_BYTES:
        raise EvidenceError("DOCX XML exceeds the extraction size limit.")
    return ET.fromstring(zf.read(item))


def _docx_segments(path: Path):
    """Body paragraphs as para.N; footnotes as fn.N and endnotes as en.N (Word note IDs)."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            root = _docx_xml(zf, "word/document.xml")
            segments = [(f"para.{i}", _docx_text(para))
                        for i, para in enumerate(root.iter(W_NS + "p"), 1)]
            for part, tag, prefix in (("word/footnotes.xml", "footnote", "fn"),
                                      ("word/endnotes.xml", "endnote", "en")):
                if part not in names:
                    continue
                for note in _docx_xml(zf, part).iter(W_NS + tag):
                    if note.get(W_NS + "type") in ("separator", "continuationSeparator",
                                                    "continuationNotice"):
                        continue
                    note_id = note.get(W_NS + "id", "")
                    if not note_id.isdigit() or int(note_id) <= 0:
                        continue
                    text = "\n".join(_docx_text(p) for p in note.iter(W_NS + "p")).strip()
                    if text:
                        segments.append((f"{prefix}.{note_id}", text))
            return segments
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise EvidenceError("Invalid DOCX or missing word/document.xml.") from exc


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
        segments = _docx_segments(path)
        extractor = "docx-body-notes-v2"
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


def add_claim(workspace, question, statement, kind="fact", rival_of=None):
    if kind not in KINDS or not question.strip() or not statement.strip():
        raise EvidenceError("Valid kind, nonempty question and statement are required.")
    with connect(workspace) as conn:
        rival = None
        if rival_of:
            rival = parse_identifier(rival_of, "C")
            if not conn.execute("SELECT 1 FROM claims WHERE claim_id=?", (rival,)).fetchone():
                raise EvidenceError("Unknown claim ID for --rival-of.")
        cursor = conn.execute(
            "INSERT INTO claims(question,statement,kind,created_at,rival_of) VALUES (?,?,?,?,?)",
            (question.strip(), statement.strip(), kind, now(), rival))
        return f"C{cursor.lastrowid:04d}"


def parse_identifier(identifier, prefix):
    if not identifier.startswith(prefix) or not identifier[len(prefix):].isdigit():
        raise EvidenceError(f"Invalid ID: {identifier}")
    return int(identifier[len(prefix):])


# ── locators and quote matching ─────────────────────────────────────────────

_LOCATOR = re.compile(r"^(.*?)(\d+)$")


def split_range(locator):
    """'L12-L14' / 'L12-14' / 'p.3-p.4' -> (start, end); single locator -> (locator, None)."""
    if "-" not in locator:
        return locator, None
    start, end = locator.split("-", 1)
    m_start = _LOCATOR.match(start)
    if not m_start or not end:
        raise EvidenceError(f"Invalid locator range: {locator}")
    if end.isdigit():
        end = m_start.group(1) + end
    m_end = _LOCATOR.match(end)
    if not m_end or m_end.group(1) != m_start.group(1):
        raise EvidenceError("A locator range must stay within one locator type, e.g. L12-L14.")
    if int(m_end.group(2)) <= int(m_start.group(2)):
        raise EvidenceError("Locator range end must come after its start.")
    return start, end


def format_locator(start, end):
    return f"{start}-{end}" if end else start


def segment_text(conn, doc_id, start, end=None):
    """Exact stored text at a locator, or consecutive segments joined by newlines."""
    row = conn.execute("SELECT rowid, content FROM segments WHERE doc_id=? AND locator=?",
                       (doc_id, start)).fetchone()
    if row is None:
        raise EvidenceError("Unknown source locator.")
    if end is None:
        return row["content"]
    last = conn.execute("SELECT rowid FROM segments WHERE doc_id=? AND locator=?",
                        (doc_id, end)).fetchone()
    if last is None:
        raise EvidenceError("Unknown source locator at range end.")
    rows = conn.execute(
        "SELECT locator, content FROM segments WHERE doc_id=? AND rowid BETWEEN ? AND ? ORDER BY rowid",
        (doc_id, row["rowid"], last["rowid"])).fetchall()
    prefix = _LOCATOR.match(start).group(1)
    if len(rows) > MAX_RANGE_SEGMENTS:
        raise EvidenceError(f"Locator ranges are limited to {MAX_RANGE_SEGMENTS} segments.")
    if any(_LOCATOR.match(r["locator"]).group(1) != prefix for r in rows):
        raise EvidenceError("Locator range crosses a different locator type.")
    return "\n".join(r["content"] for r in rows)


def _normalized_with_map(text):
    """NFKC-normalize and drop whitespace; return (normalized, index map to original)."""
    chars, index = [], []
    for i, ch in enumerate(text):
        for n in unicodedata.normalize("NFKC", ch):
            if not n.isspace():
                chars.append(n)
                index.append(i)
    return "".join(chars), index


def find_source_span(text, quote):
    """Locate quote ignoring whitespace and full/half-width differences.

    Returns the verbatim source span (so the registry always stores real source
    text), or None. Used only when the researcher opts in with --normalized.
    """
    norm_text, index = _normalized_with_map(text)
    norm_quote, _ = _normalized_with_map(quote)
    if not norm_quote:
        return None
    pos = norm_text.find(norm_quote)
    if pos < 0:
        return None
    return text[index[pos]:index[pos + len(norm_quote) - 1] + 1]


def add_evidence(workspace, claim_id, doc_id, locator, quote, relation="supports",
                 normalized=False):
    if relation not in RELATIONS or not quote.strip():
        raise EvidenceError("Valid relation and nonempty exact quote required.")
    cid = parse_identifier(claim_id, "C")
    start, end = split_range(locator)
    with connect(workspace) as conn:
        row = conn.execute("SELECT * FROM documents WHERE doc_id=?", (doc_id,)).fetchone()
        if row is None:
            raise EvidenceError("Unknown document ID.")
        if not document_integrity(workspace, row):
            raise EvidenceError("Source snapshot integrity check failed.")
        text = segment_text(conn, doc_id, start, end)
        mode = "exact"
        if quote not in text:
            span = find_source_span(text, quote)
            if span is None:
                raise EvidenceError("Quote not found verbatim at locator; no approximate matching.")
            if not normalized:
                raise EvidenceError(
                    "Quote not found verbatim at locator. It matches only after ignoring "
                    "whitespace/full-width differences; rerun with --normalized to record the "
                    "verbatim source span instead.")
            quote, mode = span, "normalized"
        if not conn.execute("SELECT 1 FROM claims WHERE claim_id=?", (cid,)).fetchone():
            raise EvidenceError("Unknown claim ID.")
        try:
            cursor = conn.execute(
                """INSERT INTO evidence(claim_id,doc_id,locator,locator_end,quote,relation,
                   match_mode,created_at) VALUES (?,?,?,?,?,?,?,?)""",
                (cid, doc_id, start, end, quote, relation, mode, now()))
        except sqlite3.IntegrityError as exc:
            raise EvidenceError("Evidence link already exists; refusing duplicate.") from exc
        return f"E{cursor.lastrowid:04d}"


def _evidence_matches(conn, item):
    try:
        text = segment_text(conn, item["doc_id"], item["locator"], item["locator_end"])
    except EvidenceError:
        return False
    return item["quote"] in text


def review_evidence(workspace, evidence_id, status, reviewer, note=""):
    if status not in {"verified", "disputed", "rejected"}:
        raise EvidenceError("Review status must be verified, disputed or rejected.")
    if not reviewer.strip() or (status != "verified" and not note.strip()):
        raise EvidenceError("Reviewer required; disputed/rejected reviews require a reason.")
    eid = parse_identifier(evidence_id, "E")
    with connect(workspace) as conn:
        item = conn.execute(
            """SELECT e.*,d.sha256,d.relative_source FROM evidence e
            JOIN documents d ON d.doc_id=e.doc_id WHERE e.evidence_id=?""",
            (eid,)).fetchone()
        if not item:
            raise EvidenceError("Evidence ID not found.")
        if not document_integrity(workspace, item) or not _evidence_matches(conn, item):
            raise EvidenceError("Quote or source snapshot integrity failed; cannot review.")
        conn.execute(
            "UPDATE evidence SET status=?,reviewer=?,reviewed_at=?,note=? WHERE evidence_id=?",
            (status, reviewer.strip(), now(), note.strip(), eid))
        return f"E{eid:04d}"


# ── audit and export ────────────────────────────────────────────────────────

def audit(workspace):
    issues = []
    with connect(workspace) as conn:
        docs = conn.execute("SELECT * FROM documents ORDER BY doc_id").fetchall()
        claims = conn.execute("SELECT * FROM claims ORDER BY claim_id").fetchall()
        evidence = conn.execute("SELECT * FROM evidence ORDER BY evidence_id").fetchall()
        for doc in docs:
            if not document_integrity(workspace, doc):
                issues.append({"severity": "error", "code": "source_hash_mismatch",
                               "item": doc["doc_id"]})
        for item in evidence:
            eid = f"E{item['evidence_id']:04d}"
            if not _evidence_matches(conn, item):
                issues.append({"severity": "error", "code": "quote_locator_mismatch", "item": eid})
            if item["status"] == "unverified":
                issues.append({"severity": "warning", "code": "pending_manual_review", "item": eid})
            if item["status"] == "disputed":
                issues.append({"severity": "warning", "code": "disputed_evidence", "item": eid})
            if item["status"] in ("verified", "disputed", "rejected") and not item["reviewer"]:
                issues.append({"severity": "error", "code": "missing_reviewer", "item": eid})
            if item["match_mode"] == "normalized" and item["status"] == "unverified":
                issues.append({"severity": "info", "code": "normalized_match_check_context",
                               "item": eid})
        evidence_counts = {row["claim_id"]: row["total"] for row in conn.execute(
            "SELECT claim_id, COUNT(*) total FROM evidence WHERE status != 'rejected' GROUP BY claim_id"
        )}
        rivals = {}
        for claim in claims:
            if claim["rival_of"]:
                rivals.setdefault(claim["rival_of"], []).append(claim["claim_id"])
        for claim in claims:
            cid = claim["claim_id"]
            label = f"C{cid:04d}"
            if not evidence_counts.get(cid, 0):
                code = "rival_untested" if claim["rival_of"] else "claim_without_evidence"
                issues.append({"severity": "warning", "code": code, "item": label})
            if claim["kind"] == "causal":
                issues.append({"severity": "warning", "code": "causal_design_requires_review",
                               "item": label})
                if not claim["rival_of"] and not rivals.get(cid):
                    issues.append({"severity": "warning", "code": "no_rival_explanation",
                                   "item": label})
    return {"documents": len(docs), "claims": len(claims), "evidence": len(evidence),
            "ok": not any(i["severity"] == "error" for i in issues), "issues": issues}


def export_registry(workspace, fmt="md", include_quotes=False, redactor=None):
    if fmt not in ("md", "json"):
        raise EvidenceError("Export must be md or json.")
    with connect(workspace) as conn:
        claims = []
        for r in conn.execute("SELECT * FROM claims ORDER BY claim_id"):
            c = dict(r)
            c["rival_of"] = f"C{c['rival_of']:04d}" if c["rival_of"] else None
            claims.append(c)
        evidence = []
        for r in conn.execute(
                """SELECT evidence_id,claim_id,doc_id,locator,locator_end,quote,relation,
                   match_mode,status,reviewer,reviewed_at,note FROM evidence ORDER BY evidence_id"""):
            e = dict(r)
            e["locator"] = format_locator(e.pop("locator"), e.pop("locator_end"))
            if not include_quotes:
                e.pop("quote")
            evidence.append(e)
        report = audit(workspace)
    if redactor is not None:
        claims = redactor.apply(claims)
        evidence = redactor.apply(evidence)
    if fmt == "json":
        payload = {"audit": report, "claims": claims, "evidence": evidence}
        if redactor is not None:
            payload["redaction"] = redactor.summary()
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    def cell(s):
        return str(s or "").replace("\n", " ").replace("|", r"\|")
    out = ["# Evidence register (local research artifact)", "",
           "> Source matching is not research validity. Verified indicates manually reviewed provenance,",
           "> not proven causal inference. Do not publish without checking privacy and authorization.",
           "", f"Sources: {report['documents']} · Claims: {report['claims']} · Evidence: {report['evidence']}",
           ""]
    if redactor is not None:
        out += [f"> Redacted export: {redactor.summary()['replacements']} replacement(s). "
                "Automatic patterns are a safety net, not a guarantee; review before sharing.", ""]
    out += ["| Claim | Question | Statement | Type | Rival of |", "|---|---|---|---|---|"]
    for c in claims:
        out.append(f"| C{c['claim_id']:04d} | {cell(c['question'])} | {cell(c['statement'])} | "
                   f"{c['kind']} | {c['rival_of'] or ''} |")
    out += ["", "| Evidence | Claim | Source | Locator | Relation | Match | Review status |",
            "|---|---|---|---|---|---|---|"]
    for e in evidence:
        out.append(f"| E{e['evidence_id']:04d} | C{e['claim_id']:04d} | {e['doc_id']} | "
                   f"{cell(e['locator'])} | {e['relation']} | {e['match_mode']} | {e['status']} |")
        if include_quotes:
            out.append(f"\n> E{e['evidence_id']:04d} excerpt: {cell(e['quote'])}\n")
    out += ["", "## Integrity and research gaps"]
    for issue in report["issues"]:
        out.append(f"- {issue['severity']}: {issue['code']} — {issue['item']}")
    if not report["issues"]:
        out.append("- No registry-level issues found; this does not prove claim validity.")
    return "\n".join(out) + "\n"


# ── research progress (MPA Research Spine) ─────────────────────────────────

def progress(workspace, set_links=None, note="", todo=None, done=None, next_task=None):
    """Read or update persistent research progress so short sessions can resume."""
    with connect(workspace) as conn:
        for item in set_links or []:
            if "=" not in item:
                raise EvidenceError("Use --set LINK=STATUS, e.g. --set evidence=partial.")
            link, status = (x.strip() for x in item.split("=", 1))
            if link not in SPINE_LINKS:
                raise EvidenceError(f"Unknown spine link {link}. Use: {', '.join(SPINE_LINKS)}")
            if status not in SPINE_STATUSES:
                raise EvidenceError(f"Unknown status {status}. Use: {', '.join(sorted(SPINE_STATUSES))}")
            conn.execute(
                """INSERT INTO spine_progress(link,status,note,updated_at) VALUES (?,?,?,?)
                ON CONFLICT(link) DO UPDATE SET status=excluded.status, note=excluded.note,
                updated_at=excluded.updated_at""", (link, status, note.strip(), now()))
        if todo:
            if not todo.strip():
                raise EvidenceError("Task text must be nonempty.")
            conn.execute("INSERT INTO tasks(text,created_at) VALUES (?,?)", (todo.strip(), now()))
        if done:
            tid = parse_identifier(done, "T")
            if conn.execute("UPDATE tasks SET status='done', is_next=0, done_at=? WHERE task_id=?",
                            (now(), tid)).rowcount == 0:
                raise EvidenceError("Task ID not found.")
        if next_task:
            tid = parse_identifier(next_task, "T")
            row = conn.execute("SELECT status FROM tasks WHERE task_id=?", (tid,)).fetchone()
            if row is None or row["status"] != "open":
                raise EvidenceError("Next task must be an existing open task.")
            conn.execute("UPDATE tasks SET is_next=0")
            conn.execute("UPDATE tasks SET is_next=1 WHERE task_id=?", (tid,))
        stored = {r["link"]: dict(r) for r in conn.execute("SELECT * FROM spine_progress")}
        spine = [{"link": link, "status": stored.get(link, {}).get("status", "missing"),
                  "note": stored.get(link, {}).get("note", ""),
                  "updated_at": stored.get(link, {}).get("updated_at")} for link in SPINE_LINKS]
        tasks = [{"task_id": f"T{r['task_id']:04d}", "text": r["text"], "next": bool(r["is_next"])}
                 for r in conn.execute("SELECT * FROM tasks WHERE status='open' ORDER BY task_id")]
        finished = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='done'").fetchone()[0]
    suggested = next((t for t in tasks if t["next"]), None) or (tasks[0] if tasks else None)
    if suggested:
        suggestion = {"type": "task", **suggested}
    else:
        gap = next((s for s in spine if s["status"] in ("missing", "partial")), None)
        suggestion = ({"type": "spine_gap", "link": gap["link"], "status": gap["status"]}
                      if gap else None)
    return {"spine": spine, "open_tasks": tasks, "done_tasks": finished,
            "suggested_next": suggestion}
