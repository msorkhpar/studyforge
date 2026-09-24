"""Mirror of `src/studyforge/skills/adapter/parts/suite.py` (R12)."""

from __future__ import annotations

import ast
import json

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.parts.suite import SUITE_PARTS
from studyforge.validate.source import SKIP_DIRS, repository_ignores, source_files
from tests.studyforge.skills.adapter import corpora


def files():
    """The generated test modules, rendered for the walkthrough corpus.

    ⚠️ Modules only: the directory also carries its bytecode ignore file.
    """
    made = scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))))
    return {
        item.where: item.text
        for item in made.files
        if item.where.startswith("tests/") and item.where.endswith(".py")
    }


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
    assert "shutil.copytree(CORPUS_ROOT, where, ignore=left_out)" in text
    assert "emit(root," in text and "emit(CORPUS_ROOT," not in text


def test_the_working_copy_asks_the_one_ignore_reader_and_keeps_no_list():
    # ⛔ What a copy leaves behind is the repository's answer,
    # read through the one ignore reader. A pattern list beside it is a second
    # reader that is wrong for the first scratch directory it does not name.
    text = files()["tests/ingest/test_emit.py"]
    assert repository_ignores.__name__ in _imported_from_validate_source(text)
    assert "repository_ignores(CORPUS_ROOT, asked)" in text
    assert "ignore_patterns" not in text
    assert "__pycache__" not in text and ".pytest_cache" not in text


def test_the_emission_test_holds_every_container_to_its_documents_date():
    # ⛔ The generated suite carries the property, so a
    # regenerated corpus inherits it (R19).
    text = files()["tests/ingest/test_emit.py"]
    assert "def test_every_container_is_dated_with_its_documents(tmp_path):" in text
    assert "rglob(CONTAINER_FILENAME)" in text


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


def _imported_from_validate_source(text: str) -> str:
    """The generated module's one import line from `studyforge.validate.source`."""
    [line] = [
        line for line in text.splitlines() if line.startswith("from studyforge.validate.source")
    ]
    return line


def test_the_copy_takes_validates_root_rule_and_types_no_store_name():
    # ⛔ One rule: what a copy leaves out by name is `validate`'s own `SKIP_DIRS`,
    # at the corpus root only, and a nested store is `validate`'s own `source_files`
    # answer. A name typed into the template would be a second copy that drifts.
    text = files()["tests/ingest/test_emit.py"]
    imported = _imported_from_validate_source(text)
    assert "SKIP_DIRS" in imported and source_files.__name__ in imported
    assert "source_files(CORPUS_ROOT).stores" in text
    assert "if here == CORPUS_ROOT:" in text
    typed = [name for name in SKIP_DIRS if f'"{name}"' in text or f"'{name}'" in text]
    assert typed == [], f"the template types {typed} instead of asking validate"
