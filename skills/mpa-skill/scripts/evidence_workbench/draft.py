"""Draft self-check: map draft sentences to registered claims and evidence status.

The researcher tags sentences with claim IDs such as [C0003] (or 【C0003】).
This is a deterministic, heuristic check of *traceability and wording*, not a
judgement of whether the argument is correct.
"""
from __future__ import annotations

import re
from pathlib import Path

from .core import MAX_BYTES, EvidenceError, connect, extract

CLAIM_TAG = re.compile(r"[\[【](C\d{4,})[\]】]")
SENTENCE = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")
# Wording that asserts causation; flagged when not backed by a tagged causal claim.
CAUSAL = re.compile(
    r"导致|造成|引起|促使|使得|归因于|决定了|带来了|推动了|促进了|提升了|提高了|降低了|减少了|增加了|"
    r"由于|得益于|\bcaused?\b|\bled to\b|\bresult(?:ed|s)? in\b|\bdue to\b|\bdrives?\b",
    re.IGNORECASE)
# Wording stronger than an MPA case or survey design can usually carry.
OVERCLAIM = re.compile(r"证明了|充分证明|必然|毫无疑问|彻底解决|根本解决|\bprove[sd]?\b|\bundoubtedly\b",
                       re.IGNORECASE)


def _draft_sentences(path: Path):
    if path.stat().st_size > MAX_BYTES:
        raise EvidenceError("Draft exceeds the 30 MiB limit.")
    _, segments = extract(path)
    for locator, content in segments:
        for match in SENTENCE.finditer(content):
            sentence = match.group(0).strip()
            if sentence and not sentence.startswith("#"):
                yield locator, sentence


def _claim_state(conn):
    states = {}
    for claim in conn.execute("SELECT claim_id, kind, statement FROM claims"):
        rows = conn.execute(
            "SELECT status, relation FROM evidence WHERE claim_id=? AND status != 'rejected'",
            (claim["claim_id"],)).fetchall()
        states[f"C{claim['claim_id']:04d}"] = {
            "kind": claim["kind"],
            "statement": claim["statement"],
            "evidence": len(rows),
            "verified": sum(r["status"] == "verified" for r in rows),
            "disputed": sum(r["status"] == "disputed" for r in rows),
            "challenges": sum(r["relation"] == "challenges" for r in rows),
        }
    return states


def check_draft(workspace, draft_path):
    path = Path(draft_path).expanduser().resolve(strict=True)
    with connect(workspace) as conn:
        states = _claim_state(conn)
    issues, used, sentences, tagged = [], {}, 0, 0

    def flag(severity, code, where, sentence, claim=None):
        item = {"severity": severity, "code": code, "where": where, "sentence": sentence[:160]}
        if claim:
            item["claim"] = claim
        issues.append(item)

    for where, sentence in _draft_sentences(path):
        sentences += 1
        tags = CLAIM_TAG.findall(sentence)
        causal_words = bool(CAUSAL.search(sentence))
        if tags:
            tagged += 1
        elif causal_words:
            flag("warning", "untagged_causal_statement", where, sentence)
        if OVERCLAIM.search(sentence):
            flag("warning", "overclaiming_language", where, sentence)
        for cid in tags:
            used[cid] = used.get(cid, 0) + 1
            state = states.get(cid)
            if state is None:
                flag("error", "unknown_claim", where, sentence, cid)
                continue
            if state["evidence"] == 0:
                flag("warning", "claim_without_evidence", where, sentence, cid)
            elif state["verified"] == 0:
                flag("info", "evidence_unreviewed", where, sentence, cid)
            if state["disputed"]:
                flag("warning", "disputed_evidence_cited", where, sentence, cid)
            if state["challenges"]:
                flag("info", "counterevidence_exists", where, sentence, cid)
            if causal_words and state["kind"] != "causal":
                flag("warning", "causal_wording_on_noncausal_claim", where, sentence, cid)
    coverage = [{"claim": cid, "kind": s["kind"], "cited_in_draft": used.get(cid, 0),
                 "evidence": s["evidence"], "verified": s["verified"]}
                for cid, s in sorted(states.items())]
    unused = [c["claim"] for c in coverage if not c["cited_in_draft"]]
    return {
        "draft": path.name,
        "sentences": sentences,
        "tagged_sentences": tagged,
        "ok": not any(i["severity"] == "error" for i in issues),
        "claim_coverage": coverage,
        "claims_not_used": unused,
        "issues": issues,
        "note": ("Heuristic traceability check. Untagged sentences are not wrong by default; "
                 "flags mark where a reader may ask 'what is the evidence?'."),
    }
