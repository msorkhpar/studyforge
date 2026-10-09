"""`edition-unshared`: one task in two languages that is not one practice's editions."""

from __future__ import annotations

from studyforge.validate import validate
from studyforge.validate.languages import RULE_EDITION
from tests.studyforge.validate.test_languages import READING, corpus, document


def practices(**first):
    return [
        document(),
        document(kind="practice", ordinal=1, lang="aa", title="Count by a key (Aa)", **first),
        document(kind="practice", ordinal=2, lang="bb", title="Count by a key (Bb)"),
    ]


def test_one_task_in_two_languages_with_no_shared_edition_is_a_warning_by_default(tmp_path):
    report = validate(corpus(tmp_path, practices(), practices=2))
    assert report.ok, report.lines()
    assert [one.rule for one in report.advice] == [RULE_EDITION]
    assert report.summary().endswith("1 warning(s)")


def test_under_editions_required_it_is_a_finding(tmp_path):
    root = corpus(tmp_path, practices(), manifest={**READING, "editions": "required"}, practices=2)
    report = validate(root)
    assert RULE_EDITION in report.rules and not report.ok


def test_editions_that_share_one_id_are_valid(tmp_path):
    shared = [
        document(),
        document(kind="practice", ordinal=1, lang="aa", title="Count by a key", edition="count"),
        document(kind="practice", ordinal=2, lang="bb", title="Count by a key", edition="count"),
    ]
    report = validate(corpus(tmp_path, shared, manifest={**READING, "editions": "required"}, practices=2))
    assert report.findings == () and report.advice == ()


def test_two_tasks_and_a_corpus_with_none_are_not_asked(tmp_path):
    different = [
        document(),
        document(kind="practice", ordinal=1, lang="aa", title="Count by a key"),
        document(kind="practice", ordinal=2, lang="bb", title="Sort the words"),
    ]
    report = validate(corpus(tmp_path, different, manifest={**READING, "editions": "required"}, practices=2))
    assert report.findings == () and report.advice == ()
    assert "warning" not in report.summary()
