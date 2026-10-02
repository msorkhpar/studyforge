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

⛔ **A mode shows the sections of its `prose` language and the common ones.**
Which code tabs it opens, and the practices it lists, are other parts' work.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from studyforge.render import templates
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
PARTS = (STYLESHEET_NAME, SCRIPT_NAME)

#: The attribute the root element carries and the stylesheet keys on.
MODE_ATTRIBUTE = "data-mode"

#: What `outside_mode` says when a page outside the chosen mode is closed. ⭐ The root carries
#: it only then: absent is `open`, which is today's page.
LOCKED = "locked"
OUTSIDE_ATTRIBUTE = "data-outside"

#: The languages an entry belongs to (a row, a module, and the root of a page that is one), and
#: the words that name them.
ENTRY_ATTRIBUTE = "data-entry-lang"
LABEL_ATTRIBUTE = "data-entry-label"

NEWLINE = "\n"


@dataclass(frozen=True, slots=True)
class Choice:
    """One mode as a page offers it: its id, its words and the language whose prose it reads."""

    id: str
    label: str
    summary: str
    prose: str


@dataclass(frozen=True, slots=True)
class Tag:
    """What an entry (a unit or a module) belongs to when it has nothing common to every mode.

    ⭐ `languages` are the ids its sections are tagged with, `label` the declared names of
    them for a reader, `readers` the `(id, label)` of each mode that shows it normally, and
    `locked` whether, under `outside_mode: locked`, the default mode's view cannot open it.
    ⛔ An entry with common prose has no tag at all: it is never greyed.
    """

    languages: tuple[str, ...]
    label: str
    readers: tuple[tuple[str, str], ...]
    locked: bool = False


@dataclass(frozen=True, slots=True)
class Offer:
    """What a page offers a reader: the modes in declared order and the one a page shows unasked.

    ⭐ Data the renderer takes, so no renderer imports the manifest. `outside` is the
    corpus's `outside_mode` and `tags` the entries that belong to some languages only, by
    their unit or group key.
    """

    choices: tuple[Choice, ...]
    default: str
    outside: str = "open"
    tags: Mapping[str, Tag] = field(default_factory=dict)

    @property
    def locks(self) -> bool:
        """Whether an entry outside the chosen mode is closed rather than only greyed."""
        return self.outside == LOCKED


def offer(
    reading: Reading | None, entries: Mapping[str, tuple[str, ...]] | None = None
) -> Offer | None:
    """The offer a corpus makes, or `None` when it declares no modes (today's page).

    `entries` is `key -> language ids` for each unit or group with nothing common to every mode.
    """
    if reading is None or not reading.modes or reading.default_mode is None:
        return None
    labels = {language.id: language.label for language in reading.languages}
    prose = next(mode.prose for mode in reading.modes if mode.id == reading.default_mode)
    locks = reading.outside_mode == LOCKED
    tags = {
        key: Tag(
            languages=found,
            label=", ".join(labels[language] for language in found),
            readers=tuple((mode.id, mode.label) for mode in reading.modes if mode.prose in found),
            locked=locks and prose not in found,
        )
        for key, found in (entries or {}).items()
        if found
    }
    return Offer(
        choices=tuple(
            Choice(mode.id, mode.label, mode.summary, mode.prose) for mode in reading.modes
        ),
        default=reading.default_mode,
        outside=reading.outside_mode,
        tags=tags,
    )


def attributes(tag: Tag | None) -> str:
    """The attribute an entry's row carries to say which languages it belongs to, or `''`."""
    if tag is None:
        return ""
    return f' {ENTRY_ATTRIBUTE}="{escape_attribute(" ".join(tag.languages))}"'


def label(tag: Tag | None) -> str:
    """The words naming an entry's languages, shown by the stylesheet only outside the mode."""
    if tag is None:
        return ""
    return f"<span {LABEL_ATTRIBUTE}>{escape(tag.label)}</span>"


def openable(tag: Tag | None) -> bool:
    """Whether the default mode's view of this entry is a link."""
    return tag is None or not tag.locked


def link(tag: Tag | None, target: str, body: str) -> str:
    """An entry's link; for a locked entry an anchor with no `href`, out of the tab order.

    ⭐ The address stays in `data-href`, so the client gives the link back when a mode
    that reads the entry is chosen.
    """
    where = escape_attribute(target)
    if tag is not None and tag.locked:
        return f'<a aria-disabled="true" tabindex="-1" data-href="{where}">{body}</a>'
    return f'<a href="{where}">{body}</a>'


