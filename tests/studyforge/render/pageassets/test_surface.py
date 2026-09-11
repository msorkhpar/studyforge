"""Mirror of `src/studyforge/render/pageassets/surface.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.archive.blocks import BLOCK_TYPES
from studyforge.render.pageassets import (
    HOOK_CLASSES,
    STYLE_PARTS,
    SURFACE_CLASSES,
    SURFACE_HOOKS,
    class_for,
    is_vendored,
    text,
)
from studyforge.render.pageassets.surface import (
    _CLASS_OF,
    _FORM_OF,
    ATTRIBUTE_FORM,
    CLASS_FORM,
    KIND_FORM,
)
from tests.support import repository_root

#: ⛔ Derived, not retyped. The unstyled types are whatever the vocabulary has
#: that the surface gives no hook to, so a block type added tomorrow is
#: covered by this test on the day it appears.
UNSTYLED = tuple(name for name in BLOCK_TYPES if name not in SURFACE_CLASSES)

#: The authored parts whose classes are NOT this contract's. ⛔ Vendored CSS
#: names its own classes and is not ours to keep in step with anything;
#: `code-highlight.css` selects on classes **Prism** writes at run time inside
#: the `<code>` the page already shipped, and `video-player.css` on classes Plyr
#: writes into the DOM it builds — no renderer emits either, so they are not part
#: of the markup contract. Two tests below pin each of them to one hook.
LIBRARY_CLASS_PARTS = ("code-highlight.css", "video-player.css")

#: The parts whose class names a RENDERER must emit. ⭐ **Derived from the bundle
#: rather than listed** (`SF-34`): the listed form silently excluded
#: `chrome.css` on the day it was added, which is the shape of defect the whole
#: both-directions contract exists to catch — a new authored stylesheet could
#: target a class nobody publishes and this check would have reported success.
AUTHORED_CSS = tuple(
    name for name in STYLE_PARTS if not is_vendored(name) and name not in LIBRARY_CLASS_PARTS
)

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
    published = set(SURFACE_CLASSES.values()) | set(HOOK_CLASSES.values())
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
    published = set(SURFACE_CLASSES.values()) | set(HOOK_CLASSES.values())
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
    published = set(SURFACE_CLASSES.values()) | set(HOOK_CLASSES.values())
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
    published = set(SURFACE_CLASSES.values()) | set(HOOK_CLASSES.values())
    for name in ("copy-code.js", "video-player.js"):
        for selector in re.findall(r"querySelectorAll\('([^']+)'\)", text(name)):
            for klass in re.findall(r"\.([a-zA-Z][\w-]*)", selector):
                assert klass in published, f"{name} queries an unpublished class {klass!r}"


# --- the population this contract is checked over --------------------------


def test_the_authored_population_is_inhabited_and_comes_from_the_bundle():
    # ⛔ Ruling 48, at the set the two both-directions checks above walk. The
    # listed form of `AUTHORED_CSS` read `("reset.css", "palette.css",
    # "focus.css", "reading.css")`, and on the day `chrome.css` joined the
    # bundle it was silently outside the contract — a new authored stylesheet
    # could have targeted a class nobody publishes and both checks would have
    # reported success. Derived from `STYLE_PARTS`, it cannot happen again.
    assert AUTHORED_CSS, "no authored stylesheet is in the class contract at all"
    assert set(AUTHORED_CSS) == {
        name for name in STYLE_PARTS if not is_vendored(name) and name not in LIBRARY_CLASS_PARTS
    }
    assert "chrome.css" in AUTHORED_CSS
    assert not any(is_vendored(name) for name in AUTHORED_CSS)


def test_the_library_class_parts_are_authored_and_deliberately_outside_the_contract():
    # ⭐ The control for the exclusion: these are ours to ship and not ours to
    # keep class names in step with, and the two tests at the end of this module
    # are what holds each of them to one hook.
    assert all(name in STYLE_PARTS for name in LIBRARY_CLASS_PARTS)
    assert all(not is_vendored(name) for name in LIBRARY_CLASS_PARTS)
    assert not set(AUTHORED_CSS) & set(LIBRARY_CLASS_PARTS)


# --- a hook has a form, and the form decides how it is checked -------------


def test_every_hook_is_answered_for_either_way():
    # ⛔ The half a `KeyError` at import cannot state, in `_CLASS_OF`'s own
    # shape: a hook *removed* from the mapping leaves a form behind for
    # something that no longer exists, and nothing would fail.
    assert tuple(_FORM_OF) == tuple(SURFACE_HOOKS)


@pytest.mark.parametrize("hook", sorted(SURFACE_HOOKS))
def test_every_hook_takes_one_of_the_three_forms_and_no_fourth(hook):
    assert _FORM_OF[hook] in (CLASS_FORM, ATTRIBUTE_FORM, KIND_FORM)


def test_hook_classes_is_exactly_the_class_shaped_subset():
    # ⛔ Derived in the module and re-derived here from the other direction, so
    # a hook that changes form moves out of the class contract on the same day.
    assert HOOK_CLASSES == {
        hook: value for hook, value in SURFACE_HOOKS.items() if _FORM_OF[hook] == CLASS_FORM
    }
    assert set(HOOK_CLASSES) < set(SURFACE_HOOKS), "every hook is a class — then why two names?"


@pytest.mark.parametrize("hook", sorted(h for h, f in _FORM_OF.items() if f == ATTRIBUTE_FORM))
def test_an_attribute_hook_is_the_name_of_a_data_attribute(hook):
    # ⚠️ The form is not cosmetic: it is what decides whether a stylesheet
    # reaches for `.x` or for `[x]`, and those are different pages.
    assert SURFACE_HOOKS[hook].startswith("data-")


@pytest.mark.parametrize("hook", sorted(h for h, f in _FORM_OF.items() if f != ATTRIBUTE_FORM))
def test_a_class_or_kind_hook_is_not_an_attribute_name(hook):
    assert not SURFACE_HOOKS[hook].startswith("data-")


# --- spelled once, and the consumers take it rather than typing it ----------

#: Where a `data-*` hook may be spelled. ⛔ One module, ruled CTO round 45 §12
#: from `SF-14/1` — and this is the census that makes the ruling checkable
#: rather than remembered.
HOOK_OWNER = "src/studyforge/render/pageassets/surface.py"

#: The renderers that address their rows by `data-*`, and the hook each of their
#: published constants must be. ⚠️ Both of them say the same two things about
#: the same rows, which is why the spelling had to stop being plural.
HOOK_CONSUMERS = (
    "src/studyforge/render/container/listing.py",
    "src/studyforge/render/index/disclosure.py",
)

#: `the constant a renderer publishes -> the hook it must be`.
HOOK_CONSTANTS = {
    "KIND_ATTRIBUTE": "kind",
    "LEVEL_KIND": "level",
    "NUMBERING_KIND": "numbering",
    "READABLE_ATTRIBUTE": "readable",
}


def modules_holding(literal):
    """Every Python module under `src/` whose text holds `literal`, as repo paths."""
    root = repository_root()
    return sorted(
        str(path.relative_to(root))
        for path in sorted((root / "src").rglob("*.py"))
        if literal in path.read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("hook", sorted(h for h, f in _FORM_OF.items() if f == ATTRIBUTE_FORM))
def test_an_attribute_hook_is_spelled_as_a_literal_in_exactly_one_module(hook):
    # ⛔ The quoted form, so a sentence in a docstring describing the markup a
    # reader will see — `data-readable="false"` — is prose and not a second
    # definition, while `"data-readable"` on the right of an assignment is.
    found = modules_holding(f'"{SURFACE_HOOKS[hook]}"')
    assert found == [HOOK_OWNER], f"{hook} is spelled in {found}, and the home is ruled"


@pytest.mark.parametrize("path", HOOK_CONSUMERS)
def test_a_consumer_takes_its_hooks_from_the_contract_and_types_none_of_them(path):
    # ⭐ Asserted here rather than in each renderer's own mirror because the
    # claim is the CONTRACT's: *spelled once* is a statement about consumers, and
    # a claim checked only where it is consumed is checked once per consumer and
    # nowhere as a whole.
    source = (repository_root() / path).read_text(encoding="utf-8")
    present = sorted(name for name in HOOK_CONSTANTS if f"\n{name} = " in source)
    assert present, f"{path} publishes no hook constant — renamed, or no longer a consumer?"
    for name in present:
        hook = HOOK_CONSTANTS[name]
        assert f'{name} = SURFACE_HOOKS["{hook}"]' in source, (
            f"{path}: {name} is not taken from the contract"
        )
