"""A non-object block reaches no `.get` on the READ path either.

⛔ **A module of its own rather than a section of `test_blocks.py`, and R11 is the
reason**: the answer to a module near its ceiling is a SPLIT, not a shorter comment.

⭐ **The subject is also genuinely its own**: `test_blocks.py` asserts the
VOCABULARY and the BUILD path's guard; this asserts what happens to a document that
was never built here — one a hand or an adapter wrote and `parse` read off disk.

## ⛔ The builder refuses, and so must the reader

⚠️ `archive.blocks.counts_of` refuses a non-object block by name through
`archive.document.build`. ⛔ **But nothing BUILDS a hand-written document.** It is
parsed, and `parse` checks the key set and the version and never a block's SHAPE —
so `read_layout` must guard `tail[0].get("type")` itself.

⛔ `read_layout` over the document these tests build, three ways, without the guard:

```text
A: read_layout, hand-written        AttributeError: 'str' object has no attribute 'get'
B: parse() then read_layout         parse ACCEPTED it; then the same AttributeError
C: the same blocks through build()  ArchiveError: …blocks[5] is a str; a block is an
                                    object with a type
```

⭐ **C is the sentence the reader needs and A and B are not**: an `AttributeError`
names a TYPE, where a refusal has to name the BLOCK and the FILE.
"""

from __future__ import annotations

import json

import pytest

from studyforge.archive.blocks import (
    LESSON_HEADING,
    STARTING_CODE_HEADING,
    STATEMENT_HEADING,
    Layout,
    read_layout,
)
from studyforge.archive.document import RAW_API, parse
from studyforge.archive.errors import ArchiveError

#: Everything `json.loads` can produce where a block belongs, but an object.
#: ⛔ Closed on the *domain* rather than on taste (a closed set, R6): JSON has
#: six value kinds and five of them are here, so the shape nobody thought of cannot
#: be the one that gets through. ⚠️ Spelled again rather than imported from
#: `test_blocks.py`: a test module importing another test module's fixtures couples
#: two subjects that this split exists to separate, and the set is a property of
#: JSON rather than of either module.
NOT_OBJECTS = ("a string", 7, 1.5, True, None, ["nested"])


def practice(tail=None) -> dict:
    """A laid-out practice document, assembled from the vocabulary's own headings.

    ⭐ The three headings are IMPORTED, never retyped, so this fixture cannot drift
    from the constants `read_layout` matches against — which is the whole of what
    "derive from one source of truth" asks of a test.
    """
    blocks = [
        {"type": "heading", "level": 2, "text": STATEMENT_HEADING},
        {"type": "para", "text": "Do the thing."},
        {"type": "heading", "level": 2, "text": LESSON_HEADING},
        {"type": "para", "text": "Here is how."},
        {"type": "heading", "level": 2, "text": STARTING_CODE_HEADING},
    ]
    blocks.extend(tail if tail is not None else [{"type": "code", "lang": "java", "text": "//"}])
    return {"kind": "practice", "blocks": blocks}


#: Where the fence sits in `practice()`'s blocks. ⛔ Derived rather than retyped, so
#: a change to the fixture moves every assertion with it.
FENCE_AT = len(practice()["blocks"]) - 1


@pytest.mark.parametrize("block", NOT_OBJECTS)
def test_W297_a_non_object_block_is_refused_by_name_through_read_layout(block):
    # ⛔ The refusal `build` gives, given by the reader too.
    # ⭐ `ArchiveError` is a `ValueError`, so an `AttributeError` escaping here
    # FAILS this test rather than passing it — which is what makes the assertion
    # an instrument and not a restatement of the fix.
    with pytest.raises(ArchiveError) as raised:
        read_layout(practice(tail=[block]), "practice-1.json")

    assert f"blocks[{FENCE_AT}]" in str(raised.value), "the refusal names which block"
    assert "practice-1.json" in str(raised.value), "and which document"
    assert "a block is an object with a type" in str(raised.value)


