r"""Every block's shape, read once for `validate` and for the fixture check.

**What it does.** Walks every block, into container blocks and into list items, and names
where one breaks spec §6: a block that is not an object, a type not in `BLOCK_TYPES`, keys
that are not its fields then only its `BLOCK_OPTIONAL` keys, and for a `list` block an item
that is neither a string nor an array of strings and whole blocks of an `ITEM_BLOCKS` type
(a nested list or a code block), or a `start` that is not an integer.

**How you use it.** `block_problems(blocks)` yields `(where, what)` pairs, and
`check_block_shapes(walk)` yields them as `document` findings. ⛔ `tests/fixture_checks` calls
`block_problems` through this module too, so the two agree through ONE reader.

**Depends on.** `archive.blocks` for the vocabulary, `describe`, `validate.corpus`,
`validate.report`. ⛔ Not `archive.markdown`: this reads what was written, never how.

⚠️ **A block of an unknown type is named and read no further**: there is no row to read its
keys or what it holds against.
"""

from __future__ import annotations

from collections.abc import Iterator

from studyforge.archive.blocks import (
    BLOCK_FIELDS,
    BLOCK_OPTIONAL,
    BLOCK_TYPES,
    CONTAINER_TYPES,
    ITEM_BLOCKS,
)
from studyforge.describe import describe
from studyforge.sourcepath import source_path_fault
from studyforge.validate.corpus import RULE_DOCUMENT, Walk
from studyforge.validate.report import Finding

LIST = "list"
EXAMPLE = "example"

#: An example's tab, its flags and what it holds. ⛔ Spelled here as `archive.example` spells
#: them, and a test pins the two equal: the archive's names stay inside the archive.
EXAMPLE_TAB_KEYS = ("lang", "span")
EXAMPLE_TAB_OPTIONAL = ("code",)
EXAMPLE_MAX_TABS = 8
EXAMPLE_OUTPUTS = ("compiler", "warning")
EXAMPLE_BLOCKS = ("code",)


def block_problems(blocks: object, where: str = "blocks") -> Iterator[tuple[str, str]]:
    """Every place a block in `blocks` breaks spec §6, at any depth."""
    if not isinstance(blocks, list):
        return
    for index, block in enumerate(blocks):
        yield from _block(block, f"{where}[{index}]")


def _block(block: object, at: str) -> Iterator[tuple[str, str]]:
    if not isinstance(block, dict):
        yield at, f"is {describe(block)}; a block is an object with a type"
        return
    kind = block.get("type")
    if kind not in BLOCK_TYPES:
        yield at, f"has type {describe(kind)}; the block types are {list(BLOCK_TYPES)}"
        return
    fields, optional = BLOCK_FIELDS[kind], BLOCK_OPTIONAL[kind]
    keys = tuple(block)
    extra = keys[len(fields) :]
    if keys[: len(fields)] != fields or extra != tuple(key for key in optional if key in extra):
        then = f", then only {list(optional)}" if optional else ""
        yield at, f"has keys {list(keys)}; a {kind} carries {list(fields)}{then}"
    if kind == LIST:
        yield from _list(block, at)
    elif kind in CONTAINER_TYPES:
        yield from block_problems(block.get("blocks"), f"{at}.blocks")
        if kind == EXAMPLE:
            yield from _example(block, at)


def _example(block: dict, at: str) -> Iterator[tuple[str, str]]:
    """An example's id, its tabs (distinct languages whose spans cover its blocks) and output."""
    if not isinstance(block.get("id"), str) or not block["id"]:
        yield f"{at}.id", f"is {describe(block.get('id'))}; an example is named by an id"
    if "output" in block and block["output"] not in EXAMPLE_OUTPUTS:
        said = describe(block["output"])
        yield f"{at}.output", f"is {said}; output is one of {list(EXAMPLE_OUTPUTS)}"
    blocks = block.get("blocks")
    held = blocks if isinstance(blocks, list) else []
    for number, part in enumerate(held):
        if isinstance(part, dict) and part.get("type") not in EXAMPLE_BLOCKS:
            yield (
                f"{at}.blocks[{number}]",
                f"is {describe(part.get('type'))}; an example holds "
                f"blocks of {list(EXAMPLE_BLOCKS)}",
            )
    tabs = block.get("tabs")
    if not isinstance(tabs, list) or not tabs:
        yield f"{at}.tabs", f"is {describe(tabs)}; tabs is a non-empty array"
        return
    if len(tabs) > EXAMPLE_MAX_TABS:
        yield f"{at}.tabs", f"has {len(tabs)} tabs; an example has at most {EXAMPLE_MAX_TABS}"
    seen: list[object] = []
    covered = 0
    for number, tab in enumerate(tabs):
        here = f"{at}.tabs[{number}]"
        if not isinstance(tab, dict) or tuple(tab) not in (
            EXAMPLE_TAB_KEYS,
            (*EXAMPLE_TAB_KEYS, *EXAMPLE_TAB_OPTIONAL),
        ):
            yield (
                here,
                f"is {describe(tab)}; a tab is an object with {list(EXAMPLE_TAB_KEYS)}"
                f" and optionally {list(EXAMPLE_TAB_OPTIONAL)}",
            )
            continue
        if "code" in tab:
            fault = source_path_fault(tab["code"]) if isinstance(tab["code"], str) else "not text"
            if fault:
                yield f"{here}.code", f"is {fault}; code is the corpus-relative path of a file"
        if not isinstance(tab["lang"], str) or not tab["lang"]:
            yield f"{here}.lang", f"is {describe(tab['lang'])}; a tab names a language by its id"
        elif tab["lang"] in seen:
            yield f"{here}.lang", "repeats a language; the tabs of an example name distinct ones"
        else:
            seen.append(tab["lang"])
        span = tab["span"]
        if not isinstance(span, int) or isinstance(span, bool) or span < 1:
            yield f"{here}.span", f"is {describe(span)}; span is a positive integer"
        else:
            covered += span
    if covered != len(held):
        yield f"{at}.tabs", "do not cover the example's blocks exactly once, in order"


def _list(block: dict, at: str) -> Iterator[tuple[str, str]]:
    if "start" in block and (
        not isinstance(block["start"], int) or isinstance(block["start"], bool)
    ):
        yield f"{at}.start", f"is {describe(block['start'])}; start is an integer"
    items = block.get("items")
    if not isinstance(items, list):
        yield f"{at}.items", f"is {describe(items)}; items is an array"
        return
    for number, item in enumerate(items):
        yield from _item(item, f"{at}.items[{number}]")


def _item(item: object, at: str) -> Iterator[tuple[str, str]]:
    if isinstance(item, str):
        return
    if not isinstance(item, list):
        yield at, f"is {describe(item)}; an item is a string, or an array of strings and blocks"
        return
    for number, part in enumerate(item):
        here = f"{at}[{number}]"
        if isinstance(part, dict) and part.get("type") in ITEM_BLOCKS:
            yield from _block(part, here)
        elif not isinstance(part, str):
            yield (
                here,
                f"is {describe(part)}; a part of an item is a string or a whole block "
                f"of a type in {list(ITEM_BLOCKS)}",
            )


def check_block_shapes(walk: Walk) -> Iterator[Finding]:
    """Refuse, by where it sits, every block spec §6 does not admit."""
    for unit in walk.units:
        for at, what in block_problems(unit.document.get("blocks")):
            yield Finding(RULE_DOCUMENT, unit.where, f"{at} {what} (spec §6)")
