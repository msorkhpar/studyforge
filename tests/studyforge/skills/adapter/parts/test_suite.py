"""Mirror of `src/studyforge/skills/adapter/parts/suite.py` (R12)."""

from __future__ import annotations

import ast
import json

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.parts.suite import SUITE_PARTS
from tests.studyforge.skills.adapter import corpora


def files():
    """The generated test tree, rendered for the walkthrough corpus."""
    made = scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))))
    return {item.where: item.text for item in made.files if item.where.startswith("tests/")}


def test_the_three_tests_mirror_the_three_steps():
    assert [part.where for part in SUITE_PARTS] == [
        "tests/{package}/test_read.py",
        "tests/{package}/test_emit.py",
        "tests/{package}/test_audit.py",
    ]


def test_every_generated_test_module_parses_and_holds_tests():
    for where, text in files().items():
        tree = ast.parse(text)
        named = [
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        assert named, f"{where} is a test module with no tests"
        assert ast.get_docstring(tree), f"{where} has no contract (R17)"


def test_the_emission_test_asserts_the_exit_code_and_not_a_shape():
    # ⛔ R2: the definition of done is `validate`, not a tree somebody agreed
    # looked right. A generated test that compared filenames would be checking
    # the scaffold against itself.
    text = files()["tests/ingest/test_emit.py"]
    assert "report = validate(root)" in text
    assert "assert report.ok" in text


def test_the_emission_test_never_writes_into_the_corpus_it_reads():
    text = files()["tests/ingest/test_emit.py"]
    assert "shutil.copytree(CORPUS_ROOT, where, ignore=NOT_COPIED)" in text
    assert "emit(root," in text and "emit(CORPUS_ROOT," not in text


def test_the_archive_is_the_one_thing_a_working_copy_leaves_behind():
    # ⛔ A test that emitted over the last run's output would pass on a corpus
    # this run can no longer produce.
    text = files()["tests/ingest/test_emit.py"]
    assert '"archive"' in text and '".archive-staging"' in text


def test_the_determinism_test_holds_the_date_fixed():
    # ⭐ R10: two runs differ only in `ingested`, so a moving date would make
    # the comparison meaningless rather than strict.
    text = files()["tests/ingest/test_emit.py"]
    assert 'INGESTED = "2026-01-01"' in text
    assert "date.today" not in text


def test_no_generated_test_finds_its_corpus_from_the_working_directory():
    for where, text in files().items():
        assert "Path.cwd()" not in text, f"{where} depends on where pytest was started"
        assert "Path(__file__).resolve().parents[2]" in text, where
