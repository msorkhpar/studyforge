"""Mirror of `generate/mathpages.py` (R12): which corpus carries math at all."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from studyforge.generate import mathpages


def corpus_with(root: Path, lesson: dict) -> SimpleNamespace:
    unit = root / "unit-01"
    unit.mkdir(parents=True)
    (unit / "lesson-1.json").write_text(json.dumps(lesson), encoding="utf-8")
    return SimpleNamespace(units=(SimpleNamespace(directory=unit),))


def test_a_math_block_marks_the_corpus(tmp_path):
    block = {"blocks": [{"type": "code", "lang": "math", "text": "x"}]}
    assert mathpages.wanted(corpus_with(tmp_path, block))


def test_an_inline_formula_marks_the_corpus(tmp_path):
    inline = {"blocks": [{"type": "paragraph", "text": "with $`x`$ here"}]}
    assert mathpages.wanted(corpus_with(tmp_path, inline))


def test_code_and_dollar_amounts_alone_do_not(tmp_path):
    plain = {"blocks": [{"type": "code", "lang": "python", "text": "x = 1"},
                        {"type": "paragraph", "text": "It costs $5 and runs `solve()`."}]}
    assert not mathpages.wanted(corpus_with(tmp_path, plain))
