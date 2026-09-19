"""`W362`: the page's own identity, and every tell of the design brief kept out of it.

Mirrors no source module: it asserts things about the authored stylesheets, the
page templates and the palette, which are data. ⭐ Every tell is asserted BOTH
WAYS (R12, the row's clause 7): the shipped files pass, and a planted instance
of the same tell is caught by the same check, by name.

The brief is `docs/conventions/ui-design.md`, §2 and §3.
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
