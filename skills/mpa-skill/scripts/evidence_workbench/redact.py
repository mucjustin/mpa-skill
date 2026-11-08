"""Local de-identification for exports and text shared outside the workspace.

Researcher-supplied terms (names, units, places) are the primary control.
Automatic patterns catch common Chinese identifiers but are a safety net,
not a guarantee: always review redacted output before sharing it.
"""
from __future__ import annotations

import re
from pathlib import Path

from .core import EvidenceError

AUTO_PATTERNS = (
    ("身份证号", re.compile(r"(?<![0-9A-Za-z])\d{17}[\dXx](?![0-9A-Za-z])")),
    ("手机号", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")),
    ("电话", re.compile(r"(?<!\d)0\d{2,3}-\d{7,8}(?!\d)")),
    ("邮箱", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("文号", re.compile(r"[一-龥]{1,10}[〔\[［(（]\d{4}[〕\]］)）]\s*\d{1,4}\s*号")),
)


class Redactor:
    def __init__(self, terms=None, auto=True):
        self.terms = []
        for original, replacement in (terms or {}).items():
            if original:
                self.terms.append((original, replacement))
        # Longest first so "某某街道办事处" wins over "某某街道".
        self.terms.sort(key=lambda t: len(t[0]), reverse=True)
        self.auto = auto
        self.count = 0

    @classmethod
    def from_file(cls, path, auto=True):
        """Lines: `原词=替代词` or just `原词` (gets [R01], [R02] ...). `#` starts a comment."""
        terms, auto_id = {}, 0
        text = Path(path).expanduser().read_text(encoding="utf-8-sig")
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                original, replacement = (x.strip() for x in line.split("=", 1))
            else:
                auto_id += 1
                original, replacement = line, f"[R{auto_id:02d}]"
            if not original:
                raise EvidenceError(f"Empty redaction term in line: {raw!r}")
            terms[original] = replacement
        return cls(terms, auto=auto)

    def text(self, value: str) -> str:
        for original, replacement in self.terms:
            if original in value:
                self.count += value.count(original)
                value = value.replace(original, replacement)
        if self.auto:
            for label, pattern in AUTO_PATTERNS:
                value, n = pattern.subn(f"[{label}]", value)
                self.count += n
        return value

    def apply(self, data):
        if isinstance(data, str):
            return self.text(data)
        if isinstance(data, list):
            return [self.apply(x) for x in data]
        if isinstance(data, dict):
            return {k: self.apply(v) for k, v in data.items()}
        return data

    def summary(self):
        return {"terms": len(self.terms), "auto_patterns": self.auto,
                "replacements": self.count}
