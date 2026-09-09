"""What a slug is, and how a title becomes a candidate one.

**What it does.** Defines the one shape every address segment must already
have — lowercase, ASCII alphanumerics separated by single hyphens — and offers
`slugify` for turning a human title into a candidate of that shape.

**How you use it.** `require_slug(value, what)` at any boundary that accepts a
segment; `is_slug(value)` to ask without raising; `slugify(title)` in an
**adapter**, which then records what it produced. ⛔ Framework code slugifies
nothing at read time: §6 rules that an address is *recorded, never derived*.

**Depends on.** `re` and `errors`. No filesystem, no corpus, no manifest.

⭐ **A slug is a fixed point of `slugify`**, and that is the whole definition —
`is_slug(v)` is `v == slugify(v)` and `v` non-empty. One rule, stated once, so
"is this a slug?" and "make me a slug" can never drift apart. The extraction
source had the same property and used it the same way.

⚠️ **`slugify` is lossy, and the design tolerates that because nothing depends
on it being reversible.** It is ASCII-only: every character outside `[a-z0-9]`
becomes a separator, so `café` and `cafe` both produce `cafe`-ish output and two
distinct titles *can* collide. That is survivable only because §6 rules an
address is **recorded, never derived** — measured on the extraction source's
catalogue, **157 of 1,290 units (12.2%) are served at a slug their title does
not produce**, so deriving one would send one link in eight to a page that is
not there. ⛔ An adapter that slugifies its titles owes itself a collision
check; the framework cannot make one for it, because by the time the framework
sees an address the title is gone.
"""

from __future__ import annotations

import re

from studyforge.address.errors import AddressError

#: Apostrophes are **elided** before the separator rule runs, so `Beginner's`
#: becomes `beginners` and not `beginner-s`. Inherited, and it is measured
#: rather than tasteful: the extraction source serves a lesson at
#: `...-a-beginners-guide`, and the derived `...-a-beginner-s-guide` 404s. An
#: apostrophe sits INSIDE a word where every other mark this rule meets sits
#: BETWEEN words, so dropping it keeps the word whole. Both the typewriter and
#: the curly form are listed: a title copied out of a rendered page carries
#: U+2019 far more often than U+0027.
_APOSTROPHE = re.compile(r"['’ʼ]")

#: Every other run of non-alphanumerics collapses to one hyphen.
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Return `text` as a candidate slug: lowercased, apostrophes dropped, hyphenated.

    Returns the empty string when nothing survives, rather than raising —
    "this title has no slug" is an answer the caller often wants to handle
    (`require_slug` is where it becomes an error).
    """
    lowered = _APOSTROPHE.sub("", (text or "").lower())
    return _NON_ALNUM.sub("-", lowered).strip("-")


def is_slug(value: object) -> bool:
    """Return whether `value` is already a slug — a non-empty fixed point of `slugify`."""
    return isinstance(value, str) and bool(value) and value == slugify(value)


def require_slug(value: object, what: str) -> str:
    """Return `value` unchanged, or raise `AddressError` naming `what` it was.

    ⛔ **It never slugifies for you**, and that is the point of the function.
    Accepting a title here would make "pass a title where a slug is required"
    a silent success, and the failure surfaces later as a directory nobody
    created or a link nobody can follow. `what` names the field so the message
    says where to look — `require_slug(value, "address segment 1")`.
    """
    if not isinstance(value, str) or not value:
        raise AddressError(f"{what} must be a non-empty str, got {value!r}")
    if not is_slug(value):
        raise AddressError(
            f"{what} must already be a slug, got {value!r} "
            f"(did you pass a title? slugify() it first, and record the result)"
        )
    return value
