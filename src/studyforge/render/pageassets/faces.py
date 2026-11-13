"""The three typefaces every page is set in, vendored, pinned and embedded.

**What it does.** Names each vendored face, the weight and style it is, the
archive it came from and the sha256 of both, and composes the `@font-face`
rules that carry the faces **inside** the page stylesheet as base64.

**How you use it.** `rules()` returns the CSS `bundle.stylesheet()` puts first;
`FACES` and `ARCHIVES` are the pins record; `licence_for_face(name)` names the
licence beside a face.

**Depends on.** `base64`, `hashlib`, and `source` for the bytes.

## ⭐ Why these three (the plan's §5, revised by the 2026-11 redesign)

Charis comes from SIL's literacy work, a face drawn for people learning to
read, and it sets the prose. Plus Jakarta Sans, a crisp geometric sans, sets
headings, navigation and controls: the redesign replaced Andika, whose
primer-like shapes read as a children's book beside technical prose. JetBrains
Mono sets code and nothing else. All three are SIL Open Font License 1.1.

## ⛔ Unmodified where a name is reserved

Charis reserves its names ("Charis", "SIL"). A subset is a Modified Version,
which may not carry the name, so its files are the release's own, byte for
byte. Plus Jakarta Sans reserves no name; its release ships TTF only, so its
three weights are the release's TTFs compressed to WOFF2 with fontTools 4.55.3
(`fonttools ttLib.woff2 compress`, lossless: the glyphs, metrics and tables are
the release's). `test_faces` recomputes every sha256 below against the bytes on
disk. ⚠️ Base64 is an encoding of those bytes, not a modification of the font
software.

## ⛔ Base64 in the stylesheet, never a relative `url()`

A page below the site root would load a face from a parent directory, and
Firefox under its default strict file-origin policy refuses a `file://` font
outside the document's own directory tree. So a relative face breaks R8 in
Firefox. Embedded, the face arrives with the stylesheet and no page requests a
font at all.

## ⚠️ The weight set is small on purpose, because the bytes are real

Each SIL file is about 300 KB. Charis has regular, italic and bold (prose uses
all three); Plus Jakarta Sans has regular (controls, navigation), semibold
(labels, emphasis in the chrome) and bold (headings), about 42 KB each;
JetBrains Mono has regular and bold (bold keywords). No mono italic is vendored: a code comment keeps its slant as the
browser's synthesised oblique, and is told apart by its pencil colour first.
A weight is added only with a stated reason.
"""

from __future__ import annotations

import base64
import functools
import hashlib
from dataclasses import dataclass

from studyforge.describe import describe
from studyforge.render.pageassets.errors import AssetError
from studyforge.render.pageassets.source import data


@dataclass(frozen=True, slots=True)
class Archive:
    """One upstream release archive, as fetched and pinned."""

    family: str
    release: str
    url: str
    sha256: str
    second_source: str
    licence: str


@dataclass(frozen=True, slots=True)
class Face:
    """One vendored face file: which family, weight and style it is, and its pin."""

    name: str
    family: str
    weight: int
    style: str
    sha256: str


#: The archives, each pinned by its digest.
ARCHIVES: tuple[Archive, ...] = (
    Archive(
        family="Charis",
        release="v7.000",
        url="https://github.com/silnrsi/font-charis/releases/download/v7.000/Charis-7.000.zip",
        sha256="e3237b1303c5d31af8f59b1d1914886c5e873b77c71390e4742fb3bc1c187666",
        second_source="GitHub's published asset digest agrees",
        licence="Charis.LICENSE",
    ),
    Archive(
        family="Plus Jakarta Sans",
        release="2.7.1",
        url=(
            "https://github.com/tokotype/PlusJakartaSans/releases/download/2.7.1/"
            "PlusJakartaSans-2.7.1.zip"
        ),
        sha256="4bfc5cdf97d750423bb3d1d40ed8e529bc92288924d9c65e18ff486acefac66c",
        second_source="none published; single-source",
        licence="PlusJakartaSans.LICENSE",
    ),
    Archive(
        family="JetBrains Mono",
        release="v2.304",
        url=(
            "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/"
            "JetBrainsMono-2.304.zip"
        ),
        sha256="6f6376c6ed2960ea8a963cd7387ec9d76e3f629125bc33d1fdcd7eb7012f7bbf",
        second_source="none published; single-source",
        licence="JetBrainsMono.LICENSE",
    ),
)

