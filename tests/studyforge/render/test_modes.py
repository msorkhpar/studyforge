"""Mirror of `src/studyforge/render/modes.py` (R12): the reading-modes slots and files."""

from __future__ import annotations

from studyforge.corpus.manifest.reading import Language, Mode, Reading
from studyforge.render import modes, templates

LANGUAGES = (Language("aa", "Aa", ("aa",)), Language("bb", "Bb", ("bb",)))
MODES = (
    Mode("only-aa", "Aa <only>", "Aa & nothing else", "aa", ("aa",), ("aa",)),
    Mode("only-bb", "Bb", "Bb only", "bb", ("bb",), ("bb",)),
    Mode("both", "Both", "Aa first", "aa", ("aa", "bb"), ("aa", "bb")),
)
READING = modes.offer(Reading(languages=LANGUAGES, modes=MODES, default_mode="only-bb"))


def href(name: str) -> str:
    return f"../x/{name}"


def test_no_reading_and_no_modes_fill_four_empty_slots_and_write_no_file():
    languages_only = modes.offer(Reading(languages=LANGUAGES))
    assert languages_only is None and modes.offer(None) is None
    assert modes.slots(None, href) == dict.fromkeys(modes.SLOTS, "")
    assert modes.files(None) == {}


def test_the_slots_are_exactly_the_skeletons_new_placeholders():
    assert set(modes.SLOTS) <= templates.placeholders("page.html")
    for name in modes.SLOTS:
        assert f"${{{name}}}" in templates.template("page.html").template


def test_the_root_carries_the_default_mode_and_the_head_links_the_two_files():
    slots = modes.slots(READING, href)
    assert slots["rootattributes"] == ' data-mode="only-bb"'
    assert '<link rel="stylesheet" href="../x/modes.css">' in slots["modehead"]
    assert '<script src="../x/modes.js" defer></script>' in slots["modehead"]
    assert set(slots) == {"rootattributes", "modehead", "modeswitch"}
    assert slots["modehead"].endswith("\n") and slots["modeswitch"].endswith("\n")


def test_the_boot_reads_the_session_cache_never_local_storage_and_knows_every_mode():
    boot = modes.slots(READING, href)["modehead"]
    assert 'sessionStorage.getItem("studyforge.boot.mode.v1")' in boot
    assert "localStorage" not in boot
    assert 'm==="only-aa"||m==="only-bb"||m==="both"' in boot
    assert 'location.protocol!=="file:"' in boot
    assert boot.count("try{") == 1 and "catch(e)" in boot


def test_the_switch_and_the_question_list_exactly_the_declared_modes_escaped():
    switch = modes.slots(READING, href)["modeswitch"]
    assert switch.count('data-mode-choice="') == 2 * len(MODES)
    for mode in MODES:
        assert switch.count(f'data-mode-choice="{mode.id}"') == 2
    assert "Aa &lt;only&gt;" in switch and "Aa &amp; nothing else" in switch
    assert switch.count("hidden>") == 2
    assert 'data-mode-default="only-bb"' in switch


def test_the_offer_is_the_declared_modes_in_order_with_the_declared_default():
    assert [choice.id for choice in READING.choices] == ["only-aa", "only-bb", "both"]
    assert READING.default == "only-bb"
    first = modes.offer(Reading(languages=LANGUAGES, modes=MODES, default_mode="only-aa"))
    assert first is not None and first.default == "only-aa"


def test_the_stylesheet_has_one_rule_per_mode_and_the_script_is_the_asset():
    written = modes.files(READING)
    assert set(written) == {"modes.css", "modes.js"}
    css = written["modes.css"]
    for mode in READING.choices:
        hidden = f'section[data-lang]:not([data-lang="{mode.prose}"])'
        assert f'html[data-mode="{mode.id}"] {hidden}' in css
    assert "ligature" in css
    assert "localStorage" not in written["modes.js"]
    assert "window.studyforge.progress" in written["modes.js"]


def test_the_shared_bundle_never_carries_any_of_it():
    from studyforge.render import pageassets

    shared = "".join(pageassets.written_files().values())
    for word in ("data-mode", "mode-question", "studyforge.boot.mode"):
        assert word not in shared


def test_an_untagged_entry_renders_the_link_it_always_did():
    assert modes.link(None, "a/b.html", "Body") == '<a href="a/b.html">Body</a>'
    assert modes.attributes(None) == "" and modes.label(None) == "" and modes.openable(None)


def test_a_closed_entry_is_an_anchor_with_no_href_out_of_the_tab_order():
    tag = modes.Tag(("bb",), "Bb", (("only-bb", "Bb"),), locked=True)
    closed = modes.link(tag, "a/b.html", "Body")
    assert closed == '<a aria-disabled="true" tabindex="-1" data-href="a/b.html">Body</a>'
    assert not modes.openable(tag)
    assert modes.attributes(tag) == ' data-entry-lang="bb"'
    assert modes.label(tag) == "<span data-entry-label>Bb</span>"
