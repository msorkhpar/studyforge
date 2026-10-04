"""Mirror of `generate/exampleruns.py` (R12): which corpora get the Run strip's two files."""

from __future__ import annotations

import json
from types import SimpleNamespace

from studyforge.generate.exampleruns import wanted


def corpus(tmp_path, *tabs_per_unit):
    units = []
    for number, tabs in enumerate(tabs_per_unit):
        directory = tmp_path / f"unit-{number}"
        directory.mkdir()
        block = {"type": "example", "id": "e", "tabs": tabs, "blocks": []}
        (directory / "lesson-1.json").write_text(json.dumps({"blocks": [block]}), encoding="utf-8")
        units.append(SimpleNamespace(directory=directory))
    return SimpleNamespace(units=tuple(units))


def test_a_corpus_whose_example_tab_names_a_file_wants_the_files(tmp_path):
    assert wanted(corpus(tmp_path, [{"lang": "python", "span": 1, "code": "examples/a.py"}]))


def test_a_corpus_with_only_plain_example_tabs_wants_none(tmp_path):
    assert not wanted(corpus(tmp_path, [{"lang": "python", "span": 1}]))


def test_one_unit_naming_a_file_is_enough_and_no_unit_is_no(tmp_path):
    plain = [{"lang": "python", "span": 1}]
    named = [{"lang": "python", "span": 1, "code": "examples/a.py"}]
    assert wanted(corpus(tmp_path, plain, named))
    assert not wanted(SimpleNamespace(units=()))


def test_an_unreadable_lesson_document_is_skipped_not_fatal(tmp_path):
    made = corpus(tmp_path, [{"lang": "python", "span": 1}])
    (made.units[0].directory / "lesson-2.json").write_text("{", encoding="utf-8")
    assert not wanted(made)
