"""Mirror of `src/studyforge/render/pageassets/bundle.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.render import modes
from studyforge.render.pageassets import (
    SCRIPT_NAME,
    SCRIPT_PARTS,
    SPRITE_PART,
    SPRITE_PLACEHOLDER,
    STYLE_PARTS,
    STYLESHEET_NAME,
    is_vendored,
    licence_names,
    names,
    script,
    stylesheet,
    text,
    written_files,
)

BUNDLES = (STYLE_PARTS, SCRIPT_PARTS)


@pytest.mark.parametrize("parts", BUNDLES)
def test_every_declared_part_exists_on_disk(parts):
    missing = [name for name in parts if name not in names()]
    assert missing == [], f"declared but absent: {missing}"


def test_every_part_on_disk_is_in_exactly_one_bundle_or_is_the_sprite():
    # ⭐ Both directions, because each failure is silent on its own: a part no
    # bundle reads is dead weight nobody notices, and a part in two bundles
    # ships twice. The sprite is the one exception and it is named — it is
    # substituted into the script rather than concatenated.
    # ⭐ The two files a corpus declaring modes writes beside the bundle are parts on
    # disk too, composed by `render.modes` and never into the shared bundle.
    used = list(STYLE_PARTS) + list(SCRIPT_PARTS) + [SPRITE_PART, *modes.PARTS]
    assert sorted(used) == sorted(names()), "the directory and the bundles disagree"
    assert len(used) == len(set(used)), "a part is composed into more than one bundle"


def test_the_order_is_stated_and_is_not_the_sorted_order():
    # ⛔ Two rules of equal specificity: the last one wins. So the sequence is
    # part of the design, and a bundle built from `names()` would be a
    # stylesheet whose meaning came from the alphabet.
    assert list(STYLE_PARTS) != sorted(STYLE_PARTS)
    assert list(SCRIPT_PARTS) != sorted(SCRIPT_PARTS)


def test_the_reset_comes_first_and_the_palette_before_anything_that_paints():
    order = list(STYLE_PARTS)
    assert order[0] == "reset.css"
    assert order.index("palette.css") < order.index("reading.css")
    assert order.index("reading.css") < order.index("code-highlight.css")
    assert order.index("plyr.css") < order.index("video-player.css")


def test_a_library_comes_before_the_code_that_calls_it():
    order = list(SCRIPT_PARTS)
    assert order.index("plyr.js") < order.index("video-player.js")


@pytest.mark.parametrize("part", ["reset.css", "palette.css", "reading.css", "video-player.css"])
def test_a_part_reaches_the_stylesheet_unaltered(part):
    # A bundle is a concatenation and nothing else: no minifier, no reflow, no
    # re-indent. What is in the file is what is on the page.
    assert text(part) in stylesheet()


def test_composing_twice_gives_identical_bytes():
    # ⛔ R10, asserted rather than assumed: no clock, no directory order, no
    # set iteration anywhere in the composition.
    assert stylesheet() == stylesheet()
    assert script() == script()


def test_the_written_names_carry_no_content_digest():
    # ⛔ §8.2. A digest in the name
    # renames the file and rewrites every page that links it whenever a colour
    # changes — a thousand-file diff for one hex value.
    for name in written_files():
        assert re.fullmatch(r"page\.(css|js)", name), name
        assert not re.search(r"[.-][0-9a-f]{6,}\.", name), f"{name} looks digested"
    assert (STYLESHEET_NAME, SCRIPT_NAME) == ("page.css", "page.js")


def test_the_written_names_are_relative_and_name_no_directory():
    # ⛔ R8 and R4 together: a page's assets resolve relative to the page, so
    # a moved page renders unstyled rather than breaking its identity.
    for name in written_files():
        assert not name.startswith("/") and "/" not in name


def test_written_files_is_the_pair_and_nothing_else():
    written = written_files()
    assert set(written) == {STYLESHEET_NAME, SCRIPT_NAME}
    assert written[STYLESHEET_NAME] == stylesheet()
    assert written[SCRIPT_NAME] == script()


def test_the_icon_sprite_is_substituted_and_not_left_as_a_placeholder():
    # ⭐ One source on disk for the sprite, and no derived copy committed
    # beside it. ⛔ And no fetch: Plyr would otherwise pull it from a CDN on
    # every init, which the `file://` floor cannot do (R8).
    composed = script()
    assert SPRITE_PLACEHOLDER not in composed
    assert "<svg" in composed
    assert "plyr-play" in composed


def test_the_sprite_survives_being_made_into_a_javascript_string():
    # The escape order matters: backslashes first, then quotes, or the second
    # pass escapes the backslash the first one added.
    composed = script()
    sprite = text(SPRITE_PART)
    for marker in re.findall(r'id="(plyr-[a-z-]+)"', sprite)[:5]:
        assert marker in composed


def test_a_part_ending_in_a_line_comment_cannot_swallow_the_next_part():
    # ⛔ The join is a newline for exactly this reason, and the stylesheet is
    # where it can be proved without the sprite substitution in the way.
    from studyforge.render.pageassets import compose

    composed = compose(STYLE_PARTS)
    for first, second in zip(STYLE_PARTS, STYLE_PARTS[1:], strict=False):
        assert text(first) + "\n" + text(second) in composed


def test_no_licence_is_concatenated_into_a_bundle():
    # A licence belongs beside the code it covers; shipping it inside the
    # script would be 1 KB on every page saying nothing to the reader.
    for licence in licence_names():
        assert text(licence) not in script()


#: The properties that make an element a containing block for a `position: fixed`
#: descendant, in the spellings a stylesheet writes them in.
PINNING = re.compile(r"^\s*(?:-\w+-)?(transform|filter|will-change|perspective|contain)\s*:", re.M)


def test_no_authored_stylesheet_makes_a_containing_block_for_a_fixed_descendant():
    # ⛔ **A PROPERTY the practice workspace depends on**.
    # `practice-workspace.css` lays an open practice over the page with
    # `position: fixed`, which answers to the VIEWPORT only while nothing above
    # it makes a containing block: one `transform`, `filter`, `will-change`,
    # `perspective` or `contain` anywhere on an ancestor pins the workspace to
    # that box instead — and it then opens at the width of the reading column
    # with nothing failing anywhere.
    #
    # ⚠️ **VENDORED parts are excluded and the reason is stated.** Plyr's
    # transport and the classes Prism writes inside a `<code>` style their own
    # widget, and no practice panel is ever inside either — so a transform there
    # cannot reach this one. ⭐ Declarations only: comments are stripped first,
    # because `reading.css` says the word in prose.
    authored = [name for name in STYLE_PARTS if not is_vendored(name)]
    assert authored, "no authored stylesheet was read, so this asserts nothing"
    guilty = {}
    for name in authored:
        declarations = re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)
        found = sorted(set(PINNING.findall(declarations)))
        if found:
            guilty[name] = found
    assert not guilty, (
        f"a stylesheet over the practice panel creates a containing block: {guilty} — "
        "the workspace would size to that box instead of the viewport"
    )
