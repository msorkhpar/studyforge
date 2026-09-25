r"""The source's own outline number, left off every title and heading a reader is served.

**What it does.** Removes a leading outline number — `5.1.1.1 `, `3.2.1. `,
`10.7.2 — `, `1. ` — from a title or a heading's text, and from every heading
block in a run of blocks, and leaves every other word alone.

**How you use it.** `without_outline_number(text)` for one string;
`headings_without_outline_numbers(blocks)` for a section's blocks. The served
unit builder applies both to what it serves, and the contents tree to every
title it lists, so the page, its chrome and its narration all read the same
words.

**Depends on.** `re` and `archive.blocks` for the one recursion over the
vocabulary.

## ⛔ Why the number goes, and where it stays

⭐ **The site lists and orders everything itself.** The contents, the rail and
the index already put each unit in its place, so a title that repeats the
source's `5.1.1.1` is a second numbering beside the site's own, and read aloud
it is four numbers before every heading. ⛔ **The archive keeps it**: the
archive records what the source says, `origin.section` is matched against the
heading as the file writes it, and a container map's titles are records. Only
what a reader is SERVED leaves it off, which is a rule this framework applies
to every corpus rather than a setting a corpus chooses.

## ⛔ A number that is part of the words is never touched

⚠️ **The shape is narrow on purpose.** An outline number is at the very start,
is either dotted (`3.2`, `3.2.1`, `3.2.1.`) or one number closed by a full stop
(`3.`), has at most three digits per part, and is followed by a space and then
the words, with an optional dash or colon between. ⭐ So `Java 21 features`,
`ISO 8583 messages`, `Top 10 pitfalls`, `10 tips`, `2024 in review` and a
bare `3.2.1` with nothing after it keep every character. ⚠️ A two-part number
with no closing stop, followed by a lower-case word, reads as a quantity
(`1.5 million requests`, `3.5 seconds`) and is kept too.
"""

from __future__ import annotations

import re

from studyforge.archive.blocks import CONTAINER_TYPES

#: A leading outline number and what separates it from the words.
#: ⛔ Dotted, or a single number closed by a stop; each part at most three digits.
OUTLINE_NUMBER = re.compile(
    r"^(?P<number>\d{1,3}(?:\.\d{1,3})+(?P<stop>\.)?|\d{1,3}\.(?P<single>))"
    r"(?:[ \t]*[—–:]|[ \t]+-)?[ \t]+(?=(?P<next>\S))"
)

#: How many dotted parts make a number that could be a quantity when unstopped.
QUANTITY_PARTS = 2


def without_outline_number(text: str) -> str:
    """Return `text` with its leading outline number removed, or `text` itself.

    ⛔ A value that is not a string is returned as it came: refusing a malformed
    title is the reader's job, never this one's.
    """
    if not isinstance(text, str):
        return text
    match = OUTLINE_NUMBER.match(text)
    if match is None:
        return text
    number = match.group("number")
    unstopped = match.group("single") is None and match.group("stop") is None
    if unstopped and number.count(".") + 1 == QUANTITY_PARTS and match.group("next").islower():
        return text
    return text[match.end() :]


def headings_without_outline_numbers(blocks: object) -> object:
    """Return `blocks` with every heading's outline number removed, at any depth.

    ⭐ **A copy, never an edit**: the blocks are the archive's, and the served
    document is built beside them. A block that is not a heading and holds no
    blocks is the same object; anything that is not a list comes back as it came.
    """
    if not isinstance(blocks, list):
        return blocks
    return [_block(block) for block in blocks]


def _block(block: object) -> object:
    if not isinstance(block, dict):
        return block
    if block.get("type") == "heading":
        return {**block, "text": without_outline_number(block.get("text"))}
    if block.get("type") in CONTAINER_TYPES:
        return {**block, "blocks": headings_without_outline_numbers(block.get("blocks"))}
    return block
