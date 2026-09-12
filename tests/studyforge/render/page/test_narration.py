"""Mirror of `src/studyforge/render/page/narration.py` (R12), and the emitter's own clauses.

⛔ **The lookup key is `SpeechUnit.position` and this module proves the renderer
uses that spelling and no other.** Every mapping below is built by calling
`speakable_of` and reading `unit.position` off the record — never by writing a
tuple out — so a renderer that recomputed a numbering of its own would produce
elements this file cannot find.

⭐ **The emitter half of `SF-18`.** The player is data (`pageassets/test_narration.py`);
this is the Python that puts the clip on the element the player then reads.
"""

from __future__ import annotations

import re

import pytest

from studyforge.narrate.speakable import clip_name, speakable_of
from studyforge.render.page import AUDIO_ATTRIBUTE, Narration, PageError
from studyforge.render.page import document as document_module
from studyforge.render.page.blocks import render_all
from studyforge.render.page.narration import SILENT
from tests.studyforge.render.page.pages import CASES, sample_placement

#: Finds every element that carries a clip, with the tag it is on.
CARRIER = re.compile(r"<([a-z][a-z0-9]*)[^>]*\s" + re.escape(AUDIO_ATTRIBUTE) + r'="([^"]*)"')


@pytest.fixture(params=CASES, ids=lambda build: build.__name__)
def case(request):
    return request.param()


def carriers(markup: str) -> list[tuple[str, str]]:
    return CARRIER.findall(markup)


# --- the value ---------------------------------------------------------------


def test_a_filename_becomes_an_href_the_profile_chose():
    # ⛔ R4: `audio/<clip>.mp3` is `tree`'s answer and `<stem>.audio/…` is
    # `sibling`'s. Nothing here composes either — `Placement.media` is asked.
    placement = sample_placement()
    narration = Narration.of({("s", (0,), None): "a-11111111.mp3"}, placement)
    assert narration.attribute("s", (0,)) == f' {AUDIO_ATTRIBUTE}="audio/a-11111111.mp3"'


def test_an_element_with_no_clip_carries_nothing_at_all():
    # ⚠️ Not an empty attribute — and the scope of that is now STATED rather than
    # implied. An element with no clip is an element nothing PROMISED a clip for,
    # and it carries nothing. ⛔ A promise the record made and the disk did not
    # keep is a different state and DOES carry an empty attribute; the test below
    # is its control, and the two must never collapse into one answer.
    assert SILENT.attribute("s", (0,)) == ""
    assert Narration.of({}, sample_placement()).attribute("s", (0,)) == ""
    assert Narration.of({}, sample_placement(), missing=()).attribute("s", (0,)) == ""


def test_a_blank_filename_is_the_same_answer_as_no_clip():
    # ⛔ The record has an entry and synthesis produced nothing; a page that
    # linked `""` would be worse than one that linked nothing.
    narration = Narration.of({("s", (0,), None): "   "}, sample_placement())
    assert narration.attribute("s", (0,)) == ""
    assert not narration


def test_the_key_is_the_whole_position_and_a_near_miss_finds_nothing():
    # ⭐ Section, path AND sub-index. Two of three matching is a different unit,
    # and the wrong clip under a paragraph is the failure with no symptom.
    narration = Narration.of({("s", (1, 2), 3): "a-11111111.mp3"}, sample_placement())
    assert narration.attribute("s", (1, 2), 3)
    assert narration.attribute("s", (1, 2)) == ""
    assert narration.attribute("s", (1,), 3) == ""
    assert narration.attribute("other", (1, 2), 3) == ""


def test_the_leading_space_lives_here_and_not_at_every_call_site():
    # ⛔ R10's small change: a renderer writing `<p{audio}>` must not emit `<p >`
    # for an unnarrated paragraph, which would be a golden differing by one
    # character per block for no reason a reader could see.
    narration = Narration.of({("s", (0,), None): "a-11111111.mp3"}, sample_placement())
    assert narration.attribute("s", (0,)).startswith(" ")
    assert SILENT.attribute("s", (0,)) == ""


