"""The tabs of a two-language example: their look, their keys, and what each mode shows of them.

**What it does.** Composes the part of `modes.css` and `modes.js` that belongs to the
`example` block: the static look and script, then one set of rules per mode (which
languages have a tab, in which order, and whether the block shows at all).

**How you use it.** `render.modes.files` calls `style(choices)` and `script(choices)` and
appends the answers to its own two files; nothing else calls them.

**Depends on.** `pageassets.source` only. ⛔ It names no language (R1): the ids are the
mode's own `tabs` list.

## ⛔ Absent means today, byte for byte

Nothing here is reached for a corpus that declares no modes: `modes.files` answers `{}`
for it and never calls this module, so no rule and no line of this reaches the shared
bundle or the page of any other corpus.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Protocol

from studyforge.render.pageassets.source import text

#: The two parts on disk, composed into `modes.css` and `modes.js`.
STYLE_PART = "example-tabs.css"
SCRIPT_PART = "example-tabs.js"
PARTS = (STYLE_PART, SCRIPT_PART)

#: Where the script takes its data, written once in the part and replaced here.
MARKER = "/*MODE_TABS*/{}"

NEWLINE = "\n"


class Mode(Protocol):
    """What this reads of a mode: its id and the languages it opens a tab for, in order."""

    id: str
    tabs: tuple[str, ...]


def style(choices: Iterable[Mode]) -> str:
    """The look, then one set of rules per mode."""
    return text(STYLE_PART) + NEWLINE.join(_rules(choice) for choice in choices) + NEWLINE


def script(choices: Iterable[Mode]) -> str:
    """The script with each mode's tab order written in."""
    order = {choice.id: list(choice.tabs) for choice in choices}
    return text(SCRIPT_PART).replace(MARKER, json.dumps(order, sort_keys=True))


def _rules(choice: Mode) -> str:
    root = f'html[data-mode={json.dumps(choice.id)}] div[data-example]'
    kept = "".join(f":not([data-lang={json.dumps(lang)}])" for lang in choice.tabs)
    listed = "".join(f":not([data-langs~={json.dumps(lang)}])" for lang in choice.tabs)
    rules = [
        f"{root}{listed} {{ display: none; }}",
        f"{root} [data-lang]{kept} {{ display: none; }}",
    ]
    for position, lang in enumerate(choice.tabs):
        both = f"[data-lang={json.dumps(lang)}]"
        rules.append(f"{root} {both} {{ order: {position}; }}")
    if len(choice.tabs) < 2:
        rules.append(f"{root} [data-example-label] {{ display: none; }}")
    return NEWLINE.join(rules)
