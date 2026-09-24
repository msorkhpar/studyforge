"""The narration transport and its highlight: everything a text can establish.

Mirrors no source module — it asserts things about `render/assets/narration.js`
and `render/assets/narration.css`, which are data, the way `test_chrome` does
for `chrome.css` and `test_progress` for the reader's store.

## ⛔ Why the two-sided spellings are asserted against the REAL other side

⚠️ **A script and a template cannot import one another**, so every hook on this
page is spelled twice — and two spellings that agree today disagree the day one
of them is renamed, with no symptom but a control that never lights. ⭐ So every
name below is read out of the *other* side rather than retyped here: the audio
attribute out of `render.page.assets`, the state names out of
`templates/player.html`, the element ids out of the same template, and the
bundle position out of `pageassets.script()` rather than out of a tuple this
file rebuilt.

## ⚠️ What is NOT asserted here, and where it is

⛔ **No JavaScript runs in this file.** Whether the highlight actually moves is a
*runtime* reading and lives in `test_narration_runtime.py`, which runs the real
part under the pinned image's JS runtime against a stub DOM. ⭐ Whether it looks
right in a browser is a third thing again and belongs to `tests/visual/`.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.render import templates
from studyforge.render.page import AUDIO_ATTRIBUTE
from studyforge.render.pageassets import (
    SCRIPT_PARTS,
    STYLE_PARTS,
    compose,
    script,
    text,
)

#: The two parts this task owns, and the template they are the other side of.
PART = "narration.js"
STYLE = "narration.css"
PLAYER = "player.html"

#: The highlight hook. ⭐ Deliberately NOT in `pageassets.SURFACE_HOOKS`, and the
#: test at the end of this file is the control for that decision rather than a
#: silence about it.
SPEAKING = "data-speaking"


def player_markup() -> str:
    return templates.template(PLAYER).template


def uncommented(name: str) -> str:
    """The part's text with its comments removed.

    ⚠️ Not fastidiousness, and `test_palette` needs the same thing for the same
    reason: this part's own prose quotes the spellings it is being checked for,
    so a check that read comments would report the sentence explaining a rule as
    a violation of it.
    """
    return re.sub(r"/\*.*?\*/", "", text(name), flags=re.DOTALL)


# --- where it sits in the page ----------------------------------------------


def test_both_parts_reach_the_page_at_all():
    # ⛔ The failure this catches is total and silent: a part on disk that no
    # bundle names ships to nobody, and every other assertion in this file would
    # still pass. Read out of the composed bundles, never out of the tuples.
    assert text(PART) in script()
    assert text(STYLE) in compose(STYLE_PARTS)


def test_the_highlight_is_painted_after_the_syntax_colours_it_washes_over():
    # ⛔ Two rules of equal specificity: the last one wins. The narration
    # highlight refines the inside of a code block the highlighter has just
    # painted, so a part ordered before it would be a wash that never appears.
    order = list(STYLE_PARTS)
    assert order.index("code-highlight.css") < order.index(STYLE)


def test_nothing_authored_follows_the_vendored_player_theme():
    # ⭐ `bundle.py`'s standing rule, asserted at the part that was added after
    # it was written: theme the vendored stylesheet from outside, never fork it,
    # and never let an authored part win over it.
    order = list(STYLE_PARTS)
    assert order.index(STYLE) < order.index("plyr.css")


def test_the_store_s_consumer_is_still_the_last_script_part():
    # ⚠️ `read-mark.js` reads the reader's store with NO existence guard so a
    # wrong bundle order fails loudly, and it is LAST so a throw of its own
    # reaches no other part. Adding a part must not have cost that.
    order = list(SCRIPT_PARTS)
    assert order[-1] == "read-mark.js"
    assert order.index(PART) < order.index("read-mark.js")


# --- the attribute is the one Python declares -------------------------------


def test_the_player_reads_the_attribute_python_declares_and_not_a_copy_of_it():
    # ⛔ `render/page/assets.py` named `AUDIO_ATTRIBUTE` one milestone before its
    # writer for exactly this reason: "a definition arriving after its first
    # writer is a definition two tasks each guess at differently."
    assert f"'{AUDIO_ATTRIBUTE}'" in uncommented(PART)


def test_the_player_composes_no_clip_path_of_its_own():
    # ⛔ R4, and it is the failure that renders both ways. `audio/<clip>.mp3` is
    # the `tree` profile's answer and `audio/<stem>/<clip>.mp3` is `sibling`'s —
    # a script that spelled either would be correct under one and silently wrong
    # under the other, with the page rendering identically in both cases.
    body = uncommented(PART)
    for dirname in UNIT_MEDIA_DIRNAMES:
        assert f"'{dirname}/" not in body, f"the player spells the {dirname} directory"
        assert f'"{dirname}/' not in body, f"the player spells the {dirname} directory"
    assert ".mp3" not in body, "the player assumes an audio format"


def test_the_player_mints_no_clip_name_either():
    # ⛔ There is exactly one minter (`narrate/speakable/naming.py`) and it is in
    # Python. A digest computed here would be a second one, and the symptom of a
    # second minter is a page asking for a file the placer never wrote.
    body = uncommented(PART).lower()
    for forbidden in ("sha", "digest", "crypto"):
        assert forbidden not in body, f"the player looks like it derives a name: {forbidden}"


# --- every sentence is markup ------------------------------------------------


def test_the_script_types_no_word_a_reader_sees():
    # ⛔ R13, in the strict form `read-mark.js` already holds: a sentence in a
    # script is a sentence no template check reads. The only two things this part
    # writes into the page are a COUNT and a heading COPIED off the page.
    body = uncommented(PART)
    typed = re.findall(r"textContent\s*=\s*(['\"])((?:(?!\1).)*)\1", body)
    literals = [value for _quote, value in typed]
    assert all(not re.search(r"[A-Za-z]", value) for value in literals), (
        f"the script types prose into the page: {literals}"
    )
    assert "innerHTML" not in body, "narration builds no markup"


def test_every_state_the_script_knows_is_a_sentence_the_template_carries():
    # ⭐ The two-sided spelling, both directions. A state the script can enter
    # and the template has no sentence for announces NOTHING, silently — which
    # is precisely the honest-degradation clause failing in the one mode nobody
    # would notice, because the page looks fine.
    markup = player_markup()
    in_markup = set(re.findall(r'data-state="([a-z]+)"', markup))
    in_script = set(re.findall(r"var [A-Z]+ = '([a-z]+)';", uncommented(PART)))
    named = in_script & in_markup
    assert in_markup == named, f"the template carries a sentence nothing shows: {in_markup - named}"


@pytest.mark.parametrize("state", ["missing", "blocked", "none"])
def test_the_three_honest_states_each_have_their_own_sentence(state):
    # ⛔ R6, named one state at a time so a missing one is a named failure and
    # not a count that happens to still add up. A clip that is not on disk, a
    # browser that refused to start, and a unit with nothing to play are three
    # different things to say and are never collapsed into one.
    markup = player_markup()
    match = re.search(rf'data-state="{state}" hidden>([^<]+)<', markup)
    assert match, f"no sentence for the {state} state"
    assert len(match.group(1)) > 40, f"the {state} sentence is a label, not an explanation"


def test_the_nothing_to_play_sentence_does_not_claim_the_unit_was_never_narrated():
    # ⛔ **`W202` Q4, at the one sentence that could still undo it.** After the
    # promise states landed, a page reaches this transport ONLY when a narration
    # record exists — a corpus nobody ever narrated emits no passage at all and
    # this part returns before unhiding anything. ⚠️ So *"no audio has been
    # generated for this unit yet"* became a sentence that can only be FALSE when
    # it is shown, and it is the exact conflation this row was dispatched to
    # remove: the reader is told the unit was never narrated when in fact its
    # clips went missing.
    #
    # ⭐ **PLANT `P14`.** Reverting the wording was caught only by the committed
    # goldens, which the next person regenerates without knowing why they moved.
    # This states the intent, so the wording has a reason rather than a hash.
    match = re.search(r'data-state="none" hidden>([^<]+)<', player_markup())
    assert match, "no sentence for the none state"
    sentence = match.group(1)
    assert "never" not in sentence.lower()
    assert "has been generated" not in sentence, (
        "the transport tells the reader nothing was narrated, in the one state "
        "that is only reachable when something WAS"
    )


def test_the_play_button_carries_both_of_its_faces_rather_than_being_relabelled():
    # ⚠️ A button whose label the script types is a button in one language. Both
    # faces are markup and the script only unhides one, which is `read-mark.html`'s
    # shape exactly.
    markup = player_markup()
    assert 'data-state="paused"' in markup
    assert 'data-state="playing" hidden' in markup


# --- no dead control ---------------------------------------------------------


def test_the_transport_ships_hidden_and_the_script_is_what_unhides_it():
    # ⛔ The row's own acceptance: *no dead control*. With scripting off, three
    # buttons that cannot play are the dead one, so the region ships hidden and
    # comes back only once this part has something behind it — `read-mark.html`
    # ships hidden for the same reason and states it in the same words.
    assert '<footer id="player" hidden>' in player_markup()
    assert "player.hidden = false" in uncommented(PART)


def test_a_unit_with_nothing_to_play_disables_the_controls_rather_than_hiding_the_reason():
    # ⚠️ Hiding the transport in that case would be honest about the control and
    # silent about the cause. The stated message and disabled controls say both.
    body = uncommented(PART)
    assert "disabled = true" in body
    assert "say(NONE)" in body


# --- the keyboard contract the template promises -----------------------------


def test_the_script_keeps_every_promise_the_template_s_own_sentence_makes():
    # ⭐ The template tells the reader "Space plays and pauses. Left and right
    # arrows move to the next passage… Click any paragraph to start reading from
    # there." ⛔ That sentence is shipped prose, so it is a CONTRACT, and a
    # promise printed on the page that the script does not keep is worse than an
    # absent feature.
    markup = player_markup()
    body = uncommented(PART)
    assert "Space plays and pauses" in markup
    assert "arrows move to the next passage" in markup
    assert "Click any paragraph" in markup
    assert "' '" in body and "'Spacebar'" in body
    assert "'ArrowLeft'" in body and "'ArrowRight'" in body
    assert "'click'" in body


def test_space_is_left_alone_where_it_already_means_something():
    # ⛔ A page-wide Space that fires on a focused button presses that button
    # twice, and in a field it eats the space. Both are how a shortcut becomes a
    # bug nobody can type around.
    body = uncommented(PART)
    for tag in ("INPUT", "TEXTAREA", "SELECT", "BUTTON"):
        assert tag in body, f"Space is not excused on a focused {tag}"
    assert "isContentEditable" in body


def test_a_modified_key_is_not_the_page_s_to_take():
    # ⚠️ Ctrl+Left is a word jump and Cmd+Left is a history step; taking either
    # breaks the browser rather than the page.
    body = uncommented(PART)
    for modifier in ("altKey", "ctrlKey", "metaKey"):
        assert modifier in body


# --- the stylesheet ----------------------------------------------------------


def test_the_highlight_hook_is_reached_by_both_halves_of_this_task():
    # ⭐ One task owns both ends of this spelling, which is why it is not in
    # `SURFACE_HOOKS` — see the next test, which is the control for that.
    assert SPEAKING in uncommented(PART)
    assert f"[{SPEAKING}]" in uncommented(STYLE)


def test_the_highlight_hook_is_deliberately_not_published_and_needs_no_renderer():
    # ⛔ `data-marked` IS published because `chrome.css` paints a state
    # `read-mark.js` writes — two offices holding the two ends of one spelling.
    # Here both ends are this task's and no renderer emits it, so publishing it
    # would oblige a contract with no second side. ⚠️ Asserted so the omission
    # reads as a decision rather than as something nobody got to.
    from studyforge.render.pageassets import SURFACE_HOOKS

    assert SPEAKING not in SURFACE_HOOKS.values()
    for name in templates.names():
        assert SPEAKING not in templates.template(name).template, (
            f"{name} emits the highlight hook, so it now has a second side"
        )


def test_the_stylesheet_defines_no_colour_and_no_measure_of_its_own():
    # ⛔ `test_palette` asserts the first half over every authored part; this is
    # the same property said at this part, so a raw value added here fails with
    # this task's name on it rather than as a line in a sweep.
    body = uncommented(STYLE)
    assert re.search(r"#[0-9a-fA-F]{3,8}\b", body) is None
    assert re.search(r"\brgba?\(", body) is None


def test_the_stylesheet_paints_the_five_tokens_that_were_waiting_for_it():
    # ⭐ `chrome.css` deferred exactly this region and named the tokens: "the
    # narration player is the only `<footer>` a page carries, it is narration's at
    # M3, and `--player-height`, `--panel` and `--shadow` are defined and waiting
    # for it." ⛔ `tests/visual/palette.py`'s ledger called four more UNPAINTED
    # with this task named against each, and painting one forces somebody to say
    # which ground its contrast is taken against.
    body = uncommented(STYLE)
    for token in ("--player-height", "--panel", "--shadow", "--hl-bg", "--hl-bar", "--hl-fg"):
        assert f"var({token})" in body, f"{token} is still unpainted"


def test_the_code_wash_does_not_repaint_the_ground_the_syntax_ratios_were_taken_against():
    # ⛔ The seven syntax colours are measured against `--code-bg`. Repainting a
    # lit code block's background would invalidate all seven at once, invisibly:
    # the page would look fine to whoever changed it.
    body = uncommented(STYLE)
    wash = re.search(rf"\[{SPEAKING}\] pre,\s*\[{SPEAKING}\] code \{{(.*?)\}}", body, re.DOTALL)
    assert wash, "the code wash rule is gone"
    assert "--hl-code" in wash.group(1)
    assert "background:" not in wash.group(1), (
        "the wash replaces the ground instead of laying over it"
    )
    assert "color:" not in wash.group(1), "the wash repaints the syntax colours"


def test_lighting_a_passage_does_not_move_it():
    # ⚠️ A highlight drawn with padding reflows the paragraph, so the text jumps
    # away from the reader on every single advance — which is the one moment
    # they are certainly looking at it.
    body = uncommented(STYLE)
    rule = re.search(rf"^\[{SPEAKING}\] \{{(.*?)\}}", body, re.DOTALL | re.MULTILINE)
    assert rule, "the highlight rule is gone"
    assert "padding" not in rule.group(1)
    assert "box-shadow" in rule.group(1)


def test_the_transport_does_not_answer_the_page_column_a_second_time():
    # ⛔ `chrome.css` bounds the column ONCE, on `body` (`PO-22/6`). A fixed
    # footer would have to be paid for with a `padding-bottom` on `body` here,
    # which is the two-rules-for-one-question defect; sticky costs nothing.
    # ⭐ `W388` places the footer in the grid with `body:has(…) > footer#player`,
    # a rule whose subject is the FOOTER; what is refused is a rule on `body`.
    body = uncommented(STYLE)
    assert on_body(body) == []
    assert "position: sticky" in body


def on_body(css: str) -> list[str]:
    """Every rule whose subject is `body` itself rather than something inside it."""
    return [
        selector.strip()
        for selector in re.findall(r"(?m)^([^{}@/*][^{}]*)\{", css)
        if re.fullmatch(r"body(?::[\w-]+(?:\([^)]*\))?)*", selector.strip().split(",")[-1].strip())
    ]


def test_a_planted_rule_on_body_is_caught_and_a_rule_on_the_footer_is_not():
    assert on_body("body { padding-bottom: 4rem; }") == ["body"]
    assert on_body("body:has(nav) { padding-bottom: 4rem; }") == ["body:has(nav)"]
    assert on_body("body:has(nav) > footer#player { grid-column: 2 / -1; }") == []
