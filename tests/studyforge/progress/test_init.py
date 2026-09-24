"""Mirror of `src/studyforge/progress/__init__.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge import progress
from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.progress import RAISES, Progress, ProgressError
from tests.support import assert_package_contract

HOME = "/" + "home/jane"


def test_states_its_contract():
    assert_package_contract(progress, "studyforge.progress")


def unreadable(root):
    store = Progress(root, 2)
    store.path.mkdir(parents=True)  # a directory where the record should be
    return store


def carries_personal_data(root):
    store = Progress(root, 2)
    store.record_run(
        Address.of("basics", "intro"),
        1,
        "practice-java",
        mode="test",
        exit_code=0,
        commands=["./gradlew test"],
        when="2026-09-12T10:00:00+00:00",
    )
    store.path.write_text(store.path.read_text("utf-8").replace("./gradlew", HOME), "utf-8")
    return store


#: ⛔ Every member of `RAISES` reached from the reader by a fixture.
REACHES = {ProgressError: unreadable, PersonalDataLeak: carries_personal_data}


def test_every_member_of_raises_has_a_fixture_and_nothing_else_does():
    assert set(REACHES) == set(RAISES)


@pytest.mark.parametrize("member", RAISES, ids=lambda m: m.__name__)
def test_each_member_of_raises_is_reached_from_the_reader(tmp_path, member):
    store = REACHES[member](tmp_path)
    with pytest.raises(member):
        store.read()
