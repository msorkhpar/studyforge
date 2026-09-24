"""Mirror of `src/studyforge/skills/onboarding/compose.py` (R12)."""

from __future__ import annotations

import ast

import pytest

from studyforge.skills.onboarding.compose import ComposeError, module


def test_a_composed_module_parses_and_says_it_is_generated():
    text = module(
        summary="A check.",
        imports=["import json"],
        body=["def test_nothing():", "    assert True"],
    )

    ast.parse(text)
    assert "rather than a fix" in text
    assert "onboarding" in text


def test_a_module_with_nothing_to_say_is_refused_rather_than_emitted():
    with pytest.raises(ComposeError):
        module(summary="  ", imports=[], body=["assert True"])
    with pytest.raises(ComposeError):
        module(summary="A check.", imports=[], body=["", "   "])


def test_the_generated_sentence_has_one_copy():
    # ⚠️ Two generated modules cannot come to describe the same rule
    # differently if there is only one place the sentence lives.
    first = module(summary="One.", imports=[], body=["x = 1"])
    second = module(summary="Two.", imports=[], body=["y = 2"])

    assert "\n".join(first.splitlines()[2:5]) == "\n".join(second.splitlines()[2:5])