def pager_attributes(tag: Tag | None, target: str, rel: str, shown: bool) -> str:
    """The attributes of one neighbour in a bar that holds a chain of them.

    ⭐ The one shown has `rel`; each of the others is `hidden`. A neighbour that belongs to some
    languages only says which, so the client can show it in a mode that reads it.
    """
    lang = ""
    if tag is not None:
        lang = f' data-pager-lang="{escape_attribute(" ".join(tag.languages))}"'
    where = f' href="{escape_attribute(target)}"'
    return f'{lang} rel="{rel}"{where}' if shown else f"{lang}{where} hidden"


def slots(
    made: Offer | None, href: Callable[[str], str], entry: Tag | None = None
) -> dict[str, str]:
    """The three skeleton slots; every one is `''` for a corpus that declares no modes.

    `href` turns a shared file's name into the address this page uses for it, and `entry`
    is the tag of the page's own unit or module, which adds the note a page outside a mode shows.
    """
    if made is None:
        return dict.fromkeys(SLOTS, "")
    known = "||".join(f'm==="{choice.id}"' for choice in made.choices)
    return {
        "rootattributes": (
            f' {MODE_ATTRIBUTE}="{escape_attribute(made.default)}"'
            + (f' {OUTSIDE_ATTRIBUTE}="{LOCKED}"' if made.locks else "")
            + attributes(entry)
        ),
        "modehead": templates.fill(
            "mode-head.html",
            stylesheet=escape_attribute(href(STYLESHEET_NAME)),
            script=escape_attribute(href(SCRIPT_NAME)),
            known=known,
        )
        + NEWLINE,
        "modeswitch": _switch(made) + NEWLINE + _note(made, entry),
    }


def files(made: Offer | None) -> dict[str, str]:
    """`filename -> content` for what a corpus with modes writes beside the bundle; else `{}`."""
    if made is None:
        return {}
    rules = NEWLINE.join(_rule(choice, made.locks) for choice in made.choices)
    return {
        STYLESHEET_NAME: text(STYLESHEET_NAME) + NEWLINE + rules + NEWLINE,
        SCRIPT_NAME: text(SCRIPT_NAME),
    }


def _switch(made: Offer) -> str:
    buttons = NEWLINE.join(
        templates.fill(
            "mode-button.html",
            id=escape_attribute(choice.id),
            prose=escape_attribute(choice.prose),
            label=escape(choice.label),
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


def _note(made: Offer, entry: Tag | None) -> str:
    """The note a page outside a mode shows, in the header; the stylesheet shows it when it applies.

    ⭐ It names the modes that read the page; under `locked` it also holds one control for
    each, which the client answers like the switch.
    """
    if entry is None:
        return ""
    names = ", ".join(escape(name) for _, name in entry.readers)
    readers = f" It is read in: {names}." if names else ""
    if not made.locks:
        return templates.fill("mode-outside-open.html", readers=readers) + NEWLINE
    buttons = " ".join(
        templates.fill("mode-outside-button.html", id=escape_attribute(ident), label=escape(name))
        for ident, name in entry.readers
    )
    return templates.fill("mode-outside-locked.html", readers=readers, buttons=buttons) + NEWLINE


def _rule(choice: Choice, locks: bool) -> str:
    """The rules for one mode: what it hides, and how an entry outside it looks.

    ⭐ A section tagged with another language is not displayed, and an outline line with it.
    A row that belongs to other languages only is greyed and shows its label; a page that does
    carries the note and reads in its own language whatever the mode (every section shown),
    and under `locked` shows nothing else. A section a link points into stays shown while it
    is the target (`data-linked`, set by the client).
    """
    lang = json.dumps(choice.prose)
    root = f'html[{MODE_ATTRIBUTE}="{choice.id}"]'
    outside = f"[{ENTRY_ATTRIBUTE}]:not([{ENTRY_ATTRIBUTE}~={lang}])"
    rules = [
        f"{root} section[data-lang]:not([data-lang={lang}]),\n"
        f'{root} nav[aria-label="Outline"] li[data-lang]:not([data-lang={lang}]) '
        "{ display: none; }",
        f"{root} section[data-lang][data-linked]:not([data-lang={lang}]) {{ display: block; }}",
        f"{root}{outside} section[data-lang]:not([data-lang={lang}]) {{ display: block; }}",
        f'{root}{outside} nav[aria-label="Outline"] li[data-lang]:not([data-lang={lang}]) '
        "{ display: list-item; }",
        f"{root} li{outside}, {root} li{outside} a {{ color: var(--muted); }}",
        f"{root} li{outside} [{LABEL_ATTRIBUTE}] {{ display: inline-block; }}",
        f'{root}{outside} aside[data-section="mode-outside"] {{ display: block; }}',
    ]
    if locks:
        rules.append(
            f"{root}{outside} body > :not(header):not(script) {{ display: none; }}"
        )
    return NEWLINE.join(rules)
