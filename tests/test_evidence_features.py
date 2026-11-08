"""v2.3 workbench features, exercised with synthetic material only."""
import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "mpa-skill" / "scripts"))
from evidence_workbench import core
from evidence_workbench.cli import main
from evidence_workbench.draft import check_draft
from evidence_workbench.redact import Redactor

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main([str(a) for a in argv])
    return code, (json.loads(out.getvalue()) if code == 0 or out.getvalue() else None), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.ws = self.root / "ws"
        core.initialize(self.ws)

    def source(self, name, text):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return core.import_document(self.ws, p)["doc_id"]


class TestQuoteMatching(Base):
    def test_normalized_match_requires_opt_in_and_stores_source_span(self):
        doc = self.source("pdfish.txt", "街道 办事处 于２０２４年 启动\n")
        claim = core.add_claim(self.ws, "何时启动", "街道办事处于2024年启动")
        with self.assertRaisesRegex(core.EvidenceError, "--normalized"):
            core.add_evidence(self.ws, claim, doc, "L1", "街道办事处于2024年启动")
        with self.assertRaisesRegex(core.EvidenceError, "verbatim"):
            core.add_evidence(self.ws, claim, doc, "L1", "街道办事处于2025年", normalized=True)
        eid = core.add_evidence(self.ws, claim, doc, "L1", "街道办事处于2024年启动", normalized=True)
        data = json.loads(core.export_registry(self.ws, "json", include_quotes=True))
        item = data["evidence"][0]
        self.assertEqual(item["match_mode"], "normalized")
        self.assertEqual(item["quote"], "街道 办事处 于２０２４年 启动")  # verbatim source text
        self.assertIn("normalized_match_check_context",
                      [i["code"] for i in core.audit(self.ws)["issues"]])
        core.review_evidence(self.ws, eid, "verified", "R1", "checked")
        self.assertTrue(core.audit(self.ws)["ok"])

    def test_range_locator_quotes_across_lines(self):
        doc = self.source("minutes.md", "第一行\n会议决定由社区\n牵头组织协商\n第四行\n")
        claim = core.add_claim(self.ws, "谁牵头", "社区牵头组织协商")
        with self.assertRaises(core.EvidenceError):
            core.add_evidence(self.ws, claim, doc, "L2", "由社区\n牵头")
        eid = core.add_evidence(self.ws, claim, doc, "L2-L3", "由社区\n牵头")
        self.assertEqual(core.add_evidence(self.ws, claim, doc, "L2-3", "社区"), "E0002")
        data = json.loads(core.export_registry(self.ws, "json"))
        self.assertEqual(data["evidence"][0]["locator"], "L2-L3")
        core.review_evidence(self.ws, eid, "verified", "R1")
        self.assertTrue(core.audit(self.ws)["ok"])
        for bad in ("L3-L2", "L2-p.3", "L2-", "L1-L30"):
            with self.subTest(bad=bad), self.assertRaises(core.EvidenceError):
                core.add_evidence(self.ws, claim, doc, bad, "社区")

    def test_docx_footnotes_and_endnotes(self):
        path = self.root / "thesis.docx"
        body = f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:t>正文段落</w:t></w:r></w:p></w:body></w:document>'
        notes = (f'<w:footnotes xmlns:w="{W}"><w:footnote w:type="separator" w:id="-1"><w:p/></w:footnote>'
                 f'<w:footnote w:id="1"><w:p><w:r><w:t>参见某市2023年工作报告。</w:t></w:r></w:p></w:footnote></w:footnotes>')
        endnotes = (f'<w:endnotes xmlns:w="{W}"><w:endnote w:id="2"><w:p><w:r><w:t>访谈编号 A03。</w:t>'
                    f'</w:r></w:p></w:endnote></w:endnotes>')
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("word/document.xml", body)
            zf.writestr("word/footnotes.xml", notes)
            zf.writestr("word/endnotes.xml", endnotes)
        doc = core.import_document(self.ws, path)["doc_id"]
        locators = [s["locator"] for s in core.list_segments(self.ws, doc)]
        self.assertEqual(locators, ["para.1", "fn.1", "en.2"])
        claim = core.add_claim(self.ws, "来源", "引用工作报告")
        core.add_evidence(self.ws, claim, doc, "fn.1", "2023年工作报告")


