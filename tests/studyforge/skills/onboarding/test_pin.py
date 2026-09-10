"""Mirror of `src/studyforge/skills/onboarding/pin.py` (R12).

⭐ **Two rules are load-bearing here and neither is about JSON:** the pin
records a commit and never a path (R7), and the framework is a sibling checkout
and never a submodule (R18, amended).
"""

from __future__ import annotations

import ast

import pytest

from studyforge.skills.onboarding import pin
from tests.studyforge.skills.onboarding import corpora


def test_the_pin_records_a_commit_and_a_sibling():
    document = pin.pin_document(corpora.COMMIT)

    assert document["commit"] == corpora.COMMIT
    assert document["where"] == "sibling"
    assert document["framework"] == "studyforge"


@pytest.mark.parametrize(
    "value",
    ["../studyforge", "/somewhere/studyforge", "HEAD", "a" * 39, "A" * 40, None, 40],
)
def test_anything_that_is_not_a_commit_is_refused(value):
    # ⛔ The check that keeps a path out of the pin. A relative sibling path is
    # the value most likely to be passed here by mistake, and it is exactly the
    # shape that carries a home directory once somebody resolves it.
    with pytest.raises(pin.PinRefused):
        pin.pin_document(value)


def test_the_refused_value_is_not_quoted_back():
    # ⚠️ W19's rule: the branch fires *because* the value looks like a path,
    # which is precisely when reproducing it puts one in a log.
    with pytest.raises(pin.PinRefused) as refused:
        pin.pin_document("/somewhere/studyforge")

    assert "/somewhere/studyforge" not in str(refused.value)


def test_a_stub_carries_the_pin_and_points_at_a_sibling_rather_than_a_path():
    text = pin.stub("adapter", corpora.COMMIT)

    assert f"pin: {corpora.COMMIT}" in text
    assert "../studyforge/src/studyforge/skills/adapter/SKILL.md" in text
    assert "/home" not in text and "~" not in text


def test_no_stub_copies_a_procedure():
    # ⭐ A pointer, not a copy: the whole stub is a handful of lines, so it
    # cannot have quietly become a stale duplicate of the real procedure.
    assert len(pin.stub("onboarding", corpora.COMMIT).splitlines()) < 15


def test_an_unknown_skill_is_refused_rather_than_stubbed():
    with pytest.raises(pin.PinRefused):
        pin.stub("delivery", corpora.COMMIT)
    with pytest.raises(pin.PinRefused):
        pin.stub_paths(("adapter", "delivery"))


def test_every_declared_skill_has_a_procedure_in_this_repository():
    # ⭐ Checked here rather than in the corpus: a corpus cannot check a skill
    # it does not carry, and a stub pointing at a file that does not exist is
    # the failure a pointer is supposed to make impossible.
    from tests.support import repository_root

    skills = repository_root() / "src" / "studyforge" / "skills"
    missing = [name for name in pin.SKILLS if not (skills / name / "SKILL.md").exists()]
    assert not missing, f"these declared skills have no procedure: {missing}"


def test_the_generated_check_is_a_module_that_parses():
    # ⚠️ Generated code nothing lints, so the parse is the lint.
    ast.parse(pin.pin_test())


def test_the_generated_check_refuses_a_submodule():
    # ⛔ R18, amended: nothing here is pushed to any remote, so a submodule URL
    # has no legal form. The corpus asserts it rather than being told it.
    text = pin.pin_test()

    assert ".gitmodules" in text
    assert "submodule" in text


def test_the_generated_check_names_every_stub_it_must_agree_with():
    text = pin.pin_test(("adapter", "onboarding"))

    assert ".studyforge/skills/adapter.md" in text
    assert ".studyforge/skills/onboarding.md" in text
    assert ".studyforge/skills/reconnaissance.md" not in text


def test_the_generated_check_says_it_is_generated():
    assert "R19" in pin.pin_test()
