"""Mirror of `render/absent_language.py` (R12): what a corpus that greys a missing language adds."""

from __future__ import annotations

from studyforge.corpus.manifest.reading import Language, Mode, Reading
from studyforge.render import absent_language, modes

LANGUAGES = (Language("aa", "Aa", ("aa",)), Language("bb", "Bb", ("bb",)), Language("cc", "Cc"))
MODES = (
    Mode("only-aa", "Aa", "Aa", "aa", ("aa",), ("aa",)),
    Mode("mixed", "Mixed", "Mixed", "aa", ("cc", "aa", "bb"), ("bb", "cc")),
)


def offer(absent: str):
    reading = Reading(
        languages=LANGUAGES, modes=MODES, default_mode="only-aa", absent_language=absent
    )
    return modes.offer(reading)


def test_a_corpus_that_hides_what_a_language_lacks_never_reaches_this_module():
    written = modes.files(offer("hide"))
    for name in absent_language.PARTS:
        assert name not in written
    assert "data-example-missing" not in written["modes.css"]
    assert "data-practice-carriers" not in written["modes.js"]


def test_a_grey_corpus_appends_the_look_and_the_script_after_the_tabs_own():
    written = modes.files(offer("grey"))
    css = written["modes.css"]
    assert css.index('div[data-example] [role="tab"]') < css.index("data-example-missing")
    assert written["modes.js"].endswith(absent_language.script())
    assert "MODE_TABS*/" not in absent_language.script(), "the script carries no per-corpus data"


def test_each_mode_shows_the_sentence_for_each_language_it_lists_a_tab_for():
    css = absent_language.style(offer("grey").choices)
    mixed = 'html[data-mode="mixed"] div[data-example][data-missing~='
    for lang in ("cc", "aa", "bb"):
        assert f'{mixed}"{lang}"] [data-example-missing] {{ display: block; }}' in css
    assert 'html[data-mode="only-aa"] div[data-example][data-missing~="bb"]' not in css


def test_a_card_is_greyed_in_a_mode_whose_practice_languages_it_has_none_of():
    css = absent_language.style(offer("grey").choices)
    card = 'html[data-mode="mixed"] li[data-practice-card][data-practice-lang]'
    outside = ':not([data-practice-lang~="bb"]):not([data-practice-lang~="cc"])'
    assert f"{card}{outside} [data-practice-carriers] {{ display: block; }}" in css
    assert f"{card}{outside}, {card}{outside} a {{ color: var(--muted); }}" in css


def test_a_practice_a_mode_lists_reads_whatever_the_modes_prose():
    css = absent_language.style(offer("grey").choices)
    reads = 'html[data-mode="mixed"] section[data-kind="practice"][data-lang~="cc"]'
    assert reads in css and "{ display: revert; }" in css


def test_a_mode_that_lists_no_practice_language_greys_every_tagged_card():
    bare = Mode("bare", "Bare", "Bare", "aa", ("aa",), ())
    css = absent_language.style(modes.offer(Reading(LANGUAGES, (bare,), "bare")).choices)
    assert 'html[data-mode="bare"] li[data-practice-card][data-practice-lang] [data-practice' in css


def test_the_card_and_the_panel_carry_a_tag_only_for_a_grey_corpus():
    grey, hide = offer("grey"), offer("hide")
    assert modes.card_attributes(grey, "aa bb") == ' data-practice-lang="aa bb"'
    assert modes.card_attributes(hide, "aa bb") == ""
    assert modes.card_attributes(grey, None) == "" and modes.card_attributes(None, "aa") == ""
    assert modes.card_note(grey, "bb aa") == "<p data-practice-carriers>Available in: Aa, Bb.</p>\n"
    assert modes.card_note(hide, "aa") == ""
    panel = '<section data-practice="k" tabindex="-1">\n<p>x</p>\n</section>'
    tagged = modes.tag_panel(grey, "aa", panel)
    assert tagged.startswith('<section data-practice="k" tabindex="-1" data-lang="aa">')
    assert modes.tag_panel(hide, "aa", panel) == panel and modes.tag_panel(grey, "aa", "") == ""


def test_the_carriers_follow_the_declared_order_whatever_order_a_tag_names_them():
    assert modes.carriers(offer("grey"), "cc aa") == "Aa, Cc"
    assert modes.carriers(None, "aa") == ""
