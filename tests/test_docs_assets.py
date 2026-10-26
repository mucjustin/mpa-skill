"""Validate edited SVG sources and README relative links."""
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = ["logo.svg", "logo-mono.svg", "brand-lockup.svg", "banner.svg", "spine.svg", "workflow.svg", "evidence-flow.svg"]


class TestDocsAssets(unittest.TestCase):
    def test_svg_are_valid_xml_and_accessible(self):
        for file in SVG:
            with self.subTest(file=file):
                root = ET.parse(ROOT / "assets" / file).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIn("viewBox", root.attrib)
                self.assertTrue(root.attrib.get("aria-label"))

    def test_logo_letters_are_real_paths(self):
        for name in ("logo.svg", "logo-mono.svg", "brand-lockup.svg", "banner.svg"):
            with self.subTest(name=name):
                root = ET.parse(ROOT / "assets" / name).getroot()
                ids = {element.attrib.get("id") for element in root.iter()}
                self.assertTrue({"mpa-reference-mark", "joined-mp", "a-upper", "a-lower", "evidence-curve", "gold-point"}.issubset(ids))
                self.assertIn("MPA", root.attrib["aria-label"])

    def test_bilingual_documents_have_real_local_targets(self):
        for name in ("README.md", "README.en.md", "docs/install-and-compatibility.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("MPA Research Agent", text)
            for raw in re.findall(r"\]\(([^)]+)\)", text):
                path = raw.split("#", 1)[0]
                if not path or "://" in path or path.startswith(("mailto:", "data:")):
                    continue
                with self.subTest(document=name, link=path):
                    self.assertTrue(((ROOT / name).parent / path).exists(),
                                    f"{name}: broken local link {path}")
            for path in re.findall(r'<img[^>]*src="(assets/[^"]+)"', text):
                self.assertTrue((ROOT / path).is_file(), path)

    def test_generated_old_images_removed_but_historical_sources_retained(self):
        self.assertFalse((ROOT / "assets" / "xiaohei-illustrations").exists())
        self.assertFalse((ROOT / "ml-analysis" / "output").exists())
        self.assertTrue((ROOT / "ml-analysis" / "mpa_ml_analysis.py").is_file())
        self.assertTrue((ROOT / "docs" / "validation" / "v1.0.0-benchmark.md").is_file())


if __name__ == "__main__":
    unittest.main()
