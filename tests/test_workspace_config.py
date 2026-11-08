"""Cross-platform workspace setup (successor of the former PowerShell scripts)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "mpa-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from evidence_workbench import workspace
from evidence_workbench.core import EvidenceError


class TestWorkspaceConfig(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()

    def snapshot(self):
        return sorted((str(p), p.stat().st_size) for p in self.root.rglob("*") if p.is_file())

    def test_initialize_inspect_and_refuse_overwrite(self):
        config = self.root / "cfg" / "config.json"
        ws = self.root / "Workspace"
        zotero = self.root / "Apps" / "Zotero.app"
        result = workspace.initialize_workspace(ws, config, zotero)
        self.assertTrue(result["created"])
        for name in ("", "Obsidian", "ZoteroAttachments", "ResearchData", "ResearchProjects"):
            self.assertTrue((ws / name).is_dir(), name)
        data = json.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(sorted(data), sorted(workspace.CONFIG_KEYS))
        self.assertEqual(data["zotero_executable"], str(zotero))

        original = config.read_bytes()
        second = self.root / "Second"
        for dry in (False, True):
            with self.subTest(dry_run=dry), self.assertRaisesRegex(EvidenceError, "already exists"):
                workspace.initialize_workspace(second, config, dry_run=dry)
        self.assertFalse(second.exists())
        self.assertEqual(config.read_bytes(), original)

        before = self.snapshot()
        report = workspace.inspect_environment(config, probe_zotero=False)
        self.assertEqual(before, self.snapshot(), "env-check must be read-only")
        self.assertTrue(report["config_found"])
        self.assertTrue(report["workspace_root_exists"] and report["obsidian_vault_exists"])
        self.assertFalse(report["zotero_executable_exists"])
        self.assertEqual(report["missing_keys"], [])

    def test_dry_run_and_unsafe_targets(self):
        cfg = self.root / "dry.json"
        result = workspace.initialize_workspace(self.root / "DryRun", cfg, dry_run=True)
        self.assertFalse(result["created"])
        self.assertFalse((self.root / "DryRun").exists())
        self.assertFalse(cfg.exists())
        with self.assertRaisesRegex(EvidenceError, "filesystem root"):
            workspace.initialize_workspace(Path(self.root.anchor), self.root / "r.json", dry_run=True)
        target = self.root / "file"
        target.write_text("x", encoding="utf-8")
        with self.assertRaisesRegex(EvidenceError, "existing file"):
            workspace.initialize_workspace(target, self.root / "f.json", dry_run=True)

    def test_platform_default_paths(self):
        with mock.patch.object(sys, "platform", "darwin"):
            self.assertEqual(workspace.default_config_path(),
                             Path.home() / "Library/Application Support/mpa-skill/config.json")
            self.assertIn(Path("/Applications/Zotero.app"), workspace.zotero_candidates())
        if os.name != "nt":
            with mock.patch.object(sys, "platform", "linux"), \
                    mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)}):
                self.assertEqual(workspace.default_config_path(),
                                 self.root / "mpa-skill" / "config.json")
        with mock.patch.dict(os.environ, {"MPA_WORKSPACE_CONFIG": str(self.root / "env.json")}):
            self.assertEqual(workspace.resolve_config_path(), self.root / "env.json")

    def test_cli_entrypoint_without_powershell(self):
        cfg = self.root / "c.json"
        env = {**os.environ, "PYTHONPATH": "", "PYTHONIOENCODING": "utf-8"}
        entry = SCRIPTS / "mpa_evidence.py"

        def cli(*args):
            p = subprocess.run([sys.executable, "-S", str(entry), *map(str, args)], env=env,
                               capture_output=True, encoding="utf-8", timeout=30, cwd=self.root)
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        self.assertTrue(cli("workspace-init", self.root / "W", "--config", cfg)["created"])
        self.assertTrue(cli("env-check", "--config", cfg, "--no-zotero-probe")["config_found"])


if __name__ == "__main__":
    unittest.main()
