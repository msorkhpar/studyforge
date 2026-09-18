"""What a manifest already records, and what a second run would change (`W329`)."""

from __future__ import annotations

import json

import pytest

from studyforge.skills.onboarding.manifest import render
from studyforge.skills.onboarding.recorded import GROWS, moved, refusal
from tests.studyforge.skills.onboarding import corpora

#: One recorded manifest, in the shape `render` writes it.
RECORDED = render(
    {
        "corpus_api": 2,
        "source": "walkthrough",
        "title": "A Walkthrough Corpus",
        "levels": ["course"],
        "variants": ["prose"],
        "exercises": False,
        "placement": "tree",
        "content": {
            "include": ["src/*.md"],
            "not_material": [{"glob": "README.md", "why": corpora.NOTES["why"]}],
        },
    }
)


def written(**changes) -> str:
    """The same manifest with fields replaced — what a second run would write."""
    document = json.loads(RECORDED)
    content = {**document["content"], **changes.pop("content", {})}
    return render({**document, **changes, "content": content})


def test_an_identical_second_manifest_moves_nothing():
    assert moved(RECORDED, written()) == ()


def test_the_flipped_exercises_answer_is_named():
    # ⛔ The measured failure, at its smallest: a re-survey read this
    # framework's own generated checks as the corpus's graders.
    assert moved(RECORDED, written(exercises=True)) == ("exercises",)


def test_a_changed_include_is_named_and_the_field_list_is_the_manifests_own():
    # ⭐ Derived, never a list somebody remembers to extend: a field added to
    # the contract is compared the day it exists.
    assert moved(RECORDED, written(content={"include": ["*.md"]})) == ("content.include",)


def test_every_answer_that_moved_is_named_at_once():
    # ⛔ `validate`'s rule, for `validate`'s reason: an operator told about one
    # changed answer, who settles it and is then told about the next, has been
    # given a guessing game.
    changed = moved(RECORDED, written(exercises=True, placement="sibling"))

    assert set(changed) == {"exercises", "placement"}


def test_a_grown_not_material_block_is_never_named_here():
    # ⛔ Not an exemption: `W283` states the finer rule for that one field, and
    # comparing it as a single answer would forbid its one legal change.
    grown = {GROWS: [*json.loads(RECORDED)["content"][GROWS], corpora.NOTES]}

    assert moved(RECORDED, written(content=grown)) == ()


@pytest.mark.parametrize("text", ["not json", "[]", '"a manifest"'])
def test_an_unreadable_manifest_names_nothing_here(text):
    # ⚠️ It is refused, in the manifest's own words, by the caller that reads
    # it; a second reason invented here would be a guess.
    assert moved(text, RECORDED) == () and moved(RECORDED, text) == ()


def test_the_refusal_spells_a_scalar_both_ways_and_names_the_ways_forward():
    after = written(exercises=True)

    message = refusal(moved(RECORDED, after), RECORDED, after)

    assert "exercises (False -> True)" in message
    assert "uninstall" in message and "draft" in message


def test_the_refusal_names_a_list_field_without_quoting_it():
    # ⛔ R7: a list carries paths, and a refusal is the first thing anybody
    # pastes somewhere.
    after = written(content={"include": ["*.md"]})

    message = refusal(moved(RECORDED, after), RECORDED, after)

    assert "content.include" in message and "*.md" not in message
