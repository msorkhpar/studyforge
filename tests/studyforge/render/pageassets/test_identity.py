"""The page's own identity, and every tell of the design brief kept out of it.

Mirrors no source module: it asserts things about the authored stylesheets, the
page templates and the palette, which are data. ⭐ Every tell is asserted BOTH
WAYS (R12, the row's clause 7): the shipped files pass, and a planted instance
of the same tell is caught by the same check, by name.

The brief is the UI design convention's §2 and §3, kept on the branch `archive/process`.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render import templates
from studyforge.render.pageassets import STYLE_PARTS, is_vendored, text
from tests.studyforge.render.pageassets.test_palette import contrast, declarations

PALETTE = "palette.css"

#: The brief's banned faces, and the pieces of a bare system stack (§2).
BANNED_FACES = (
    "Inter",
    "Roboto",
    "Open Sans",
    "Lato",
    "Arial",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
)

#: The slip is the ONE filled area of the sign colour, on these selectors only.
SLIP_SELECTORS = (
    'nav[aria-label="Between units"] a[rel="next"]',
    'nav[aria-label="Up next"] a',
    'nav[aria-label="Up next"] > p',
)


def authored() -> dict[str, str]:
    """Every authored stylesheet part, comments removed."""
    return {
        name: re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)
        for name in STYLE_PARTS
        if not is_vendored(name)
    }


def markup() -> dict[str, str]:
    """Every page template, as written."""
    return {name: templates.template(name).template for name in templates.names()}


# --- the checks, each one a function so it can be run against a plant --------


def banned_faces(css: str) -> list[str]:
    """Every banned face named in a `font-family` or a `--font-*` token."""
    stacks = re.findall(r"(?:font-family|--font-[a-z]+)\s*:\s*([^;]+);", css)
    return sorted(
        {
            face
            for stack in stacks
            for face in BANNED_FACES
            if re.search(rf"(?<![\w-]){re.escape(face)}(?![\w-])", stack)
        }
    )


def shouted_labels(css: str) -> list[str]:
    """Every rule that sets text in capitals — the ALL-CAPS eyebrow tell."""
    return [
        selector.strip()
        for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        if re.search(r"text-transform\s*:\s*uppercase", block)
    ]


def dotted(css_or_markup: str) -> bool:
    """Whether a middle dot is drawn or written — the `A · B · C` tell."""
    return bool(re.search(r"·|&middot;|\\00b7|&#183;", css_or_markup))


def arrowed(template_text: str) -> bool:
    """Whether an arrow is appended to a label — the `→` tell."""
    return bool(re.search(r"[←→]|&#8592;|&#8594;|&larr;|&rarr;", template_text))


def signs(css: str) -> list[str]:
    """Every selector whose rule FILLS a ground with the sign colour."""
    return [
        " ".join(selector.split())
        for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        if re.search(r"background(?:-color)?\s*:\s*var\(--sign\)", block)
    ]


# --- the shipped files pass ---------------------------------------------------


def test_no_authored_stylesheet_names_a_banned_face():
    offenders = {name: banned_faces(css) for name, css in authored().items()}
    assert {name: found for name, found in offenders.items() if found} == {}


def test_no_authored_stylesheet_shouts():
    offenders = {name: shouted_labels(css) for name, css in authored().items()}
    assert {name: found for name, found in offenders.items() if found} == {}


def test_nothing_draws_or_writes_a_middle_dot():
    assert [name for name, css in authored().items() if dotted(css)] == []
    assert [name for name, body in markup().items() if dotted(body)] == []


def test_no_template_appends_an_arrow_to_a_label():
    assert [name for name, body in markup().items() if arrowed(body)] == []


def test_the_sign_colour_fills_the_slip_and_nothing_else():
    filled = [selector for css in authored().values() for selector in signs(css)]
    flattened = {part.strip() for selector in filled for part in selector.split(",")}
    assert flattened, "nothing is filled with the sign colour, so there is no bold element"
    # ⭐ The slip and its own tab (a child of the slip) are one element.
    astray = sorted(s for s in flattened if not s.startswith(SLIP_SELECTORS))
    assert astray == []


# --- and a planted tell is caught, by name -----------------------------------


@pytest.mark.parametrize("face", BANNED_FACES)
def test_a_planted_banned_face_is_caught_by_name(face):
    planted = f'body {{ font-family: "Charis", {face}, serif; }}'
    assert face in banned_faces(planted)


def test_a_planted_capital_eyebrow_is_caught_by_name():
    planted = "nav p { text-transform: uppercase; letter-spacing: .08em; }"
    assert shouted_labels(planted) == ["nav p"]


@pytest.mark.parametrize("planted", ['#counter::before { content: " · "; }', "<p>a &middot; b</p>"])
def test_a_planted_middle_dot_is_caught(planted):
    assert dotted(planted)


@pytest.mark.parametrize("planted", ["Next &#8594;", "&#8592; Prev", "Next →"])
def test_a_planted_arrow_is_caught(planted):
    assert arrowed(planted)


def test_a_planted_second_sign_is_caught_by_selector():
    planted = "aside { background: var(--sign); }"
    assert signs(planted) == ["aside"]


# --- the palette: both themes, computed contrast ------------------------------


def blocks() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """The light block, the system-dark block and the forced-dark block."""
    body = text(PALETTE)
    at_media = body.index("@media (prefers-color-scheme: dark)")
    at_forced = body.index(':root[data-theme="dark"]')
    return (
        declarations(body[:at_media]),
        declarations(body[at_media:at_forced]),
        declarations(body[at_forced:]),
    )


def test_the_forced_dark_theme_is_the_system_dark_theme_value_for_value():
    # ⛔ Two spellings of one theme: `[data-theme="dark"]` exists so a page can
    # ask for dark whatever the system says, and it must not drift.
    _, system, forced = blocks()
    assert system == forced


def test_the_dark_theme_is_guarded_both_ways():
    body = text(PALETTE)
    assert ':root:not([data-theme="light"])' in body
    assert ':root[data-theme="dark"]' in body


#: `(foreground, background, floor)` — text at 4.5, a mark or a control edge at 3.
PAIRS = (
    ("--fg", "--bg", 4.5),
    ("--fg-soft", "--bg", 4.5),
    ("--muted", "--bg", 4.5),
    ("--muted", "--surface", 4.5),
    ("--muted", "--panel", 4.5),
    ("--fg", "--panel", 4.5),
    ("--sign-ink", "--sign", 4.5),
    ("--hl-fg", "--hl-bg", 4.5),
    ("--practice", "--practice-soft", 4.5),
    ("--bg", "--fg", 4.5),
    ("--sign", "--bg", 3.0),
    ("--done", "--bg", 3.0),
    ("--rule-strong", "--bg", 3.0),
    ("--hl-bar", "--surface-2", 3.0),
    ("--focus", "--bg", 3.0),
    ("--accent", "--accent-soft", 3.0),
)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize(("foreground", "background", "floor"), PAIRS)
def test_every_pair_the_design_paints_clears_its_floor(theme, foreground, background, floor):
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    ratio = contrast(values[foreground], values[background])
    assert ratio >= floor, (
        f"{theme}: {foreground} on {background} is {ratio:.2f}:1, below {floor}:1"
    )


# --- The palette against the two reference pages -----------------------------

#: The band each ink that carries running text sits in, as ratios, `token ->
#: (floor, ceiling)`. ⛔ NOT WCAG AA AND NOT A MAXIMUM — the bounds are taken
#: from a reference page read for hours: its body ink is 12.14:1, its quieter
#: ink 8.33:1 and its faintest 5.59:1, and all three sit inside the bands below.
#: ⚠️ One band of 4.5–9.0 for all three reads as too dim — the FLOOR matters —
#: and the ceiling refuses near-white chalk on a dark board.
BANDS = {"--fg": (10.0, 14.0), "--fg-soft": (6.5, 10.0), "--muted": (4.5, 7.0)}

#: The inks that carry running text, against the ground they are read on.
BODY_TEXT = (("--fg", "--bg"), ("--fg-soft", "--bg"), ("--muted", "--bg"))

#: How far from neutral a ground or an ink may be, as `(red - blue) / 255`. ⛔ A
#: SIGNED bound and not a spread: warm means red above blue. Both reference pages
#: are at or below zero; a parchment ground and its ink are above it.
WARMTH = 0.015

#: The grounds and inks the warmth bound applies to — everything a reader looks
#: at for an hour. ⛔ The accent is not among them: it is a mark, and warm is
#: exactly what it is for.
NEUTRALS = (
    "--bg",
    "--surface",
    "--surface-2",
    "--panel",
    "--fg",
    "--fg-soft",
    "--muted",
    "--rule",
    "--rule-strong",
    "--margin",
)

#: What the palette may paint a LINE with at rest, as chroma — the spread
#: between the strongest and weakest sRGB channel, scaled to 0–1. ⛔ Structure
#: stays on the neutral scale: nothing on the page is told apart by a hairline's
#: hue. ⚠️ A bound read against a warm grey would be too tight:
#: the slate scale both reference pages use is a TINTED neutral (its blue
#: channel leads by about a seventh), so the bound is the scale's own spread
#: plus room, and the rules are held to the warmth bound above as well — a red
#: hairline is caught by that one whatever its spread.
RULE_CHROMA = 0.20

#: ⛔ THE ACCENT'S BOUND IS A FLOOR. A cap would allow a washed ink blue, and a
#: live accent that is nearly grey is not an accent. The reference page sets its
#: accent at 0.80.
ACCENT_CHROMA = 0.45

#: `token -> the chroma it may not exceed`. Lines only.
AT_REST = {"--rule": RULE_CHROMA, "--rule-strong": RULE_CHROMA, "--margin": RULE_CHROMA}

#: The tokens that must be LOUD, each against `ACCENT_CHROMA` as a floor.
LIVE = ("--accent", "--sign", "--focus", "--hl-bar")

#: The hue arc a colour is called green over, in degrees, and the chroma below
#: which a hue is not worth naming. ⛔ REGISTER RULING, 2026-09-19: no green
#: in the palette. Both reference pages use one — the route planner's guide-sign green
#: and the documentation site's emerald — and it is the one thing taken from
#: neither. ⚠️ Read over every colour token in both themes, not only the accent.
GREEN = (70.0, 170.0)
NAMEABLE = 0.15


def chroma(colour: str) -> float:
    """How far from neutral a hex colour is, as the spread of its sRGB channels."""
    body = colour.lstrip("#")
    channels = [int(body[at : at + 2], 16) for at in (0, 2, 4)]
    return (max(channels) - min(channels)) / 255


def warmth(colour: str) -> float:
    """How far a hex colour leans red over blue, scaled to -1..1."""
    body = colour.lstrip("#")
    red, _, blue = (int(body[at : at + 2], 16) for at in (0, 2, 4))
    return (red - blue) / 255


def hue(colour: str) -> float:
    """The hue of a hex colour in degrees, 0 at red, going through green at 120."""
    body = colour.lstrip("#")
    red, green, blue = (int(body[at : at + 2], 16) / 255 for at in (0, 2, 4))
    high, low = max(red, green, blue), min(red, green, blue)
    if high == low:
        return 0.0
    spread = high - low
    if high == red:
        return (60 * ((green - blue) / spread)) % 360
    if high == green:
        return 60 * (2 + (blue - red) / spread)
    return 60 * (4 + (red - green) / spread)


def greens(values: dict[str, str]) -> list[str]:
    """Every token in `values` painted a green anybody would call green."""
    return sorted(
        token
        for token, colour in values.items()
        if colour.startswith("#")
        and chroma(colour) >= NAMEABLE
        and GREEN[0] <= hue(colour) <= GREEN[1]
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize(("ink", "ground"), BODY_TEXT)
def test_body_text_is_inside_the_band_the_users_own_page_sets(theme, ink, ground):
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    floor, ceiling = BANDS[ink]
    ratio = contrast(values[ink], values[ground])
    assert floor <= ratio <= ceiling, (
        f"{theme}: {ink} on {ground} is {ratio:.2f}:1, outside {floor}:1–{ceiling}:1"
    )


def test_the_reference_page_the_user_gave_us_sits_inside_the_same_bands():
    # ⭐ The bands are not invented here: these are the route planner's own three
    # inks on its own ground, and each lands inside the band named after it.
    for ink, measured in (("--fg", ("#f1f2ee", "#2b2e31")), ("--fg-soft", ("#c8cbc6", "#2b2e31"))):
        floor, ceiling = BANDS[ink]
        assert floor <= contrast(*measured) <= ceiling, ink
    floor, ceiling = BANDS["--muted"]
    assert floor <= contrast("#a2a7a3", "#2b2e31") <= ceiling


def test_both_palettes_this_row_replaced_are_caught_by_the_same_bands():
    # ⭐ Both ways, and both bounds, against two palettes the bands must
    # refuse: near-black ink on cool paper breaks the CEILING, and warm-grey ink
    # on warm paper breaks the FLOOR in both themes.
    assert contrast("#1b2236", "#f1f5f2") > BANDS["--fg"][1]
    assert contrast("#534e46", "#f6f1e7") < BANDS["--fg"][0]
    assert contrast("#bdb6a8", "#2a2825") < BANDS["--fg"][0]


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_no_ground_or_ink_is_warm(theme):
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    warm = {
        token: round(warmth(values[token]), 3)
        for token in NEUTRALS
        if warmth(values[token]) > WARMTH
    }
    assert warm == {}, f"{theme}: {warm}"


def test_the_warm_paper_that_shipped_is_caught_and_the_reference_is_not():
    # ⭐ Both ways: four warm values, and the two reference grounds.
    assert [warmth(colour) > WARMTH for colour in ("#f6f1e7", "#534e46", "#2a2825", "#bdb6a8")] == [
        True,
        True,
        True,
        True,
    ]
    assert warmth("#2b2e31") <= WARMTH and warmth("#f1f2ee") <= WARMTH
    assert warmth("#0f172a") <= WARMTH and warmth("#f1f5f9") <= WARMTH


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_no_line_is_saturated_at_rest(theme):
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    loud = {
        token: f"{chroma(values[token]):.3f} > {bound}"
        for token, bound in AT_REST.items()
        if chroma(values[token]) > bound
    }
    assert loud == {}, f"{theme}: {loud}"


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_the_live_accent_is_not_a_grey(theme):
    # ⛔ The stage-1 reversal, asserted: the bound is a floor and not a cap.
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    washed = {
        token: round(chroma(values[token]), 3)
        for token in LIVE
        if chroma(values[token]) < ACCENT_CHROMA
    }
    assert washed == {}, f"{theme}: {washed}"


def test_the_saturated_rule_and_the_washed_accent_that_shipped_are_both_caught():
    # ⭐ A red margin rule breaks the line bound and the warmth bound; a
    # saturated blue breaks the line bound; two washed ink blues are below the
    # accent floor; a slate hairline is inside every one.
    assert chroma("#cf8f98") > RULE_CHROMA
    assert warmth("#cf8f98") > WARMTH and warmth("#8a5257") > WARMTH
    assert chroma("#23449a") > RULE_CHROMA
    assert chroma("#46618c") < ACCENT_CHROMA
    assert chroma("#9fb2d2") < ACCENT_CHROMA
    assert chroma("#dbe3ec") <= RULE_CHROMA


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_nothing_in_the_palette_is_green(theme):
    light, dark, _ = blocks()
    values = dict(light, **dark) if theme == "dark" else light
    assert greens(values) == []


def test_every_green_the_two_reference_pages_use_is_caught_by_name():
    # ⭐ The other way, over the greens this palette had to give up: the route
    # planner's guide sign and its bash ink, the documentation site's emerald,
    # and an olive string ink in both themes.
    planted = {
        "--sign": "#0b5a3a",
        "--bash": "#cde688",
        "--brand": "#10b981",
        "--tok-string-light": "#4f6a35",
        "--tok-string-dark": "#a3bf8a",
    }
    assert greens(planted) == sorted(planted)
    assert greens({"--accent": "#ffc933", "--focus": "#38bdf8", "--fg": "#d2dbe6"}) == []


def test_a_planted_pair_below_its_floor_is_caught():
    # ⭐ The same arithmetic on a pair that fails: pencil grey on the chrome
    # ground at the old warm-grey value.
    assert contrast("#9b958b", "#f1f5f2") < 4.5


# --- the page carries what §3 asks of it --------------------------------------


def test_the_theme_colour_is_the_ground_of_each_theme():
    light, dark, _ = blocks()
    page = templates.template("page.html").template
    found = dict(
        re.findall(
            r'<meta name="theme-color" media="\(prefers-color-scheme: (light|dark)\)" '
            r'content="(#[0-9a-f]{6})">',
            page,
        )
    )
    assert found == {"light": light["--bg"], "dark": dict(light, **dark)["--bg"]}


def test_the_skip_link_is_the_first_thing_in_the_body():
    page = templates.template("page.html").template
    inside = page.split("<body>", 1)[1].lstrip()
    assert inside.startswith('<a href="#content">'), inside[:40]
    assert '<main id="content">' in page


def test_the_sticky_player_cannot_cover_what_the_keyboard_reaches():
    reset = text("reset.css")
    assert "scroll-padding-bottom" in reset and "var(--player-height)" in reset
    assert "scroll-padding-top" in reset


def test_motion_answers_the_readers_preference_and_nothing_moves_on_load():
    css = "\n".join(authored().values())
    assert "prefers-reduced-motion: reduce" in css
    assert "@keyframes" not in css, "a load animation would be a resting state behind motion"
