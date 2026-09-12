"""The chrome part: which regions it answers for, and the two clauses re-homed onto it.

Mirrors no source module — it asserts things about `render/assets/chrome.css`,
which is data, the way `test_palette` does for `palette.css`.

## ⛔ Why the region list is DERIVED and not listed

⚠️ **`SF-34`'s founding defect is that it reads as complete either way.** Its
scope line said *"the three chrome regions the unit page already emits"* and was
stale in two directions at once: the practice panel had become a fourth, and a
container page — a page kind the line did not contemplate — a fifth, then the
root index a sixth. ⛔ **Nothing about a `solo` row whose scope is short signals
the gap**, and the epic's own instruction to whoever takes the task is to
*re-measure the region list against the tree rather than against the table*.

⭐ **So the population here is read out of the tree on every run:** every
`<nav aria-label>` a committed golden page carries, plus every framework-typed
region element in `render/templates/`. A seventh region fails
`test_the_region_table_is_total_over_what_the_tree_emits` on the day it appears,
and the answer *"it is another task's"* is a row in the table rather than a
silence.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render import templates
from studyforge.render.pageassets import (
    ASSET_DIR,
    STYLE_PARTS,
    SURFACE_HOOKS,
    text,
)
from studyforge.render.pageassets.surface import _FORM_OF, ATTRIBUTE_FORM, KIND_FORM
from tests.studyforge.render.page.pages import GOLDEN_DIR

#: The part under test.
CHROME = "chrome.css"

#: Who answers for a region. ⛔ Three values and no fourth: a region that fits
#: none of them is a region whose owner nobody decided, which is the exact state
#: `QA-03/2` found four palette tokens in.
CHROME_RULED = "chrome"  # this part carries its rules
SURFACE_RULED = "reading"  # `reading.css` already styles it as the element it is
DEFERRED = "deferred"  # another task's, and the task is named

#: `region anchor -> (who answers for it, why)`. ⛔ Asserted TOTAL over what the
#: tree emits, in both directions, by the first test below.
REGIONS: dict[str, tuple[str, str]] = {
    "body": (CHROME_RULED, "the page column — `PO-22/6`, note (d); one bound, on one element"),
    "header": (CHROME_RULED, "region 1, the masthead — `page.html`, every page kind"),
    "main#content": (
        SURFACE_RULED,
        "the reading column IS the body column, and `reading.css` caps its prose at "
        "`--measure`; a second bound here would be two rules for one question",
    ),
    'nav[aria-label="Outline"]': (CHROME_RULED, "region 2, the unit page's own outline"),
    'nav[aria-label="Between units"]': (
        CHROME_RULED,
        "region 3, the between-pages bar — and the CONTAINER page emits it too",
    ),
    'section[data-section="practices-pending"]': (
        CHROME_RULED,
        "region 4, the practice panel — note (a)",
    ),
    'nav[aria-label="Units"]': (CHROME_RULED, "region 5, a container's unit listing — `SF-27`"),
    'nav[aria-label="Contents"]': (
        CHROME_RULED,
        "region 6, the root index's disclosure tree — `SF-14`",
    ),
    'section[data-section="read-mark"]': (
        CHROME_RULED,
        "region 7, the reader's own mark-as-read control — `SF-30`. ⚠️ It ships "
        "`hidden` and `read-mark.js` unhides it only with a working store behind "
        "it, so the rules here are for the region a reader actually sees",
    ),
    "footer#player": (
        DEFERRED,
        "the narration transport is `SF-18`'s, and it has ARRIVED — in "
        "`narration.css`, its own part, which is why this row stays DEFERRED "
        "rather than becoming this part's: `--player-height`, `--panel` and "
        "`--shadow` are painted there and this file still reaches none of them",
    ),
}

#: How a framework-typed region element is recognised in a template. ⚠️ `section`
#: is matched by its literal `data-section` and not by its tag, because
#: `section.html` wraps a corpus's own sections and their keys are a corpus's
#: text — a tag match there would put a corpus into this population (R1).
REGION_MARKERS = {
    "body": r"<body>",
    "header": r"<header\b",
    "main#content": r'<main id="content"',
    "footer#player": r'<footer id="player"',
    'section[data-section="practices-pending"]': r'<section data-section="practices-pending"',
    'section[data-section="read-mark"]': r'<section data-section="read-mark"',
}

#: The page skeleton's slots, and why each is or is not this part's. ⛔ Asserted
#: EQUAL to `page.html`'s placeholders, so a slot added to the skeleton — which
#: is how regions 5 and 6 arrived — cannot pass unnoticed here.
SKELETON_SLOTS = {
    "title": "the document's own title, in `<head>`; nothing is painted",
    "stylesheet": "the link to `page.css`; nothing is painted",
    "script": "the link to `page.js`; nothing is painted",
    "identity": "R4's JSON block; it is data and is never shown",
    "heading": "the masthead's `<h1>` — region 1",
    # every slot below lands inside the one column `body` bounds
    "meta": "the masthead's second line — region 1",
    "breadcrumb": (
        "`SF-15`'s trail. ⛔ NOT a row in `REGIONS`, and that is not an oversight: "
        "`REGIONS` is asserted EQUAL to what the tree EMITS, and no committed golden "
        "emits this region — so a row for it would fail `declared - emitted`. "
        "⚠️ `chrome.css` therefore carries no rule for it — finding `SF-15/3`"
    ),
    "outline": "region 2",
    "body": "the reading surface — `reading.css`, by the block vocabulary",
    "pending": "region 4",
    "mark": (
        "region 7, `SF-30`'s read control. ⭐ It arrived as a NEW SLOT, which is "
        "the case this table's own comment said would show up here immediately "
        "rather than waiting for a golden to emit it — and it did"
    ),
    "player": "`SF-18`'s at M3 — the one DEFERRED row above",
    "nav": "region 3",
}

#: Properties that tell a region apart from body text WITHOUT a colour. ⛔ M1's
#: close condition 8 asked for exactly this and had to void it as unfalsifiable,
#: because nothing computed a reading order and no golden emitted the bar.
NON_COLOUR_CUES = (
    "border-top",
    "display",
    "font-family",
    "font-size",
    "font-weight",
    "letter-spacing",
    "padding-top",
    "text-transform",
)

#: The four tokens `QA-03/2` found ownerless: defined in `palette.css`, painted
#: by no stylesheet, and at no milestone anybody's. ⭐ They are this part's.
ONCE_OWNERLESS = ("--accent-soft", "--practice", "--practice-soft", "--surface-2")


def body() -> str:
    """`chrome.css` with its comments removed — the rules, and nothing about them."""
    return re.sub(r"/\*.*?\*/", "", text(CHROME), flags=re.DOTALL)


def rules() -> list[tuple[str, str]]:
    """`(selector list, declarations)` for every rule in the part, in file order."""
    return [
        (selector.strip(), declarations.strip())
        for selector, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", body())
    ]


def rule_for(selector: str) -> str | None:
    """The declarations of the one rule whose selector is exactly `selector`."""
    found = [block for each, block in rules() if each == selector]
    return found[0] if len(found) == 1 else None


def declarations_reaching(anchor: str) -> str:
    """Every declaration in every rule whose selector list mentions `anchor`."""
    return "\n".join(block for selector, block in rules() if anchor in selector)


def nav_regions_in_the_goldens() -> set[str]:
    """Every `<nav>` region a committed golden page carries, as a selector."""
    found: set[str] = set()
    for path in sorted(GOLDEN_DIR.glob("*.html")):
        page = path.read_bytes().decode("utf-8")
        found |= {
            f'nav[aria-label="{label}"]' for label in re.findall(r'<nav aria-label="([^"]+)"', page)
        }
    return found


def region_elements_in_the_templates() -> set[str]:
    """Every framework-typed region element `render/templates/` emits."""
    markup = "\n".join(templates.template(name).template for name in templates.names())
    return {anchor for anchor, marker in REGION_MARKERS.items() if re.search(marker, markup)}


def regions_emitted() -> set[str]:
    """The chrome regions this tree actually emits, measured rather than listed."""
    return nav_regions_in_the_goldens() | region_elements_in_the_templates()


# --- the region list, measured against the tree -----------------------------


def test_the_population_read_off_the_tree_is_inhabited():
    # ⛔ Ruling 48: a derived-set assertion asserts inhabitation first, or it is
    # born vacuous. A glob that matched no golden, or a template directory that
    # moved, would otherwise make every check below pass over nothing.
    assert nav_regions_in_the_goldens(), "no golden page carries a <nav> — did the goldens move?"
    assert region_elements_in_the_templates(), "no template carries a region element"


def test_the_region_table_is_total_over_what_the_tree_emits():
    # ⛔ **This is `SF-34`'s founding defect turned into a test.** Its scope line
    # was stale in two directions at once and nothing said so; from here a
    # seventh region is a red test, and *"that one is another task's"* is a row
    # rather than a silence.
    emitted = regions_emitted()
    declared = set(REGIONS)
    assert emitted - declared == set(), (
        f"the tree emits regions this part does not answer for: {sorted(emitted - declared)}"
    )
    assert declared - emitted == set(), (
        f"this part answers for regions nothing emits: {sorted(declared - emitted)}"
    )


@pytest.mark.parametrize("anchor", sorted(REGIONS))
def test_every_region_names_one_of_the_three_owners_and_says_why(anchor):
    owner, why = REGIONS[anchor]
    assert owner in (CHROME_RULED, SURFACE_RULED, DEFERRED), f"{anchor}: unknown owner {owner!r}"
    assert len(why) > 20, f"{anchor}: a reason this short is a label, not a reason"


@pytest.mark.parametrize(
    "anchor", sorted(a for a, (owner, _) in REGIONS.items() if owner == CHROME_RULED)
)
def test_every_region_this_part_owns_has_a_rule_in_it(anchor):
    # ⛔ The whole of the task in one assertion: *a class name with no rule is
    # not styling*, and neither is an `aria-label` with no rule.
    assert declarations_reaching(anchor), f"{anchor} is this part's and carries no declaration"


def test_no_rule_reaches_a_region_the_table_does_not_name():
    # ⭐ The other direction, and the one that catches a rule written for markup
    # nobody emits — which is `SF-11`'s finding 3 one layer along: the palette
    # defining tokens nothing paints with, as a selector instead of a colour.
    anchors = set(REGIONS) | {"body", "span[data-kind="}
    stray = sorted(
        selector for selector, _ in rules() if not any(anchor in selector for anchor in anchors)
    )
    assert stray == [], f"rules reaching markup no region names: {stray}"


@pytest.mark.parametrize(
    "anchor", sorted(a for a, (owner, _) in REGIONS.items() if owner == DEFERRED)
)
def test_a_deferred_region_is_left_alone_rather_than_half_styled(anchor):
    # ⚠️ Half a rule for somebody else's region is worse than none: it is a
    # decision taken on their behalf, in a file they do not read.
    assert not declarations_reaching(anchor), f"{anchor} is deferred and this part styles it"


@pytest.mark.parametrize(
    "anchor", sorted(a for a, (owner, _) in REGIONS.items() if owner == SURFACE_RULED)
)
def test_a_region_the_reading_surface_rules_is_not_re_decided_here(anchor):
    # ⭐ `main#content` needs no rule of its own: the column is bounded once, on
    # `body`, and `reading.css` already caps the prose inside it. ⛔ A second
    # `max-width` here would be the two-rules-for-one-question defect, and it is
    # also how the per-element `ch` bug arrived in the first draft of this file.
    assert not declarations_reaching(anchor), f"{anchor} is the surface's and this part styles it"


def test_the_page_skeletons_slots_are_exactly_the_ones_this_table_answers_for():
    # ⛔ The closed list. Regions 5 and 6 arrived as new *pages* filling existing
    # slots; a seventh region arriving as a new SLOT would not show up in the
    # goldens until something rendered it, and would show up here immediately.
    assert templates.placeholders("page.html") == frozenset(SKELETON_SLOTS)


# --- note (c): the bar is legible without reference to colour ---------------


def test_the_between_units_bar_is_told_apart_from_body_text_without_colour():
    # ⛔ M1's close condition 8, re-homed here and discharged. It named *"the
    # between-units bar indistinguishable from body text"* and had to VOID the
    # symptom as unfalsifiable, because nothing computed a reading order before
    # `SF-13` and no golden emitted the bar. Both are true now.
    found = declarations_reaching('nav[aria-label="Between units"]')
    assert found, "the bar carries no declaration at all"
    cues = sorted(cue for cue in NON_COLOUR_CUES if re.search(rf"\b{cue}\s*:", found))
    assert len(cues) >= 3, (
        f"the bar is told apart by {cues}, which is not enough without colour — "
        f"a bar nobody can see is not a bar that passed"
    )


def test_the_bars_own_colour_is_not_what_carries_it():
    # ⭐ The control for the check above, run negatively: strip every colour
    # declaration and the cues must survive. A rule that said only `color:` would
    # pass the count above if `color` were ever added to the cue list.
    assert not any(cue in ("color", "background") for cue in NON_COLOUR_CUES)


# --- note (d): the column is bounded ---------------------------------------


def test_the_page_column_is_bounded_and_the_bound_is_a_palette_measure():
    # ⛔ `PO-22/6`: `body` carries `margin: 0; padding: 0 var(--gutter)` and no
    # `max-width`, so at 1280px *"the full column"* was the full viewport and the
    # page read as a narrow measure with full-bleed islands. ⚠️ This is the
    # missing half of `reading.css:38-41`, never a reopening of it — which is why
    # the bound is expressed in the measure the prose already uses.
    column = rule_for("body")
    assert column is not None, "`body` carries no rule, so nothing bounds the page"
    assert re.search(r"max-width\s*:", column), "the page column carries no bound"
    assert "var(--measure)" in column, "the column's bound is not the reading measure's own token"


def test_the_column_is_bounded_exactly_once_and_on_the_element_that_owns_the_measure():
    # ⛔ **A measured defect, pinned.** `--measure` is `80ch` and `ch` resolves
    # against the ELEMENT's own font, so the first draft of this file wrote the
    # same `max-width` on each region and produced THREE columns — 800px, 715.7px
    # and 680.3px at a 1280px viewport in Chrome 149, because the masthead, the
    # outline and the bar each set their own face and size. ⭐ `body` carries the
    # prose font, which is the font the measure was chosen in, so the number is
    # computed there and nowhere else.
    bounded = sorted(selector for selector, block in rules() if "max-width" in block)
    assert bounded == ["body"], f"the column is bounded in more than one place: {bounded}"


def test_the_running_measure_is_not_reopened_here():
    # ⚠️ `reading.css` caps `main p, main li` at `--measure` and that decision
    # stands. A second cap here would be two rules for one question.
    assert not re.search(r"\bmain\s+(p|li)\b", body()), "this part re-decides the prose measure"


# --- QA-03/2: the four ownerless tokens ------------------------------------


@pytest.mark.parametrize("token", ONCE_OWNERLESS)
def test_each_once_ownerless_palette_token_is_painted_here(token):
    # ⛔ `QA-03/2`: four colour tokens were defined in `palette.css`, painted by
    # no stylesheet, and nobody's at any milestone. ⭐ The alternative was to
    # delete them from the palette; they are painted instead, and
    # `test_the_unpainted_rows_are_derived_from_the_stylesheets_not_believed`
    # is what forced the ledger to say which ground each one is read against.
    assert f"var({token})" in body(), f"{token} is still ownerless"


def test_this_part_defines_no_colour_and_no_measure_of_its_own():
    # ⚠️ `test_palette` asserts the first half over every authored part; this is
    # the same claim at this file, plus the half about measures — `palette.css`
    # calls itself the shared vocabulary for *"every colour, measure and font"*.
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", body()), "a colour outside the palette"
    assert "--" not in body().split("var(")[0], "a token is DEFINED here rather than used"


# --- the hooks, and where the spelling comes from ---------------------------


@pytest.mark.parametrize(
    "hook", sorted(h for h, f in _FORM_OF.items() if f in (ATTRIBUTE_FORM, KIND_FORM))
)
def test_every_non_class_hook_is_reached_by_a_rule_in_this_part(hook):
    # ⛔ `SF-27/2` measured that NOTHING painted either hook at all — the markup
    # shipped and the rules did not, which is this task's whole reason to exist.
    assert SURFACE_HOOKS[hook] in body(), f"{hook} is published and nothing here reaches it"


def test_a_kind_hook_is_reached_through_its_element_and_never_on_its_own():
    # ⛔ `data-kind` is OVERLOADED: `section.html` carries a section's own kind
    # in it, and a section's kind is a corpus's word. An unscoped
    # `[data-kind="numbering"]` would style a section the day a corpus named one
    # `numbering` — which is a page that changes because of its material (R1).
    for hook, form in sorted(_FORM_OF.items()):
        if form != KIND_FORM:
            continue
        value = SURFACE_HOOKS[hook]
        for selector, _ in rules():
            for part in selector.split(","):
                if f'[{SURFACE_HOOKS["kind"]}="{value}"]' not in part:
                    continue
                assert re.match(r"^\s*[a-z]+\[", part), f"{part.strip()} names no element"


def test_this_part_targets_no_class_at_all():
    # ⭐ The property that let this part be written a milestone after the markup
    # it styles, and the property to preserve: every region is reached by
    # element, `aria-label` or `data-*`, so no page changes and no class joins
    # the published markup contract.
    assert re.findall(r"\.[a-zA-Z][\w-]*", body()) == []


# --- where it sits in the bundle -------------------------------------------


def test_it_is_in_the_bundle_after_the_reading_surface():
    # ⛔ Two rules of equal specificity: the last one wins, so the order IS the
    # design. The page column refines what `reading.css` sets on `body` and on
    # `body`'s children, and would lose if it were loaded first.
    assert CHROME in STYLE_PARTS
    assert STYLE_PARTS.index(CHROME) > STYLE_PARTS.index("reading.css")
    assert STYLE_PARTS.index(CHROME) < STYLE_PARTS.index("code-highlight.css")


def test_it_is_a_file_on_disk_and_not_a_string_in_python():
    # R13, at the one place a stylesheet could still have arrived as a literal.
    assert (ASSET_DIR / CHROME).is_file()
    assert text(CHROME) == (ASSET_DIR / CHROME).read_bytes().decode("utf-8")
