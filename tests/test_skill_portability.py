"""Portable installation acceptance: only the shipped Skill directory is present.

Run with the repository test suite, but every subprocess executes from a temporary
copy of the installed Skill folder, with site-packages and PYTHONPATH disabled.
All sources and claims are synthetic.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestPortableSkill(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        repo = Path(__file__).resolve().parents[1]
        self.installed = self.root / "isolated install" / "mpa-skill"
        shutil.copytree(repo / "skills" / "mpa-skill", self.installed)
        self.entry = self.installed / "scripts" / "mpa_evidence.py"
        self.workspace = self.root / "private workspace"
        self.source = self.root / "public policy sample.txt"
        self.source.write_text("政策目标为改善服务。\n实施记录尚缺失。\n", encoding="utf-8")
        self.other_cwd = self.root / "unrelated cwd"
        self.other_cwd.mkdir()
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = ""
        self.env["PYTHONIOENCODING"] = "utf-8"

    def run_cli(self, *args, expected=0):
        p = subprocess.run(
            [sys.executable, "-S", str(self.entry), *map(str, args)],
            cwd=self.other_cwd, env=self.env, text=True, encoding="utf-8",
            capture_output=True, timeout=30,
        )
        self.assertEqual(p.returncode, expected,
                         f"exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}")
        return json.loads(p.stdout) if expected == 0 else p.stderr

    def test_self_contained_startup_doctor_and_case_lifecycle(self):
        # Source is not in the original repository or installed globally.
        self.assertTrue(self.entry.is_file())
        self.assertFalse((self.installed / "evidence_workbench").exists())
        doctor = self.run_cli("doctor", "--workspace", self.workspace)
        self.assertTrue(doctor["python_supported"])
        self.assertTrue(doctor["sqlite_available"])
        self.assertFalse(doctor["workspace_initialized"])
        self.assertTrue(doctor["read_only"])
        self.assertFalse(self.workspace.exists(), "Doctor must not create workspace")
        self.assertEqual(doctor["text_formats"], [".txt", ".md", ".csv", ".docx"])

        init = self.run_cli("init", self.workspace)
        self.assertTrue(Path(init["registry"]).is_dir())
        self.assertTrue(self.run_cli("doctor", "--workspace", self.workspace)["workspace_initialized"])
        doc = self.run_cli("ingest", self.workspace, self.source)
        self.assertFalse(doc["duplicate"])
        doc_id = doc["doc_id"]
        self.assertEqual(len(doc["snapshot_sha256"]), 64)
        self.assertIn("政策目标", self.run_cli("segments", self.workspace, doc_id, "--locator", "L1")[0]["content"])

        claim = self.run_cli(
            "claim", self.workspace, "--question", "政策是否落实",
            "--statement", "文件提出服务目标", "--kind", "fact"
        )["claim_id"]
        evidence = self.run_cli(
            "cite", self.workspace, "--claim", claim, "--document", doc_id,
            "--locator", "L1", "--quote", "改善服务", "--relation", "supports",
        )["evidence_id"]
        audit = self.run_cli("audit", self.workspace, "--json")
        self.assertIn("pending_manual_review", [issue["code"] for issue in audit["issues"]])
        out = self.root / "evidence-matrix.md"
        self.run_cli("export", self.workspace, "--output", out)
        exported = out.read_text(encoding="utf-8")
        self.assertIn(doc_id, exported)
        self.assertIn("unverified", exported)
        self.assertNotIn("excerpt: 改善服务", exported)

        # This action simulates a researcher's explicitly commanded confirmation;
        # the production Skill must never decide to verify on its own.
        self.run_cli("review", self.workspace, evidence, "--status", "verified",
                     "--reviewer", "test-researcher", "--note", "checked original")
        audit = self.run_cli("audit", self.workspace)
        self.assertNotIn("pending_manual_review", [issue["code"] for issue in audit["issues"]])
        self.assertFalse(any(self.installed.rglob("registry.sqlite3")),
                         "The install directory must not store user data")

    def test_wrong_quote_rejected_without_side_effect(self):
        self.run_cli("init", self.workspace)
        doc = self.run_cli("ingest", self.workspace, self.source)["doc_id"]
        claim = self.run_cli(
            "claim", self.workspace, "--question", "政策落实",
            "--statement", "协同成功"
        )["claim_id"]
        error = self.run_cli(
            "cite", self.workspace, "--claim", claim, "--document", doc,
            "--locator", "L1", "--quote", "协同成功", expected=2
        )
        self.assertIn("Quote not found verbatim", error)
        self.assertEqual(self.run_cli("audit", self.workspace)["evidence"], 0)

    def test_installed_guidance_prevents_model_self_verification(self):
        skill = (self.installed / "SKILL.md").read_text(encoding="utf-8")
        guide = (self.installed / "references" / "evidence-workbench-usage.md").read_text(encoding="utf-8")
        self.assertIn("doctor", skill)
        self.assertIn("Never run", skill)
        self.assertIn("Only after the researcher explicitly reports", guide)
        self.assertIn("no terminal", guide.lower())


if __name__ == "__main__":
    unittest.main()
