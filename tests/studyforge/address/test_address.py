"""Mirror of `src/studyforge/address/address.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import (
    SEPARATOR,
    Address,
    AddressError,
    parse_key,
    parse_unit_key,
    unit_name,
)

#: ⭐ **Spec §4's table, verbatim**, plus a synthetic depth 3 and depth 4 so the
#: acceptance's "depths 1 through 4" is met by material rather than by claim.
#: Two of the four real rows are **depth 1**; nothing here is written for two
#: levels and then checked against one.
#:
#: `(name, levels, segments, key, ordinal)`
ADDRESSES = [
    ("SPARQL", ["course"], ("sparql-tutorial",), "sparql-tutorial", 7),
    ("ISO-8583", ["group"], ("iso-fundamentals",), "iso-fundamentals", 2),
    (
        "Java-senior",
        ["section", "module"],
        ("concurrency", "23-executors"),
        "concurrency/23-executors",
        2,
    ),
    (
        "CodeSignal",
        ["path", "course"],
        ("kotlin-programming-for-beginners", "getting-started-with-kotlin"),
        "kotlin-programming-for-beginners/getting-started-with-kotlin",
        3,
    ),
    (
        "synthetic depth 3",
        ["track", "section", "module"],
        ("backend", "concurrency", "23-executors"),
        "backend/concurrency/23-executors",
        1,
    ),
    (
        "synthetic depth 4",
        ["programme", "track", "section", "module"],
        ("msc", "backend", "concurrency", "23-executors"),
        "msc/backend/concurrency/23-executors",
        11,
    ),
]

CASES = [pytest.param(*row[1:], id=row[0]) for row in ADDRESSES]


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_an_address_carries_its_key_and_its_depth(levels, segments, key, ordinal):
    address = Address(segments)
    assert address.key == key
    assert address.depth == len(levels)
    assert str(address) == key


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_a_key_round_trips_through_parse_key(levels, segments, key, ordinal):
    # ⭐ SF-01's acceptance, at depths 1 through 4: `parse_key` is a true
    # inverse of `.key`, which holds only because no slug can contain the
    # separator.
    assert parse_key(key, depth=len(levels)) == Address(segments)
    assert parse_key(key, depth=len(levels)).key == key


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_a_unit_key_round_trips_too(levels, segments, key, ordinal):
    address = Address(segments)
    unit_key = address.unit_key(ordinal)
    assert unit_key == f"{key}{SEPARATOR}{unit_name(ordinal)}"
    assert parse_unit_key(unit_key, depth=len(levels)) == (address, ordinal)


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_an_address_is_hashable_and_compares_by_value(levels, segments, key, ordinal):
    # Two addresses built the two documented ways are the same address, so a
    # set of them de-duplicates and a dict keyed on one works.
    assert Address(segments) == Address.of(*segments)
    assert len({Address(segments), Address.of(*segments)}) == 1


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_a_json_list_is_accepted_because_that_is_how_the_archive_stores_it(
    levels, segments, key, ordinal
):
    # `container.json` and every archive document spell an address as a JSON
    # array. Refusing a list would make every caller write the same
    # conversion, and one of them would eventually write it wrong.
    assert Address(list(segments)) == Address(segments)
    assert isinstance(Address(list(segments)).segments, tuple)


# --- arity: the SF-01/SF-02 boundary ---------------------------------------


def test_a_key_of_the_wrong_arity_for_a_declared_depth_is_rejected():
    # ⛔ SF-01's acceptance, and the failure it prevents is silent: a
    # two-segment key handed to a one-level corpus resolves to a container
    # that does not exist, and nothing says so.
    with pytest.raises(AddressError) as raised:
        parse_key("concurrency/23-executors", depth=1)
    message = str(raised.value)
    assert "2 segment" in message
    assert "1 level" in message


def test_a_one_segment_key_is_rejected_for_a_two_level_corpus():
    with pytest.raises(AddressError, match="declares 2 level"):
        parse_key("sparql-tutorial", depth=2)


def test_require_depth_is_available_on_its_own():
    # For a caller that already holds an address and a manifest.
    address = Address.of("basics", "01-getting-started")
    assert address.require_depth(2) is address
    with pytest.raises(AddressError):
        address.require_depth(1)


@pytest.mark.parametrize("depth", [0, -1, "2", None, True, 1.0])
def test_a_declared_depth_must_itself_be_a_positive_int(depth):
    with pytest.raises(AddressError, match="declared depth"):
        Address.of("basics").require_depth(depth)


def test_parse_key_will_not_let_you_skip_the_depth():
    # ⚠️ The generalisation the extraction source could hardcode: its
    # `parse_key` always checked arity, because the arity was always 2. Here
    # the number is data — so it is required, not optional, or a check that
    # always ran becomes one that usually does not.
    with pytest.raises(TypeError):
        parse_key("basics/01-getting-started")  # type: ignore[call-arg]


# --- what an address refuses -----------------------------------------------


@pytest.mark.parametrize(
    "segments",
    [
        ("Getting Started",),  # a title
        ("basics", "Getting Started"),  # a title in the second position
        ("basics", ""),  # an empty segment
        ("basics", None),
        ("basics", 7),
    ],
)
def test_an_address_refuses_a_segment_that_is_not_a_slug(segments):
    with pytest.raises(AddressError, match="address segment"):
        Address(segments)


def test_the_message_says_which_segment_of_how_many():
    with pytest.raises(AddressError) as raised:
        Address(("basics", "Getting Started"))
    assert "address segment 2 of 2" in str(raised.value)


@pytest.mark.parametrize("segments", [(), []])
def test_an_address_must_have_at_least_one_segment(segments):
    # Depth 0 is not a corpus shape; `levels` is non-empty by SF-02's own
    # acceptance, so an address with no segments cannot correspond to one.
    with pytest.raises(AddressError, match="at least one segment"):
        Address(segments)


@pytest.mark.parametrize("segments", ["basics", "basics/01-getting-started", 7, None])
def test_a_bare_string_is_not_a_sequence_of_segments(segments):
    # ⛔ The mistake this catches is `Address("basics/01-getting-started")`,
    # which would otherwise iterate the string into 26 one-character
    # "segments" and fail with a message about the letter 'b'.
    with pytest.raises(AddressError, match="list or tuple"):
        Address(segments)


def test_an_address_cannot_be_edited_after_it_is_validated():
    address = Address.of("basics", "01-getting-started")
    with pytest.raises(Exception):  # noqa: B017 — FrozenInstanceError is a dataclass detail
        address.segments = ("other",)  # type: ignore[misc]


# --- identifiers ------------------------------------------------------------


def test_identifiers_are_returned_per_segment_and_never_joined():
    # ⛔ How they join — a dotted package, a directory chain — is a placement
    # decision (SF-03). This package does not make placement decisions.
    address = Address.of("basics", "01-getting-started")
    assert address.identifiers == ("basics", "_01_getting_started")


@pytest.mark.parametrize("levels,segments,key,ordinal", CASES)
def test_every_address_has_one_identifier_per_segment(levels, segments, key, ordinal):
    assert len(Address(segments).identifiers) == len(segments)


# --- unit keys --------------------------------------------------------------


def test_a_unit_key_is_composed_in_exactly_one_place():
    address = Address.of("basics", "01-getting-started")
    assert address.unit_key(7) == "basics/01-getting-started/unit-07"


@pytest.mark.parametrize(
    "key",
    [
        "basics/01-getting-started/unit-7",  # unpadded
        "basics/01-getting-started/unit-007",  # over-padded
        "basics/01-getting-started/unit-",
        "basics/01-getting-started/unit-xx",
        "basics/01-getting-started/lesson-07",
        "unit-07",  # no address at all
    ],
)
def test_a_unit_key_that_is_not_the_one_we_write_is_refused(key):
    # ⛔ `unit-7` and `unit-007` both parse to 7 and would be written back as
    # `unit-07`, so two spellings of one unit would exist and compare unequal
    # on every surface that joins these keys by string equality.
    with pytest.raises(AddressError):
        parse_unit_key(key, depth=2)


def test_a_unit_key_of_the_wrong_arity_is_refused():
    with pytest.raises(AddressError, match="declares 1 level"):
        parse_unit_key("basics/01-getting-started/unit-07", depth=1)


@pytest.mark.parametrize("value", ["", None, 7])
def test_parse_functions_refuse_a_non_string(value):
    with pytest.raises(AddressError, match="non-empty str"):
        parse_key(value, depth=1)
    with pytest.raises(AddressError, match="non-empty str"):
        parse_unit_key(value, depth=1)
