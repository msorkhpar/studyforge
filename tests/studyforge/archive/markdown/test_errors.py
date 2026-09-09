"""Mirror of `src/studyforge/archive/markdown/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, parse
from studyforge.archive.markdown.errors import MarkdownError as Direct


def test_the_error_is_the_package_s_own_and_is_exported():
    assert MarkdownError is Direct
    assert issubclass(MarkdownError, Exception)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("```py\nx = 1\n", "code fence"),
        ("<details>\n<summary>s</summary>\n\nhidden\n", "<details>"),
        ('<img alt="no source">\n', "<img>"),
    ],
)
def test_the_three_refusals_name_what_could_not_be_represented(text, expected):
    # ⛔ R6: fail loud, never silently short — and name it. A refusal that says
    # only "parse error" makes the next person read the whole document.
    with pytest.raises(MarkdownError) as raised:
        parse(text)
    assert expected in str(raised.value)


def test_a_refusal_names_the_line():
    with pytest.raises(MarkdownError) as raised:
        parse("intro\n\n```py\nx = 1\n")
    assert "line 3" in str(raised.value)


def test_nothing_else_raises_and_prose_is_the_catch_all():
    # ⭐ Only a *classifiable* line must not be swallowed. Everything else
    # falls into a paragraph rather than into an exception — a reader that
    # raised on anything unfamiliar would stop an ingest dead, and the answer
    # to that is a vocabulary that covers real material, not a stricter parser.
    for odd in ("&nbsp; entity", "$$x^2$$", "%%%", ":::note", "a < b > c", "\\newcommand"):
        assert parse(odd + "\n")[0]["type"] == "para", odd
