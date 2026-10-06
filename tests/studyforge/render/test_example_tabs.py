"""Mirror of `render/example_tabs.py` (R12): what each mode shows of an example's tabs."""

from __future__ import annotations

import json

from studyforge.corpus.manifest.reading import Language, Mode, Reading
from studyforge.render import example_tabs, modes

LANGUAGES = (Language("aa", "Aa", ("aa",)), Language("bb", "Bb", ("bb",)))
MODES = (
    Mode("only-aa", "Aa", "Aa", "aa", ("aa",), ("aa",)),
    Mode("only-bb", "Bb", "Bb", "bb", ("bb",), ("bb",)),
    Mode("bb-first", "Both", "Both", "aa", ("bb", "aa"), ("aa", "bb")),
)
OFFER = modes.offer(Reading(languages=LANGUAGES, modes=MODES, default_mode="bb-first"))


def test_a_corpus_with_no_modes_writes_no_file_and_so_none_of_this():
    assert modes.files(None) == {}


def test_the_two_files_of_a_modes_corpus_carry_the_tabs_after_the_modes_own_part():
    written = modes.files(OFFER)
    assert set(written) == {"modes.css", "modes.js"}
    assert written["modes.css"].index("[data-mode=") < written["modes.css"].index("data-example")
    assert "localStorage" not in written["modes.js"]
    assert example_tabs.MARKER not in written["modes.js"]


def test_each_mode_lists_the_languages_that_have_a_tab_in_its_own_order():
    css = modes.files(OFFER)["modes.css"]
    one_aa = 'html[data-mode="only-aa"] div[data-example]'
    root = 'html[data-mode="only-bb"] div[data-example]'
    assert f'{root}:not([data-langs~="bb"]) {{ display: none; }}' in css
    assert (
        'html[data-mode="only-bb"] div[data-example] [data-lang]:not([data-lang="bb"]) '
        "{ display: none; }"
    ) in css
    assert 'html[data-mode="bb-first"] div[data-example] [data-lang="bb"] { order: 0; }' in css
    assert 'html[data-mode="bb-first"] div[data-example] [data-lang="aa"] { order: 1; }' in css
    assert 'html[data-mode="bb-first"] div[data-example] [data-example-label]' not in css
    assert f"{one_aa} [data-example-label] {{ display: none; }}" in css


def test_the_script_is_given_each_modes_tab_order():
    script = modes.files(OFFER)["modes.js"]
    order = {"bb-first": ["bb", "aa"], "only-aa": ["aa"], "only-bb": ["bb"]}
    assert f"var MODE_TABS = {json.dumps(order, sort_keys=True)};" in script


def test_the_script_keeps_the_keys_of_the_tabs_pattern():
    script = example_tabs.script(OFFER.choices)
    for word in ("ArrowRight", "ArrowLeft", "Home", "End", "aria-selected", "tabindex"):
        assert word in script