class TestRivalsAndMigration(Base):
    def test_causal_claim_needs_tested_rival(self):
        doc = self.source("obs.txt", "试点后投诉下降。\n同期上级加大了督查。\n")
        main_claim = core.add_claim(self.ws, "投诉为何下降", "试点导致投诉下降", "causal")
        codes = lambda: {(i["code"], i["item"]) for i in core.audit(self.ws)["issues"]}
        self.assertIn(("no_rival_explanation", main_claim), codes())
        rival = core.add_claim(self.ws, "投诉为何下降", "上级督查导致投诉下降", "causal",
                               rival_of=main_claim)
        self.assertNotIn(("no_rival_explanation", main_claim), codes())
        self.assertIn(("rival_untested", rival), codes())
        core.add_evidence(self.ws, rival, doc, "L2", "加大了督查")
        self.assertNotIn(("rival_untested", rival), codes())
        with self.assertRaisesRegex(core.EvidenceError, "rival-of"):
            core.add_claim(self.ws, "q", "s", rival_of="C0999")
        md = core.export_registry(self.ws, "md")
        self.assertIn("| causal | C0001 |", md)

    def test_v1_registry_is_migrated_without_losing_evidence(self):
        legacy = self.root / "legacy"
        store = legacy / core.STORE
        (store / "sources").mkdir(parents=True)
        src = self.root / "old.txt"
        src.write_text("旧证据。\n", encoding="utf-8")
        digest = core.digest_file(src)
        (store / "sources" / (digest + ".txt")).write_bytes(src.read_bytes())
        conn = sqlite3.connect(store / core.DB_FILE)
        conn.executescript(f"""
            CREATE TABLE documents (doc_id TEXT PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
              format TEXT NOT NULL, extractor TEXT NOT NULL, imported_at TEXT NOT NULL, relative_source TEXT NOT NULL);
            CREATE TABLE segments (doc_id TEXT NOT NULL, locator TEXT NOT NULL, content TEXT NOT NULL,
              PRIMARY KEY (doc_id, locator));
            CREATE TABLE claims (claim_id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL,
              statement TEXT NOT NULL, kind TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE evidence (evidence_id INTEGER PRIMARY KEY AUTOINCREMENT, claim_id INTEGER NOT NULL,
              doc_id TEXT NOT NULL, locator TEXT NOT NULL, quote TEXT NOT NULL, relation TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'unverified', reviewer TEXT, reviewed_at TEXT,
              note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
              UNIQUE(claim_id, doc_id, locator, quote, relation));
            INSERT INTO documents VALUES ('D-1','{digest}','old.txt','.txt','utf8-lines-v1','t','sources/{digest}.txt');
            INSERT INTO segments VALUES ('D-1','L1','旧证据。');
            INSERT INTO claims(question,statement,kind,created_at) VALUES ('q','s','fact','t');
            INSERT INTO evidence(claim_id,doc_id,locator,quote,relation,status,reviewer,created_at)
              VALUES (1,'D-1','L1','旧证据','supports','verified','R1','t');
            PRAGMA user_version = 1;""")
        conn.commit()
        conn.close()
        report = core.audit(legacy)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["evidence"], 1)
        with core.connect(legacy) as conn2:
            self.assertEqual(conn2.execute("PRAGMA user_version").fetchone()[0], core.SCHEMA_VERSION)
            row = conn2.execute("SELECT match_mode, status FROM evidence").fetchone()
        self.assertEqual((row["match_mode"], row["status"]), ("exact", "verified"))
        self.assertEqual(core.progress(legacy)["spine"][0]["status"], "missing")


class TestRedaction(Base):
    def test_terms_and_patterns(self):
        r = Redactor({"张三": "受访者A", "某某街道": ""}, auto=True)
        text = r.text("张三（13812345678，zs@example.org）称某某街道依据京政发〔2024〕3号文件执行，身份证11010119900101123X。")
        for leaked in ("张三", "13812345678", "zs@example.org", "某某街道", "京政发", "11010119900101123X"):
            self.assertNotIn(leaked, text)
        self.assertIn("受访者A", text)
        self.assertIn("[手机号]", text)
        self.assertGreaterEqual(r.summary()["replacements"], 6)

    def test_export_and_redact_commands(self):
        terms = self.root / "terms.txt"
        terms.write_text("# 名单\n李四\n城东社区=社区X\n", encoding="utf-8")
        doc = self.source("interview.txt", "李四说城东社区先行试点。\n")
        claim = core.add_claim(self.ws, "城东社区是否先行", "李四认为城东社区先行")
        core.add_evidence(self.ws, claim, doc, "L1", "城东社区先行试点")
        out = self.root / "matrix.md"
        code, result, err = run("export", self.ws, "--output", out, "--include-quotes",
                                "--redact-terms", terms)
        self.assertEqual(code, 0, err)
        text = out.read_text(encoding="utf-8")
        self.assertNotIn("李四", text)
        self.assertNotIn("城东社区", text)
        self.assertIn("[R01]", text)
        self.assertIn("社区X", text)
        self.assertIn("Redacted export", text)
        self.assertGreater(result["redaction"]["replacements"], 0)

        transcript = self.root / "t.md"
        transcript.write_text("受访人李四，电话 13900001111。\n", encoding="utf-8")
        cleaned = self.root / "t.redacted.md"
        code, result, err = run("redact", transcript, "--output", cleaned, "--redact-terms", terms)
        self.assertEqual(code, 0, err)
        self.assertEqual(cleaned.read_text(encoding="utf-8"), "受访人[R01]，电话 [手机号]。\n")
        code, _, _ = run("redact", transcript, "--output", cleaned)
        self.assertEqual(code, 2)  # refuses to overwrite silently


