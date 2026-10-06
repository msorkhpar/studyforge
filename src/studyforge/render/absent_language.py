"""What a corpus that greys the languages a block or a practice lacks adds to the modes files.

**What it does.** Composes the part of `modes.css` and `modes.js` that belongs to
`absent_language: grey`: the static look and script, then one set of rules per mode that
shows the sentence naming the languages that carry an example, greys a practice card the mode
does not list, and lets a practice the mode lists read in any language its prose is not.

**How you use it.** `render.modes.files` calls `style(choices)` and `script()` for an offer
whose `grey` is set and appends the answers to its own two files; nothing else calls them.

**Depends on.** `pageassets.source` only. ⛔ It names no language (R1): the ids are each mode's
own `tabs` and `practices` lists.

## ⛔ Absent means today, byte for byte

A corpus that leaves `absent_language` out (or says `hide`) never reaches this module, so no
rule and no line of it is written for it.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Protocol

from studyforge.render.pageassets.source import text

STYLE_PART = "absent-language.css"
SCRIPT_PART = "absent-language.js"
PARTS = (STYLE_PART, SCRIPT_PART)

NEWLINE = "\n"


class Mode(Protocol):
    """What this reads of a mode: its id and the languages it opens a tab and practices for."""

    id: str
    tabs: tuple[str, ...]
    practices: tuple[str, ...]


def style(choices: Iterable[Mode]) -> str:
    """Return the look, then one set of rules per mode."""
    return text(STYLE_PART) + NEWLINE.join(_rules(choice) for choice in choices) + NEWLINE


def script() -> str:
    """Return the script, which holds no per-corpus data: it reads the page."""
    return text(SCRIPT_PART)


def _rules(choice: Mode) -> str:
    mode = f"html[data-mode={json.dumps(choice.id)}]"
    rules = [
        f"{mode} div[data-example][data-missing~={json.dumps(lang)}] "
        "[data-example-missing] { display: block; }"
        for lang in choice.tabs
    ]
    #: ⭐ A practice's statement and panel read with the languages the mode lists practices for,
    #: whatever language its prose is. `revert` leaves a closed one closed: the workspace shuts the
    #: ones it is not showing with `hidden`, which the browser's own rule honours.
    for lang in choice.practices:
        word = json.dumps(lang)
        rules.append(
            ", ".join(
                f"{mode} section[{mark}][data-lang~={word}]"
                for mark in ('data-kind="practice"', "data-practice", "data-practice-quiz")
            )
            + " { display: revert; }"
        )
    outside = "".join(
        f":not([data-practice-lang~={json.dumps(lang)}])" for lang in choice.practices
    )
    card = f"{mode} li[data-practice-card][data-practice-lang]{outside}"
    rules.append(f"{card}, {card} a {{ color: var(--muted); }}")
    rules.append(f"{card} [data-practice-carriers] {{ display: block; }}")
    return NEWLINE.join(rules)