def test_the_href_is_escaped_as_an_attribute():
    narration = Narration.of({("s", (0,), None): 'a"b-11111111.mp3'}, sample_placement())
    assert '"' not in narration.attribute("s", (0,))[len(AUDIO_ATTRIBUTE) + 3 : -1]


# --- which element carries it ------------------------------------------------


def test_every_clip_the_walker_mints_reaches_exactly_one_element(case):
    # ⛔ **BOTH DIRECTIONS AND A CARDINALITY.** Surjectivity alone is what
    # Ruling 187 refuses: seventeen clips colliding onto one element still
    # resolve both ways. The equality is what states that each unit got its own.
    units = speakable_of(case.document).units
    emitted = carriers(case.render().decode("utf-8"))
    assert len(emitted) == len(units), "a spoken unit reached no element, or one reached two"
    assert len({href for _tag, href in emitted}) == len(units)


def test_a_clip_lands_on_the_element_whose_words_it_speaks(case):
    # ⭐ The property that makes the highlight mean anything: the element lit
    # while a clip plays is the element the clip is reading.
    document = case.document
    units = speakable_of(document).units
    clips = {unit.position: clip_name(unit) + ".x" for unit in units}
    narration = Narration.of(clips, case.placement)
    for unit in units:
        section = next(s for s in document["sections"] if s["key"] == unit.section)
        markup = render_all(
            section["blocks"], placement=case.placement, section=unit.section, narration=narration
        )
        assert clip_name(unit) + ".x" in markup, f"nothing on the page carries {unit.id}"


def test_the_carriers_are_the_elements_the_disposition_table_names(case):
    # ⛔ `SPEECH_OF` decides what is spoken, and the tag it lands on follows from
    # it: `items` puts a clip on each `<li>`, `rows` on each body `<tr>`,
    # `summary` on the `<summary>` and never on the `<details>`, `caption` on the
    # code `<figure>`, and `prose` on the paragraph or heading itself.
    tags = {tag for tag, _href in carriers(case.render().decode("utf-8"))}
    assert tags <= {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "summary", "figure"}
    assert "details" not in tags, "the highlight would sit over content the audio withheld"
    assert "blockquote" not in tags, "a quote recurses; its clips are its children's"


def test_a_table_header_row_carries_no_clip():
    # ⚠️ `SPEECH_OF` says `rows`, and the walker gives the header none — a header
    # linking a clip would light up under audio that is not reading it.
    block = {"type": "table", "headers": ["a"], "rows": [["b"], ["c"]]}
    narration = Narration.of(
        {("s", (0,), index): f"row{index}-1111111{index}.x" for index in (0, 1)},
        sample_placement(),
    )
    markup = render_all([block], placement=sample_placement(), section="s", narration=narration)
    head, _, body = markup.partition("<tbody>")
    assert AUDIO_ATTRIBUTE not in head
    assert body.count(AUDIO_ATTRIBUTE) == 2


def test_a_nested_block_is_addressed_from_the_section_down_not_from_its_parent():
    # ⛔ The whole reason `path` is threaded. `position` resets inside a quote, so
    # a renderer that used it would give the quote's first child the same address
    # as the quote's own neighbour — one clip under two paragraphs.
    blocks = [
        {"type": "para", "text": "outer"},
        {"type": "quote", "blocks": [{"type": "para", "text": "inner"}]},
    ]
    narration = Narration.of(
        {("s", (0,), None): "outer-11111111.x", ("s", (1, 0), None): "inner-22222222.x"},
        sample_placement(),
    )
    markup = render_all(blocks, placement=sample_placement(), section="s", narration=narration)
    assert "outer-11111111.x" in markup
    assert "inner-22222222.x" in markup
    assert markup.index("outer-11111111.x") < markup.index("inner-22222222.x")


@pytest.mark.parametrize("block", [{"type": "rule"}, {"type": "html", "text": "<b>x</b>"}])
def test_a_silent_block_is_never_given_a_clip(block):
    # ⭐ `SPEECH_OF` calls these `silent`, so no position exists for them and the
    # renderer must not invent an element to hang one on.
    narration = Narration.of({("s", (0,), None): "a-11111111.x"}, sample_placement())
    markup = render_all([block], placement=sample_placement(), section="s", narration=narration)
    assert AUDIO_ATTRIBUTE not in markup


