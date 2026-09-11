"""The palette is the shared vocabulary, and the vocabulary is complete.

Mirrors no source module: it asserts things about `render/assets/palette.css`,
which is data. ⭐ The three properties here are each invisible to whoever broke
them — a token defined in one theme looks right to the person who only uses
that theme, a `var()` with no definition renders as *unstyled* rather than as
an error, and a contrast failure is only visible to somebody it fails.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render.pageassets import STYLE_PARTS, is_vendored, text

#: The one file allowed to hold a colour.
PALETTE = "palette.css"

#: ⚠️ Black behind a video and white on top of it are not theme colours: the
#: first is the absence of picture and the second is a control drawn on it, so
#: both stay the same in light and dark. The exemption is by file and by value,
#: so it cannot quietly widen.
RAW_COLOUR_EXEMPTIONS = {"video-player.css": {"#000", "#fff"}}

COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)")
DEFINED = re.compile(r"^\s*(--[\w-]+)\s*:", re.MULTILINE)
USED = re.compile(r"var\(\s*(--[\w-]+)")

#: WCAG AA for body text. The syntax colours are small text on a code
#: background, which is the hardest case on the page.
MIN_CONTRAST = 4.5

#: `token -> the background it is read against`, per theme.
CODE_BACKGROUND = "--code-bg"


def authored_parts():
    return [name for name in STYLE_PARTS if not is_vendored(name)]


def themes():
    """`(name, {token: value})` for the light and dark blocks of the palette.

    ⛔ Split on the media query rather than parsed as CSS: the point is that
    the *file* defines each token twice, and a real parser would happily
    resolve a cascade that a human reading the file could not.
    """
    body = text(PALETTE)
    at = body.index("@media (prefers-color-scheme: dark)")
    return (("light", declarations(body[:at])), ("dark", declarations(body[at:])))


def uncommented(name):
    """The part's text with its comments removed.

    ⚠️ Not fastidiousness: this file's own prose says `var(--token)`, and a
    check that read comments would report the sentence explaining the rule as
    a violation of it.
    """
    return re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)


def declarations(chunk):
    without_comments = re.sub(r"/\*.*?\*/", "", chunk, flags=re.DOTALL)
    return {
        name: value.strip()
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", without_comments)
    }


def luminance(colour):
    parts = colour.lstrip("#")
    if len(parts) == 3:
        parts = "".join(c * 2 for c in parts)
    channels = [int(parts[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground, background):
    """The WCAG contrast ratio between two hex colours."""
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# --- one place holds the colours -------------------------------------------


def test_only_the_palette_holds_a_colour():
    # ⭐ This is the whole of what R13 bought: changing the page's look is
    # editing one file. A raw hex in another part is a colour that cannot be
    # re-themed and will not follow the reader's theme.
    offenders = []
    for name in authored_parts():
        if name == PALETTE:
            continue
        allowed = RAW_COLOUR_EXEMPTIONS.get(name, set())
        offenders += [
            f"{name}: {colour}"
            for colour in COLOUR.findall(uncommented(name))
            if colour not in allowed
        ]
    assert offenders == [], "a colour outside the palette: " + ", ".join(offenders)


def test_every_token_used_anywhere_is_defined():
    # ⚠️ A `var(--typo)` renders as unstyled, which looks deliberate.
    defined = set(DEFINED.findall(uncommented(PALETTE)))
    offenders = []
    for name in authored_parts():
        used = set(USED.findall(uncommented(name)))
        # Plyr's own properties are set BY us and read by the library.
        offenders += [f"{name}: {t}" for t in sorted(used - defined) if not t.startswith("--plyr")]
    assert offenders == [], "undefined token: " + ", ".join(offenders)


# --- both themes, always ----------------------------------------------------


def test_every_colour_token_is_defined_in_both_themes():
    # ⛔ The page declares `color-scheme: light dark`. A token defined once is
    # a token that is wrong in one of them.
    (_, light), (_, dark) = themes()
    colours = {name for name, value in light.items() if COLOUR.search(value)}
    missing = sorted(colours - set(dark))
    assert missing == [], "defined for light only: " + ", ".join(missing)


def test_the_dark_theme_redefines_nothing_that_is_not_a_colour():
    # A measure or a font stack that differed between themes would be a layout
    # that moves when the reader's system clock crosses sunset.
    (_, light), (_, dark) = themes()
    structural = {name for name, value in light.items() if not COLOUR.search(value)}
    assert sorted(structural & set(dark)) == []


# --- and each one is readable ----------------------------------------------


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_every_syntax_colour_clears_the_contrast_threshold(theme):
    # ⭐ Counted, not inherited. The tuned claim is that every token clears
    # 4.5:1 against the code background it actually sits on; this recomputes
    # it rather than trusting the comment that says so.
    values = dict(themes())[theme]
    background = values[CODE_BACKGROUND]
    failures = {
        name: round(contrast(value, background), 2)
        for name, value in values.items()
        if name.startswith("--tok-") and contrast(value, background) < MIN_CONTRAST
    }
    assert failures == {}, f"{theme}: below {MIN_CONTRAST}:1 on {background} — {failures}"


@pytest.mark.parametrize(
    "theme,foreground,background",
    [
        ("light", "--fg", "--bg"),
        ("light", "--muted", "--bg"),
        ("light", "--accent", "--bg"),
        ("light", "--code-fg", "--code-bg"),
        ("dark", "--fg", "--bg"),
        ("dark", "--muted", "--bg"),
        ("dark", "--accent", "--bg"),
        ("dark", "--code-fg", "--code-bg"),
        # ⭐ The six pairs `chrome.css` creates (`SF-34`). ⚠️ They are here and
        # not only in the browser-driven harness because the browser-driven half
        # DOES NOT RUN in the pinned image (`QA-03/1`), and a contrast rule that
        # only an unpinned machine can check erodes exactly like an unenforced
        # ceiling. ⛔ Not a new instrument: the same parametrised node, with the
        # pairs the new stylesheet actually paints.
        ("light", "--muted", "--surface-2"),
        ("light", "--accent", "--surface-2"),
        ("light", "--fg", "--surface-2"),
        ("light", "--accent", "--accent-soft"),
        ("light", "--practice", "--practice-soft"),
        ("light", "--fg-soft", "--practice-soft"),
        ("dark", "--muted", "--surface-2"),
        ("dark", "--accent", "--surface-2"),
        ("dark", "--fg", "--surface-2"),
        ("dark", "--accent", "--accent-soft"),
        ("dark", "--practice", "--practice-soft"),
        ("dark", "--fg-soft", "--practice-soft"),
    ],
)
def test_every_reading_colour_clears_the_contrast_threshold(theme, foreground, background):
    values = dict(themes())[theme]
    ratio = contrast(values[foreground], values[background])
    assert ratio >= MIN_CONTRAST, (
        f"{theme}: {foreground} on {background} is {ratio:.2f}:1, below {MIN_CONTRAST}:1"
    )


def test_the_seven_syntax_tokens_are_the_ones_the_highlighter_paints_with():
    # Both directions. A palette token nothing paints with is dead; a rule
    # painting with a token the palette never defines renders unstyled.
    defined = {t for t in DEFINED.findall(uncommented(PALETTE)) if t.startswith("--tok-")}
    painted = {
        token
        for token in USED.findall(uncommented("code-highlight.css"))
        if token.startswith("--tok-")
    }
    assert defined == painted
