"""Mirror of `src/studyforge/serve/programs.py` (R12): the program an example tab names."""

from __future__ import annotations

import json
from types import SimpleNamespace

from studyforge.execute import CODE_COPY
from studyforge.serve.programs import program_of, program_runs


def served(tmp_path, *tabs):
    unit = tmp_path / "unit-01"
    unit.mkdir()
    blocks = [{"type": "code", "lang": "x", "text": "x"}] * len(tabs)
    example = {"type": "example", "id": "e", "tabs": list(tabs), "blocks": blocks}
    (unit / "lesson-1.json").write_text(json.dumps({"blocks": [example]}), encoding="utf-8")
    units = (SimpleNamespace(directory=unit),)
    return SimpleNamespace(corpus=SimpleNamespace(units=units))


def test_a_tab_s_program_is_its_record_s_argv_started_in_the_copy(tmp_path):
    corpus = served(tmp_path, {"lang": "x", "span": 1, "code": "a/A.x", "run": ["tool", "a"]})
    assert program_of(corpus, "a/A.x") == ["tool", "a"]
    assert program_runs(corpus) == [(CODE_COPY, ["tool", "a"])]


def test_no_run_two_different_runs_or_an_option_first_name_no_program(tmp_path):
    corpus = served(
        tmp_path,
        {"lang": "x", "span": 1, "code": "a/A.x", "run": ["tool", "a"]},
        {"lang": "y", "span": 1, "code": "a/A.x", "run": ["tool", "b"]},
        {"lang": "z", "span": 1, "code": "b/B.x", "run": ["-rf", "b"]},
        {"lang": "w", "span": 1, "code": "c/C.x"},
    )
    assert program_of(corpus, "a/A.x") is None
    assert program_of(corpus, "b/B.x") is None and program_of(corpus, "c/C.x") is None
    assert program_runs(corpus) == []
