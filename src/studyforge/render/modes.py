"""The reading-modes client: the question a first visit asks, the switch, and what each mode shows.

**What it does.** For a corpus that declares modes, fills three slots of the page
skeleton (the root attribute, the head's two links and boot, the switch with
the first-visit question) and returns the two files written beside
the shared bundle: `modes.css` (the look, then one rule per mode) and `modes.js`.

**How you use it.** A placement calls `slots(offer, href)` for the skeleton and
the site build calls `files(offer)` for the shared directory. Both answer
nothing (empty strings, no files) for a corpus that declares no modes.

**Depends on.** `templates` and `pageassets.source`; `offer` reads a declared
`Reading` and nothing else does.
⛔ It names no language (R1): ids, labels and summaries are the corpus's data.

## ⛔ Absent means today, byte for byte

A corpus with no `modes` gets three empty slots, so the skeleton fills to the
bytes it had before the slots existed, and `files` is empty, so no stylesheet and
no script of this part is written. The shared `page.css` and `page.js` never
carry a rule or a line of it.

## ⭐ What the page carries, and why scripts off still reads right

The markup carries `data-mode="<default_mode>"` on the root element and the
stylesheet carries one rule per mode keyed on that attribute: a section tagged
with a language the mode does not read is not displayed. So with scripts off, in
a crawl, in the preview before an answer and where storage is refused, the page
is the `default_mode` view with no script involved. ⚠️ The switch and the
question ship `hidden`; the script shows them.

⛔ **A mode shows the sections of its `prose` language and the common ones.** The tabs
of an example are `example_tabs`'s, composed into the two files; the practices a mode
lists are another part's work.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from studyforge.render import example_tabs, templates
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.pageassets.source import text

if TYPE_CHECKING:
    from studyforge.corpus.manifest.reading import Reading

#: What the two files are written as, beside `page.css` and `page.js`.
STYLESHEET_NAME = "modes.css"
SCRIPT_NAME = "modes.js"

#: The slots this part fills, in the skeleton's order.
SLOTS = ("rootattributes", "modehead", "modeswitch")

#: The two files, as `pageassets` finds them on disk.
PARTS = (STYLESHEET_NAME, SCRIPT_NAME, *example_tabs.PARTS)

#: The attribute the root element carries and the stylesheet keys on.
MODE_ATTRIBUTE = "data-mode"

NEWLINE = "\n"


@dataclass(frozen=True, slots=True)
class Choice:
    """One mode as a page offers it: its id, its words and the language whose prose it reads."""

    id: str
    label: str
    summary: str
    prose: str
    #: ⭐ The languages the mode opens a tab for, first tab first.
    tabs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Offer:
    """What a page offers a reader: the modes in declared order and the one a page shows unasked.

    ⭐ Data the renderer takes, so no renderer imports the manifest.
    """

    choices: tuple[Choice, ...]
    default: str
    #: ⭐ `(id, label)` of each declared language, for the label over a tab.
    languages: tuple[tuple[str, str], ...] = ()


def offer(reading: Reading | None) -> Offer | None:
    """The offer a corpus makes, or `None` when it declares no modes (today's page)."""
    if reading is None or not reading.modes or reading.default_mode is None:
        return None
    return Offer(
        choices=tuple(
            Choice(mode.id, mode.label, mode.summary, mode.prose, tuple(mode.tabs))
            for mode in reading.modes
        ),
        default=reading.default_mode,
        languages=tuple((language.id, language.label) for language in reading.languages),
    )


def slots(made: Offer | None, href: Callable[[str], str]) -> dict[str, str]:
    """The three skeleton slots; every one is `''` for a corpus that declares no modes.

    `href` turns a shared file's name into the address this page uses for it.
    """
    if made is None:
        return dict.fromkeys(SLOTS, "")
    known = "||".join(f'm==="{choice.id}"' for choice in made.choices)
    return {
        "rootattributes": f' {MODE_ATTRIBUTE}="{escape_attribute(made.default)}"',
        "modehead": templates.fill(
            "mode-head.html",
            stylesheet=escape_attribute(href(STYLESHEET_NAME)),
            script=escape_attribute(href(SCRIPT_NAME)),
            known=known,
        )
        + NEWLINE,
        "modeswitch": _switch(made) + NEWLINE,
    }


def files(made: Offer | None) -> dict[str, str]:
    """`filename -> content` for what a corpus with modes writes beside the bundle; else `{}`."""
    if made is None:
        return {}
    rules = NEWLINE.join(_rule(choice) for choice in made.choices)
    return {
        STYLESHEET_NAME: text(STYLESHEET_NAME)
        + NEWLINE
        + rules
        + NEWLINE
        + example_tabs.style(made.choices),
        SCRIPT_NAME: text(SCRIPT_NAME) + NEWLINE + example_tabs.script(made.choices),
    }


def _switch(made: Offer) -> str:
    buttons = NEWLINE.join(
        templates.fill(
            "mode-button.html", id=escape_attribute(choice.id), label=escape(choice.label)
        )
        for choice in made.choices
    )
    options = "".join(
        templates.fill(
            "mode-option.html",
            id=escape_attribute(choice.id),
            label=escape(choice.label),
            summary=escape(choice.summary),
        )
        for choice in made.choices
    )
    return templates.fill(
        "mode-switch.html", default=escape_attribute(made.default), buttons=buttons, options=options
    )


def _rule(choice: Choice) -> str:
    """The rule that hides what this mode does not read: tagged sections of other languages.

    ⭐ Reached by the section and the outline's line only, so a part that tags
    something else (a tab) is not hidden by it.
    """
    lang = json.dumps(choice.prose)
    root = f'html[{MODE_ATTRIBUTE}="{choice.id}"]'
    return (
        f"{root} section[data-lang]:not([data-lang={lang}]),\n"
        f'{root} nav[aria-label="Outline"] li[data-lang]:not([data-lang={lang}]) '
        "{ display: none; }"
    )