class TestProgress(Base):
    def test_spine_and_tasks_resume(self):
        state = core.progress(self.ws)
        self.assertEqual([s["status"] for s in state["spine"]], ["missing"] * 8)
        self.assertEqual(state["suggested_next"], {"type": "spine_gap", "link": "problem",
                                                   "status": "missing"})
        core.progress(self.ws, set_links=["problem=established", "stakeholders=partial"],
                      note="开题已通过")
        core.progress(self.ws, todo="整理 3 份访谈记录")
        core.progress(self.ws, todo="补充政策文件")
        state = core.progress(self.ws, next_task="T0002")
        self.assertEqual(state["suggested_next"]["task_id"], "T0002")
        state = core.progress(self.ws, done="T0002")
        self.assertEqual(state["suggested_next"]["task_id"], "T0001")
        self.assertEqual(state["done_tasks"], 1)
        self.assertEqual(state["spine"][0]["note"], "开题已通过")
        for bad in ({"set_links": ["theory=done"]}, {"set_links": ["budget=partial"]},
                    {"done": "T0099"}, {"next_task": "T0002"}):
            with self.subTest(bad=bad), self.assertRaises(core.EvidenceError):
                core.progress(self.ws, **bad)
        code, result, _ = run("progress", self.ws, "--set", "evidence=partial")
        self.assertEqual(code, 0)
        self.assertEqual(result["spine"][4], {**result["spine"][4], "status": "partial"})


class TestDraftCheck(Base):
    def test_tags_causal_wording_and_unknown_claims(self):
        doc = self.source("src.txt", "试点社区投诉量下降。\n")
        fact = core.add_claim(self.ws, "投诉变化", "试点社区投诉量下降")
        core.add_evidence(self.ws, fact, doc, "L1", "投诉量下降")
        bare = core.add_claim(self.ws, "原因", "网格化导致投诉下降", "causal")
        draft = self.root / "draft.md"
        draft.write_text(
            "# 第四章\n"
            f"试点社区投诉量明显下降[{fact}]。\n"
            f"网格化管理导致了投诉下降【{bare}】。\n"
            "这充分证明了改革的成功。\n"
            "数字化平台提高了办事效率。\n"
            "错误标注[C0099]。\n", encoding="utf-8")
        report = check_draft(self.ws, draft)
        codes = {(i["code"], i.get("claim")) for i in report["issues"]}
        self.assertIn(("evidence_unreviewed", fact), codes)
        self.assertIn(("claim_without_evidence", bare), codes)
        self.assertIn(("overclaiming_language", None), codes)
        self.assertIn(("untagged_causal_statement", None), codes)
        self.assertIn(("unknown_claim", "C0099"), codes)
        self.assertNotIn(("causal_wording_on_noncausal_claim", bare), codes)
        self.assertFalse(report["ok"])
        self.assertEqual(report["tagged_sentences"], 3)
        self.assertEqual(report["claims_not_used"], [])
        code, _, _ = run("check-draft", self.ws, draft)
        self.assertEqual(code, 2)

    def test_causal_wording_on_fact_claim(self):
        doc = self.source("s.txt", "平台上线后办件量上升。\n")
        fact = core.add_claim(self.ws, "办件量", "平台上线后办件量上升")
        core.add_evidence(self.ws, fact, doc, "L1", "办件量上升")
        draft = self.root / "d.txt"
        draft.write_text(f"平台上线促进了办件量上升[{fact}]。\n", encoding="utf-8")
        report = check_draft(self.ws, draft)
        self.assertTrue(report["ok"])
        self.assertIn("causal_wording_on_noncausal_claim", [i["code"] for i in report["issues"]])


if __name__ == "__main__":
    unittest.main()
