"""Mirror of `src/studyforge/render/pageassets/source.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.pageassets import (
    ASSET_DIR,
    LICENCE_SUFFIX,
    PART_SUFFIXES,
    AssetError,
    licence_names,
    names,
    text,
)


def test_the_asset_directory_is_a_data_directory_and_not_a_package():
    # ⚠️ §3.2: `render/assets/` holds no `__init__.py` and never will.
    # `[tool.setuptools.package-data]` is what ships it, and that declaration
    # already exists — this task adds files, not build configuration.
    assert ASSET_DIR.is_dir()
    assert not (ASSET_DIR / "__init__.py").exists()


def test_a_part_is_returned_exactly_as_it_sits_on_disk():
    # ⛔ Read as bytes and decoded, never `read_text`: universal-newline
    # translation would rewrite a CRLF on the way in and silently change what
    # the page ships. Compared against the raw bytes, which is the only
    # comparison that can catch it.
    raw = (ASSET_DIR / "palette.css").read_bytes()
    assert text("palette.css") == raw.decode("utf-8")


def test_names_are_sorted_rather_than_in_directory_order():
    # ⛔ R10: two machines enumerating a directory can disagree, and a page
    # that differs between them cannot be compared byte for byte.
    listed = names()
    assert list(listed) == sorted(listed)


def test_every_name_is_a_part_and_no_licence_is():
    # ⭐ A licence sits beside the code it covers, because a licence in another
    # tree is one that goes missing when the directory is copied — but nothing
    # composes it into a page, so it is not a part.
    assert all(name.endswith(PART_SUFFIXES) for name in names())
    assert all(name.endswith(LICENCE_SUFFIX) for name in licence_names())
    assert not set(names()) & set(licence_names())


def test_the_directory_holds_nothing_that_is_neither():
    on_disk = {path.name for path in ASSET_DIR.iterdir() if path.is_file()}
    assert on_disk == set(names()) | set(licence_names()), (
        "a file in the asset directory is neither a part nor a licence"
    )


@pytest.mark.parametrize("name", ["", ".", "..", "sub/dir.css", "a\\b.css"])
def test_a_name_that_could_escape_the_directory_is_refused(name):
    with pytest.raises(AssetError, match="one filename"):
        text(name)


def test_reading_the_same_part_twice_gives_the_same_text():
    # R10 again, at the smallest scale: nothing here caches, mutates or
    # normalises, so two reads of one file are one answer.
    assert text("reset.css") == text("reset.css")
