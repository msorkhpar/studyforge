"""The stylesheet rules and the script line of the reading modes: what each mode hides.

**What it does.** Holds the per-mode CSS rules of `modes.css` and the swap that lets
`modes.js` read a mode's prose as a list of languages.

**How you use it.** `render.modes.files` calls `rule(choice, locks, several)` once per mode
and `reads(script, offer)` on the script; nothing else does.

**Depends on.** `json`; the offer and choice types are `render.modes`'s, named only for typing.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from studyforge.render.modes import Choice, Offer

#: The attribute the root element carries and the stylesheet keys on.
MODE_ATTRIBUTE = "data-mode"

NEWLINE = "\n"

#: The languages an entry belongs to (a row, a module, and the root of a page that is one), and
#: the words that name them.
ENTRY_ATTRIBUTE = "data-entry-lang"
LABEL_ATTRIBUTE = "data-entry-label"

#: ⭐ What the client does with a mode's prose languages. A mode that reads one language keeps the
#: script's own line; only a corpus with a mode that reads several swaps it for the list-aware one.
SINGLE_READ = "tokens(node, name).indexOf(prose[mode]) === -1"
LISTED_READ = (
    "!prose[mode].split(' ').some(function (one) { "
    "return tokens(node, name).indexOf(one) !== -1; })"
)


def reads(script: str, made: Offer) -> str:
    """Return the script, reading a mode's prose as a list when some mode has several."""
    if not any(choice.prose_also for choice in made.choices):
        return script
    if SINGLE_READ not in script:
        raise ValueError("modes.js no longer holds the line that reads a mode's prose language")
    return script.replace(SINGLE_READ, LISTED_READ)


def rule(choice: Choice, locks: bool, several: bool = False) -> str:
    """Return the rules for one mode: what it hides, and how an entry outside it looks.

    ⭐ A section tagged with another language is not displayed, and an outline line with it.
    A row that belongs to other languages only is greyed and shows its label; a page that does
    carries the note and reads in its own language whatever the mode (every section shown),
    and under `locked` shows nothing else. A section a link points into stays shown while it
    is the target (`data-linked`, set by the client).
    """
    root = f'html[{MODE_ATTRIBUTE}="{choice.id}"]'
    #: ⭐ A mode that reads several languages hides a section only when it is tagged with none of
    #: them (one `:not` each, in the order listed); with one language it is the rule it always was.
    #: ⭐ `=` while each section names one language, `~=` once one may name several.
    match = "~=" if several else "="
    tagged = "".join(f":not([data-lang{match}{json.dumps(one)}])" for one in choice.reads)
    outside = f"[{ENTRY_ATTRIBUTE}]" + "".join(
        f":not([{ENTRY_ATTRIBUTE}~={json.dumps(one)}])" for one in choice.reads
    )
    rules = [
        f"{root} section[data-lang]{tagged},\n"
        f'{root} nav[aria-label="Outline"] li[data-lang]{tagged} '
        "{ display: none; }",
        f"{root} section[data-lang][data-linked]{tagged} {{ display: block; }}",
        f"{root}{outside} section[data-lang]{tagged} {{ display: block; }}",
        f'{root}{outside} nav[aria-label="Outline"] li[data-lang]{tagged} '
        "{ display: list-item; }",
        f"{root} li{outside}, {root} li{outside} a {{ color: var(--muted); }}",
        f"{root} li{outside} [{LABEL_ATTRIBUTE}] {{ display: inline-block; }}",
        f'{root}{outside} aside[data-section="mode-outside"] {{ display: block; }}',
    ]
    if locks:
        rules.append(f"{root}{outside} body > :not(header):not(script) {{ display: none; }}")
    return NEWLINE.join(rules)
