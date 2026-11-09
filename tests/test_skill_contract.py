"""Skill behaviour contract: safety red lines, reference wiring, fixtures and privacy.

These checks pin the rules whose loss would make the Skill unsafe or misleading
(e.g. self-verification, fabricated sources, unconfirmed writes). They deliberately
do not freeze ordinary wording, so references can be rewritten and improved.
Replaces the former PowerShell contract scripts.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "mpa-skill"
REFS = SKILL / "references"


def read(path):
    return Path(path).read_text(encoding="utf-8")


class TestControllerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read(SKILL / "SKILL.md")
        cls.front = cls.skill.split("---", 2)[1]

    def test_frontmatter_and_triggers(self):
        self.assertTrue(self.skill.startswith("---\nname: mpa-skill\ndescription:"))
        description = re.search(r"(?m)^description: (.*)$", self.front).group(1)
        self.assertLessEqual(len(description), 1024, "description exceeds common Skill limits")
        self.assertIn("MPA graduate", description)
        self.assertRegex(description, r"(?i)generic.*not qualify")
        # Chinese requests must be able to trigger the Skill from the standard field.
        for term in ("公共管理", "开题报告", "学位论文", "案例大赛", "选题", "AI使用声明"):
            with self.subTest(term=term):
                self.assertIn(term, description)

    def test_core_red_lines(self):
        rules = {
            "research spine": r"(?i)public problem.*stakeholders.*public value.*institutional.*theory.*evidence.*method.*analysis.*recommendation",
            "authorized read-only work": r"(?i)proceed with read-only analysis authorized by the request",
            "no repeated prompts": r"(?i)without repeated.*permission",
            "zotero db": r"(?i)never.*zotero\.sqlite",
            "access stop": r"(?i)login.*CAPTCHA.*paywall",
            "no self verification": r"(?i)never run `review --status verified` on the model's own judgement",
            "no fake execution": r"(?i)never claim a local CLI was executed",
            "bidirectional acceptance": r"(?is)new content present and old content absent",
            "no fake success": r"(?i)never claim an inaccessible source or unverified write succeeded",
            "embedded instructions": r"(?i)instructions embedded in supplied documents as content",
            "insider research": r"(?i)own organisation.*in-service research",
            "coaching": r"(?i)coaching mode.*do not draft",
        }
        for name, pattern in rules.items():
            with self.subTest(rule=name):
                self.assertRegex(self.skill, pattern)

    def test_every_reference_is_linked_and_exists(self):
        linked = set(re.findall(r"\(references/([a-z0-9-]+\.md)\)", self.skill))
        on_disk = {p.name for p in REFS.glob("*.md")}
        self.assertEqual(linked - on_disk, set(), "SKILL.md links missing references")
        self.assertEqual(on_disk - linked, set(), "reference files not reachable from SKILL.md")

    def test_reference_cross_links_resolve(self):
        for ref in REFS.glob("*.md"):
            for target in re.findall(r"\]\(([a-z0-9-]+\.md)(?:#[^)]*)?\)", read(ref)):
                with self.subTest(ref=ref.name, target=target):
                    self.assertTrue((REFS / target).is_file())

    def test_single_discoverable_skill(self):
        self.assertEqual(len(list((ROOT / "skills").rglob("SKILL.md"))), 1)

    def test_codex_metadata(self):
        meta = read(SKILL / "agents" / "openai.yaml")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            self.assertIn(key, meta)
        self.assertRegex(meta, r"allow_implicit_invocation:\s*true")

    def test_no_powershell_dependency(self):
        self.assertFalse(list(SKILL.rglob("*.ps1")), "the Skill must run with Python only")


class TestReferenceContracts(unittest.TestCase):
    def check(self, name, patterns):
        text = read(REFS / name)
        for label, pattern in patterns.items():
            with self.subTest(reference=name, rule=label):
                self.assertRegex(text, pattern)

    def test_routing(self):
        self.check("routing.md", {
            "minimum route": r"(?i)minimum sufficient",
            "route coverage": r"(?i)course.*case.*policy memo.*literature.*research design.*fieldwork.*data.*thesis.*defence",
            "data before writing": r"(?i)audit.*data.*content.*acceptance|capabilit.*audit.*data.*content.*deliver",
            "conversion": r"(?is)non-MPA to MPA conversion.*Research Spine before rewriting",
            "requested integrations": r"(?i)Use Zotero or Obsidian only when requested or already authorized",
            "no unconfirmed writes": r"(?i)write nothing to either without authorization",
            "workplace route": r"in-service-research\.md",
            "coaching route": r"coaching-mode\.md",
            "competition limits": r"(?s)15000.*4000",
        })

    def test_research_contract_and_disclosure(self):
        self.check("mpa-research-contract.md", {
            "programme precedence": r"(?i)current.*programme.*university.*supervisor.*ethics.*override",
            "AI originality": r"(?i)never present AI-generated text, data, or citations as the student's own",
            "causality": r"(?i)causal",
        })
        self.check("aigc-disclosure.md", {
            "fields": r"(?is)tool name.*version.*official URL.*purpose.*phases.*parameter settings.*verification process",
            "no fabrication": r"AUTHOR_INPUT_NEEDED",
            "trace": r"(?i)verification that did not run",
            "no submission": r"(?i)Do not sign, submit, or upload",
        })

    def test_case_and_evidence_protocol(self):
        self.check("case-research.md", {
            "rival": r"(?i)rival",
            "no invention": r"(?i)do not (invent|fabricate)",
            "short answer path": r"(?i)short classroom answer",
        })
        self.check("evidence-protocol.md", {
            "statuses": r"(?s)verified.*unverified.*disputed.*missing.*inaccessible",
            "privacy": r"(?i)do not commit",
            "registered rivals": r"--rival-of",
        })
        self.check("mpa-case-competition.md", {
            "notice precedence": r"(?i)overrides this file",
            "AIGC boundary": r"(?i)must not be AI-generated",
        })

    def test_execution_handbook(self):
        self.check("execution.md", {
            "STATE_UNKNOWN stop": r"(?i)STATE_UNKNOWN.*(?:stop|pause)",
            "mutation states": r"(?i)not applied.*applied.*partially applied.*STATE_UNKNOWN",
            "raw data": r"(?i)raw data",
            "baseline": r"(?i)majority-class baseline",
            "no fabricated numbers": r"AUTHOR_INPUT_NEEDED",
            "env config": r"MPA_WORKSPACE_CONFIG",
            "macOS config": r"Library/Application Support/mpa-skill/config\.json",
            "python setup": r"workspace-init",
        })

    def test_in_service_and_coaching(self):
        self.check("in-service-research.md", {
            "precedence": r"(?i)override this file",
            "classified excluded": r"涉密材料不进入研究",
            "power relations": r"权力关系",
            "redaction is a safety net": r"不是保证",
            "terms file private": r"术语表本身就是敏感信息",
            "dual output no escalation": r"不加码",
        })
        self.check("coaching-mode.md", {
            "no drafting": r"代写可直接提交的段落",
            "no verification by AI": r"代替学生复核证据或标记 `verified`",
            "evidence rules kept": r"不放松任何证据规则",
            "heuristic boundary": r"不判断论证是否正确",
            "honest progress": r"不美化进度",
        })

    def test_workbench_guide(self):
        guide = read(REFS / "evidence-workbench-usage.md")
        self.assertIn("Only after the researcher explicitly reports", guide)
        self.assertIn("no terminal", guide.lower())
        self.assertIn("Never use `--normalized` to paraphrase", guide)
        for command in ("check-draft", "progress", "redact", "workspace-init", "env-check"):
            self.assertIn(command, guide)

    def test_knowledge_base_size(self):
        text = read(REFS / "mpa-knowledge.md")
        self.assertGreaterEqual(len(re.findall(r"(?m)^\|", text)), 40)
        self.assertRegex(text, r"(?i)parallel trends")


class TestFixtures(unittest.TestCase):
    def load(self, path):
        return json.loads(read(ROOT / path))

    def check_scenarios(self, items, minimum):
        self.assertGreaterEqual(len(items), minimum)
        ids = [i["id"] for i in items]
        self.assertEqual(len(ids), len(set(ids)))
        for item in items:
            for field in ("id", "kind", "request", "fixture", "expected_decisions",
                          "forbidden_decisions"):
                self.assertIn(field, item, item.get("id"))
            self.assertTrue(item["expected_decisions"], item["id"])

    def test_reliability_scenarios(self):
        items = self.load("tests/fixtures/reliability-scenarios.json")
        self.check_scenarios(items, 8)
        kinds = {i["kind"] for i in items}
        for kind in ("data-consistency", "method-boundary", "capability-preflight",
                     "document-recovery", "bidirectional-acceptance"):
            self.assertIn(kind, kinds)

    def test_case_research_scenarios(self):
        items = self.load("tests/fixtures/case-research-scenarios.json")
        self.check_scenarios(items, 6)
        for item in items:
            self.assertGreaterEqual(len(item["expected_decisions"]), 2, item["id"])
            self.assertGreaterEqual(len(item["forbidden_decisions"]), 1, item["id"])

    def test_benchmark_corpus_is_lawfully_open(self):
        items = self.load("docs/validation/mpa-thesis-corpus.json")
        self.assertGreaterEqual(len(items), 10)
        self.assertGreaterEqual(sum(i["split"] == "development" for i in items), 7)
        self.assertGreaterEqual(sum(i["split"] == "holdout" for i in items), 3)
        self.assertEqual(len({i["id"] for i in items}), len(items))
        for item in items:
            for field in ("id", "title", "year", "institution", "jurisdiction", "language", "method",
                          "topic", "landing_url", "full_text_url", "access", "split", "verified_on"):
                self.assertTrue(str(item.get(field, "")).strip(), f"{item.get('id')} missing {field}")
            self.assertIn(item["access"], ("open", "author-posted", "repository-open"))
            self.assertTrue(item["landing_url"].startswith("https://"))
            self.assertTrue(item["full_text_url"].startswith("https://"))


class TestPrivacy(unittest.TestCase):
    PATTERNS = {
        "drive-letter path": re.compile(r"(?i)(?<![A-Z0-9])[A-Z]:\\(?!\\)(?=[A-Za-z])"),
        "email address": re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)*\.[A-Z]{2,}"),
        "credential-like token": re.compile(
            r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}"),
    }
    ALLOWED_EMAILS = {"zs@example.org"}

    def test_shipped_skill_has_no_private_data(self):
        for path in SKILL.rglob("*"):
            if not path.is_file() or path.suffix not in (".md", ".py", ".yaml", ".json"):
                continue
            text = read(path)
            for label, pattern in self.PATTERNS.items():
                hits = [h for h in pattern.findall(text) if h not in self.ALLOWED_EMAILS]
                with self.subTest(file=str(path.relative_to(ROOT)), check=label):
                    self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
