"""What the framework generated here, read from the corpus's own record."""

from __future__ import annotations

import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.reconnaissance.installed import INSTALL_RECORD, generated
from tests.studyforge.skills.reconnaissance import sources

#: One generated file, in the shape onboarding writes it.
GENERATED = {"ONBOARDING.md": "# Generated\n", "tests/test_pin.py": "def test_pin(): pass\n"}


def test_the_record_names_every_file_the_framework_wrote(tmp_path):
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), GENERATED)

    assert generated(root) == frozenset(GENERATED)


def test_a_corpus_nobody_onboarded_has_no_footprint(tmp_path):
    # ⭐ The control that makes the clause above mean something: a first survey
    # is unchanged by everything this module does.
    assert generated(sources.flat_prose(tmp_path / "c")) == frozenset()


@pytest.mark.parametrize("text", ["not json at all", "[]", '{"files": "two"}', '{"files": [1]}'])
def test_a_record_that_cannot_be_read_as_a_file_list_reads_as_no_footprint(tmp_path, text):
    # ⛔ Never a guess and never a raise: a corpus whose record is malformed
    # surveys exactly as one that was never onboarded.
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), GENERATED)
    (root / INSTALL_RECORD).write_text(text, encoding="utf-8")

    assert generated(root) == frozenset()


def test_a_record_carrying_personal_data_raises_rather_than_reading_as_empty(tmp_path):
    # ⛔ R7's gate runs before a field is read, and a leak is refused as itself
    # rather than swallowed with the malformed ones above.
    # ⚠️ A placeholder, split so the literal never sits in this file whole.
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), GENERATED)
    document = {"installed_api": 2, "files": [{"where": "/" + "home/jane/ONBOARDING.md"}]}
    (root / INSTALL_RECORD).write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(PersonalDataLeak):
        generated(root)
