"""Mirror of `src/studyforge/skills/execution/standalone/profile.py` (R12): the lock's profile.

⭐ The lock's `profile` key is optional, and a lock without it reads and checks as it always did
(`test_bases.py`, unmodified). The profile named here is made up: nothing reads a real name.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.execution.standalone import bases
from tests.studyforge.skills.execution.standalone.test_bases import (
    EDITOR_TAG,
    RUNNER_TAG,
    check,
    lock,
    parsed,
)

NAME = "example-profile"
THREES, FOURS = "sha256:" + "3" * 64, "sha256:" + "4" * 64
COMPUTED = {"runner": "pr", "editor": "pe"}
IMAGE_EDITOR = f"{bases.PUBLISHED['editor']}-{NAME}"


def entry(**changes) -> dict:
    document = {
        "name": NAME,
        "runner": {"image": f"{bases.PUBLISHED['runner']}-{NAME}", "tag": "pr", "digest": THREES},
        "editor": {"image": f"{bases.PUBLISHED['editor']}-{NAME}", "tag": "pe", "digest": FOURS},
    }
    document.update(changes)
    return document


def locked(**changes) -> bases.Bases:
    return parsed(lock(profile=entry(**changes)))


def test_a_lock_without_a_profile_reads_with_none_and_checks_with_none_declared():
    assert parsed(lock()).profile is None
    check(parsed(lock()))


def test_a_profile_names_its_images_by_the_base_s_published_name_then_the_profile_s():
    one = locked().profile
    assert one.name == NAME
    assert one.runner.reference == f"studyforge-code-toolchain-runner-{NAME}:pr@{THREES}"
    assert one.editor.reference == f"studyforge-code-toolchain-editor-{NAME}:pe@{FOURS}"
    assert bases.profile_image("editor", NAME) == one.editor.image


def test_each_image_of_a_profile_is_optional_but_one_is_needed():
    only = entry()
    del only["editor"]
    assert parsed(lock(profile=only)).profile.editor is None
    with pytest.raises(bases.BasesRefused, match="names profile 'example-profile' and no image"):
        parsed(lock(profile={"name": NAME}))


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ("a string", "profile must be an object"),
        ({"runner": entry()["runner"]}, "must hold a 'name'"),
        ({**entry(), "name": "Bad Name"}, "must hold a 'name'"),
        ({**entry(), "extra": 1}, "unread \\['extra'\\]"),
        ({**entry(), "runner": {**entry()["runner"], "image": "studyforge-code-toolchain-runner"}},
         "profile runner image must be"),
        (
            {**entry(), "editor": {**entry()["editor"], "image": "acct/" + IMAGE_EDITOR}},
            "not a bare name",
        ),
        ({**entry(), "runner": {**entry()["runner"], "digest": "sha256:abc"}}, "digest"),
        ({**entry(), "runner": {**entry()["runner"], "note": "x"}}, "exactly"),
    ],
)
def test_a_profile_entry_that_could_not_be_pulled_or_is_not_the_published_name_is_refused(
    document, message
):
    with pytest.raises(bases.BasesRefused, match=message):
        parsed(lock(profile=document))


def test_a_profile_the_course_declares_and_the_toolchain_computes_passes():
    check(locked(), profile_declared=NAME, profile_tags=COMPUTED)


def test_a_profile_with_a_runner_only_passes_and_needs_the_runner():
    only = entry()
    del only["editor"]
    check(parsed(lock(profile=only)), profile_declared=NAME, profile_tags=COMPUTED)
    no_runner = entry()
    del no_runner["runner"]
    with pytest.raises(bases.BasesRefused, match="names no runner for profile"):
        check(parsed(lock(profile=no_runner)), profile_declared=NAME, profile_tags=COMPUTED)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"profile_declared": None}, "and the course declares no profile"),
        ({"profile_declared": "other"}, "and the course declares 'other'"),
        ({"profile_tags": None}, "cannot be checked"),
        ({"profile_tags": {"runner": "x", "editor": "pe"}}, "runner of profile .*locked at tag pr"),
        ({"profile_tags": {"runner": "pr", "editor": "x"}}, "editor of profile .*locked at tag pe"),
    ],
)
def test_a_profile_that_is_not_the_course_s_or_not_computed_is_refused_by_name(kwargs, message):
    arguments = {"profile_declared": NAME, "profile_tags": COMPUTED, **kwargs}
    with pytest.raises(bases.BasesRefused, match=message):
        check(locked(), **arguments)


def test_a_course_that_declares_a_profile_and_a_lock_without_one_is_refused():
    refusal = "declares profile 'example-profile'.*names no profile"
    with pytest.raises(bases.BasesRefused, match=refusal):
        check(parsed(lock()), profile_declared=NAME, profile_tags=COMPUTED)


def test_the_profile_is_checked_beside_the_unchanged_checks_of_the_base():
    with pytest.raises(bases.BasesRefused, match="runner base is locked at tag a"):
        check(locked(), profile_declared=NAME, profile_tags=COMPUTED,
              toolchain={"runner": "z", "editor": EDITOR_TAG})
    assert RUNNER_TAG == "a"


def test_the_lock_s_text_round_trips_through_the_reader(tmp_path):
    path = tmp_path / "bases.json"
    path.write_text(json.dumps(lock(profile=entry())), encoding="utf-8")
    assert bases.read(path, placeholder=True).profile.name == NAME
