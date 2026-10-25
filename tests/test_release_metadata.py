"""Guard against stale GitHub release versions and unsafe publishing workflows."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "tools/check_release.py"
spec = importlib.util.spec_from_file_location("release_checker", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseContractTests(unittest.TestCase):
    def test_version_matches_release_docs(self):
        self.assertEqual(module.skill_version(), "2.2.0")
        self.assertEqual(module.validate(), "2.2.0")

    def test_different_changelog_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills/mpa-skill").mkdir(parents=True)
            (root / "skills/mpa-skill/SKILL.md").write_text(
                '---\nname: mpa-skill\nversion: "2.3.0"\n---\n',
                encoding="utf-8",
            )
            (root / "CHANGELOG.md").write_text(
                "## [Unreleased]\n\n## [2.2.0] - 2026-10-26\n\n## [2.1.0] - 2026-08-25",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "CHANGELOG"):
                module.validate(root)

    def test_ci_gates_release_after_all_tests(self):
        source = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        for required in (
            "needs: test",
            "github.event_name == 'push' && github.ref == 'refs/heads/main'",
            "contents: write",
            "gh release create",
            "gh release view",
            "SHA256SUMS",
            "tools/check_release.py",
            "--notes-file",
            "--target",
        ):
            with self.subTest(required=required):
                self.assertIn(required, source)

    def test_release_notes_are_complete(self):
        notes = (ROOT / "docs/releases/v2.2.0.md").read_text(encoding="utf-8")
        for term in ("v2.2.0", "mpa-skill.zip", "SHA256SUMS", "SQLite", "WorkBuddy"):
            with self.subTest(term=term):
                self.assertIn(term, notes)


if __name__ == "__main__":
    unittest.main()
