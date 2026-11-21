"""Diagnostics: a failed command must say what to do next.

The registry never relaxes matching. These tests only pin the messages an agent
or student needs to recover from the three most common dead ends: an unguessable
document ID, a quote taken from the wrong locator, and a near-verbatim quote.
All sources are synthetic.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "mpa-skill" / "scripts"))
from evidence_workbench import core
from evidence_workbench.cli import main


class TestDiagnostics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ws = self.root / "workspace"
        core.initialize(self.ws)
        self.source = self.root / "case.md"
        self.source.write_text("政策目标为改善服务。\n实施记录尚缺失。\n", encoding="utf-8")
        self.doc_id = core.import_document(self.ws, self.source)["doc_id"]
        self.claim = core.add_claim(self.ws, "政策是否落实", "文件提出服务目标")

    def cli(self, *args, expected=0):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([str(arg) for arg in args])
        self.assertEqual(code, expected, err.getvalue())
        return json.loads(out.getvalue()) if code == 0 else err.getvalue()

    # ── fix 5: unguessable content-derived document IDs ─────────────────────

    def test_unknown_document_lists_registered_ids(self):
        with self.assertRaises(core.EvidenceError) as caught:
            core.list_segments(self.ws, "D-0000000000000000")
        message = str(caught.exception)
        self.assertIn("D-0000000000000000", message)
        self.assertIn(self.doc_id, message)
        self.assertIn("Registered documents", message)
        self.assertIn("case.md", message)

    def test_unknown_document_on_empty_workspace_suggests_ingest(self):
        empty = self.root / "empty"
        core.initialize(empty)
        with self.assertRaises(core.EvidenceError) as caught:
            core.add_evidence(empty, "C0001", "D-deadbeef", "L1", "任意")
        message = str(caught.exception)
        self.assertIn("Unknown document ID", message)
        self.assertIn("ingest", message)

    def test_cli_exit_two_and_stderr_carry_the_hint(self):
        stderr = self.cli("segments", self.ws, "D-0000000000000000", expected=2)
        self.assertIn(self.doc_id, stderr)

    # ── fix 4: cite failures explain themselves, matching stays exact ───────

    def test_quote_at_another_locator_names_that_locator(self):
        with self.assertRaises(core.EvidenceError) as caught:
            core.add_evidence(self.ws, self.claim, self.doc_id, "L2", "政策目标为改善服务。")
        message = str(caught.exception)
        self.assertIn("verbatim at L1", message)
        self.assertIn("not at L2", message)

    def test_near_verbatim_quote_shows_the_extra_characters(self):
        with self.assertRaises(core.EvidenceError) as caught:
            core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "政策目标为改善服务。。")
        message = str(caught.exception)
        self.assertIn("extra character", message)
        self.assertIn("政策目标为改善服务", message)
        # Still exact: the near miss must not be stored.
        self.assertEqual(core.audit(self.ws)["evidence"], 0)

    def test_unrelated_quote_sends_the_researcher_back_to_the_segment(self):
        with self.assertRaises(core.EvidenceError) as caught:
            core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "完全不同的表述内容")
        message = str(caught.exception)
        self.assertIn("segments", message)
        self.assertIn(self.doc_id, message)
        self.assertIn("--locator L1", message)
        self.assertIn(str(self.ws.resolve()), message, "hint must be runnable as printed")

    def test_normalized_quote_still_works_and_needs_no_hint(self):
        evidence = core.add_evidence(self.ws, self.claim, self.doc_id, "L1",
                                     "政策目标为改善服务。", normalized=True)
        self.assertEqual(evidence, "E0001")

    # ── fix 3: audit as a scripted gate ─────────────────────────────────────

    def test_audit_defaults_to_integrity_errors_only(self):
        core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "政策目标为改善服务。")
        report = core.audit(self.ws)
        self.assertTrue(report["ok"])
        self.assertFalse(report["strict"])
        self.assertEqual(report["counts"]["error"], 0)
        self.assertGreaterEqual(report["counts"]["warning"], 1)
        self.cli("audit", self.ws)

    def test_audit_strict_fails_on_unresolved_warnings(self):
        core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "政策目标为改善服务。")
        lenient, strict = core.audit(self.ws), core.audit(self.ws, strict=True)
        self.assertEqual(lenient["counts"], strict["counts"])
        self.assertTrue(lenient["ok"])
        self.assertFalse(strict["ok"])
        self.cli("audit", self.ws, "--strict", expected=2)

    def test_audit_strict_passes_after_human_verification(self):
        evidence = core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "政策目标为改善服务。")
        self.assertFalse(core.audit(self.ws, strict=True)["ok"])
        core.review_evidence(self.ws, evidence, "verified", "R1", "Compared with the original")
        report = core.audit(self.ws, strict=True)
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"], {"error": 0, "warning": 0, "info": 0})
        self.cli("audit", self.ws, "--strict")

    def test_audit_strict_still_reports_integrity_errors(self):
        core.add_evidence(self.ws, self.claim, self.doc_id, "L1", "政策目标为改善服务。")
        with core.connect(self.ws) as conn:
            row = conn.execute("SELECT * FROM documents WHERE doc_id=?", (self.doc_id,)).fetchone()
            snapshot = core.snapshot_path(self.ws, row)
        snapshot.write_text("篡改", encoding="utf-8")
        report = core.audit(self.ws, strict=True)
        self.assertFalse(report["ok"])
        self.assertIn("source_hash_mismatch", [issue["code"] for issue in report["issues"]])
        self.assertGreaterEqual(report["counts"]["error"], 1)

    # ── fix 1: an honest interpreter report ─────────────────────────────────

    def test_doctor_states_supported_minimum_and_usability_separately(self):
        result = self.cli("doctor")
        self.assertEqual(result["python_minimum"], "3.10")
        self.assertTrue(result["python_usable"])
        self.assertEqual(result["python_supported"], sys.version_info >= (3, 10))
        self.assertEqual(bool(result["warnings"]), not result["python_supported"])
        self.assertIn("python_status", result)
        if not result["python_supported"]:
            self.assertIn("untested", result["warnings"][0])


if __name__ == "__main__":
    unittest.main()
