"""The chrome part: which regions it answers for, and the two clauses re-homed onto it.

Mirrors no source module — it asserts things about `render/assets/chrome.css`,
which is data, the way `test_palette` does for `palette.css`.

## ⛔ Why the region list is DERIVED and not listed

⚠️ **A typed region list reads as complete either way.** A new page kind or a
new panel adds a region, and nothing about a short list signals the gap, so the
region list is measured against the tree rather than against a table.

⭐ **So the population here is read out of the tree on every run:** every
`<nav aria-label>` a committed golden page carries, plus every framework-typed
region element in `render/templates/`. A seventh region fails
`test_the_region_table_is_total_over_what_the_tree_emits` on the day it appears,
and the answer *"it is another task's"* is a row in the table rather than a
silence.

⛔ **And what the tree can AUTHOR, not only what it emits**:
a `<nav>` a template or an emitter can write and no golden carries was invisible
to that population — the trail was. `authoring.py` reads every authoring site's
RESOLVED label, and `authorable ⊆ REGIONS` is asserted as a subset.
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
from tests.studyforge.render.pageassets import authoring

#: The part under test.
CHROME = "chrome.css"

#: ⭐ The part is split at named seams for R11: `chrome.css` is where things
#: are, `lists.css` what the reader navigates, `onward.css` where they go
#: next, `notes.css` what the page tells them. Every claim below is about the
#: four together, read as one part.
CHROME_PARTS = (CHROME, "lists.css", "onward.css", "notes.css")

#: Who answers for a region. ⛔ Three values and no fourth: a region that fits
#: none of them is a region whose owner nobody decided, which is the exact state
#: an ownerless palette token is in.
CHROME_RULED = "chrome"  # this part carries its rules
SURFACE_RULED = "reading"  # `reading.css` already styles it as the element it is
DEFERRED = "deferred"  # another part's, and the part is named

#: `region anchor -> (who answers for it, why)`. ⛔ Asserted TOTAL over what the
#: tree emits, in both directions, by the first test below.
REGIONS: dict[str, tuple[str, str]] = {
    "body": (CHROME_RULED, "the page column — note (d); one bound, on one element"),
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
    'nav[aria-label="Breadcrumb"]': (
        CHROME_RULED,
        "region 9, the unit page's trail. ⛔ No committed golden emits it, "
        "so it is here because the tree can AUTHOR it",
    ),
    'nav[aria-label="Units"]': (CHROME_RULED, "region 5, a container's unit listing"),
    'nav[aria-label="Containers"]': (
        CHROME_RULED,
        "region 10, the rail that reaches the OTHER containers. ⛔ Without it a unit "
        "page's navs never leave its own container, so the only crossing is "
        "back through the root index. ⭐ Laid "
        "out BESIDE the reading column where a viewport has room for one, and as a "
        "card in the column where it has not — so it is the one region "
        "that does not resolve the reading surface's column at every width",
    ),
    'nav[aria-label="Contents"]': (
        CHROME_RULED,
        "region 6, the root index's disclosure tree",
    ),
    'section[aria-label="About this site"]': (
        CHROME_RULED,
        "region 12, the root index's plain explanation and its short columns. "
        "⚠️ Not a `<nav>` and not in a template, so the census reaches it "
        "through the index renderer's own markup",
    ),
    'section[aria-label="Progress"]': (
        CHROME_RULED,
        "region 13, the progress line and the segmented strip on the index and a container page",
    ),
    'form[role="search"]': (
        CHROME_RULED,
        "region 14, the index's filter and its expand and collapse controls",
    ),
    'nav[aria-label="Up next"]': (
        CHROME_RULED,
        "region 11, the Up next slip on the root index and a container page. "
        "⭐ The one filled area of `--sign` on the page",
    ),
    # ⚠️ `data-practice`, never `data-section`: that one carries a CORPUS's key (R1).
    "section[data-practice]": (DEFERRED, "region 15, the practice panel — `practice.css`'s"),
    'section[data-section="read-mark"]': (
        CHROME_RULED,
        "region 7, the reader's own mark-as-read control. ⚠️ It ships "
        "`hidden` and `read-mark.js` unhides it only with a working store behind "
        "it, so the rules here are for the region a reader actually sees",
    ),
    "footer#player": (
        DEFERRED,
        "the narration transport — painted in "
        "`narration.css`, its own part, which is why this region stays DEFERRED "
        "rather than becoming this part's: `--player-height`, `--panel` and "
        "`--shadow` are painted there and this file still reaches none of them",
    ),
    'section[data-section="narration-gap"]': (
        DEFERRED,
        "region 8, the panel that names a narration promise the disk did not keep "
        "⛔ It is the transport's own region and is painted in "
        "`narration.css` beside `footer#player`, for the same reason and against "
        "the same `--panel` ground — so this file reaches none of it either. "
        "⚠️ It is NOT on every page: a corpus that was never narrated is complete "
        "rather than short, and carries no notice at all",
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
    'section[data-section="narration-gap"]': r'<section data-section="narration-gap"',
    "section[data-practice]": r"<section data-practice",
    'section[aria-label="About this site"]': r'<section aria-label="About this site"',
    'section[aria-label="Progress"]': r'<section aria-label="Progress"',
    'form[role="search"]': r'<form role="search"',
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
    "headingattributes": (
        "the anchor and the clip the `<h1>` carries when the material's own "
        "opening heading was promoted into it; it is addressing and "
        "narration, and nothing is painted"
    ),
    # every slot below lands inside the one column `body` bounds
    "meta": "the masthead's second line — region 1",
    "breadcrumb": (
        "region 9, the trail. ⭐ A row in `REGIONS`: the census reads what the tree "
        "can AUTHOR, so a region no golden emits is still visible to it"
    ),
    "outline": "region 2",
    "body": "the reading surface — `reading.css`, by the block vocabulary",
    "pending": "region 4",
    "mark": (
        "region 7, the read control. ⭐ A slot shows up here as soon as the "
        "skeleton carries it, without waiting for a golden to emit it"
    ),
    "rootattributes": "the mode attribute on `<html>` of a modes corpus; nothing is painted",
    "modehead": "a modes corpus' stylesheet, script and boot, in `<head>`; nothing is painted",
    "modeswitch": "a modes corpus' switch and first-visit question, inside the top bar",
    "modenote": "the note a page outside the reading mode shows, in the masthead under the bar",
    "player": "the narration transport's — the DEFERRED row above",
    "nav": "region 3",
    "rail": (
        "region 10, the rail across containers. ⭐ A slot shows up here as soon as "
        "the skeleton carries it, without waiting for a golden to emit it"
    ),
}


def body() -> str:
    """`chrome.css` with its comments removed — the rules, and nothing about them."""
    joined = "\n".join(text(part) for part in CHROME_PARTS)
    return re.sub(r"/\*.*?\*/", "", joined, flags=re.DOTALL)


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
    """Every framework-typed region element `render/templates/` or a golden emits.

    ⚠️ The goldens as well: the index's head and the progress
    region are written by the index and container renderers, not by a template.
    """
    markup = "\n".join(templates.template(name).template for name in templates.names())
    markup += "\n".join(
        path.read_bytes().decode("utf-8") for path in sorted(GOLDEN_DIR.glob("*.html"))
    )
    return {anchor for anchor, marker in REGION_MARKERS.items() if re.search(marker, markup)}


def regions_emitted() -> set[str]:
    """The chrome regions this tree actually emits, measured rather than listed."""
    return nav_regions_in_the_goldens() | region_elements_in_the_templates()


# --- the region list, measured against the tree -----------------------------


def test_the_population_read_off_the_tree_is_inhabited():
    # ⛔ A derived-set assertion asserts inhabitation first, or it is
    # born vacuous. A glob that matched no golden, or a template directory that
    # moved, would otherwise make every check below pass over nothing.
    assert nav_regions_in_the_goldens(), "no golden page carries a <nav> — did the goldens move?"
    assert region_elements_in_the_templates(), "no template carries a region element"


def test_the_region_table_is_total_over_what_the_tree_emits():
    # ⛔ **A typed list that reads as complete either way, turned into a test.**
    # A new region is a red test, and *"that one is another task's"* is a row
    # rather than a silence.
    emitted = regions_emitted()
    declared = set(REGIONS)
    assert emitted - declared == set(), (
        f"the tree emits regions this part does not answer for: {sorted(emitted - declared)}"
    )
    # ⛔ Against EMITTED alone, declaring the trail — a region the tree authors
    # and no golden emits — would fail here. A stale row is still caught; a row the tree can
    # author is not refused for being unrendered.
    reachable = emitted | authoring.authorable()
    assert declared - reachable == set(), (
        f"this part answers for regions the tree can neither emit nor author: "
        f"{sorted(declared - reachable)}"
    )


# --- What the tree can AUTHOR, and never only what it emits ----------------


def test_every_nav_the_tree_can_author_resolves_to_a_label():
    # ⛔ An authoring site whose label is not a value — a local, a call,
    # a concatenation — is a region the census below cannot name, so it is a red
    # check here rather than a site the sweep quietly dropped.
    sites = authoring.sites()
    assert sites, "no <nav> is authored anywhere under src/ — did the sweep move?"
    unresolved = sorted(site.where for site in sites if not site.resolved)
    assert unresolved == [], f"<nav> opened with a label nothing resolves: {unresolved}"


def test_every_region_a_golden_emits_is_one_the_tree_can_author():
    # ⭐ **The literal-sweep tell, as a test.** Two labels are composed from
    # `LIST_LABEL`, so an authorable side built from literals misses both and
    # still passes the subset below — over less. Every emitted region must be
    # authorable, or the authorable side is the blind one.
    missing = nav_regions_in_the_goldens() - authoring.authorable()
    assert missing == set(), f"emitted and not authorable, so the sweep is blind: {sorted(missing)}"


def test_every_region_the_tree_can_author_is_one_this_table_recognises():
    # ⛔ **`authorable ⊆ recognisable`, a SUBSET and never the
    # equality** — a row stated ahead of its renderer is legitimate, a region
    # authored with no row is the only direction that can hide one.
    authorable = authoring.authorable()
    unrecognised = sorted(authorable - set(REGIONS))
    assert unrecognised == [], (
        f"the tree can author regions this part does not answer for: {unrecognised}\n"
        f"  authorable: {sorted(authorable)}\n"
        f"  painted:    {sorted(authoring.painted())}\n"
        f"  declared:   {sorted(a for a in REGIONS if a.startswith('nav['))}"
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
    # ⛔ The whole of the part in one assertion: *a class name with no rule is
    # not styling*, and neither is an `aria-label` with no rule.
    assert declarations_reaching(anchor), f"{anchor} is this part's and carries no declaration"


def test_no_rule_reaches_a_region_the_table_does_not_name():
    # ⭐ The other direction, and the one that catches a rule written for markup
    # nobody emits — the same defect as a palette
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
    # `max-width` here would be the two-rules-for-one-question defect, and the
    # per-element `ch` one besides.
    assert not declarations_reaching(anchor), f"{anchor} is the surface's and this part styles it"


def test_the_page_skeletons_slots_are_exactly_the_ones_this_table_answers_for():
    # ⛔ The closed list. Regions 5 and 6 arrived as new *pages* filling existing
    # slots; a seventh region arriving as a new SLOT would not show up in the
    # goldens until something rendered it, and would show up here immediately.
    assert templates.placeholders("page.html") == frozenset(SKELETON_SLOTS)


# --- note (d): the column is bounded ---------------------------------------


def test_the_page_column_is_bounded_and_the_bound_is_a_palette_measure():
    # ⛔ Without a `max-width` on `body`, the full column is the full viewport
    # and the page reads as a narrow measure with full-bleed islands. ⚠️ This
    # completes `reading.css`'s measure, never reopens it — which is why the
    # bound is expressed in the measure the prose already uses.
    column = rule_for("body")
    assert column is not None, "`body` carries no rule, so nothing bounds the page"
    assert re.search(r"max-width\s*:", column), "the page column carries no bound"
    assert "var(--measure)" in column, "the column's bound is not the reading measure's own token"


def test_the_column_is_bounded_only_ever_on_the_element_that_owns_the_measure():
    # ⛔ `--measure` is `80ch` and `ch` resolves against the ELEMENT's own
    # font, so the same `max-width` on each region would produce three columns
    # of different widths, because the masthead, the outline and the bar each
    # set their own face and size. ⭐ `body` carries the
    # prose font, which is the font the measure was chosen in, so the number is
    # computed there and nowhere else.
    #
    # ⚠️ The rail beside the column is a second bound on the SAME element under
    # a media query, and the defect this clause exists for is a bound on a
    # DIFFERENT element. ⭐ So the subject is asserted, in both directions: every bounding
    # selector's subject is `body`,
    # and there is at least one, so a file that bounded nothing cannot pass.
    # ⚠️ `max-width: none` is the ABSENCE of a bound (a list row is not
    # running text, so it gives up the prose measure `reading.css` sets on every
    # `main li`), and is not counted as one.
    bounded = sorted(
        selector for selector, block in rules() if re.search(r"max-width:\s*(?!\s|none\b)", block)
    )
    assert bounded, "nothing in this part bounds a column at all"
    astray = sorted(
        selector for selector in bounded if selector != "body" and not selector.startswith("body:")
    )
    assert astray == [], f"the column is bounded on an element other than `body`: {astray}"


# --- The second shape, and the two tokens it paints ------------------------


def test_the_rail_beside_the_column_is_declared_under_exactly_one_threshold():
    # ⛔ **One threshold, because the browser arm READS IT BACK.**
    # `tests/visual/test_rail.py` takes its two viewport widths from this file
    # rather than repeating the number, and asserts they straddle it — so a
    # second `min-width` here would leave that arm judging one of two layouts
    # twice with nothing saying so. ⚠️ A media query resolves `rem` against the
    # INITIAL font size, never `html`'s, which is why the threshold is readable
    # as a number at all.
    thresholds = re.findall(r"@media\s*\(min-width:\s*([0-9.]+)rem\)", body())
    assert len(thresholds) == 1, f"this part declares {len(thresholds)} width thresholds, not one"


def test_the_two_shapes_are_one_markup_and_the_wide_one_is_asked_for_by_the_region():
    # ⭐ The rail moves beside the column on a wide viewport and folds
    # back into it on a narrow one, over the SAME bytes. ⛔ The wide shape is
    # conditioned on the page CARRYING the region — the root index carries none,
    # and a grid declared unconditionally would give it an empty rail track.
    wide = [
        selector
        for selector, block in rules()
        if "grid-column" in block or "grid-template" in block
    ]
    assert wide, "nothing in this part lays the rail out beside the column"
    assert all("body" in selector for selector in wide), wide
    assert any(":has(" in selector for selector in wide), (
        "the two-column page is declared unconditionally, so a page with no rail "
        f"gets an empty track down its left: {wide}"
    )


@pytest.mark.parametrize("token", ("--rail", "--page-max"))
def test_the_layout_tokens_this_file_left_unpainted_are_painted_now(token):
    # ⛔ A token defined for a layout and painted by nothing is dead. ⭐ The
    # rail-and-content layout here is the layout both exist for.
    assert f"var({token})" in body(), f"{token} is still unpainted"


def test_the_running_measure_is_not_reopened_here():
    # ⚠️ `reading.css` caps `main p, main li` at `--measure` and that decision
    # stands. A second cap here would be two rules for one question.
    assert not re.search(r"\bmain\s+(p|li)\b", body()), "this part re-decides the prose measure"


# --- the hooks, and where the spelling comes from ---------------------------


@pytest.mark.parametrize(
    "hook", sorted(h for h, f in _FORM_OF.items() if f in (ATTRIBUTE_FORM, KIND_FORM))
)
def test_every_non_class_hook_is_reached_by_a_rule_in_this_part(hook):
    # ⛔ Markup that ships a hook no rule paints is a hook that does nothing.
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


# --- the read words, off the screen and in the accessibility tree --

READ_STATE = f'span[{SURFACE_HOOKS["kind"]}="{SURFACE_HOOKS["read_state"]}"]'


def test_the_read_words_are_kept_off_the_screen_but_not_out_of_the_tree():
    # ⭐ The visual mark is the tick; the words are for assistive technology.
    rule = rule_for(READ_STATE)
    assert rule is not None, "no rule keeps the read words off the screen"
    for declaration in ("position: absolute", "width: 1px", "height: 1px", "clip-path: inset(50%)"):
        assert declaration in rule
    # ⛔ The other way: nothing here removes them from what a screen reader reads.
    for hiding in ("display", "visibility", "content"):
        assert hiding not in rule, f"{hiding} would take the words away from a screen reader"
