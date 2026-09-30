"""Mirror of `src/studyforge/narrate/speakable/script.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES
from studyforge.archive.markdown import parse
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.narrate.speakable.naming import SUB_MARKER
from studyforge.narrate.speakable.records import SpeakableError
from studyforge.narrate.speakable.script import SPEECH_OF, ordinal_word, units_of
from tests.support import personal_data_shapes

UNIT = "corpus--unit-01"

#: ⛔ Assembled, never written as a literal: this file is swept by the repository's
#: own hygiene check, and a real home path in a fixture is the violation the gate
#: exists to refuse. Nothing here came from any real machine or account.
HOME = "/" + "home/jane"


def said(blocks: list) -> list[tuple[str, str]]:
    """The `(id, words)` pairs one block list produces, for a readable assertion."""
    units, _withheld = units_of(UNIT, "shared", blocks)
    return [(unit.id, unit.speak) for unit in units]


def withheld(blocks: list) -> int:
    """How many blocks one block list holds back."""
    return units_of(UNIT, "shared", blocks)[1]


# --------------------------------------------------------------------------
# ⛔ The disposition table is closed, and that is asserted against the vocabulary
# --------------------------------------------------------------------------


def test_every_block_type_in_the_vocabulary_has_a_disposition():
    # ⛔ The twelfth block type cannot land without somebody deciding what it sounds
    # like. Derived from `BLOCK_TYPES`, never listed a second time.
    assert sorted(SPEECH_OF) == sorted(BLOCK_TYPES)


def test_the_table_names_nothing_the_vocabulary_does_not():
    assert set(SPEECH_OF) <= set(BLOCK_TYPES)


def test_both_container_types_are_accounted_for_and_they_differ():
    # ⭐ `quote` is walked into; `disclosure` is not. Two containers, two rules, and
    # the set comes from the vocabulary rather than from this test.
    rules = {kind: SPEECH_OF[kind] for kind in CONTAINER_TYPES}
    assert set(rules) == set(CONTAINER_TYPES)
    assert len(set(rules.values())) == 2, f"both containers share one rule: {rules}"


def test_an_unknown_block_type_is_refused_rather_than_read_as_a_paragraph():
    # ⛔ The extraction source's rule was "anything unrecognised is spoken as a
    # paragraph" — an open set that fails toward acceptance.
    with pytest.raises(SpeakableError):
        units_of(UNIT, "shared", [{"type": "carousel", "text": "read me aloud"}])


@pytest.mark.parametrize("kind", [name for name, rule in SPEECH_OF.items() if rule == "silent"])
def test_a_shown_but_never_spoken_block_yields_no_unit(kind):
    assert said([{"type": kind, "text": "not read", "src": "x.png", "alt": "a"}]) == []


# --------------------------------------------------------------------------
# Prose, fences, lists, tables
# --------------------------------------------------------------------------


def test_prose_is_read_as_written_and_numbered_from_one():
    assert said([{"type": "heading", "level": 2, "text": "A heading"}]) == [
        (f"{UNIT}.shared.b1", "A heading")
    ]


@pytest.mark.parametrize("lang", ["java", "gherkin", "", None, "sh -c 'x'"])
def test_a_fence_yields_no_speech_unit_whatever_its_language(lang):
    # ⛔ Narration is lesson prose only. A fence says
    # nothing, and no caption stands in for it.
    body = "Given a reading\nWhen it is written down\nThen the book agrees\n"
    assert said([{"type": "code", "lang": lang, "text": body}]) == []
    assert SPEECH_OF["code"] == "silent"


def test_prose_fence_prose_yields_exactly_the_two_prose_units_at_their_own_positions():
    fence = {"type": "code", "lang": "java", "text": "class A { void go() {} }"}
    blocks = [{"type": "para", "text": "Before it."}, fence, {"type": "para", "text": "After it."}]
    assert said(blocks) == [
        (f"{UNIT}.shared.b1", "Before it."),
        (f"{UNIT}.shared.b3", "After it."),
    ]


def test_a_list_is_read_item_by_item_under_its_own_marker():
    marker = SUB_MARKER["list"]
    assert said([{"type": "list", "ordered": False, "items": ["one", "two"]}]) == [
        (f"{UNIT}.shared.b1.{marker}1", "one"),
        (f"{UNIT}.shared.b1.{marker}2", "two"),
    ]


def test_an_ordered_list_numbers_each_item_aloud_in_words():
    pairs = said([{"type": "list", "ordered": True, "items": ["first thing", "second thing"]}])
    assert pairs[0][1].startswith("First, ")
    assert pairs[1][1].startswith("Second, ")


def test_a_nested_list_is_spoken_inside_its_parent_items_clip():
    # ⛔ One unit per top-level item, as before, and the nested items are
    # said in reading order inside it — numbered when that list is ordered.
    marker = SUB_MARKER["list"]
    nested = {"type": "list", "ordered": True, "items": ["zero", "one"]}
    block = {"type": "list", "ordered": False, "items": [["Version:", nested, "then more"], "b"]}
    assert said([block]) == [
        (f"{UNIT}.shared.b1.{marker}1", "Version: First, zero. Second, one. then more"),
        (f"{UNIT}.shared.b1.{marker}2", "b"),
    ]


def test_a_list_item_holding_a_code_part_speaks_its_prose_only():
    # ⛔ an item's code says what a top-level fence says: nothing at all.
    snippet = {"type": "code", "lang": "java", "text": "int[] a;"}
    block = {"type": "list", "ordered": True, "items": [["Return:", snippet, "then read it."]]}
    assert [words for _id, words in said([block])] == ["First, Return: then read it."]
    only_code = {"type": "list", "ordered": False, "items": [[snippet]]}
    assert said([only_code]) == [], "an item that is only code says nothing"


def test_an_ordered_list_counts_aloud_from_the_number_its_author_started_at():
    # ⛔ From the source: the continued step list says "Second", not "First".
    continued = parse("1. one\n\n```\nx\n```\n\n2. two\n3. three\n")[2]
    assert [words for _id, words in said([continued])] == ["Second, two", "Third, three"]


def test_a_nested_ordered_list_counts_aloud_from_its_own_start():
    nested = {"type": "list", "ordered": True, "items": ["x"], "start": 4}
    block = {"type": "list", "ordered": False, "items": [["a:", nested]]}
    assert said([block])[0][1] == "a: Fourth, x"


@pytest.mark.parametrize(("position", "word"), [(1, "First"), (20, "Twentieth"), (21, "Item 21")])
def test_an_ordinal_is_spelled_out_until_it_runs_out(position, word):
    assert ordinal_word(position) == word


def test_a_table_row_labels_each_cell_by_its_own_header():
    marker = SUB_MARKER["table"]
    pairs = said(
        [{"type": "table", "headers": ["Day", "Depth"], "rows": [["1", "2 mm"], ["2", "3 mm"]]}]
    )
    assert pairs[0] == (f"{UNIT}.shared.b1.{marker}1", "Day: 1. Depth: 2 mm.")
    assert pairs[1][0] == f"{UNIT}.shared.b1.{marker}2"


def test_a_header_row_is_never_spoken_on_its_own():
    # ⚠️ It is folded into every cell below it; saying it twice is how a table stops
    # being listenable.
    pairs = said([{"type": "table", "headers": ["Day"], "rows": [["1"]]}])
    assert len(pairs) == 1


def test_a_table_with_no_headers_numbers_its_rows_instead():
    pairs = said([{"type": "table", "headers": [], "rows": [["a", "b"]]}])
    assert pairs[0][1] == "Row 1: a, b"


# --------------------------------------------------------------------------
# ⛔ A disclosure's summary is spoken and its body is withheld
# --------------------------------------------------------------------------


def test_a_disclosures_summary_is_spoken_and_no_block_inside_it_has_an_id():
    block = {
        "type": "disclosure",
        "summary": "Why there is no exercise here",
        "open": False,
        "blocks": [{"type": "para", "text": "The answer the reader chose not to see."}],
    }
    pairs = said([block])
    assert pairs == [(f"{UNIT}.shared.b1", "Why there is no exercise here")]
    assert "answer" not in pairs[0][1]


def test_the_withheld_count_is_the_body_recursively():
    block = {
        "type": "disclosure",
        "summary": "Open me",
        "open": False,
        "blocks": [
            {"type": "para", "text": "one"},
            {"type": "quote", "blocks": [{"type": "para", "text": "nested"}]},
        ],
    }
    # the para, the quote, and the para inside the quote
    assert withheld([block]) == 3


def test_nothing_is_invented_to_announce_the_hidden_section():
    # ⛔ That would be narration writing prose the author did not.
    pairs = said(
        [
            {
                "type": "disclosure",
                "summary": "Label",
                "open": False,
                "blocks": [{"type": "para", "text": "x"}],
            }
        ]
    )
    assert pairs[0][1] == "Label"


def test_a_quote_is_walked_into_and_its_children_carry_a_nested_position():
    pairs = said([{"type": "quote", "blocks": [{"type": "para", "text": "quoted words"}]}])
    assert pairs == [(f"{UNIT}.shared.b1.b1", "quoted words")]


def test_a_quote_carries_no_unit_of_its_own():
    pairs = said([{"type": "quote", "blocks": []}])
    assert pairs == []


# --------------------------------------------------------------------------
# Numbering, emptiness, and the gate
# --------------------------------------------------------------------------


def test_an_empty_block_spends_its_number_and_shifts_nothing_after_it():
    pairs = said(
        [
            {"type": "para", "text": "first"},
            {"type": "para", "text": "   "},
            {"type": "para", "text": "third"},
        ]
    )
    assert [identifier for identifier, _words in pairs] == [
        f"{UNIT}.shared.b1",
        f"{UNIT}.shared.b3",
    ]


def test_a_figure_keeps_its_block_number_so_a_lesson_that_gains_one_renumbers_little():
    pairs = said(
        [
            {"type": "para", "text": "before"},
            {"type": "image", "src": "d.svg", "alt": "", "width": None},
            {"type": "para", "text": "after"},
        ]
    )
    assert [identifier for identifier, _words in pairs] == [
        f"{UNIT}.shared.b1",
        f"{UNIT}.shared.b3",
    ]


def test_the_gate_refuses_a_leaking_string():
    # ⛔ R7, re-entered here regardless of what ran upstream.
    with pytest.raises(PersonalDataLeak):
        said([{"type": "para", "text": f"The corpus lives at {HOME}/corpus."}])


def test_the_gate_refuses_a_leak_inside_a_list_item_and_a_table_cell():
    with pytest.raises(PersonalDataLeak):
        said([{"type": "list", "ordered": False, "items": [f"see {HOME}/x"]}])
    with pytest.raises(PersonalDataLeak):
        said([{"type": "table", "headers": ["Where"], "rows": [[f"{HOME}/x"]]}])


def test_an_r7_refusal_is_never_translated_into_this_packages_error_family():
    # ⛔ R7: a caller looping over a corpus must not log a leak as "that unit
    # did not narrate" and finish.
    with pytest.raises(PersonalDataLeak) as refused:
        said([{"type": "para", "text": f"at {HOME}/x"}])
    assert not isinstance(refused.value, SpeakableError)


def test_the_refusal_names_the_speech_id_rather_than_the_text():
    with pytest.raises(PersonalDataLeak) as refused:
        said([{"type": "para", "text": f"at {HOME}/x"}])
    message = str(refused.value)
    assert f"{UNIT}.shared.b1" in message
    assert "jane" not in message


def test_the_gate_refuses_rather_than_rewriting_what_the_source_said():
    # ⭐ `archive.scrub`'s own rule: scrub our words, refuse the source's. A clip that
    # quietly said a placeholder would be a rewritten record nobody could audit.
    with pytest.raises(PersonalDataLeak):
        said([{"type": "para", "text": f"{HOME}/corpus"}])


@pytest.mark.parametrize("blocks", [None, [], "not a list", 7, {}])
def test_a_section_with_no_blocks_says_nothing_and_does_not_raise(blocks):
    assert units_of(UNIT, "shared", blocks) == ((), 0)


# --------------------------------------------------------------------------
# ⛔ The emitter and the gate read as a pair, over the SHARED vocabulary
# --------------------------------------------------------------------------

#: Every shape that carries text into this module, named by where it carries it. ⭐ One
#: row per code path, because the defect a plant found was path-specific: the gate ran
#: on the *derived* string only, and the identifier splitter had already respaced
#: the machine-name shape into two words before the gate ever saw it.
CARRIERS = {
    "paragraph": lambda text: {"type": "para", "text": text},
    "heading": lambda text: {"type": "heading", "level": 2, "text": text},
    "list item": lambda text: {"type": "list", "ordered": False, "items": [text]},
    "ordered item": lambda text: {"type": "list", "ordered": True, "items": [text]},
    "table cell": lambda text: {"type": "table", "headers": ["Where"], "rows": [[text]]},
    "table header": lambda text: {"type": "table", "headers": [text], "rows": [["x"]]},
    "unlabelled cell": lambda text: {"type": "table", "headers": [], "rows": [[text]]},
    "disclosure summary": lambda text: {
        "type": "disclosure",
        "summary": text,
        "open": False,
        "blocks": [],
    },
    "quoted paragraph": lambda text: {
        "type": "quote",
        "blocks": [{"type": "para", "text": text}],
    },
}

REFUSED_SHAPES = [row for row in personal_data_shapes() if row["gate"] == "refuse"]
ADMITTED_SHAPES = [row for row in personal_data_shapes() if row["gate"] == "pass"]


def test_both_halves_of_the_shared_shape_vocabulary_are_inhabited():
    # ⛔ The populations, asserted before either property.
    assert len(REFUSED_SHAPES) >= 4, REFUSED_SHAPES
    assert len(ADMITTED_SHAPES) >= 4, ADMITTED_SHAPES
    assert len(CARRIERS) == 9


@pytest.mark.parametrize("carrier", sorted(CARRIERS))
@pytest.mark.parametrize("row", REFUSED_SHAPES, ids=lambda row: row["shape"])
def test_every_refusing_shape_is_refused_through_every_carrier(row, carrier):
    # ⛔ A local hostname in a list item would be ADMITTED if the gate ran only
    # after `split_identifier`, which destroys the dot the gate anchors on. The transform must not
    # be able to launder a leak.
    with pytest.raises(PersonalDataLeak):
        units_of(UNIT, "shared", [CARRIERS[carrier]("".join(row["spelling"]))])


@pytest.mark.parametrize("carrier", sorted(CARRIERS))
@pytest.mark.parametrize("row", ADMITTED_SHAPES, ids=lambda row: row["shape"])
def test_every_passing_shape_is_still_admitted_through_every_carrier(row, carrier):
    # ⭐ The other half of the pair. A gate that refused these would refuse a
    # legitimate corpus with a diagnosis that looks exactly like a leak.
    units_of(UNIT, "shared", [CARRIERS[carrier]("".join(row["spelling"]))])


def test_the_refusal_says_which_shape_and_never_what_matched():
    for row in REFUSED_SHAPES:
        with pytest.raises(PersonalDataLeak) as refused:
            units_of(UNIT, "shared", [{"type": "para", "text": "".join(row["spelling"])}])
        assert row["shape"].split()[-1] in str(refused.value)
        assert "jane" not in str(refused.value)


# --------------------------------------------------------------------------
# ⛔ A fence is silent at any depth, not only at a section's top level
# --------------------------------------------------------------------------

NESTED_FENCE = {"type": "code", "lang": "java", "text": "class A {}"}

#: A fence one container down, in each container type, with prose beside it.
NESTED = {
    "quote": {
        "type": "quote",
        "blocks": [{"type": "para", "text": "Quoted."}, NESTED_FENCE],
    },
    "disclosure": {
        "type": "disclosure",
        "summary": "Show it",
        "open": False,
        "blocks": [{"type": "para", "text": "Hidden."}, NESTED_FENCE],
    },
}


@pytest.mark.parametrize("container", sorted(NESTED))
def test_a_fence_nested_in_a_container_yields_no_speech_unit(container):
    # ⛔ Code is never spoken, whatever holds it.
    units, _held = units_of(UNIT, "shared", [NESTED[container]])
    assert [unit.block_path for unit in units if unit.kind == "code"] == []
    assert (0, 1) not in [unit.block_path for unit in units]
    # ⭐ The control: the container's own speech is still there.
    assert units, f"the {container} said nothing at all; the reading is vacuous"


# --------------------------------------------------------------------------
# ⛔ A heading over nothing spoken is silent (the code-examples ruling)
# --------------------------------------------------------------------------

#: One source and one test line of a lesson's code examples, as the archive writes them.
SOURCE_LINE = "Source: [Wrapper.java](../../m/src/main/java/p/Wrapper.java)"
TEST_LINE = "Test: [WrapperTest.java](../../m/src/test/java/p/WrapperTest.java)"


def listing(*items) -> dict:
    return {"type": "list", "ordered": False, "items": list(items)}


def test_a_heading_over_nothing_but_code_examples_is_silent():
    blocks = [
        {"type": "para", "text": "The lesson."},
        {"type": "heading", "level": 2, "text": "Code Examples"},
        listing(SOURCE_LINE, TEST_LINE),
    ]
    assert said(blocks) == [(f"{UNIT}.shared.b1", "The lesson.")]


def test_a_silent_subheading_leaves_nothing_spoken_under_the_heading_above_it():
    blocks = [
        {"type": "heading", "level": 2, "text": "Code Examples"},
        {"type": "heading", "level": 3, "text": "Wrapper"},
        listing(SOURCE_LINE),
        {"type": "heading", "level": 2, "text": "Afterwards"},
        {"type": "para", "text": "More prose."},
    ]
    assert said(blocks) == [
        (f"{UNIT}.shared.b4", "Afterwards"),
        (f"{UNIT}.shared.b5", "More prose."),
    ]


def test_a_heading_over_examples_and_prose_still_speaks():
    # ⭐ The control: something spoken under it, so it introduces something.
    blocks = [
        {"type": "heading", "level": 2, "text": "Code Examples"},
        listing(SOURCE_LINE),
        {"type": "para", "text": "Read the test first."},
    ]
    assert [identifier for identifier, _ in said(blocks)] == [
        f"{UNIT}.shared.b1",
        f"{UNIT}.shared.b3",
    ]


def test_a_heading_over_nothing_but_a_fence_or_nothing_at_all_still_speaks():
    # ⭐ The control: silence under a heading is not enough; a panel must be there.
    fence = {"type": "code", "lang": "java", "text": "class A {}"}
    assert said([{"type": "heading", "level": 2, "text": "Example"}, fence]) == [
        (f"{UNIT}.shared.b1", "Example")
    ]
    bare = [{"type": "heading", "level": 2, "text": "Alone"}]
    assert said(bare) == [(f"{UNIT}.shared.b1", "Alone")]


def test_a_silent_heading_is_still_gated_before_it_falls_silent():
    heading = {"type": "heading", "level": 2, "text": f"See {HOME}/notes"}
    with pytest.raises(PersonalDataLeak):
        said([heading, listing(SOURCE_LINE)])
