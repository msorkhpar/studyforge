"""A lesson that ends in a code-examples list, for the ruling that silences the panel.

⭐ Register ruling (2026-09-26): a lesson's code-example panel is a code example,
and a code example is never narrated. This is the fixture every clause of it is
read against: prose, a *Code Examples* heading over a list of one source and its
test, then a later heading and more prose, so the surviving prose has neighbours
on both sides of what falls silent.
"""

from __future__ import annotations

import copy

#: The two code files the list links, relative to the corpus root.
SOURCE = "m/src/main/java/p/Wrapper.java"
TEST = "m/src/test/java/p/WrapperTest.java"

#: The heading that introduces the examples, and the one that ends its blocks.
EXAMPLES_HEADING = "Code Examples"
AFTER_HEADING = "Afterwards"
AFTER_PROSE = "More prose follows the examples, and it is still spoken."


def lesson_key(document: dict) -> str:
    """The key of the document's first lesson section: the one the examples join."""
    return next(one["key"] for one in document["sections"] if one.get("kind") != "practice")


def examples_list(up: str = "../../") -> dict:
    """The list a page draws as its panel: each item one code link and a short label."""
    return {
        "type": "list",
        "ordered": False,
        "items": [
            f"Source: [Wrapper.java]({up}{SOURCE})",
            f"Test: [WrapperTest.java]({up}{TEST})",
        ],
    }


def with_code_examples(document: dict, up: str = "../../") -> dict:
    """A copy of `document` whose first lesson ends in the examples and more prose.

    `up` climbs from the unit's page to the corpus root, so a page placed beside
    the corpus's files marks each link as a code file of it.
    """
    changed = copy.deepcopy(document)
    key = lesson_key(changed)
    section = next(one for one in changed["sections"] if one["key"] == key)
    section["blocks"] = [
        *section["blocks"],
        {"type": "heading", "level": 2, "text": EXAMPLES_HEADING},
        examples_list(up),
        {"type": "heading", "level": 2, "text": AFTER_HEADING},
        {"type": "para", "text": AFTER_PROSE},
    ]
    return changed
