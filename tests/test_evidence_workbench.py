"""Behavioral tests with synthetic case-study material only."""
import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

# Import from the single canonical Skill-bundled package (not from a root duplicate).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "mpa-skill" / "scripts"))
from evidence_workbench import core
from evidence_workbench.cli import main


class TestEvidenceWorkbench(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ws = self.root / "workspace"
        core.initialize(self.ws)

    def source(self, name, text):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_exact_quote_and_review_status(self):
        d = core.import_document(self.ws, self.source("case.md", "政策启动\n居民尚未表态\n"))
        self.assertTrue(core.import_document(self.ws, self.root / "case.md")["duplicate"])
        c = core.add_claim(self.ws, "是否协同？", "政策已启动")
        with self.assertRaisesRegex(core.EvidenceError, "verbatim"):
            core.add_evidence(self.ws, c, d["doc_id"], "L1", "协同已经成功")
        eid = core.add_evidence(self.ws, c, d["doc_id"], "L1", "政策启动")
        self.assertIn("pending_manual_review", [x["code"] for x in core.audit(self.ws)["issues"]])
        self.assertEqual(json.loads(core.export_registry(self.ws, "json"))["evidence"][0]["status"], "unverified")
        core.review_evidence(self.ws, eid, "verified", "R1", "Checked quote")
        report = core.audit(self.ws)
        self.assertTrue(report["ok"])
        self.assertNotIn("pending_manual_review", [x["code"] for x in report["issues"]])
        data = json.loads(core.export_registry(self.ws, "json"))
        self.assertNotIn("quote", data["evidence"][0])
        self.assertNotIn(str(self.root), core.export_registry(self.ws, "json"))

    def test_source_tamper_cannot_be_silently_verified(self):
        source = self.source("agency.txt", "政策调整方案。\n")
        d = core.import_document(self.ws, source)
        c = core.add_claim(self.ws, "政策情况", "政策有调整方案")
        e = core.add_evidence(self.ws, c, d["doc_id"], "L1", "政策调整方案")
        with core.connect(self.ws) as conn:
            row = conn.execute("SELECT * FROM documents WHERE doc_id=?", (d["doc_id"],)).fetchone()
            p = core.snapshot_path(self.ws, row)
        p.write_text("篡改", encoding="utf-8")
        self.assertFalse(core.audit(self.ws)["ok"])
        self.assertIn("source_hash_mismatch", [x["code"] for x in core.audit(self.ws)["issues"]])
        with self.assertRaisesRegex(core.EvidenceError, "integrity"):
            core.review_evidence(self.ws, e, "verified", "R1")
        with self.assertRaises(core.EvidenceError):
            core.import_document(self.ws, source)

    def test_conflicting_accounts_and_rival_evidence(self):
        a = core.import_document(self.ws, self.source("official.txt", "部门称已协商。\n"))
        b = core.import_document(self.ws, self.source("resident.txt", "居民称未参与。\n"))
        c = core.add_claim(self.ws, "公众参与情况", "各方参与协商", "inference")
        first = core.add_evidence(self.ws, c, a["doc_id"], "L1", "已协商")
        second = core.add_evidence(self.ws, c, b["doc_id"], "L1", "未参与", "challenges")
        with self.assertRaises(core.EvidenceError):
            core.review_evidence(self.ws, second, "disputed", "R1")
        core.review_evidence(self.ws, first, "verified", "R1")
        core.review_evidence(self.ws, second, "disputed", "R1", "Contradiction unresolved")
        self.assertIn("disputed_evidence", [x["code"] for x in core.audit(self.ws)["issues"]])
        self.assertEqual([x["relation"] for x in json.loads(core.export_registry(self.ws, "json"))["evidence"]],
                         ["supports", "challenges"])

    def test_docx_csv_and_versioning(self):
        docx = self.root / "meeting.docx"
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:body><w:p><w:r><w:t>会议记录甲</w:t></w:r></w:p></w:body></w:document>')
        with zipfile.ZipFile(docx, "w") as zf:
            zf.writestr("word/document.xml", xml)
        d = core.import_document(self.ws, docx)
        self.assertIn("记录甲", core.list_segments(self.ws, d["doc_id"], locator="para.1")[0]["content"])
        p = self.source("data.csv", "group,value\nA,支持\nB,反对\n")
        first = core.import_document(self.ws, p)
        self.assertIn("反对", core.list_segments(self.ws, first["doc_id"], locator="row.3")[0]["content"])
        p.write_text("group,value\nB,反对\n", encoding="utf-8")
        second = core.import_document(self.ws, p)
        self.assertNotEqual(first["doc_id"], second["doc_id"])

    def test_cli_export_guard(self):
        p = self.source("policy.txt", "项目启动\n")
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(["ingest", str(self.ws), str(p)]), 0)
        doc = json.loads(stdout.getvalue())["doc_id"]
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(["claim", str(self.ws), "--question", "发生了什么",
                                   "--statement", "项目启动"]), 0)
        cid = json.loads(stdout.getvalue())["claim_id"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["cite", str(self.ws), "--claim", cid, "--document", doc,
                                   "--locator", "L1", "--quote", "项目启动"]), 0)
        output = self.root / "evidence.md"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["export", str(self.ws), "--output", str(output)]), 0)
        self.assertNotIn("excerpt: 项目启动", output.read_text(encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["export", str(self.ws), "--output", str(output)]), 2)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["export", str(self.ws), "--output", str(output),
                                   "--overwrite", "--include-quotes"]), 0)
        self.assertIn("excerpt: 项目启动", output.read_text(encoding="utf-8"))

    def test_reject_empty_and_flag_causality(self):
        with self.assertRaisesRegex(core.EvidenceError, "no extractable text"):
            core.import_document(self.ws, self.source("empty.txt", "\n"))
        core.add_claim(self.ws, "政策是否有效", "政策导致结果改变", "causal")
        flags = {x["code"] for x in core.audit(self.ws)["issues"]}
        self.assertIn("causal_design_requires_review", flags)
        self.assertIn("claim_without_evidence", flags)

    def test_scanned_pdf_not_fake_success(self):
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest("Optional pypdf not installed")
        writer = PdfWriter()
        writer.add_blank_page(width=80, height=80)
        p = self.root / "scanned.pdf"
        with p.open("wb") as fp:
            writer.write(fp)
        with self.assertRaisesRegex(core.EvidenceError, "no extractable text"):
            core.import_document(self.ws, p)


if __name__ == "__main__":
    unittest.main()