@pytest.mark.parametrize("at", range(FENCE_AT + 1))
def test_W297_the_guard_runs_before_the_layout_is_read_and_not_only_at_the_fence(at):
    # ⛔ **The neighbour, asserted rather than assumed** (a
    # demonstrated guarantee lends its credibility to the undemonstrated thing
    # beside it). `tail[0]` was the read that CRASHED — but `_is_h2` merely returns
    # False for a non-object, so guarding only the fence would leave every other
    # position silently unread and the document refused for the WRONG reason:
    # "its blocks do not carry the three headings", when the truth is that one of
    # them is a string.
    blocks = practice()["blocks"]
    blocks[at] = "not an object"

    with pytest.raises(ArchiveError) as raised:
        read_layout({"kind": "practice", "blocks": blocks}, "practice-1.json")

    assert f"blocks[{at}]" in str(raised.value)
    assert "a block is an object with a type" in str(raised.value)


def test_W297_the_read_path_refuses_what_the_builder_already_refuses():
    # ⛔ **The whole guard, taken through the door such a document actually
    # arrives by.** Not `build`: nothing builds a hand-written or adapter-written
    # document. ⭐ So this parses one off its own text and then reads it, which is
    # exactly what a consumer of an adapter's archive does.
    parsed = parse(json.dumps({"raw_api": RAW_API, **practice(tail=["x"])}), "practice-1.json")

    with pytest.raises(ArchiveError) as raised:
        read_layout(parsed, "practice-1.json")

    assert f"blocks[{FENCE_AT}]" in str(raised.value)


def test_W297_parse_accepts_it_and_that_is_the_boundary_not_an_oversight():
    # ⚠️ **Named so the division of labour is readable.** `parse` answers four
    # questions and shape is not among them — `validate` imports `archive`, so
    # `parse` cannot ask `validate.blocks` without the archive depending on its own
    # consumer. ⛔ That is precisely why the READER has to refuse: if neither `parse`
    # nor `read_layout` did, nothing on this path ever would.
    accepted = parse(json.dumps({"raw_api": RAW_API, **practice(tail=["x"])}), "practice-1.json")

    assert accepted["blocks"][FENCE_AT] == "x"


def test_W297_a_practice_of_objects_still_reads_its_layout_unchanged():
    # ⭐ The positive direction, or every refusal above is satisfied by a
    # `read_layout` that refuses everything.
    layout = read_layout(practice(), "practice-1.json")

    assert isinstance(layout, Layout)
    assert layout.statement == ({"type": "para", "text": "Do the thing."},)
    assert layout.lesson == ({"type": "para", "text": "Here is how."},)
    assert layout.starting_code == "//"
    assert layout.starting_lang == "java"


def test_W297_a_practice_that_is_merely_not_laid_out_still_gets_its_own_refusal():
    # ⛔ **The two refusals must not collapse into one.** A practice whose blocks
    # are all objects but carry the wrong headings is R6's "looking finished while
    # being short", and it must still be told which three headings it owes — not
    # told that a block is not an object, which would be false.
    with pytest.raises(ArchiveError) as raised:
        read_layout(practice(tail=[{"type": "para", "text": "not a fence"}]), "practice-1.json")

    message = str(raised.value)
    assert "a block is an object with a type" not in message
    for heading in (STATEMENT_HEADING, LESSON_HEADING, STARTING_CODE_HEADING):
        assert heading in message


def test_W297_a_lesson_is_not_this_functions_business_however_its_blocks_are_shaped():
    # ⚠️ **The boundary, named so it is not read as an oversight.** `read_layout`
    # asks what a PRACTICE's parts are; a lesson has none, so its `kind` returns
    # before any block is reached and nothing is refused. ⛔ A malformed block in a
    # lesson is `counts_of`'s to refuse on the way in and `validate.blocks`'s to
    # name in full — widening this function to it would make it answer a question
    # it was never asked.
    assert read_layout({"kind": "lesson", "blocks": ["not an object"]}, "x") is None
