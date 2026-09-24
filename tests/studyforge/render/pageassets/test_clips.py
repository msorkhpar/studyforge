"""Mirror of `src/studyforge/render/pageassets/clips.py` (R12).

The clip signal's three bodies are a contract with a generated shell script, so
each is read back byte for byte, and nothing else is read as a state.
"""

from __future__ import annotations

import pytest

from studyforge.render.pageassets import (
    ABSENT,
    CLIPS_NAME,
    PRESENT,
    RELEASED,
    STATES,
    clips_script,
    clips_state,
)


def test_the_three_states_are_the_three_the_page_knows():
    assert STATES == (PRESENT, ABSENT, RELEASED)
    assert CLIPS_NAME.endswith(".js") and "/" not in CLIPS_NAME


@pytest.mark.parametrize("state", STATES)
def test_each_body_is_one_ascii_line_that_reads_back_as_its_state(state):
    body = clips_script(state)
    assert body.decode("ascii").count("\n") == 1 and body.endswith(b"\n")
    assert f'"{state}"'.encode() in body
    assert clips_state(body) == state


@pytest.mark.parametrize("state", STATES)
def test_a_body_a_powershell_script_wrote_with_a_carriage_return_still_reads(state):
    assert clips_state(clips_script(state).replace(b"\n", b"\r\n")) == state


@pytest.mark.parametrize(
    "body",
    [b"", b"present\n", clips_script(PRESENT).rstrip(b"\n"), clips_script(PRESENT) + b"x"],
)
def test_anything_else_is_no_state_at_all(body):
    assert clips_state(body) is None


def test_an_unknown_state_is_refused_rather_than_written():
    with pytest.raises(ValueError):
        clips_script("maybe")


def test_the_body_leaves_the_rest_of_the_page_s_namespace_alone():
    # ⭐ The bundle's parts publish `window.studyforge.progress` and the served
    # client `.run`; a signal that assigned the whole object would erase them.
    assert b"window.studyforge = window.studyforge || {};" in clips_script(PRESENT)
