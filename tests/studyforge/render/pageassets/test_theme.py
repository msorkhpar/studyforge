"""The theme control: the reader's own choice of light, dark or the system's.

Mirrors `render/assets/theme.js` and the head boot in `render/templates/page.html`
(a light and a dark theme, and the system's).

⛔ **THE SPELLING IS TWO-SIDED AND THAT IS WHY THIS MODULE EXISTS.** The boot
runs in the head, before any bundle exists, so it cannot ask `study-progress.js`
what the store's key is — it spells the key, the version and the field a second
time. ⚠️ A second spelling that differed by one character would simply never
find the record: the page would follow the system, the control would show
*System*, every test that only ever looked at one side would stay green, and the
reader's choice would be silently forgotten on every reload. ⭐ So the two
spellings are compared here, and the comparison is refuted against a planted
mismatch.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render import templates
from studyforge.render.pageassets import SCRIPT_PARTS, text

#: The part this module mirrors, and the one that owns the store it reads.
PART = "theme.js"
STORE = "study-progress.js"

#: The skeleton the boot and the control both live in.
SKELETON = "page.html"

#: The three answers the control can record. ⛔ `system` is one of them and is
#: also what an absent record means, so the two can never disagree.
CHOICES = ("system", "light", "dark")


def boot() -> str:
    """The skeleton's head boot, as written: the first of its two inline scripts.

    ⭐ The second puts the rail's saved scroll position back (`rail-scroll.js` saves it).
    """
    found = re.findall(r"<script>(.*?)</script>", templates.template(SKELETON).template)
    assert len(found) == 2, f"the skeleton carries {len(found)} inline scripts"
    return found[0]


def code(part: str) -> str:
    """`part`'s source with every block comment taken out.

    ⛔ **A clause about what a part DOES must not read what it SAYS.**
    `test_the_part_reads_the_store_through_its_published_name` refuses the name
    `localStorage` in this part — and the part's docstring has to name it, to say
    why the head boot never touches it. ⚠️ Without this the file could only be
    made green by leaving that reason unwritten.
    """
    return re.sub(r"/\*.*?\*/", "", text(part), flags=re.S)


def declared(part: str, name: str) -> str:
    """The value `part` assigns to the `var` called `name`."""
    found = re.search(rf"var {re.escape(name)} = (.+?);", text(part))
    assert found is not None, f"{part} declares no {name}"
    return found.group(1).strip()


#: A boot that reads the display record out of `localStorage` in the `<head>`,
#: and what that costs. ⛔ **The `<head>` is the document's first touch of that
#: area**, and a document that binds the area before the previous document's
#: write has committed keeps a snapshot without it, for its whole life: a mark
#: written on one page can be missing on the next. ⛔ The reader then marks the page they are on
#: and the earlier mark is
#: DESTROYED, because the new record is composed from the stale set.
#: ⭐ It is kept here as the thing every clause below is refuted against.
BOOT_THAT_LOST_MARKS = (
    'try{var d=JSON.parse(localStorage.getItem("studyforge.display.v1"));'
    "var t=d&&d.version===1&&d.display&&d.display.theme;"
    'if(t==="light"||t==="dark"){document.documentElement.setAttribute("data-theme",t);}}'
    "catch(e){}"
)


def missing(script: str) -> list[str]:
    """Which of the mirror's spellings `script` does not carry, by name.

    ⛔ ONE function, used by the reading and by its refutation: a check written
    twice is a check that can pass in one spelling and fail in the other.

    ⚠️ **The boot does not spell the DISPLAY record's key.** What it spells is the boot CACHE the
    store keeps in
    `sessionStorage` — a different storage area, so reading it binds nothing the
    marks live in. ⛔ The key is COMPOSED by the store from a prefix, the
    preference's name and a suffix, and it is composed the same way here rather
    than written out, so a store that renames any of the three reds this.
    """
    key = (
        declared(STORE, "BOOT_PREFIX").strip("'\"")
        + declared(PART, "PREFERENCE").strip("'\"")
        + declared(STORE, "BOOT_SUFFIX").strip("'\"")
    )
    return [
        name
        for name, tell in (("key", f'"{key}"'), ("area", "sessionStorage"))
        if tell not in script
    ]


# --- the boot finds the mirror the part writes -------------------------------


def test_the_boot_spells_the_mirror_exactly_as_the_part_that_writes_it():
    # ⛔ The one thing this module exists for. The key is read from `theme.js`'s
    # source and looked for in the boot, so neither side is retyped.
    assert missing(boot()) == []


@pytest.mark.parametrize(
    ("planted", "said"),
    (
        (("studyforge.boot.theme.v1", "studyforge.boot.theme.v2"), "key"),
        (("sessionStorage", "localStorage"), "area"),
    ),
)
def test_a_boot_that_misspells_the_mirror_is_caught_by_name(planted, said):
    # ⭐ The other way (R12), through the SAME function: each spelling changed by
    # one token, and the one that moved is the one reported.
    written = boot()
    assert planted[0] in written, written
    assert missing(written.replace(*planted)) == [said]


def test_the_boot_never_touches_the_store_the_reader_s_MARKS_live_in():
    # ⛔ **Not a style rule.** The `<head>` is the earliest a document can touch
    # `localStorage`, and a snapshot taken there can be older than the write the
    # previous page made — permanently, for that document. ⚠️ The theme is worth
    # one frame of flash on the first page of a tab; it is not worth a reader's
    # marks. ⭐ The mirror lives in a DIFFERENT storage area, which is the whole
    # of the repair.
    assert "localStorage" not in boot(), (
        "the head boot binds the durable store before the page is parsed, which "
        "is what can cost a reader a mark"
    )


def test_the_boot_that_shipped_is_caught_by_that_clause():
    # ⭐ The other way, against the exact text that shipped rather than an
    # impression of it: a clause that has only ever seen the repair has not been
    # shown to notice the defect it exists for.
    assert "localStorage" in BOOT_THAT_LOST_MARKS
    assert missing(BOOT_THAT_LOST_MARKS) == ["key", "area"]


def test_the_boot_writes_the_attribute_the_palette_guards_on():
    written = boot()
    assert '"data-theme"' in written
    assert "documentElement" in written


def test_the_boot_applies_only_the_two_themes_the_palette_declares():
    # ⛔ A stored value this cannot apply is ignored, not written through: an
    # unknown value on the root would match no guard and paint the light theme
    # while the control claimed something else.
    written = boot()
    assert '"light"' in written and '"dark"' in written
    assert '"system"' not in written, "system is the absence of the attribute, not a value of it"


def test_the_boot_is_in_the_head_before_anything_is_painted():
    # ⛔ The whole reason it is inline rather than a part of the bundle: a
    # deferred script runs after the first paint, and the reader would see the
    # wrong theme for a frame on every page.
    page = templates.template(SKELETON).template
    assert page.index("<script>") < page.index("</head>")
    assert 'href="${stylesheet}"' in page


def test_the_boot_reaches_nothing_and_handles_no_event():
    written = boot()
    assert "://" not in written and "fetch" not in written and "src" not in written
    assert re.search(r"\son[a-z]+=", templates.template(SKELETON).template) is None


def test_the_boot_survives_a_browser_that_refuses_site_data():
    # ⚠️ Reading `sessionStorage` THROWS on the property access in a private
    # window or with site data blocked — not on the read — so the whole of it
    # is inside one `try`. Without that the page would stop before its title.
    written = boot()
    assert written.startswith("try{") and "catch" in written


# --- the deferred part, and where it sits in the bundle ----------------------


def test_the_part_follows_the_store_and_precedes_its_last_consumer():
    order = list(SCRIPT_PARTS)
    assert order.index(STORE) < order.index(PART) < order.index("read-mark.js")
    assert order[-1] == "read-mark.js"


def test_the_part_reads_the_store_through_its_published_name():
    # ⛔ One implementation of the store, asked questions by this part — never a
    # second reader of `localStorage`.
    body = code(PART)
    assert "window.studyforge.progress" in body
    assert "localStorage" not in body


def test_the_part_keeps_the_boot_cache_through_the_store_and_clears_it_for_system():
    # ⛔ **The cache is never an authority.** The durable answer
    # stays in the display record, which only this part reads; what is cached is
    # the one string the head boot may act on. ⚠️ *System* caches `null` rather
    # than the word, because an absent cache and a cached *system* must not be
    # two answers to one question — the boot acts on `light` and `dark` alone.
    # ⛔ Through the STORE, so `test_progress`'s clause that one part touches the
    # browser's storage stays true of a different area too.
    body = code(PART)
    assert "store.cache(" in body and "sessionStorage" not in body
    assert "null" in body[body.index("function remember(") : body.index("function paint(")]


def test_the_cache_is_written_from_the_paint_so_it_can_never_lag_the_page():
    # ⭐ Written inside `paint`, which is the ONE place the attribute is set, so
    # the frame the boot will restore is the frame the reader is looking at.
    # ⛔ Cached from `choose` instead it would be right for a press and wrong for
    # the load that follows it.
    body = code(PART)
    painting = body[body.index("function paint(") : body.index("function choose(")]
    assert "remember(choice)" in painting, (
        "the boot cache is not kept from the page's own paint, so a load and a "
        "press can leave the boot restoring a theme the reader is not looking at"
    )


@pytest.mark.parametrize("choice", CHOICES)
def test_the_part_keeps_each_stored_choice_and_the_markup_names_the_two_it_offers(choice):
    assert f"'{choice}'" in text(PART)
    markup = templates.template(SKELETON).template
    assert 'data-theme-choice="toggle"' in markup
    assert "data-to-dark=" in markup and "data-to-light=" in markup


def test_the_part_types_no_word_a_reader_sees():
    # ⛔ R13: the names are the template's. This part picks one of the two attributes the
    # button carries and types nothing else a reader can read.
    body = text(PART)
    code_only = "\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith("*")
    )
    for label in ("System", "Light", "Dark", "Switch"):
        assert f'"{label}' not in code_only and f"'{label}" not in code_only


# --- the control the skeleton carries ----------------------------------------


def toolbar() -> str:
    page = templates.template(SKELETON).template
    return page[page.index('<div role="toolbar"') : page.index("</header>")]


def test_the_control_is_in_the_top_bar_and_is_not_a_new_child_of_the_body():
    # ⛔ `chrome.css` spans the rail over the body's top-level positions. A control placed
    # beside them would move the rail rather than add a setting.
    assert 'data-section="theme"' in toolbar()


def test_the_control_is_one_focusable_icon_button_with_a_name_that_ships_hidden():
    button = re.search(r'<button[^>]*data-section="theme"[^>]*>(.*?)</button>', toolbar(), re.S)
    assert button is not None
    opening = button.group(0).split(">")[0]
    assert 'type="button"' in opening and "hidden" in opening
    assert 'aria-label="' in opening
    assert 'tabindex="-1"' not in opening
    assert button.group(1).count("<svg") == 2
    assert 'data-icon="sun"' in button.group(1) and 'data-icon="moon"' in button.group(1)
    assert 'aria-hidden="true"' in button.group(1)


def test_the_control_carries_a_word_for_each_theme_it_can_switch_to():
    markup = toolbar()
    for attribute in ("data-to-dark", "data-to-light"):
        found = re.search(rf'{attribute}="([^"]+)"', markup)
        assert found is not None and found.group(1).strip()
