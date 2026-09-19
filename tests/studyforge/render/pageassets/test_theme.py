"""The theme control: the reader's own choice of light, dark or the system's.

Mirrors `render/assets/theme.js` and the head boot in `render/templates/page.html`
(`W388` stage 2, the user: *"have the both dark and light themes in studyforge as
well"*).

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
    """The skeleton's one inline script, as written."""
    found = re.findall(r"<script>(.*?)</script>", templates.template(SKELETON).template)
    assert len(found) == 1, f"the skeleton carries {len(found)} inline scripts"
    return found[0]


def declared(part: str, name: str) -> str:
    """The value `part` assigns to the `var` called `name`."""
    found = re.search(rf"var {re.escape(name)} = (.+?);", text(part))
    assert found is not None, f"{part} declares no {name}"
    return found.group(1).strip()


def missing(script: str) -> list[str]:
    """Which of the store's three spellings `script` does not carry, by name.

    ⛔ ONE function, used by the reading and by its refutation: a check written
    twice is a check that can pass in one spelling and fail in the other.
    """
    key = declared(STORE, "DISPLAY_KEY").strip("'\"")
    field = declared(STORE, "DISPLAY_FIELD").strip("'\"")
    version = declared(STORE, "RECORD_VERSION")
    return [
        name
        for name, tell in (
            ("key", f'"{key}"'),
            ("field", f"d.{field}."),
            ("version", f"=== {version}"),
        )
        if tell not in script.replace("===", "=== ").replace("===  ", "=== ")
    ]


# --- the boot finds the record the store writes ------------------------------


def test_the_boot_spells_the_store_s_key_field_and_version_exactly():
    # ⛔ The one thing this module exists for. Each value is read from the
    # STORE's source and looked for in the boot, so neither side is retyped.
    assert missing(boot()) == []


@pytest.mark.parametrize(
    ("planted", "said"),
    (
        (("studyforge.display.v1", "studyforge.display.v2"), "key"),
        ((".display.theme", ".displays.theme"), "field"),
        (("version===1", "version===2"), "version"),
    ),
)
def test_a_boot_that_misspells_any_of_the_three_is_caught_by_name(planted, said):
    # ⭐ The other way (R12), through the SAME function: each of the three
    # changed by one character, and the one that moved is the one reported.
    written = boot()
    assert planted[0] in written, written
    assert missing(written.replace(*planted)) == [said]


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
    # ⚠️ Reading `localStorage` THROWS on the property access in a private
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
    body = text(PART)
    assert "window.studyforge.progress" in body
    assert "localStorage" not in body


@pytest.mark.parametrize("choice", CHOICES)
def test_the_part_and_the_markup_agree_on_every_choice(choice):
    assert f"'{choice}'" in text(PART)
    assert f'data-theme-choice="{choice}"' in templates.template(SKELETON).template


def test_the_part_types_no_word_a_reader_sees():
    # ⛔ R13: the labels are the template's. This part toggles `hidden` and
    # `aria-pressed` and nothing else a reader can read.
    body = text(PART)
    code = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("*"))
    for label in ("System", "Light", "Dark"):
        assert f'"{label}"' not in code and f"'{label}'" not in code


# --- the control the skeleton carries ----------------------------------------


def test_the_control_is_in_the_masthead_and_is_not_an_eleventh_child_of_the_body():
    # ⛔ `chrome.css` spans the rail over the body's ten top-level positions. A
    # control placed beside them would move the rail rather than add a setting.
    page = templates.template(SKELETON).template
    inside = page[page.index("<header>") : page.index("</header>")]
    assert 'aria-label="Theme"' in inside


def test_the_control_ships_hidden_with_a_name_and_three_pressed_states():
    page = templates.template(SKELETON).template
    group = re.search(r'<div role="group" aria-label="Theme"[^>]*>(.*?)</div>', page, re.DOTALL)
    assert group is not None, page
    assert "hidden" in group.group(0).split(">")[0]
    buttons = re.findall(r"<button([^>]*)>", group.group(1))
    assert len(buttons) == len(CHOICES)
    assert [b for b in buttons if 'type="button"' in b] == buttons
    pressed = [b for b in buttons if 'aria-pressed="true"' in b]
    assert len(pressed) == 1 and 'data-theme-choice="system"' in pressed[0]


def test_the_control_carries_a_word_for_each_choice():
    page = templates.template(SKELETON).template
    labels = re.findall(r'<button[^>]*data-theme-choice="([a-z]+)"[^>]*>([^<]+)</button>', page)
    assert [choice for choice, _ in labels] == list(CHOICES)
    assert all(word.strip() for _, word in labels)
