r"""The list of units a container page exists to show, and the one gate on it.

**What it does.** Renders a container's units, in the order the container
declared them, as an ordered list — one row per unit, linked when the unit has a
page and plainly listed when it has not.

**How you use it.** `listing.render(document.items)` returns the markup;
`container.document` puts it in the page's body.

**Depends on.** `render.markup` for escaping and the href gate, `entries`,
and `render.page` for `PageError`. ⛔ Nothing that knows where a file is: an
`Item` arrives with its href already answered.

## ⛔ A refused href RAISES here, and that is deliberate (Ruling 56)

⚠️ **`page.navigation._link` drops a slot whose scheme is refused**, on the
argument that chrome which cannot be followed is worse than chrome that is not
there. ⭐ **That argument is right for the bar and wrong for this list**: the
bar is chrome and this list is the page. ⛔ A silently dropped anchor here turns
a module's contents into unclickable text — the reader sees every title, every
row is present, `validate` passes, nothing logs, and not one unit can be opened.

⚠️ **`SF-13/1` is why this is spelled out rather than assumed.** The bar lost 6
of the `depth2` corpus's 13 slots under `sibling` placement and the acceptance
clause beside it still passed. ⭐ The lesson taken here is not *"widen the
gate"* — `W57` did that, correctly — it is that **the emitter and the gate must
agree about what a refusal means**, and a page whose whole content is links
cannot answer *"drop it"*.

## ⛔ Markup on one line, in code, and not in a template (R13)

⭐ `render/page/__init__.py` draws the line and this is on its far side: *"loop
bodies and inline wrappers stay in code, because a file for a closing tag
removes no duplication and adds a hop."* ⚠️ `navigation.outline` renders exactly
this shape — a `<nav>`, an `<ol>`, a row per entry — the same way.

## ⭐ Not one class name is typed here either

⚠️ Every hook is an element, an `aria-label` or a `data-*` attribute, which is
what let `SF-34` be scheduled a milestone after the markup it styles. ⛔ A class
would cost an entry in `SURFACE_HOOKS` and one in `chrome.css`, in two packages
this task does not own — and a class name with no rule is not styling.
"""

from __future__ import annotations

from studyforge.render.container.entries import Item
from studyforge.render.markup import escape, escape_attribute, inline, safe_href
from studyforge.render.page import PageError

#: What the list is labelled for a reader who cannot see it. ⛔ This framework's
#: own structural word, never a corpus's: every string on the page that names
#: the *material* comes out of the document (R1).
LIST_LABEL = "Units"

#: The attribute that says whether a row could be linked. ⚠️ `data-*` rather
#: than a class, so this page needs no entry in a published class set — see the
#: module docstring.
READABLE_ATTRIBUTE = "data-readable"

#: What wraps a unit's numbering, so a stylesheet can reach it without the
#: numbering being glued to the title in one string.
NUMBERING_KIND = "numbering"


def render(items: tuple[Item, ...]) -> str:
    """Return the container's units as one ordered list, in declared order.

    ⛔ **The declared order is used, never re-derived.** The container reader
    has already refused any map whose ordinals are not contiguous from 1, so the
    declared order *is* the ordinal order; a renderer that sorted would be the
    second orderer `contents` was written to prevent (`SF-13`).
    """
    rows = "".join(_row(position, item) for position, item in enumerate(items, start=1))
    return f'<nav aria-label="{LIST_LABEL}"><ol>{rows}</ol></nav>'


def _row(position: int, item: Item) -> str:
    """Return one unit's row: linked when it has a page, plain when it has not."""
    body = f"{_numbering(item)}{inline(item.title)}"
    if item.href is None:
        return f'<li {READABLE_ATTRIBUTE}="false">{body}</li>'
    target = safe_href(item.href)
    if target is None:
        # ⛔ The href is DESCRIBED by its position and never reproduced (R7).
        # This branch fires precisely because the value is not a permitted
        # relative reference — which is the branch an absolute path and a
        # rooted href both arrive at — and it runs over every unit in a corpus,
        # into a build log. The position is what tells the author where to look.
        raise PageError(
            f"the unit at position {position} of this container carries a link that is "
            f"neither a permitted scheme nor a relative reference inside the site; it "
            f"is refused rather than dropped, because on this page the links are the "
            f"content and a dropped one is a row nobody can open"
        )
    return f'<li {READABLE_ATTRIBUTE}="true"><a href="{escape_attribute(target)}">{body}</a></li>'


def _numbering(item: Item) -> str:
    """Return the reader-facing numbering and its trailing space, or `''`.

    ⚠️ Empty for material that numbers nothing, and the space goes with it —
    a conditional separator left in the caller is a page that differs from its
    golden by one character on every unnumbered corpus.
    """
    if not item.numbering:
        return ""
    return f'<span data-kind="{NUMBERING_KIND}">{escape(item.numbering)}</span> '
