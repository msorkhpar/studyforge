"""The vendored faces: pinned, unmodified, licensed, and carried inside the stylesheet.

Mirrors `render/pageassets/faces.py`.
"""

from __future__ import annotations

import base64
import hashlib
import re

import pytest

from studyforge.render.pageassets import ASSET_DIR, AssetError, faces, licence_names, stylesheet
from studyforge.render.pageassets.source import FONT_SUFFIX, data, font_names

#: Every family the palette names first in a font stack.
FAMILIES = ("Charis", "Andika", "JetBrains Mono")


def test_every_vendored_face_matches_its_pinned_sha256():
    # ⭐ Recomputed from the bytes on disk, never believed from the record.
    for face in faces.FACES:
        assert hashlib.sha256(data(face.name)).hexdigest() == face.sha256, face.name


def test_every_licence_matches_its_pinned_sha256():
    for name, pinned in faces.LICENCE_PINS.items():
        assert hashlib.sha256((ASSET_DIR / name).read_bytes()).hexdigest() == pinned, name


def test_the_record_and_the_directory_agree_in_both_directions():
    # ⛔ A face on disk the record does not pin is an unrecorded file; a pinned
    # face missing from disk is a stylesheet that cannot be built.
    assert set(font_names()) == {face.name for face in faces.FACES}


def test_every_archive_is_pinned_with_its_source_and_its_agreement():
    for archive in faces.ARCHIVES:
        assert archive.url.startswith("https://github.com/"), archive.family
        assert re.fullmatch(r"[0-9a-f]{64}", archive.sha256), archive.family
        assert archive.second_source, archive.family
        assert archive.licence in licence_names(), archive.family


def test_every_face_ships_beside_its_open_font_licence():
    for face in faces.FACES:
        licence = (ASSET_DIR / faces.licence_for_face(face.name)).read_text(encoding="utf-8")
        assert "SIL Open Font License, Version 1.1" in licence, face.name


@pytest.mark.parametrize("family", ["Charis", "Andika"])
def test_a_family_with_a_reserved_name_is_vendored_whole(family):
    # ⛔ Charis and Andika reserve their names, a subset
    # is a Modified Version that may not carry them, so no file is subset. The
    # licence says which names are reserved; this checks the claim is still true
    # of the file that ships, and that every face of the family is a full release
    # file — a subset of a SIL face is far smaller than the release's own.
    licence = (ASSET_DIR / f"{family}.LICENSE").read_text(encoding="utf-8")
    assert f'Reserved Font Names "{family}"' in licence
    for face in faces.FACES:
        if face.family == family:
            assert len(data(face.name)) > 250_000, face.name


def test_a_face_whose_bytes_changed_is_refused_by_name(monkeypatch):
    # ⭐ Asserted both ways (R12): the real faces compose; a planted change does not.
    planted = faces.FACES[0]
    original = faces.data
    monkeypatch.setattr(
        faces,
        "data",
        lambda name: original(name) + b"\0" if name == planted.name else original(name),
    )
    with pytest.raises(AssetError, match=re.escape(planted.name)):
        faces.rule(planted)


def test_the_built_stylesheet_carries_every_face_as_base64():
    css = stylesheet()
    for face in faces.FACES:
        encoded = base64.b64encode(data(face.name)).decode("ascii")
        assert f"data:font/woff2;base64,{encoded}" in css, face.name


def test_the_built_stylesheet_names_no_font_file_by_url():
    # ⛔ A relative face breaks R8 in Firefox, so every
    # `url()` in the built stylesheet is a `data:` URI and none names a file.
    urls = re.findall(r"url\(\s*['\"]?([^'\")]+)", stylesheet())
    assert urls, "the stylesheet embeds no face at all"
    assert [url for url in urls if not url.startswith("data:")] == []
    assert FONT_SUFFIX not in "".join(url for url in urls if not url.startswith("data:"))


def test_a_planted_font_file_url_would_be_caught():
    # ⭐ The check above, run against a stylesheet that does the wrong thing.
    planted = '@font-face { src: url("fonts/Charis-Regular.woff2"); }'
    urls = re.findall(r"url\(\s*['\"]?([^'\")]+)", planted)
    assert [url for url in urls if not url.startswith("data:")] == ["fonts/Charis-Regular.woff2"]


def test_the_faces_come_first_and_the_parts_follow_in_their_stated_order():
    css = stylesheet()
    assert css.startswith(faces.HEADER)
    assert css.index("@font-face") < css.index(":root")


@pytest.mark.parametrize("family", FAMILIES)
def test_every_family_the_palette_names_first_is_one_that_is_embedded(family):
    declared = {face.family for face in faces.FACES}
    assert family in declared
    palette = (ASSET_DIR / "palette.css").read_text(encoding="utf-8")
    assert re.search(rf'--font-[a-z]+:\s*"{re.escape(family)}"', palette), family


def test_composing_the_faces_twice_gives_identical_bytes():
    # R10: the page stylesheet is compared byte for byte.
    assert faces.rules() == faces.rules()


def test_a_name_that_is_not_a_face_is_refused():
    with pytest.raises(AssetError):
        data("palette.css")
    with pytest.raises(AssetError):
        faces.licence_for_face("palette.css")


def _mono_rules(css: str) -> list[str]:
    """Every rule body in `css` that sets the mono face."""
    return [body for body in re.findall(r"\{([^{}]*)\}", css) if "var(--font-mono)" in body]


def test_every_rule_that_sets_code_in_the_mono_face_draws_no_ligature():
    # ⛔ JetBrains Mono joins `!=` into a not-equal sign, which misleads in
    # code. Every rule setting the face turns ligatures off, contextual ones included.
    rules = _mono_rules(stylesheet())
    assert len(rules) >= 4, rules
    for body in rules:
        assert "font-variant-ligatures: none" in body, body
        assert '"calt" 0' in body, body
