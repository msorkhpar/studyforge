"""Mirror of `src/studyforge/archive/callouts.py` (R12): a quote's GitHub alert, read off its first
line, and a quote without one read exactly as before."""

from __future__ import annotations

import json

import pytest

from studyforge.archive.callouts import QUOTE_KINDS, marked
from studyforge.archive.markdown import parse
from studyforge.narrate.speakable import script


@pytest.mark.parametrize("kind", QUOTE_KINDS)
def test_each_kind_marks_a_quote_and_its_marker_line_is_not_its_text(kind):
    (quote,) = parse(f"> [!{kind.upper()}]\n> Read this first.\n")
    assert quote == {
        "type": "quote",
        "blocks": [{"type": "para", "text": "Read this first."}],
        "kind": kind,
    }


def test_the_kind_is_written_after_the_quote_s_fields():
    (quote,) = parse("> [!Warning]\n> Careful.\n")
    assert list(quote) == ["type", "blocks", "kind"]


@pytest.mark.parametrize(
    "markdown",
    [
        "> A plain note.\n",
        "> **In jPOS 3.** The packager moved.\n",
        "> [!FOO]\n> An unknown word stays text.\n",
        "> Not first: \n> [!NOTE]\n",
        "> [!NOTE] on the same line as text\n",
    ],
)
def test_a_quote_without_a_marker_on_its_own_first_line_is_read_exactly_as_before(markdown):
    (quote,) = parse(markdown)
    assert "kind" not in quote
    assert list(quote) == ["type", "blocks"]


def test_an_unmarked_quote_serialises_byte_for_byte_as_it_did():
    (quote,) = parse("> A plain note.\n")
    written = '{"type": "quote", "blocks": [{"type": "para", "text": "A plain note."}]}'
    assert json.dumps(quote) == written


def test_marked_reads_only_the_first_line():
    assert marked([]) == ("", [])
    assert marked(["[!TIP]", "a", "b"]) == ("tip", ["a", "b"])
    assert marked(["a", "[!TIP]"]) == ("", ["a", "[!TIP]"])


def test_narration_speaks_a_marked_quote_s_text_and_never_its_marker():
    unmarked = parse("> Read this first.\n")
    tagged = parse("> [!NOTE]\n> Read this first.\n")
    said = [(one.id, one.speak) for one in script.units_of("u", "prose", unmarked)[0]]
    assert said == [(one.id, one.speak) for one in script.units_of("u", "prose", tagged)[0]]
    assert said and all("[!" not in speak for _id, speak in said)