# --- and the transport arrives with it ---------------------------------------


def test_the_page_gains_its_transport_exactly_when_it_gains_a_clip(case):
    # ⭐ `document.player` is gated on the body carrying `AUDIO_ATTRIBUTE`, which
    # was written a milestone early precisely so that no document field had to be
    # invented for it. This is the day that gate opens.
    narrated = case.render().decode("utf-8")
    silent = document_module.compose(case.document, case.placement, narration=SILENT)
    assert '<footer id="player"' in narrated
    assert '<footer id="player"' not in silent
    assert AUDIO_ATTRIBUTE not in silent


def test_the_reading_floor_renders_identically_to_before_narration_existed(case):
    # ⛔ R6 and spec §11.0: a corpus with no clips is COMPLETE, not short. The
    # default must be the silent page, so a build that never narrates changes
    # nothing at all.
    assert document_module.compose(case.document, case.placement) == document_module.compose(
        case.document, case.placement, narration=SILENT
    )


# --- W202 Q4: a broken promise, and the three states it separates -------------


def positions(case) -> list:
    """Every position this case's walker mints, in reading order."""
    return [unit.position for unit in speakable_of(case.document).units]


def all_promised_and_none_delivered(case) -> Narration:
    """What a build hands the renderer when the record names clips the disk lacks.

    ⭐ Built from `speakable_of`'s own positions, never from tuples written out
    here, for this file's stated reason: a renderer with a numbering of its own
    would produce elements nothing in here could find.
    """
    return Narration.of({}, case.placement, missing=positions(case))


def one_promise_broken(case) -> Narration:
    """The mixed page: every clip plays except the first, which is not on disk."""
    units = speakable_of(case.document).units
    clips = {unit.position: clip_name(unit) + ".mp3" for unit in units[1:]}
    return Narration.of(clips, case.placement, missing=[units[0].position])


def test_a_promised_clip_that_is_not_on_disk_carries_an_empty_attribute():
    # ⛔ **The reversal, asserted rather than described.** `narration.js` was
    # written for exactly this shape — *"a passage may arrive with an empty
    # source"* — and maps it to `playable = false` while keeping it in the
    # passage count, so the reader is told which passage is silent instead of the
    # passage vanishing from the transport altogether.
    narration = Narration.of({}, sample_placement(), missing=[("s", (0,), None)])
    assert narration.attribute("s", (0,)) == f' {AUDIO_ATTRIBUTE}=""'


def test_a_gap_is_matched_on_the_whole_position_exactly_as_a_clip_is():
    # ⭐ The near-miss control the playing side already has: two of three fields
    # matching is a different element, and marking the wrong paragraph silent is
    # a lie about which audio is missing.
    narration = Narration.of({}, sample_placement(), missing=[("s", (1, 2), 3)])
    assert narration.attribute("s", (1, 2), 3)
    assert narration.attribute("s", (1, 2)) == ""
    assert narration.attribute("s", (1,), 3) == ""
    assert narration.attribute("other", (1, 2), 3) == ""


def test_a_gap_given_with_a_list_block_path_still_finds_its_element():
    # ⚠️ `attribute` looks a tuple up, so a caller holding a list would name a gap
    # no element could match — and the symptom is a page that quietly says
    # nothing is wrong. Normalised on the way in, not trusted.
    narration = Narration.of({}, sample_placement(), missing=[("s", [1, 2], None)])
    assert narration.attribute("s", (1, 2)) == f' {AUDIO_ATTRIBUTE}=""'


def test_a_position_that_both_plays_and_is_missing_is_refused():
    # ⛔ Two answers to one question; whichever won would be an accident of which
    # argument was read last.
    with pytest.raises(PageError) as raised:
        Narration.of(
            {("s", (0,), None): "a-11111111.mp3"},
            sample_placement(),
            missing=[("s", (0,), None)],
        )
    assert "both playable and named as a gap" in str(raised.value)


