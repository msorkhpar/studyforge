"""Mirror of `src/studyforge/render/pageassets/surface.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.archive.blocks import BLOCK_TYPES
from studyforge.render.pageassets import (
    SURFACE_CLASSES,
    SURFACE_HOOKS,
    class_for,
    text,
)
from studyforge.render.pageassets.surface import _CLASS_OF

#: ⛔ Derived, not retyped. The unstyled types are whatever the vocabulary has
#: that the surface gives no hook to, so a block type added tomorrow is
#: covered by this test on the day it appears.
UNSTYLED = tuple(name for name in BLOCK_TYPES if name not in SURFACE_CLASSES)

#: The parts whose class names a RENDERER must emit. ⛔ Vendored CSS names its
#: own classes and is not ours to keep in step with anything, and
#: `code-highlight.css` selects on classes **Prism** writes at run time inside
#: the `<code>` the page already shipped — no renderer emits one, so they are
#: not part of the markup contract. `test_highlight` covers those instead.
AUTHORED_CSS = ("reset.css", "palette.css", "focus.css", "reading.css")

#: `video-player.css` is authored, but every class in it except the hook is
#: Plyr's own, written by the library into the DOM it builds.
LIBRARY_PREFIXES = ("plyr",)


def classes_targeted(name):
    """Every class the named stylesheet selects on."""
    body = re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)
    return {match for match in re.findall(r"\.([a-zA-Z][\w-]*)", body)}


def test_every_class_the_shared_stylesheet_targets_is_published():
    # ⭐ The silent failure this exists for: a stylesheet and a template that
    # disagree about a class name produce a page that renders, carries every
    # word, and is unstyled — with no error anywhere.
    published = set(SURFACE_CLASSES.values()) | set(SURFACE_HOOKS.values())
    targeted = set()
    for name in AUTHORED_CSS:
        targeted |= classes_targeted(name)
    unpublished = sorted(targeted - published)
    assert unpublished == [], (
        "the stylesheet targets classes no renderer is told about: " + ", ".join(unpublished)
    )


def test_every_published_class_is_actually_styled():
    # The other direction: a name a renderer is told to emit, that nothing
    # styles, is a promise the surface does not keep.
    styled = set()
    for name in AUTHORED_CSS:
        styled |= classes_targeted(name)
    published = set(SURFACE_CLASSES.values()) | set(SURFACE_HOOKS.values())
    unstyled = sorted(published - styled)
    assert unstyled == [], "published but never styled: " + ", ".join(unstyled)


def test_a_class_name_is_a_hook_and_never_a_block_type_read_back():
    # ⛔ R4's argument applied to markup: the archive says what a block is; a
    # class says what the stylesheet may reach. They are deliberately not the
    # same string everywhere, so nothing can be tempted to invert the mapping.
    assert SURFACE_CLASSES["list"] == "items"


@pytest.mark.parametrize("block_type", UNSTYLED)
def test_a_block_styled_as_the_element_it_is_carries_no_class(block_type):
    # ⭐ A class that adds nothing is a class that has to be kept in step for
    # nothing. These are styled as `h2`, `p`, `hr`, `blockquote` and `table`.
    assert class_for(block_type) is None


def test_every_block_type_is_answered_for_either_way():
    # ⛔ The half a `KeyError` at import cannot state: a type *removed* from the
    # vocabulary leaves an answer here for something that no longer exists, and
    # nothing would fail. Both directions, so the mapping is exactly the
    # vocabulary and not merely a superset of it.
    assert tuple(_CLASS_OF) == BLOCK_TYPES


def test_the_keys_come_from_the_vocabulary_and_the_values_do_not():
    # ⭐ The seam, asserted. Keys are the archive's; values are this file's, and
    # `list -> items` is the non-identity entry that stops anything inverting
    # the mapping and reading a class name back as a block type.
    assert set(SURFACE_CLASSES) < set(BLOCK_TYPES)
    assert SURFACE_CLASSES["list"] == "items"


@pytest.mark.parametrize("block_type", sorted(SURFACE_CLASSES))
def test_class_for_answers_for_every_type_that_has_one(block_type):
    assert class_for(block_type) == SURFACE_CLASSES[block_type]


def test_the_player_stylesheet_reaches_for_one_hook_and_otherwise_the_library_s_own():
    # ⚠️ `video-player.css` themes Plyr from outside rather than forking it, so
    # everything it selects on is either the figure hook a renderer emits or a
    # class the library writes into the DOM it builds.
    published = set(SURFACE_CLASSES.values()) | set(SURFACE_HOOKS.values())
    stray = sorted(
        klass
        for klass in classes_targeted("video-player.css")
        if klass not in published and not klass.startswith(LIBRARY_PREFIXES)
    )
    assert stray == [], "video-player.css invents a class: " + ", ".join(stray)


def test_the_highlight_stylesheet_reaches_for_one_hook_and_otherwise_prism_s_tokens():
    # ⛔ It may reach for the code figure and for Prism's token classes, and
    # for nothing else — a highlight rule that named a renderer class would be
    # a second, quieter markup contract.
    targeted = classes_targeted("code-highlight.css")
    assert SURFACE_CLASSES["code"] in targeted
    assert "token" in targeted


def test_the_scripts_query_only_classes_the_contract_publishes():
    # The scripts are the second half of the same agreement, and they fail the
    # same silent way: `querySelectorAll` on a name nothing emits returns an
    # empty list and the enhancement simply never appears.
    published = set(SURFACE_CLASSES.values()) | set(SURFACE_HOOKS.values())
    for name in ("copy-code.js", "video-player.js"):
        for selector in re.findall(r"querySelectorAll\('([^']+)'\)", text(name)):
            for klass in re.findall(r"\.([a-zA-Z][\w-]*)", selector):
                assert klass in published, f"{name} queries an unpublished class {klass!r}"
