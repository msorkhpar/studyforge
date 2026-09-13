r"""A `list` block's shape, read once for `validate` and for the fixture check (`W263`).

**What it does.** Walks every block, into container blocks and into list items, and names
where a `list` block breaks spec §6: its keys (the fields, then only `start`), an item that
is neither a string nor an array of strings and whole `list` blocks, or a `start` that is
not an integer.

**How you use it.** `list_problems(blocks)` yields `(where, what)` pairs, and
`check_list_blocks(walk)` yields them as `document` findings. ⛔ `tests/fixture_checks` calls
`list_problems` through this module too, so the two agree through ONE reader.

**Depends on.** `archive.blocks` for the vocabulary, `describe`, `validate.corpus`,
`validate.report`. ⛔ Not `archive.markdown`: this reads what was written, never how.

⚠️ **Only a `list` block's shape.** An unknown block type or a wrong field set is still the
fixture check's alone (`W263/1`); this module does not widen what `validate` refuses beyond
the row.
"""

from __future__ import annotations

from collections.abc import Iterator

from studyforge.archive.blocks import BLOCK_FIELDS, BLOCK_OPTIONAL, CONTAINER_TYPES
from studyforge.describe import describe
from studyforge.validate.corpus import RULE_DOCUMENT, Walk
from studyforge.validate.report import Finding

LIST = "list"


def list_problems(blocks: object, where: str = "blocks") -> Iterator[tuple[str, str]]:
    """Every place a `list` block in `blocks` breaks spec §6, at any depth."""
    if not isinstance(blocks, list):
        return
    for index, block in enumerate(blocks):
        at = f"{where}[{index}]"
        if not isinstance(block, dict):
            continue
        if block.get("type") == LIST:
            yield from _list(block, at)
        elif block.get("type") in CONTAINER_TYPES:
            yield from list_problems(block.get("blocks"), f"{at}.blocks")


def _list(block: dict, at: str) -> Iterator[tuple[str, str]]:
    fields, optional = BLOCK_FIELDS[LIST], BLOCK_OPTIONAL[LIST]
    keys = tuple(block)
    extra = keys[len(fields) :]
    if keys[: len(fields)] != fields or extra != tuple(key for key in optional if key in extra):
        yield (
            at,
            f"has keys {list(keys)}; a list carries {list(fields)}, then only {list(optional)}",
        )
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
        yield at, f"is {describe(item)}; an item is a string, or an array of strings and lists"
        return
    for number, part in enumerate(item):
        here = f"{at}[{number}]"
        if isinstance(part, dict) and part.get("type") == LIST:
            yield from _list(part, here)
        elif not isinstance(part, str):
            yield here, f"is {describe(part)}; a part of an item is a string or a whole list block"


def check_list_blocks(walk: Walk) -> Iterator[Finding]:
    """Refuse, by where it sits, every `list` block spec §6 does not admit (`W263`)."""
    for unit in walk.units:
        for at, what in list_problems(unit.document.get("blocks")):
            yield Finding(RULE_DOCUMENT, unit.where, f"{at} {what} (spec §6)")