#: Every vendored face, in the order its `@font-face` rule is written (R10).
FACES: tuple[Face, ...] = (
    Face(
        "Charis-Regular.woff2",
        "Charis",
        400,
        "normal",
        "3c8db45ec0290a8b05250d221c2d42d85f34bcc5a149fcc646ca907edfc1048f",
    ),
    Face(
        "Charis-Italic.woff2",
        "Charis",
        400,
        "italic",
        "81bcb8a8e54413e22b59565d5e82bd6bb8227dbabf321ca0ac15ebaed2964893",
    ),
    Face(
        "Charis-Bold.woff2",
        "Charis",
        700,
        "normal",
        "8a7151f0308d399f5d5d78fb09570acc858bfc675779c469735b602b13d05b7f",
    ),
    Face(
        "PlusJakartaSans-Regular.woff2",
        "Plus Jakarta Sans",
        400,
        "normal",
        "e4d379687af7adac1578def9018df7d6262e499c4cdd25aad0fe4d6413770ce0",
    ),
    Face(
        "PlusJakartaSans-SemiBold.woff2",
        "Plus Jakarta Sans",
        600,
        "normal",
        "ac18183f39185bf599f70b235ef68b2063906abc283ba1a6531cc1069875f170",
    ),
    Face(
        "PlusJakartaSans-Bold.woff2",
        "Plus Jakarta Sans",
        700,
        "normal",
        "cc61cf218bdc47cdb3737a1b3686ae9f2a8e0cfe4ffd5e3908d0e9f78c897846",
    ),
    Face(
        "JetBrainsMono-Regular.woff2",
        "JetBrains Mono",
        400,
        "normal",
        "a9cb1cd82332b23a47e3a1239d25d13c86d16c4220695e34b243effa999f45f2",
    ),
    Face(
        "JetBrainsMono-Bold.woff2",
        "JetBrains Mono",
        700,
        "normal",
        "c503cc5ec5f8b2c7666b7ecda1adf44bd45f2e6579b2eba0fc292150416588a2",
    ),
)

#: The licence file of every archive, sha256-pinned like the faces.
LICENCE_PINS = {
    "Charis.LICENSE": "07b1a63504f43e26b07a8017cd5803da86badb1bc1432470869ec48ad76958ee",
    "PlusJakartaSans.LICENSE": "995c7199cab65954f545996326755daee7b63cc6b42b06c13da1f9502ab08a99",
    "JetBrainsMono.LICENSE": "30f0c136e3c88e422d0791acd97238870f9054a9729bc34cf2ff0d4ed8cac4ad",
}

#: What the composed block opens with: the provenance, in the stylesheet itself.
HEADER = (
    "/* Faces: Charis (SIL Global), Plus Jakarta Sans (Tokotype) and JetBrains\n"
    "   Mono, SIL Open Font License 1.1; each licence ships beside its files.\n"
    "   Embedded unmodified as base64 so no page requests a font. */\n"
)


def licence_for_face(name: str) -> str:
    """Return the licence filename beside the face `name`, or raise naming it."""
    for face in FACES:
        if face.name == name:
            return next(each.licence for each in ARCHIVES if each.family == face.family)
    # ⛔ Described, never echoed (R7): the refused value is not repeated back.
    raise AssetError(f"that is not a vendored face; given {describe(name)}")


def digest(content: bytes) -> str:
    """Return the sha256 of `content`, as the pins record spells it."""
    return hashlib.sha256(content).hexdigest()


def rule(face: Face) -> str:
    """Return one `@font-face` rule carrying `face` as a base64 `data:` URI.

    ⛔ Refuses a file whose bytes no longer match its pin: a face that changed
    on disk is not the face that was pinned, and shipping it would be
    shipping an unrecorded modification.
    """
    content = data(face.name)
    if digest(content) != face.sha256:
        raise AssetError(f"the vendored face {face.name!r} does not match its pinned sha256")
    encoded = base64.b64encode(content).decode("ascii")
    return (
        "@font-face {\n"
        f'  font-family: "{face.family}";\n'
        f"  font-style: {face.style};\n"
        f"  font-weight: {face.weight};\n"
        "  font-display: swap;\n"
        f'  src: url("data:font/woff2;base64,{encoded}") format("woff2");\n'
        "}\n"
    )


@functools.cache
def rules() -> str:
    """Return every `@font-face` rule, with the provenance header, in `FACES` order.

    ⚠️ Cached: the faces are pinned, so the block cannot differ within one
    process, and composing 1.7 MB of base64 per page would be the build's cost.
    """
    return HEADER + "".join(rule(face) for face in FACES)
