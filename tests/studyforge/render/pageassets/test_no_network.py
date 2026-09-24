"""R8's floor: the page opens from a file, and asks for nothing.

Mirrors no source module — it asserts a property of `render/assets/`, which is
data. ⛔ The failure it guards is the one the rendering design calls a
trap: code that passes every served test and then dies silently over `file://`.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render.pageassets import (
    SCRIPT_PARTS,
    STYLE_PARTS,
    is_vendored,
    script,
    text,
    written_files,
)

AUTHORED = tuple(name for name in STYLE_PARTS + SCRIPT_PARTS if not is_vendored(name))

#: What a browser actually goes and fetches. ⚠️ Deliberately not "any string
#: beginning `http`": an XML namespace and a DOCTYPE system identifier are
#: *identifiers*, never requests, and a check that could not tell them apart
#: would have to be turned off the first time an SVG was vendored.
FETCHING = (
    re.compile(r"@import\b"),
    re.compile(r"url\(\s*['\"]?https?:", re.IGNORECASE),
    re.compile(r"\b(?:src|href)\s*=\s*['\"]https?:", re.IGNORECASE),
    re.compile(r"\bfetch\s*\(\s*['\"]https?:", re.IGNORECASE),
    re.compile(r"\bXMLHttpRequest\b"),
    re.compile(r"@font-face\b"),
)

#: Plyr's own network paths, and the option that disarms each. ⚠️ The vendored
#: bundle CONTAINS remote endpoints — for streaming providers this site never
#: uses — so the check is that no code path here can reach one, not that the
#: bundle is free of strings. Asserting the latter would mean editing vendored
#: code to pass a test, which is the rule this project actually holds.
DISARMED = (
    ("the icon sprite", "loadSprite: false"),
    ("the icon base URL", "iconUrl: ''"),
    ("the blank video", "blankVideo: ''"),
)


@pytest.mark.parametrize("name", AUTHORED)
@pytest.mark.parametrize("pattern", FETCHING, ids=lambda p: p.pattern[:24])
def test_no_authored_asset_asks_the_network_for_anything(name, pattern):
    assert pattern.search(text(name)) is None, f"{name} would fetch: {pattern.pattern}"


@pytest.mark.parametrize("what,option", DISARMED)
def test_every_network_path_the_player_has_is_disarmed(what, option):
    assert option in text("video-player.js"), f"{what} is not turned off"


def test_the_sprite_is_carried_in_the_page_rather_than_fetched():
    # ⭐ The one place a fetch would otherwise happen on EVERY player init.
    assert "<svg" in script()
    assert "cdn." not in script().split("<svg")[0][-4000:]


def test_the_fonts_are_system_stacks_and_not_downloads():
    # ⛔ A web font is a network fetch, and it is the easiest one to add by
    # accident — a single `@import` at the top of a stylesheet.
    palette = text("palette.css")
    assert "@font-face" not in palette
    assert "@import" not in palette
    for stack in re.findall(r"--font-[\w-]+:([^;]+);", palette):
        assert "url(" not in stack


@pytest.mark.parametrize("name", ["page.css", "page.js"])
def test_what_a_build_writes_is_a_plain_local_filename(name):
    # ⛔ R4's consequence, already ruled: a page's assets resolve relative to
    # the page, which is why a moved page renders unstyled rather than
    # breaking its identity. Both are true and neither is a defect.
    assert name in written_files()
    assert not name.startswith(("/", "http"))


def test_a_vendored_bundle_may_contain_a_url_and_that_is_not_a_defect():
    # ⚠️ Pinned so a later reader does not "fix" it by editing vendored code.
    # What matters is the disarming above, which is checked separately.
    assert "https://" in text("plyr.js")
