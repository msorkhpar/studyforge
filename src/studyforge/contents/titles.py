"""Whether a published title is a declared title, or only the folder slug showing through.

**What it does.** Names every group and unit of a built `Contents` whose
title is in slug form — a group titled exactly its own address segment, or any
title that is lowercase words joined by hyphens with no space. Those are the
titles a sidebar, a breadcrumb and a root index would print as the folder name
instead of the name the corpus declares.

**How you use it.**

    from studyforge.contents import build, slug_titled

    slug_titled(built)                        # ('basics/01-intro', ...) keys, in tree order
    build(manifest, containers, declared_titles=True)   # refuses instead of reporting

**Depends on.** `entries` for the value, and `re`. Standard library only.

## ⭐ A TITLE IS DECLARED, AND THE SLUG IS NEVER A SUBSTITUTE

`build` takes every title from the container maps' own `titles` and each
unit's `title`; it derives none from a folder name. This module is the check
that a declaration was not itself written from the slug. ⛔ It only looks: the
default `build` is unchanged, and `declared_titles=True` is the opt-in that
turns the report into a refusal.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from studyforge.contents.entries import Contents, Group

#: Lowercase letters and digits in hyphen-joined words, with at least one hyphen.
SLUG_FORM = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")


def is_slug_form(title: object, segment: str | None = None) -> bool:
    """Say whether `title` is the slug form of a name: its own segment, or hyphenated lowercase words."""
    if not isinstance(title, str):
        return False
    return title == segment or SLUG_FORM.match(title) is not None


def slug_titled(contents: Contents) -> tuple[str, ...]:
    """Return the key of every group and unit whose title is in slug form, in tree order."""
    found: list[str] = []
    for group in contents.groups:
        found.extend(_walk(group))
    return tuple(found)


def _walk(group: Group) -> Iterator[str]:
    if is_slug_form(group.title, group.segment):
        yield group.key
    for entry in group.entries:
        if is_slug_form(entry.title):
            yield entry.key
    for child in group.groups:
        yield from _walk(child)
