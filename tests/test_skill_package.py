"""Cross-client package contract and isolated ZIP execution checks."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "tools" / "package_skill.py"
spec = importlib.util.spec_from_file_location("package_skill", script)
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class TestSkillPackage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "mpa research skill.zip"
        result, count = packager.package(self.path)
        self.assertEqual(result.name, self.path.name)
        self.assertTrue(result.is_file())
        self.assertGreater(count, 10)
        with zipfile.ZipFile(result) as zf:
            self.names = zf.namelist()
            self.assertIsNone(zf.testzip())
            zf.extractall(self.root / "installed")

    def test_manifest_for_workbuddy_and_codex(self):
        manifest = self.root / "installed" / "mpa-skill" / "SKILL.md"
        text = manifest.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: mpa-skill\ndescription:"))
        front = text.split("---", 2)[1]
        for key in ("name", "description", "display_name", "display_name_en",
                    "description_zh", "description_en", "version", "author",
                    "examples_zh", "examples_en"):
            self.assertRegex(front, rf"(?m)^{key}:")
        self.assertIn("scripts/mpa_evidence.py", text)
        self.assertIn("mpa-skill/SKILL.md", self.names)
        self.assertIn("mpa-skill/scripts/mpa_evidence.py", self.names)
        self.assertIn("mpa-skill/references/evidence-workbench-usage.md", self.names)
        self.assertEqual([p for p in self.names if p.lower().endswith("/skill.md")],
                         ["mpa-skill/SKILL.md"])
        self.assertTrue(all(p.startswith("mpa-skill/") for p in self.names))
        self.assertFalse(any(p.endswith((".png", ".sqlite3", ".pyc")) for p in self.names))

    def test_extracted_zip_runs_without_global_packages(self):
        target = self.root / "installed" / "mpa-skill" / "scripts" / "mpa_evidence.py"
        ws = self.root / "study"
        source = self.root / "example.txt"
        source.write_text("规划明确了公众参与。\n", encoding="utf-8")
        env = {**os.environ, "PYTHONPATH": "", "PYTHONIOENCODING": "utf-8"}
        def cli(*args):
            p = subprocess.run([sys.executable, "-S", str(target), *map(str, args)],
                               cwd=self.root, env=env, capture_output=True, encoding="utf-8",
                               timeout=30)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            return json.loads(p.stdout)
        self.assertFalse(cli("doctor", "--workspace", ws)["workspace_initialized"])
        cli("init", ws)
        doc = cli("ingest", ws, source)["doc_id"]
        claim = cli("claim", ws, "--question", "参与情况",
                    "--statement", "政策设置参与目标")["claim_id"]
        eid = cli("cite", ws, "--claim", claim, "--document", doc,
                  "--locator", "L1", "--quote", "公众参与")["evidence_id"]
        self.assertEqual(eid, "E0001")
        self.assertTrue(cli("audit", ws)["ok"])
        self.assertEqual(cli("doctor", "--workspace", ws)["workspace_initialized"], True)
        self.assertFalse(any((self.root / "installed").rglob("registry.sqlite3")))

    def test_deterministic_and_archive_is_safe(self):
        first = self.path.read_bytes()
        again, _ = packager.package(self.path)
        self.assertEqual(first, again.read_bytes())
        with zipfile.ZipFile(again) as zf:
            for name in zf.namelist():
                self.assertNotIn("..", Path(name).parts)
                self.assertFalse(name.startswith("/"))
                self.assertNotIn("sources/", name)
