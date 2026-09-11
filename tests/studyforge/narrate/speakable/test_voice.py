"""Mirror of `src/studyforge/narrate/speakable/voice.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.narrate.speakable import voice
from studyforge.narrate.speakable.voice import (
    URL_PHRASE,
    elide_urls,
    looks_like_code,
    split_identifier,
    spoken_identifiers,
    spoken_text,
    strip_emoji,
)
from studyforge.render.markup import SEGMENT_KINDS, segments

# --------------------------------------------------------------------------
# ⛔ The inline split is imported, not rewritten
# --------------------------------------------------------------------------


def test_the_inline_parser_is_the_renderers_own_and_not_a_second_copy():
    # ⛔ Display and speech must never disagree about where a marker begins. The
    # tell is that this module holds no marker expression of its own.
    source = (voice.__file__ and open(voice.__file__, encoding="utf-8").read()) or ""
    assert "from studyforge.render.markup import segments" in source
    for marker in ("\\*\\*", "[^`]+", "\\]\\("):
        assert marker not in source, f"a second inline parser is forming: {marker!r}"


@pytest.mark.parametrize("kind", SEGMENT_KINDS)
def test_every_segment_kind_contributes_its_body_and_never_its_marker(kind):
    # ⭐ Joining the bodies is what keeps the markers out of the audio, for every
    # kind the one parser can produce — derived from `SEGMENT_KINDS`, never listed.
    written = {
        "text": ("plain words", "plain words"),
        "code": ("`value`", "value"),
        "link": ("[the words](https://example.invalid/x)", "the words"),
        "strong": ("**loud**", "loud"),
        "em": ("*quiet*", "quiet"),
    }[kind]
    assert {segment[0] for segment in segments(written[0])} >= {kind}
    assert spoken_text(written[0]) == written[1]


def test_a_marker_character_never_reaches_the_spoken_string():
    said = spoken_text("A **bold** claim about `values` and [a link](https://example.invalid/x).")
    for marker in ("*", "`", "[", "]", "("):
        assert marker not in said


# --------------------------------------------------------------------------
# Identifier shape
# --------------------------------------------------------------------------


@pytest.mark.parametrize("token", ["getAllUsers", "user_name", "MAX_SIZE", "os.path.join"])
def test_an_identifier_shape_is_recognised(token):
    assert looks_like_code(token)


@pytest.mark.parametrize("token", ["item2Count", "v2Api", "x1Y2"])
def test_a_digit_boundary_alone_is_not_an_identifier_shape_and_that_is_inherited(token):
    # ⚠️ Pinned as measured, NOT as desired. The four shape gates are camel
    # (`[a-z][A-Z]`), snake, screaming and dotted; a token whose only case change
    # sits across a digit passes none of them, so `_LETTER_DIGIT` and
    # `_DIGIT_LETTER` are reachable only once some other gate has already fired.
    # ⛔ Inherited verbatim from the extraction source and deliberately not changed
    # here: widening the gate changes what every clip says, which is a decision with
    # a measurement behind it rather than a tidy-up. Filed as a finding on SF-16.
    assert not looks_like_code(token)
    assert split_identifier(token) != token.lower()  # the splitter would have handled it


@pytest.mark.parametrize("token", ["Query", "shape", "e.g.", "3.14", "READING"])
def test_an_ordinary_word_is_not_mistaken_for_code(token):
    assert not looks_like_code(token)


@pytest.mark.parametrize(
    ("token", "said"),
    [
        ("getAllUsers", "get all users"),
        ("HTTPServer", "HTTP server"),
        ("user_name", "user name"),
        ("MAX_SIZE", "MAX SIZE"),
        ("toString()", "to string"),
        ("item2", "item 2"),
    ],
)
def test_an_identifier_is_respaced_for_pronunciation(token, said):
    assert split_identifier(token) == said


def test_an_acronym_keeps_its_case_because_it_is_the_only_evidence_the_engine_has():
    assert split_identifier("parseJSONBody") == "parse JSON body"


def test_punctuation_around_an_identifier_survives():
    assert spoken_identifiers("(getUser),") == "(get user),"


def test_an_abbreviation_keeps_its_full_stop():
    # ⚠️ Without this, the dotted-path detector fires on "e.g." and speaks "e g".
    assert spoken_identifiers("e.g. this") == "e.g. this"


def test_a_dotted_path_ending_a_sentence_loses_only_the_sentence_dot():
    assert spoken_identifiers("com.example.Repo.") == "com example repo."


# --------------------------------------------------------------------------
# URLs, emoji, whitespace
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text", ["see https://example.invalid/a/b now", "see www.example.invalid/x now"]
)
def test_a_literal_url_in_prose_becomes_one_phrase(text):
    said = elide_urls(text)
    assert URL_PHRASE in said
    assert "example.invalid" not in said


def test_a_links_words_are_spoken_and_its_href_is_not_announced():
    # ⭐ Order is load-bearing: markers resolve before URLs are elided.
    assert spoken_text("Read [the guide](https://example.invalid/g).") == "Read the guide."


def test_emoji_are_dropped_and_the_marks_that_carry_meaning_are_not():
    assert strip_emoji("done ✅ now") == "done  now"
    assert strip_emoji("90° and →") == "90° and →"


def test_whitespace_collapses_and_the_string_is_stripped():
    assert spoken_text("  two\n\n  lines  ") == "two lines"


@pytest.mark.parametrize("value", [None, "", "   ", 7, [], {}])
def test_anything_with_nothing_to_say_says_nothing(value):
    assert spoken_text(value) == ""


def test_the_transform_is_deterministic_for_the_same_input():
    # ⭐ R10's clause that does apply here: the digest is taken over this string.
    once = spoken_text("A `getUser` call and a ✅ and https://example.invalid/x")
    assert spoken_text("A `getUser` call and a ✅ and https://example.invalid/x") == once