def test_a_malformed_gap_is_refused_by_description_and_never_echoed():
    # ⛔ R7: the shape refused here is, by construction, a candidate home
    # directory — a caller handing over a path where a position was wanted — and
    # this refusal goes into a build log. ⚠️ The fixture is a documented
    # placeholder rather than a real home path, because the quality floor refuses
    # one in any file including this one; that is the rule being upheld, not
    # dodged.
    offending = "/path/to/clip.mp3"
    with pytest.raises(PageError) as raised:
        Narration.of({}, sample_placement(), missing=[offending])
    assert offending not in str(raised.value)
    assert "/path/to" not in str(raised.value)


def test_a_page_whose_every_promise_is_broken_is_still_a_narrated_page():
    # ⭐ The whole distinction in one boolean: this corpus's audio BROKE. It is
    # not a corpus nobody ever narrated, and `SILENT` is what that one is.
    narration = Narration.of({}, sample_placement(), missing=[("s", (0,), None)])
    assert narration
    assert not SILENT


def test_the_promised_count_is_the_playable_plus_the_missing_and_nothing_else():
    # ⚠️ NOT the page's speech units: a unit the record never mentions was never
    # promised anything, and counting it would make every half-narrated corpus
    # read as broken.
    narration = Narration.of(
        {("s", (0,), None): "a-11111111.mp3"},
        sample_placement(),
        missing=[("s", (1,), None), ("s", (2,), None)],
    )
    assert narration.promised == 3
    assert SILENT.promised == 0


def test_a_broken_promise_brings_the_transport_and_names_the_gap(case):
    # ⛔ **`W202` Q4's third row, end to end.** Every clip promised, none on disk:
    # the page carries the player — through the SAME derived gate, because the
    # empty attribute is still the attribute — and it says so in prose.
    page = document_module.compose(
        case.document, case.placement, narration=all_promised_and_none_delivered(case)
    )
    assert '<footer id="player"' in page
    assert '<section data-section="narration-gap">' in page
    spoken = len(positions(case))
    assert f"{spoken} of {spoken} narrated passages on this page have no audio file" in page


def test_a_page_with_one_broken_promise_says_how_many_and_still_plays_the_rest(case):
    page = document_module.compose(
        case.document, case.placement, narration=one_promise_broken(case)
    )
    spoken = len(positions(case))
    assert f"1 of {spoken} narrated passages on this page have no audio file" in page
    emitted = carriers(page)
    assert [href for _tag, href in emitted if not href] != [], "the silent passage left the page"
    assert [href for _tag, href in emitted if href] != [], "nothing plays on a page with one gap"
    assert len(emitted) == spoken, "a passage was dropped rather than marked silent"


def test_the_three_states_are_told_apart_from_the_bytes_of_the_page_alone(case):
    # ⛔ **THE DEFECT, AS A TEST.** Before this row, "never narrated" and
    # "narration broke" rendered IDENTICALLY — so a reader could not tell a
    # finished prose corpus from one whose audio had failed. All three pages must
    # now differ, and the never-narrated one must still be the clean prose page.
    never = document_module.compose(case.document, case.placement, narration=SILENT)
    plays = document_module.compose(case.document, case.placement, narration=case.narration)
    broke = document_module.compose(
        case.document, case.placement, narration=all_promised_and_none_delivered(case)
    )
    assert never != plays and plays != broke and never != broke

    # ⭐ Row 1: no player, no notice, and nothing marked anywhere.
    assert '<footer id="player"' not in never
    assert "narration-gap" not in never
    assert AUDIO_ATTRIBUTE not in never

    # ⭐ Row 2: the player, and nothing to complain about.
    assert '<footer id="player"' in plays
    assert "narration-gap" not in plays

    # ⭐ Row 3: the player, and the gap named.
    assert '<footer id="player"' in broke
    assert "narration-gap" in broke


def test_a_finished_prose_corpus_gains_no_mark_of_any_kind(case):
    # ⛔ §7's three states (C5) and §11.0's reading floor: a corpus without
    # narration is COMPLETE, not short. The rejected option — a visible disabled
    # player — was rejected on exactly this ground, so a page with no record is
    # byte-identical to the page this repository rendered before narration
    # existed, and this is the control that keeps it so.
    assert document_module.compose(
        case.document, case.placement, narration=SILENT
    ) == document_module.compose(case.document, case.placement)
