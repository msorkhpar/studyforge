r"""What the root index is written as, in what order, out of which templates.

**What it does.** Composes the one page a reader lands on first: the same
skeleton every other page of the site has, filled with the corpus's own title
and its whole tree.

**How you use it.** `compose(document, placement)` returns the page's text;
`index.render` is the public entry point and turns it into bytes.

**Depends on.** `render.templates` for the markup, `disclosure` for the body,
`render.markup` for the escaping, and `render.page` for `PageError`.
⛔ Not on `corpus.placement.identity` — see below — and not on `contents`:
`assemble` has already turned the two documents into a record by the time
anything here runs.

## ⛔ The skeleton is `page.html`, the unit page's own, and that is the design

⭐ **The three documents are one product.** E03 asks this page to share the unit
page's palette and type stack *by importing them rather than restating them*;
sharing the **skeleton** is that ruling taken as far as it goes, and it is why
this task adds no template file and no asset. ⚠️ A second skeleton would be a
second `<head>`, a second masthead and a second place a `<meta viewport>` has to
be remembered — and the day one gains a region the other silently would not.

⛔ **Nine of the skeleton's slots are empty here, and they are empty
explicitly.** `templates.fill` refuses a placeholder with no value **and** a
value with no placeholder, so each one is passed `""` by name rather than
omitted — which means the day the skeleton drops a slot this module fails by
name instead of quietly losing a region. ⭐ **And the day it GAINS one this
module fails too, which is how `breadcrumb` arrived** (`SF-15`).

⚠️ **Each absence is a fact rather than an oversight:**

| slot | why this page has nothing to put in it |
|---|---|
| `breadcrumb` | ⛔ the trail says where in the hierarchy the reader is, and this
page is where every trail ends: a crumb for it would be a link to itself |
| `identity` | ⛔ see below — the index is the artifact identity does not describe |
| `meta` | a second masthead line would be this framework's own sentence about
a corpus, and there is no corpus datum for it that the tree does not already
say (R1) |
| `nav` | the between-pages bar points at neighbours in reading order, and the
index has none: it is where that order begins |
| `outline` | a unit page's outline is its own headings; this page's body *is* an outline |
| `mark` | ⛔ a read mark is a UNIT's, and the control belongs on the page
whose reading it records (`SF-30`). ⭐ The marks themselves DO reach this page —
as a state on the rows this tree already keys by unit key — but that is the
shared script's work at read time, not a region this module fills |
| `pending` | practices belong to a unit |
| `rail` | ⛔ the rail exists to reach the OTHER containers from inside one
(`W324`), and this page is inside none of them: its body already lists every
container there is, so a rail here would be the same tree rendered twice on one
page |
| `player` | narration belongs to a unit (`SF-18`) |

## ⛔ The root index carries NO identity block, and that is not an omission

⚠️ **R4's block answers *which unit or container is this*, and the index is
neither.** `placement.identity.KINDS` holds exactly two members and an
`Identity` requires a non-empty address; there is no address this page could
give, because it is the page *about* every address.

⭐ **Nothing looks for one, and that is checked rather than assumed:** a scan
globs the two page suffixes this framework mints, and `is_unit_page` and
`is_container_page` both refuse `ROOT_INDEX_FILENAME` — so the index is outside
every scan's population, by name, before any file is opened. ⛔ Minting a third
kind to say *"I am the index"* would be an `identity_api` change made to satisfy
a rule that does not reach this page.

## ⛔ This module is the format (R10)

⚠️ The order of the slots below **is** the page, and an unchanged document must
re-render to identical bytes. ⛔ So: no clock, no filesystem enumeration, no set
iteration, and every optional region is exactly empty or exactly its markup plus
one newline — never a conditional newline somewhere else.
"""

from __future__ import annotations

from studyforge.render import templates
from studyforge.render.index import disclosure
from studyforge.render.index.entries import Document
from studyforge.render.index.placement import Placement
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.page import PageError

#: The skeleton every page of this site is filled from — the unit page's own.
SKELETON = "page.html"

#: Every page ends in exactly one newline. ⚠️ Appended here rather than left as
#: a trailing blank line in the template, because the loader strips one trailing
#: newline so an editor cannot silently lengthen it.
TRAILING_NEWLINE = "\n"

#: The skeleton slots the root index has nothing to put in. ⛔ Named and passed
#: rather than omitted — see this module's docstring for what each absence is.
EMPTY_SLOTS = (
    "breadcrumb",
    "identity",
    "mark",
    "meta",
    "nav",
    "outline",
    "pending",
    "player",
    "rail",
)


def compose(document: Document, placement: Placement) -> str:
    """Return the root index's exact text.

    ⛔ Pure: the same document and the same placement give byte-identical
    output, every run, on every machine (R10).
    """
    try:
        return (
            templates.fill(
                SKELETON,
                title=escape(document.title),
                heading=escape(document.title),
                stylesheet=escape_attribute(placement.stylesheet()),
                script=escape_attribute(placement.script()),
                body=disclosure.render(document),
                **dict.fromkeys(EMPTY_SLOTS, ""),
            )
            + TRAILING_NEWLINE
        )
    except templates.TemplateError as error:
        # ⛔ Re-typed, not re-worded: `templates` owns what a fillable skeleton
        # is, and a caller rendering a whole site catches one family for every
        # kind of page. ⛔ **Narrow on purpose** — `PersonalDataLeak` is
        # deliberately outside this branch and travels through as itself
        # (Ruling 58), so a leak is never logged as one more page that did not
        # render.
        raise PageError(f"the root index cannot be composed: {error}") from None
